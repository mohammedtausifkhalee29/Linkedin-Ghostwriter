"""Tests for posts API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json


class TestGeneratePostEndpoint:
    """Tests for POST /api/v1/posts/generate endpoint."""
    
    def test_generate_post_success(self, client, auth_headers):
        """Test successful post generation."""
        request_data = {
            "post_type": "Story",
            "message": "Just completed a major AI project",
            "tone": "professional"
        }
        
        response = client.post(
            "/api/v1/posts/generate",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "content" in data
        assert "post_type" in data
        assert "tone" in data
        assert data["post_type"] == "Story"
        assert data["tone"] == "professional"
        assert data["status"] == "draft"
    
    def test_generate_post_with_reference_text(self, client, auth_headers, sample_txt_file):
        """Test post generation with reference text from file upload."""
        filename, content = sample_txt_file
        
        request_data = {
            "post_type": "How-to Guide",
            "message": "Guide to productivity",
            "tone": "educational",
            "reference_text": content.decode('utf-8')
        }
        
        response = client.post(
            "/api/v1/posts/generate",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert len(data["content"]) > 0
    
    def test_generate_post_all_types(self, client, auth_headers):
        """Test generating posts of all types."""
        post_types = ["Story", "Listicle", "How-to Guide", "Case Study", 
                      "Opinion Piece", "Industry News", "Personal Achievement"]
        
        for post_type in post_types:
            request_data = {
                "post_type": post_type,
                "message": f"Test message for {post_type}",
                "tone": "professional"
            }
            
            response = client.post(
                "/api/v1/posts/generate",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["post_type"] == post_type
    
    def test_generate_post_all_tones(self, client, auth_headers):
        """Test generating posts with all tones."""
        tones = ["professional", "casual", "inspiring", "educational", 
                 "humorous", "thought-provoking"]
        
        for tone in tones:
            request_data = {
                "post_type": "Story",
                "message": f"Test message with {tone} tone",
                "tone": tone
            }
            
            response = client.post(
                "/api/v1/posts/generate",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["tone"] == tone
    
    def test_generate_post_unauthorized(self, client):
        """Test post generation without authentication."""
        request_data = {
            "post_type": "Story",
            "message": "Test message",
            "tone": "professional"
        }
        
        response = client.post("/api/v1/posts/generate", json=request_data)
        assert response.status_code == 401
    
    def test_generate_post_invalid_type(self, client, auth_headers):
        """Test post generation with invalid post type."""
        request_data = {
            "post_type": "InvalidType",
            "message": "Test message",
            "tone": "professional"
        }
        
        response = client.post(
            "/api/v1/posts/generate",
            json=request_data,
            headers=auth_headers
        )
        
        # Should either succeed with any type or return error
        assert response.status_code in [200, 400, 422]
    
    def test_generate_post_empty_message(self, client, auth_headers):
        """Test post generation with empty message."""
        request_data = {
            "post_type": "Story",
            "message": "",
            "tone": "professional"
        }
        
        response = client.post(
            "/api/v1/posts/generate",
            json=request_data,
            headers=auth_headers
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_generate_post_missing_fields(self, client, auth_headers):
        """Test post generation with missing required fields."""
        request_data = {
            "post_type": "Story"
            # Missing message and tone
        }
        
        response = client.post(
            "/api/v1/posts/generate",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error


class TestSaveDraftEndpoint:
    """Tests for POST /api/v1/posts/draft endpoint."""
    
    def test_save_draft_success(self, client, auth_headers):
        """Test successfully saving a draft."""
        request_data = {
            "post_type": "Story",
            "message": "Draft post content",
            "tone": "professional",
            "content": "This is my draft LinkedIn post content.",
            "reference_text": "Some reference material"
        }
        
        response = client.post(
            "/api/v1/posts/draft",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "status" in data
        assert data["status"] == "draft"
        assert data["content"] == request_data["content"]
    
    def test_save_draft_unauthorized(self, client):
        """Test saving draft without authentication."""
        request_data = {
            "post_type": "Story",
            "message": "Test",
            "tone": "professional",
            "content": "Draft content"
        }
        
        response = client.post("/api/v1/posts/draft", json=request_data)
        assert response.status_code == 401


class TestSendPostEndpoint:
    """Tests for POST /api/v1/posts/send endpoint."""
    
    @patch('app.services.notification_service.NotificationService.send_telegram')
    def test_send_post_telegram_success(self, mock_send, client, auth_headers, test_post):
        """Test sending post via Telegram."""
        mock_send.return_value = {"success": True, "message": "Sent via Telegram"}
        
        request_data = {
            "post_id": test_post.id,
            "post_content": "Test LinkedIn post content",
            "channel": "telegram"
        }
        
        response = client.post(
            "/api/v1/posts/send",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "telegram" in data["message"].lower()
    
    @patch('app.services.notification_service.NotificationService.send_email')
    def test_send_post_email_success(self, mock_send, client, auth_headers, test_post):
        """Test sending post via email."""
        mock_send.return_value = {"success": True, "message": "Sent via email"}
        
        request_data = {
            "post_id": test_post.id,
            "post_content": "Test LinkedIn post content",
            "channel": "email"
        }
        
        response = client.post(
            "/api/v1/posts/send",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "email" in data["message"].lower()
    
    def test_send_post_invalid_channel(self, client, auth_headers, test_post):
        """Test sending post with invalid channel."""
        request_data = {
            "post_id": test_post.id,
            "post_content": "Test content",
            "channel": "invalid_channel"
        }
        
        response = client.post(
            "/api/v1/posts/send",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]
    
    def test_send_post_unauthorized(self, client, test_post):
        """Test sending post without authentication."""
        request_data = {
            "post_id": test_post.id,
            "post_content": "Test content",
            "channel": "telegram"
        }
        
        response = client.post("/api/v1/posts/send", json=request_data)
        assert response.status_code == 401


class TestGetPostsEndpoint:
    """Tests for GET /api/v1/posts endpoint."""
    
    def test_get_all_posts(self, client, auth_headers, test_post):
        """Test retrieving all posts."""
        response = client.get("/api/v1/posts", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check post structure
        post = data[0]
        assert "id" in post
        assert "content" in post
        assert "post_type" in post
        assert "tone" in post
        assert "status" in post
    
    def test_get_posts_filter_by_status(self, client, auth_headers, db_session, test_user):
        """Test filtering posts by status."""
        # Create posts with different statuses
        from app.db.models import Post
        
        draft_post = Post(
            user_id=test_user.id,
            post_type="Story",
            tone="professional",
            content="Draft post",
            status="draft"
        )
        published_post = Post(
            user_id=test_user.id,
            post_type="Story",
            tone="professional",
            content="Published post",
            status="published"
        )
        
        db_session.add_all([draft_post, published_post])
        db_session.commit()
        
        # Filter drafts
        response = client.get("/api/v1/posts?status=draft", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(post["status"] == "draft" for post in data)
        
        # Filter published
        response = client.get("/api/v1/posts?status=published", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(post["status"] == "published" for post in data)
    
    def test_get_posts_unauthorized(self, client):
        """Test retrieving posts without authentication."""
        response = client.get("/api/v1/posts")
        assert response.status_code == 401
    
    def test_get_posts_empty_list(self, client, auth_headers, db_session):
        """Test retrieving posts when none exist."""
        # Delete all posts for the user
        from app.db.models import Post
        db_session.query(Post).delete()
        db_session.commit()
        
        response = client.get("/api/v1/posts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestGetSinglePostEndpoint:
    """Tests for GET /api/v1/posts/{post_id} endpoint."""
    
    def test_get_post_by_id(self, client, auth_headers, test_post):
        """Test retrieving a specific post by ID."""
        response = client.get(f"/api/v1/posts/{test_post.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_post.id
        assert data["content"] == test_post.content
        assert data["post_type"] == test_post.post_type
    
    def test_get_nonexistent_post(self, client, auth_headers):
        """Test retrieving a non-existent post."""
        response = client.get("/api/v1/posts/99999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_get_post_unauthorized(self, client, test_post):
        """Test retrieving post without authentication."""
        response = client.get(f"/api/v1/posts/{test_post.id}")
        assert response.status_code == 401


class TestDeletePostEndpoint:
    """Tests for DELETE /api/v1/posts/{post_id} endpoint."""
    
    def test_delete_post_success(self, client, auth_headers, test_post):
        """Test successfully deleting a post."""
        post_id = test_post.id
        
        response = client.delete(f"/api/v1/posts/{post_id}", headers=auth_headers)
        
        assert response.status_code == 200
        
        # Verify post is deleted
        get_response = client.get(f"/api/v1/posts/{post_id}", headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_post(self, client, auth_headers):
        """Test deleting a non-existent post."""
        response = client.delete("/api/v1/posts/99999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_delete_post_unauthorized(self, client, test_post):
        """Test deleting post without authentication."""
        response = client.delete(f"/api/v1/posts/{test_post.id}")
        assert response.status_code == 401


class TestEndToEndWorkflows:
    """End-to-end workflow tests."""
    
    def test_complete_post_workflow(self, client, auth_headers):
        """Test complete workflow: generate → save draft → send."""
        # Step 1: Generate a post
        generate_data = {
            "post_type": "Story",
            "message": "E2E test post",
            "tone": "professional"
        }
        
        generate_response = client.post(
            "/api/v1/posts/generate",
            json=generate_data,
            headers=auth_headers
        )
        
        assert generate_response.status_code == 200
        post_data = generate_response.json()
        post_id = post_data["id"]
        
        # Step 2: Retrieve the post
        get_response = client.get(f"/api/v1/posts/{post_id}", headers=auth_headers)
        assert get_response.status_code == 200
        
        # Step 3: Send the post (with mocking)
        with patch('app.services.notification_service.NotificationService.send_telegram') as mock_send:
            mock_send.return_value = {"success": True, "message": "Sent"}
            
            send_data = {
                "post_id": post_id,
                "post_content": post_data["content"],
                "channel": "telegram"
            }
            
            send_response = client.post(
                "/api/v1/posts/send",
                json=send_data,
                headers=auth_headers
            )
            
            assert send_response.status_code == 200
        
        # Step 4: Delete the post
        delete_response = client.delete(f"/api/v1/posts/{post_id}", headers=auth_headers)
        assert delete_response.status_code == 200
    
    def test_draft_edit_publish_workflow(self, client, auth_headers):
        """Test workflow: save draft → edit → publish."""
        # Save draft
        draft_data = {
            "post_type": "Listicle",
            "message": "Draft message",
            "tone": "casual",
            "content": "Initial draft content"
        }
        
        draft_response = client.post(
            "/api/v1/posts/draft",
            json=draft_data,
            headers=auth_headers
        )
        
        assert draft_response.status_code == 200
        post_id = draft_response.json()["id"]
        
        # Verify it's a draft
        get_response = client.get(f"/api/v1/posts/{post_id}", headers=auth_headers)
        assert get_response.json()["status"] == "draft"
        
        # Edit and publish (via send)
        with patch('app.services.notification_service.NotificationService.send_email') as mock_send:
            mock_send.return_value = {"success": True, "message": "Sent"}
            
            send_data = {
                "post_id": post_id,
                "post_content": "Updated and published content",
                "channel": "email"
            }
            
            send_response = client.post(
                "/api/v1/posts/send",
                json=send_data,
                headers=auth_headers
            )
            
            assert send_response.status_code == 200
