import copy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = copy.deepcopy(activities)


def pytest_configure():
    # Ensure the in-memory activities dataset is reset before tests run.
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def setup_function():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity():
    email = "teststudent@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "duplicate@mergington.edu"
    response = client.post(f"/activities/Gym%20Class/signup?email={email}")
    assert response.status_code == 200

    duplicate_response = client.post(f"/activities/Gym%20Class/signup?email={email}")
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up"


def test_remove_participant():
    email = "remove_test@mergington.edu"
    activities["Programming Class"]["participants"].append(email)

    response = client.delete(f"/activities/Programming%20Class/participants?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Programming Class"
    assert email not in activities["Programming Class"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    response = client.delete("/activities/Programming%20Class/participants?email=missing@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_from_invalid_activity_returns_404():
    response = client.delete("/activities/Nonexistent/participants?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
