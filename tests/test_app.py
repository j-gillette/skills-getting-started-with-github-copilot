import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create a test client
client = TestClient(app)


class TestActivities:
    """Test suite for the activities endpoints"""
    
    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) > 0
    
    def test_activity_structure(self):
        """Test that activities have the required structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Test suite for the signup endpoint"""
    
    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@example.com"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@example.com" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_nonexistent_activity(self):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@example.com"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate(self):
        """Test that a student cannot sign up twice for the same activity"""
        email = "duplicate@example.com"
        activity = "Tennis%20Club"
        
        # First signup should succeed
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_adds_participant(self):
        """Test that signup actually adds a participant to the activity"""
        email = "participant@example.com"
        activity = "Drama%20Club"
        
        # Get initial participants count
        response_before = client.get("/activities")
        participants_before = len(response_before.json()["Drama Club"]["participants"])
        
        # Signup
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get updated participants count
        response_after = client.get("/activities")
        participants_after = len(response_after.json()["Drama Club"]["participants"])
        
        assert participants_after == participants_before + 1


class TestUnregister:
    """Test suite for the unregister endpoint"""
    
    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        email = "unregister@example.com"
        activity = "Digital%20Art"
        
        # First, sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_nonexistent_activity(self):
        """Test unregister from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/signup?email=test@example.com"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered(self):
        """Test unregistering someone who isn't registered"""
        response = client.delete(
            "/activities/Science%20Club/signup?email=notregistered@example.com"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_removes_participant(self):
        """Test that unregister actually removes a participant"""
        email = "remove@example.com"
        activity = "Debate%20Team"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get participants before unregister
        response_before = client.get("/activities")
        participants_before = response_before.json()["Debate Team"]["participants"]
        assert email in participants_before
        
        # Unregister
        client.delete(f"/activities/{activity}/signup?email={email}")
        
        # Get participants after unregister
        response_after = client.get("/activities")
        participants_after = response_after.json()["Debate Team"]["participants"]
        assert email not in participants_after


class TestRoot:
    """Test suite for the root endpoint"""
    
    def test_redirect_to_static(self):
        """Test that root redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "static/index.html" in response.headers["location"]
