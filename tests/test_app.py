import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_count = len(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == expected_count
    assert "Chess Club" in data


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "newstudent@mergington.edu"
    assert participant_email not in activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": participant_email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {participant_email} for {activity_name}"}
    assert participant_email in activities[activity_name]["participants"]


def test_signup_existing_participant_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    participant_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": participant_email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_unknown_activity_returns_not_found():
    # Arrange
    unknown_activity = "Unknown Club"
    participant_email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(unknown_activity)}/signup",
        params={"email": participant_email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Programming Class"
    participant_email = activities[activity_name]["participants"][0]
    assert participant_email in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(participant_email)}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {participant_email} from {activity_name}"}
    assert participant_email not in activities[activity_name]["participants"]


def test_remove_unknown_participant_returns_not_found():
    # Arrange
    activity_name = "Drama Club"
    unknown_email = "unknown@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(unknown_email)}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_from_unknown_activity_returns_not_found():
    # Arrange
    unknown_activity = "Unknown Club"
    participant_email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(unknown_activity)}/participants/{quote(participant_email)}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
