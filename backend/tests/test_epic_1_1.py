from fastapi.testclient import TestClient
from backend.main import app
import os

client = TestClient(app)

def test_epic_1_1_e2e_flow():
    # 1. Create Mission
    mission_data = {
        "title": "Test E2E Mission",
        "career_goal": "Software Engineer"
    }
    response = client.post("/api/v1/missions", json=mission_data)
    assert response.status_code == 200
    mission = response.json()["mission"]
    mission_id = mission["id"]
    assert mission_id is not None
    
    # 2. Upload CV (mock file)
    files = {"file": ("test_cv.pdf", b"mock pdf content", "application/pdf")}
    response = client.post(f"/api/v1/missions/{mission_id}/resume", files=files)
    assert response.status_code == 200
    assert response.json()["status"] == "uploaded"
    
    # 3. Get Mission
    response = client.get(f"/api/v1/missions/{mission_id}")
    assert response.status_code == 200
    mission_retrieved = response.json()["mission"]
    assert "resume_path" in mission_retrieved["metadata"]
    assert os.path.exists(mission_retrieved["metadata"]["resume_path"])
    
    # 4. Trigger Run (Engine)
    response = client.post(f"/api/v1/missions/{mission_id}/run")
    assert response.status_code == 200
    assert response.json()["status"] == "engine_triggered"
    
    # 5. Check Timeline
    response = client.get(f"/api/v1/missions/{mission_id}/timeline")
    assert response.status_code == 200
    assert "timeline" in response.json()

if __name__ == "__main__":
    test_epic_1_1_e2e_flow()
    print("All Epic 1.1 E2E tests passed successfully!")
