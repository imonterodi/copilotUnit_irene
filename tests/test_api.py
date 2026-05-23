"""
Tests for Mergington High School Activities API
"""

from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_dict(self):
        """Test that /activities returns a dictionary of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that /activities returns expected activity names"""
        response = client.get("/activities")
        data = response.json()
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Swimming Club",
            "Art Club",
            "Choir",
            "Debate Club",
            "Math Olympiad"
        ]
        for activity in expected_activities:
            assert activity in data

    def test_get_activities_contains_activity_details(self):
        """Test that activities contain required fields"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self):
        """Test successful signup for an activity"""
        email = "testuser@mergington.edu"
        activity_name = "Swimming Club"
        
        # Get initial participant count
        initial_participants = len(activities[activity_name]["participants"])
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email.lower() in data["message"].lower()
        
        # Verify participant was added
        assert len(activities[activity_name]["participants"]) == initial_participants + 1
        assert email.lower() in activities[activity_name]["participants"]

    def test_signup_invalid_activity(self):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Non-Existent Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_duplicate_email(self):
        """Test signup with duplicate email returns 409 Conflict"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 409
        data = response.json()
        assert "already registered" in data["detail"].lower()

    def test_signup_invalid_email(self):
        """Test signup with empty email returns 400"""
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": ""}
        )
        assert response.status_code == 400
        data = response.json()
        assert "Invalid email" in data["detail"]

    def test_signup_activity_full(self):
        """Test signup when activity is full returns 400"""
        # Get an activity with limited spots
        activity_name = "Chess Club"
        activity = activities[activity_name]
        
        # Fill the activity completely
        activity["participants"] = [f"student{i}@mergington.edu" for i in range(activity["max_participants"])]
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "full" in data["detail"].lower()
        
        # Clean up - restore original participants
        activity["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]

    def test_signup_case_insensitive(self):
        """Test that signup handles email case-insensitivity"""
        activity_name = "Swimming Club"
        email_lower = "casetest@mergington.edu"
        
        # Sign up with lowercase
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_lower}
        )
        assert response1.status_code == 200
        
        # Try to sign up again with uppercase - should fail with 409
        email_upper = email_lower.upper()
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_upper}
        )
        assert response2.status_code == 409
        
        # Clean up
        activities[activity_name]["participants"].remove(email_lower)


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self):
        """Test successful unregister from an activity"""
        activity_name = "Art Club"
        email = "mia@mergington.edu"  # Already registered
        
        # Verify participant exists before unregister
        assert email in activities[activity_name]["participants"]
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email.lower() in data["message"].lower()
        
        # Verify participant was removed
        assert email not in activities[activity_name]["participants"]
        
        # Clean up - re-add the participant
        activities[activity_name]["participants"].append(email)

    def test_unregister_invalid_activity(self):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Non-Existent Club/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_participant_not_found(self):
        """Test unregister of non-existent participant returns 404"""
        activity_name = "Swimming Club"
        email = "notregistered@mergington.edu"
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_invalid_email(self):
        """Test unregister with empty email returns 400"""
        response = client.delete(
            "/activities/Programming Class/unregister",
            params={"email": ""}
        )
        assert response.status_code == 400
        data = response.json()
        assert "Invalid email" in data["detail"]

    def test_unregister_case_insensitive(self):
        """Test that unregister handles email case-insensitivity"""
        activity_name = "Debate Club"
        email_original = "liam@mergington.edu"
        email_upper = email_original.upper()
        
        # Verify original email exists
        assert email_original in activities[activity_name]["participants"]
        
        # Unregister with different case
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_upper}
        )
        
        assert response.status_code == 200
        
        # Verify participant was removed
        assert email_original not in activities[activity_name]["participants"]
        
        # Clean up - re-add the participant
        activities[activity_name]["participants"].append(email_original)


class TestIntegration:
    """Integration tests combining multiple endpoints"""

    def test_signup_and_unregister_flow(self):
        """Test complete signup and unregister flow"""
        activity_name = "Choir"
        email = "integration_test@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        assert email.lower() in activities[activity_name]["participants"]
        
        # Verify in activities list
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email.lower() in activities_data[activity_name]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        assert email.lower() not in activities[activity_name]["participants"]
