import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_participants():
    # Reset participants before each test
    for activity in activities.values():
        activity["participants"] = []


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Soccer Team" in data


def test_signup_for_activity():
    email = "test@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    # Try duplicate signup
    response2 = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Student already signed up for this activity"


def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=foo@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity():
    email = "remove@mergington.edu"
    # First, sign up
    client.post(f"/activities/Art Club/signup?email={email}")
    assert email in activities["Art Club"]["participants"]
    # Now, unregister
    response = client.post(f"/activities/Art Club/unregister?email={email}")
    assert response.status_code == 200
    assert email not in activities["Art Club"]["participants"]
    # Try to unregister again
    response2 = client.post(f"/activities/Art Club/unregister?email={email}")
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Student not registered for this activity"


def test_unregister_activity_not_found():
    response = client.post("/activities/Nonexistent/unregister?email=foo@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
