import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesAPI:
    def test_get_activities_success(self):
        """Test GET /activities returns all activities."""
        # Arrange: No special setup needed, activities are predefined

        # Act: Make the GET request
        response = client.get("/activities")

        # Assert: Check status and response structure
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        # Verify structure of one activity
        chess = data["Chess Club"]
        assert "description" in chess
        assert "schedule" in chess
        assert "max_participants" in chess
        assert "participants" in chess
        assert isinstance(chess["participants"], list)

    def test_signup_success(self):
        """Test POST /signup for a valid activity and new email."""
        # Arrange: Choose an activity with available spots
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"

        # Act: Make the POST request
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Check success response
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Signed up {email} for {activity_name}" in data["message"]
        # Verify added to participants
        get_response = client.get("/activities")
        assert email in get_response.json()[activity_name]["participants"]

    def test_signup_activity_not_found(self):
        """Test POST /signup for a non-existent activity."""
        # Arrange: Use invalid activity name
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"

        # Act: Make the POST request
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Check error response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_already_signed_up(self):
        """Test POST /signup when student is already signed up."""
        # Arrange: Sign up first, then try again
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in list

        # Act: Make the POST request
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Check error response
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student already signed up for this activity" in data["detail"]

    def test_signup_activity_full(self):
        """Test POST /signup when activity is at capacity."""
        # Arrange: Fill an activity to capacity (Art Club has max 10, starts empty)
        activity_name = "Art Club"
        emails = [f"student{i}@mergington.edu" for i in range(10)]
        for email in emails:
            client.post(f"/activities/{activity_name}/signup?email={email}")
        new_email = "overflow@mergington.edu"

        # Act: Try to sign up one more
        response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

        # Assert: Check error response
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Activity is full" in data["detail"]

    def test_remove_success(self):
        """Test POST /remove for a valid activity and enrolled email."""
        # Arrange: Sign up first, then remove
        activity_name = "Soccer Club"
        email = "removeme@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act: Make the POST request
        response = client.post(f"/activities/{activity_name}/remove?email={email}")

        # Assert: Check success response
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Removed {email} from {activity_name}" in data["message"]
        # Verify removed from participants
        get_response = client.get("/activities")
        assert email not in get_response.json()[activity_name]["participants"]

    def test_remove_activity_not_found(self):
        """Test POST /remove for a non-existent activity."""
        # Arrange: Use invalid activity name
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"

        # Act: Make the POST request
        response = client.post(f"/activities/{activity_name}/remove?email={email}")

        # Assert: Check error response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_remove_not_signed_up(self):
        """Test POST /remove when student is not signed up."""
        # Arrange: Use activity with no participants
        activity_name = "Debate Club"
        email = "notsignedup@mergington.edu"

        # Act: Make the POST request
        response = client.post(f"/activities/{activity_name}/remove?email={email}")

        # Assert: Check error response
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student not signed up for this activity" in data["detail"]