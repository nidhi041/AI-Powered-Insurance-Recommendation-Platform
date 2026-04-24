from fastapi.testclient import TestClient
from app.main import app
from app.routes.recommend import _build_rag_query
from app.models.policy import UserProfile

client = TestClient(app)

def test_read_main():
    """Test the root endpoint for health status."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "AI Insurance Recommendation API" in response.json()["service"]

def test_health_check():
    """Test the liveness probe."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_query_builder():
    """Test the internal RAG query builder logic."""
    profile = UserProfile(
        full_name="Rahul Sharma",
        age=30,
        lifestyle="Active",
        conditions=["Diabetes", "None"],
        income="3-8L",
        city="Metro"
    )
    query = _build_rag_query(profile)
    assert "Rahul Sharma" not in query # Privacy: name shouldn't be in context
    assert "Diabetes" in query
    assert "Metro" in query
    assert "waiting period" in query.lower()
