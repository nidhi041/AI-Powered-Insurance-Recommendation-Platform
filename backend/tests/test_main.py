import unittest
import os
import tempfile
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.routes.recommend import _build_rag_query
from app.models.policy import UserProfile
from app.services import document_store


class MainApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_read_main(self):
        """Test the root endpoint for health status."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
        self.assertIn("AI Insurance Recommendation API", response.json()["service"])

    def test_health_check(self):
        """Test the liveness probe."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_query_builder(self):
        """Test the internal RAG query builder logic."""
        profile = UserProfile(
            full_name="Rahul Sharma",
            age=30,
            lifestyle="Active",
            conditions=["Diabetes", "None"],
            income="3-8L",
            city="Metro",
        )
        query = _build_rag_query(profile)
        self.assertNotIn("Rahul Sharma", query)  # Privacy check
        self.assertIn("Diabetes", query)
        self.assertIn("Metro", query)
        self.assertIn("waiting period", query.lower())


class DocumentStoreTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        settings.DOCUMENT_DB_PATH = self.temp_db.name
        document_store.init_db()

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_document_lifecycle(self):
        """Test document creation, status updates, duplicate guard, and deletion."""
        # 1. Create document
        doc_id = document_store.create_document_record(
            filename="hdfc_optima.pdf",
            original_filename="hdfc_optima.pdf",
            file_size_bytes=10240,
            file_hash="mock_hash_12345",
        )
        self.assertIsNotNone(doc_id)

        # 2. Retrieve document
        doc = document_store.get_document(doc_id)
        self.assertIsNotNone(doc)
        self.assertEqual(doc["filename"], "hdfc_optima.pdf")
        self.assertEqual(doc["processing_status"], "pending")

        # 3. Duplicate check with same hash
        dup_id = document_store.create_document_record(
            filename="hdfc_optima.pdf",
            original_filename="hdfc_optima.pdf",
            file_size_bytes=10240,
            file_hash="mock_hash_12345",
        )
        self.assertIsNone(dup_id)

        # 4. Update status to processing -> completed
        document_store.update_status(doc_id, "processing")
        doc_processing = document_store.get_document(doc_id)
        self.assertEqual(doc_processing["processing_status"], "processing")

        document_store.update_status(doc_id, "completed", chunk_count=12)
        doc_completed = document_store.get_document(doc_id)
        self.assertEqual(doc_completed["processing_status"], "completed")
        self.assertEqual(doc_completed["chunk_count"], 12)

        # 5. List all documents
        all_docs = document_store.list_all_documents()
        self.assertEqual(len(all_docs), 1)
        self.assertEqual(all_docs[0]["id"], doc_id)

        # 6. Delete document
        deleted = document_store.delete_document_record(doc_id)
        self.assertTrue(deleted)
        self.assertIsNone(document_store.get_document(doc_id))


class AdminEndpointsTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        settings.DOCUMENT_DB_PATH = self.temp_db.name
        document_store.init_db()
        self.client = TestClient(app)
        self.auth = (settings.ADMIN_USERNAME, settings.ADMIN_PASSWORD)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_list_and_get_documents_admin(self):
        doc_id = document_store.create_document_record(
            filename="star_health.pdf",
            original_filename="star_health.pdf",
            file_size_bytes=2048,
            file_hash="star_hash_999",
        )

        # Unauthorized check
        res_unauth = self.client.get("/admin/documents")
        self.assertEqual(res_unauth.status_code, 401)

        # Authorized list
        res = self.client.get("/admin/documents", auth=self.auth)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["documents"][0]["id"], doc_id)

        # Get status endpoint
        res_status = self.client.get(f"/admin/documents/{doc_id}", auth=self.auth)
        self.assertEqual(res_status.status_code, 200)
        self.assertEqual(res_status.json()["id"], doc_id)

        # Delete document endpoint
        res_del = self.client.delete(f"/admin/documents/{doc_id}", auth=self.auth)
        self.assertEqual(res_del.status_code, 200)
        self.assertEqual(res_del.json()["deleted_id"], doc_id)

        # Verify it is gone
        res_empty = self.client.get("/admin/documents", auth=self.auth)
        self.assertEqual(res_empty.json()["total"], 0)


if __name__ == "__main__":
    unittest.main()
