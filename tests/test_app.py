import os
import sys

# Ensure src/ is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastapi.testclient import TestClient

from app import app


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball" in data


def test_signup_and_unregister_flow():
    client = TestClient(app)
    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure the test email is not currently registered for the activity
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    participants = data.get(activity, {}).get("participants", [])
    if email in participants:
        client.delete(f"/activities/{activity}/unregister?email={email}")

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Confirm participant now present
    resp = client.get("/activities")
    data = resp.json()
    assert email in data[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Confirm participant removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]
