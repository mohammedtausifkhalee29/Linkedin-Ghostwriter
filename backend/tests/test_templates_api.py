"""Tests for templates API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


class TestGetTemplatesEndpoint:
    """Tests for GET /api/v1/templates endpoint."""
    
    def test_get_all_templates(self, client, auth_headers, db_session):
        """Test retrieving all templates."""
        from app.db.models import Template as TemplateModel
        
        # Create test templates
        templates_data = [
            {
                "name": "Problem-Solution-Results",
                "category": "Case Study",
                "structure": "Hook → Problem → Solution → Results → CTA",
                "prompt": "Create a case study post..."
            },
            {
                "name": "Progress Update",
                "category": "Build in Public",
                "structure": "Hook → What I Built → Challenges → Learnings → Next Steps",
                "prompt": "Create a build in public post..."
            },
            {
                "name": "Career Journey",
                "category": "Personal Story",
                "structure": "Hook → Starting Point → Turning Point → Growth → Lesson",
                "prompt": "Create a personal story post..."
            }
        ]
        
        for template_data in templates_data:
            template = TemplateModel(**template_data)
            db_session.add(template)
        db_session.commit()
        
        # Get all templates
        response = client.get("/api/v1/templates/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Verify structure
        for template in data:
            assert "id" in template
            assert "name" in template
            assert "category" in template
            assert "structure" in template
            assert "prompt" in template
            assert "created_at" in template
    
    def test_get_templates_by_category(self, client, auth_headers, db_session):
        """Test filtering templates by category."""
        from app.db.models import Template as TemplateModel
        
        # Create templates in different categories
        case_study = TemplateModel(
            name="Test Case Study",
            category="Case Study",
            structure="Hook → Body → CTA",
            prompt="Test prompt"
        )
        build_public = TemplateModel(
            name="Test Build Public",
            category="Build in Public",
            structure="Hook → Progress → Next",
            prompt="Test prompt"
        )
        
        db_session.add_all([case_study, build_public])
        db_session.commit()
        
        # Filter by Case Study
        response = client.get(
            "/api/v1/templates/?category=Case Study",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Case Study"
    
    def test_get_templates_unauthorized(self, client):
        """Test retrieving templates without authentication."""
        response = client.get("/api/v1/templates/")
        assert response.status_code == 401
    
    def test_get_templates_empty_database(self, client, auth_headers, db_session):
        """Test retrieving templates when none exist."""
        from app.db.models import Template as TemplateModel
        
        # Ensure no templates exist
        db_session.query(TemplateModel).delete()
        db_session.commit()
        
        response = client.get("/api/v1/templates/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestGenerateAutoPostEndpoint:
    """Tests for POST /api/v1/posts/generate-auto endpoint."""
    
    def test_generate_auto_post_success(self, client, auth_headers, db_session, test_user):
        """Test successful auto post generation."""
        from app.db.models import Template as TemplateModel
        
        # Create a template
        template = TemplateModel(
            name="Test Template",
            category="Case Study",
            structure="Hook → Problem → Solution → CTA",
            prompt="Create a case study post..."
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        
        # Generate auto post
        request_data = {
            "template_id": template.id,
            "message": "How we improved our conversion rate",
            "tone": "Professional",
            "reference_text": None
        }
        
        response = client.post(
            "/api/v1/posts/generate-auto",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "post" in data
        post = data["post"]
        assert "id" in post
        assert "content" in post
        assert post["status"] == "draft"
        assert len(post["content"]) > 0
    
    def test_generate_auto_post_with_reference_text(self, client, auth_headers, db_session):
        """Test auto post generation with reference text."""
        from app.db.models import Template as TemplateModel
        
        template = TemplateModel(
            name="Progress Update",
            category="Build in Public",
            structure="Hook → Progress → Challenges → Next Steps",
            prompt="Create a progress update..."
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        
        request_data = {
            "template_id": template.id,
            "message": "Launched new feature today",
            "tone": "Conversational",
            "reference_text": "New feature details: User authentication, profile management..."
        }
        
        response = client.post(
            "/api/v1/posts/generate-auto",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "post" in data
        assert len(data["post"]["content"]) > 0
    
    def test_generate_auto_post_invalid_template(self, client, auth_headers):
        """Test auto post generation with non-existent template."""
        request_data = {
            "template_id": 99999,  # Non-existent
            "message": "Test message",
            "tone": "Professional"
        }
        
        response = client.post(
            "/api/v1/posts/generate-auto",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_generate_auto_post_unauthorized(self, client, db_session):
        """Test auto post generation without authentication."""
        from app.db.models import Template as TemplateModel
        
        template = TemplateModel(
            name="Test", category="Test", structure="A → B", prompt="Test"
        )
        db_session.add(template)
        db_session.commit()
        
        request_data = {
            "template_id": template.id,
            "message": "Test",
            "tone": "Professional"
        }
        
        response = client.post("/api/v1/posts/generate-auto", json=request_data)
        assert response.status_code == 401
    
    def test_generate_auto_post_missing_fields(self, client, auth_headers):
        """Test auto post generation with missing required fields."""
        request_data = {
            "template_id": 1,
            "tone": "Professional"
            # Missing message
        }
        
        response = client.post(
            "/api/v1/posts/generate-auto",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_generate_auto_post_saves_as_draft(self, client, auth_headers, db_session, test_user):
        """Test that auto-generated posts are saved as drafts."""
        from app.db.models import Template as TemplateModel, Post as PostModel
        
        template = TemplateModel(
            name="Test", category="Test", structure="A → B", prompt="Test"
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        
        request_data = {
            "template_id": template.id,
            "message": "Test message",
            "tone": "Professional"
        }
        
        response = client.post(
            "/api/v1/posts/generate-auto",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        post_id = response.json()["post"]["id"]
        
        # Verify in database
        post = db_session.query(PostModel).filter(PostModel.id == post_id).first()
        assert post is not None
        assert post.status == "draft"
        assert post.generation_mode == "auto"
        assert post.template_id == template.id


class TestTemplateIntegration:
    """Integration tests for template workflows."""
    
    def test_complete_template_workflow(self, client, auth_headers, db_session):
        """Test complete workflow: Get templates → Generate → Get history."""
        from app.db.models import Template as TemplateModel
        
        # Step 1: Create template
        template = TemplateModel(
            name="Workflow Test",
            category="Case Study",
            structure="Hook → Problem → Solution → CTA",
            prompt="Create a case study..."
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        
        # Step 2: Get templates
        templates_response = client.get("/api/v1/templates/", headers=auth_headers)
        assert templates_response.status_code == 200
        templates = templates_response.json()
        assert len(templates) >= 1
        
        # Step 3: Generate post
        generate_response = client.post(
            "/api/v1/posts/generate-auto",
            json={
                "template_id": template.id,
                "message": "E2E workflow test",
                "tone": "Professional"
            },
            headers=auth_headers
        )
        
        assert generate_response.status_code == 200
        post_id = generate_response.json()["post"]["id"]
        
        # Step 4: Verify in history
        history_response = client.get("/api/v1/posts/", headers=auth_headers)
        assert history_response.status_code == 200
        
        posts = history_response.json()
        assert any(post["id"] == post_id for post in posts)
    
    def test_filter_template_posts_by_status(self, client, auth_headers, db_session):
        """Test filtering template posts by draft status."""
        from app.db.models import Template as TemplateModel
        
        template = TemplateModel(
            name="Filter Test",
            category="Build in Public",
            structure="Hook → Progress → Next",
            prompt="Create update..."
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        
        # Generate post (saved as draft)
        client.post(
            "/api/v1/posts/generate-auto",
            json={
                "template_id": template.id,
                "message": "Draft filter test",
                "tone": "Professional"
            },
            headers=auth_headers
        )
        
        # Get drafts
        drafts_response = client.get(
            "/api/v1/posts/?status_filter=draft",
            headers=auth_headers
        )
        
        assert drafts_response.status_code == 200
        drafts = drafts_response.json()
        assert len(drafts) >= 1
        assert all(post["status"] == "draft" for post in drafts)
