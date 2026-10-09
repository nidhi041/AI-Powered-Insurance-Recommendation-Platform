import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from chromadb.api.types import EmbeddingFunction

from app.config import settings
from app.main import app
from app.services import document_store, rag_service


class TestEmbeddingFunction(EmbeddingFunction[list[str]]):
    def __init__(self):
        pass

    @staticmethod
    def name():
        return "test_embedding"

    @staticmethod
    def build_from_config(config):
        return TestEmbeddingFunction()

    def get_config(self):
        return {}

    def __call__(self, input):
        return [[float(len(text)), 1.0, 0.5] for text in input]


def _make_text_pdf(text: str) -> bytes:
    content = (
        f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET"
    ).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ),
        (
            f"<< /Length {len(content)} >>\nstream\n".encode("ascii")
            + content
            + b"\nendstream"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_number} 0 obj\n".encode("ascii"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF"
        ).encode("ascii")
    )
    return bytes(pdf)


class RecommendationFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_chroma_path = settings.CHROMA_PERSIST_DIR
        self.previous_db_path = settings.DOCUMENT_DB_PATH
        settings.CHROMA_PERSIST_DIR = str(Path(self.temp_dir.name) / "chroma")
        settings.DOCUMENT_DB_PATH = str(Path(self.temp_dir.name) / "documents.db")
        self._reset_chroma()
        self.embedding_patch = patch(
            "app.services.rag_service.ONNXMiniLM_L6_V2",
            return_value=TestEmbeddingFunction(),
        )
        self.embedding_patch.start()
        document_store.init_db()
        self.client = TestClient(app)

    def tearDown(self):
        self.embedding_patch.stop()
        self._reset_chroma()
        settings.CHROMA_PERSIST_DIR = self.previous_chroma_path
        settings.DOCUMENT_DB_PATH = self.previous_db_path
        self.temp_dir.cleanup()

    @staticmethod
    def _reset_chroma():
        if rag_service._chroma_client is not None:
            rag_service._chroma_client.close()
        rag_service._collection = None
        rag_service._chroma_client = None
        rag_service._embedding_fn = None

    @staticmethod
    def _profile():
        return {
            "full_name": "Test Member",
            "age": 42,
            "lifestyle": "Moderate",
            "conditions": ["Diabetes"],
            "income": "3-8L",
            "city": "Metro",
        }

    def test_uploaded_pdf_chunks_are_retrieved_for_recommendation(self):
        pdf_text = (
            "Health policy covers diabetes after a four year waiting period. "
            "The policy provides hospital coverage and cashless claims."
        )

        upload = self.client.post(
            "/upload-policy",
            files={"file": ("policy.pdf", _make_text_pdf(pdf_text), "application/pdf")},
            auth=(settings.ADMIN_USERNAME, settings.ADMIN_PASSWORD),
        )
        self.assertEqual(upload.status_code, 202, upload.text)
        doc_id = upload.json()["document_id"]

        status_response = self.client.get(
            f"/admin/documents/{doc_id}",
            auth=(settings.ADMIN_USERNAME, settings.ADMIN_PASSWORD),
        )
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json()["processing_status"], "completed")

        # Reopen the persisted Chroma directory as a fresh retrieval client.
        indexed_collection = rag_service._get_collection()
        self.assertEqual(indexed_collection.name, "insurance_policies")
        self.assertEqual(indexed_collection.count(), 1)
        stored = indexed_collection.get(
            where={"document_id": doc_id},
            include=["documents", "metadatas"],
        )
        self.assertEqual(stored["metadatas"][0]["source"], "policy.pdf")
        self._reset_chroma()

        from app.routes import recommend

        recommendation = {
            "comparison_table": [],
            "coverage_details": {
                "inclusions": "Hospital coverage",
                "exclusions": "Not listed",
                "sub_limits": "Not listed",
                "copay": "Not listed",
                "claim_type": "Cashless",
            },
            "why_this_policy": "Grounded in the uploaded policy.",
        }
        with patch.object(
            recommend,
            "generate_recommendation",
            return_value=recommend.RecommendationResponse(**recommendation),
        ) as generate:
            response = self.client.post("/recommend", json=self._profile())

        self.assertEqual(response.status_code, 200, response.text)
        retrieved_documents = generate.call_args.kwargs["documents"]
        self.assertTrue(any("four year waiting period" in text for text in retrieved_documents))

    def test_empty_knowledge_base_returns_clear_service_unavailable(self):
        response = self.client.post("/recommend", json=self._profile())

        self.assertEqual(response.status_code, 503)
        self.assertIn("No indexed policy documents", response.json()["detail"])

    def test_completed_metadata_without_vector_chunks_is_reported_as_unavailable(self):
        doc_id = document_store.create_document_record(
            filename="completed-but-missing.pdf",
            original_filename="completed-but-missing.pdf",
            file_size_bytes=100,
            file_hash="completed-without-vectors",
        )
        document_store.update_status(doc_id, "completed", chunk_count=1)

        response = self.client.post("/recommend", json=self._profile())

        self.assertEqual(response.status_code, 503)
        self.assertIn("no indexed policy chunks are available", response.json()["detail"])

    def test_pending_and_failed_documents_are_not_reported_as_empty(self):
        for processing_status, expected_detail in (
            ("processing", "still being indexed"),
            ("failed", "indexing failed"),
        ):
            with self.subTest(processing_status=processing_status):
                doc_id = document_store.create_document_record(
                    filename=f"{processing_status}.pdf",
                    original_filename=f"{processing_status}.pdf",
                    file_size_bytes=100,
                    file_hash=f"hash-{processing_status}",
                )
                document_store.update_status(doc_id, processing_status)

                response = self.client.post("/recommend", json=self._profile())

                self.assertEqual(response.status_code, 503)
                self.assertIn(expected_detail, response.json()["detail"])
                document_store.delete_document_record(doc_id)

    def test_embedding_initialization_error_is_logged_and_sanitized(self):
        with patch(
            "app.services.rag_service.ONNXMiniLM_L6_V2",
            side_effect=RuntimeError("private embedding model detail"),
        ):
            with self.assertLogs("app.routes.recommend", level=logging.ERROR):
                response = self.client.post("/recommend", json=self._profile())

        self.assertEqual(response.status_code, 503)
        self.assertIn("embedding model is unavailable", response.json()["detail"])
        self.assertNotIn("private embedding model detail", response.text)

    def test_retrieval_and_database_errors_are_logged_and_sanitized(self):
        from app.routes import recommend

        with patch.object(
            recommend,
            "query_documents",
            side_effect=rag_service.VectorStoreError("private backend detail"),
        ):
            with self.assertLogs("app.routes.recommend", level=logging.ERROR):
                response = self.client.post("/recommend", json=self._profile())

        self.assertEqual(response.status_code, 503)
        self.assertIn("Policy index storage is unavailable", response.json()["detail"])
        self.assertNotIn("private backend detail", response.text)

        with patch.object(recommend, "query_documents", return_value=[]):
            with patch.object(
                document_store,
                "list_all_documents",
                side_effect=RuntimeError("private database detail"),
            ):
                with self.assertLogs("app.routes.recommend", level=logging.ERROR):
                    response = self.client.post("/recommend", json=self._profile())

        self.assertEqual(response.status_code, 503)
        self.assertIn("status database is unavailable", response.json()["detail"])
        self.assertNotIn("private database detail", response.text)

    def test_indexed_but_unretrievable_chunks_have_a_distinct_response(self):
        from app.routes import recommend

        with patch.object(
            recommend,
            "query_documents",
            side_effect=rag_service.IndexedPolicyRetrievalError("private index details"),
        ):
            with self.assertLogs("app.routes.recommend", level=logging.ERROR):
                response = self.client.post("/recommend", json=self._profile())

        self.assertEqual(response.status_code, 503)
        self.assertIn("chunks are indexed but could not be retrieved", response.json()["detail"])
        self.assertNotIn("private index details", response.text)

    def test_llm_errors_are_logged_and_not_exposed(self):
        from app.routes import recommend

        with patch.object(recommend, "query_documents", return_value=["indexed policy clause"]):
            with patch.object(
                recommend,
                "generate_recommendation",
                side_effect=RuntimeError("secret provider response"),
            ):
                with self.assertLogs("app.routes.recommend", level=logging.ERROR):
                    response = self.client.post("/recommend", json=self._profile())

        self.assertEqual(response.status_code, 502)
        self.assertIn("temporarily unavailable", response.json()["detail"])
        self.assertNotIn("secret provider response", response.text)


if __name__ == "__main__":
    unittest.main()
