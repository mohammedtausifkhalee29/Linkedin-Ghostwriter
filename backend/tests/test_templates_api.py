"""Comprehensive test suite for Template Management API (Feature 4).

This module tests:
- Template CRUD operations
- Automatic versioning logic
- Filtering and pagination
- Template statistics
- Integration with post generation
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


pytestmark = pytest.mark.asyncio


class TestTemplateEndpointsCRUD:
    """Test cases for template CRUD operations via API endpoints."""
    
    def test_create_template_success(self, client, auth_headers, db_session):
        """Test creating a new template with all fields."""
        template_data = {
            "name": "New Template",
            "category": "Thought Leadership",
            "prompt": "Write a thoughtful post about {topic}",
            "structure": "Hook + Insight + CTA",
            "tone": "Professional",
            "example": "Example post content here"
        }
        
        response = client.post(
            "/api/v1/templates/",
            headers=auth_headers,
            json=template_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == template_data["name"]
        assert data["category"] == template_data["category"]
        assert data["prompt"] == template_data["prompt"]
        assert data["structure"] == template_data["structure"]
        assert data["tone"] == template_data["tone"]
        assert data["example"] == template_data["example"]
        assert data["current_version"] == 1
        assert "id" in data
        assert "created_at" in data
    
    def test_create_template_creates_initial_version(self, client, auth_headers, db_session):
        """Test that creating a template automatically creates version 1."""
        template_data = {
            "name": "Versioned Template",
            "category": "Tutorial",
            "prompt": "Initial prompt",
            "structure": "Initial structure",
            "tone": "Professional"
        }
        
        response = client.post(
            "/api/v1/templates/",
            headers=auth_headers,
            json=template_data
        )
        
        assert response.status_code == 201
        template_id = response.json()["id"]
        
        # Check version history
        versions_response = client.get(
            f"/api/v1/templates/{template_id}/versions",
            headers=auth_headers
        )
        
        assert versions_response.status_code == 200
        versions = versions_response.json()
        assert len(versions) == 1
        assert versions[0]["version"] == 1
        assert versions[0]["prompt"] == template_data["prompt"]
    
    def test_create_template_validation_error(self, client, auth_headers):
        """Test creating template with missing required fields."""
        template_data = {
            "name": "Incomplete Template"
            # Missing category, prompt, structure, tone
        }
        
        response = client.post(
            "/api/v1/templates/",
            headers=auth_headers,
            json=template_data
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_template_by_id(self, client, auth_headers, db_session):
        """Test retrieving a specific template by ID."""
        from app.db.models import Template as TemplateModel
        
        template = TemplateModel(
            name="Test Template",
            category="Thought Leadership",
            prompt="Test prompt",
            structure="Test structure",
            tone="Professional",
            current_version=1
        )
        
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        
        response = client.get(
            f"/api/v1/templates/{template.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template.id
        assert data["name"] == template.name
        assert data["category"] == template.category
    
    def test_get_nonexistent_template(self, client, auth_headers):
        """Test getting a template that doesn't exist."""
        response = client.get(
            "/api/v1/templates/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_update_template_metadata_no_versioning(self, client, auth_headers, db_session):
        """Test updating template metadata (name/category) doesn't create new version."""
        from app.db.models import Template as TemplateModel, TemplateVersion
        
        # Create initial template
        template = TemplateModel(
            name="Original Name",
            category="Thought Leadership",
            prompt="Original prompt",
            structure="Original structure",
            tone="Professional",
            current_version=1
        )
        
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        
        # Create initial version
        version1 = TemplateVersion(
            template_id=template.id,
            version=1,
            prompt="Original prompt",
            structure="Original structure",
            tone="Professional"
        )
        db_session.add(version1)
        db_session.commit()
        
        # Update only name (should not create new version)
        update_data = {"name": "Updated Name"}
        response = client.put(
            f"/api/v1/templates/{template.id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["current_version"] == 1  # No new version
    
    def test_update_template_prompt_creates_version(self, client, auth_headers, db_session):
        """Test updating template prompt creates new version."""
        from app.db.models import Template as TemplateModel, TemplateVersion
        
        template = TemplateModel(
            name="Test Template",
            category="Thought Leadership",
            prompt="Original prompt",
            structure="Original structure",
            tone="Professional",
            current_version=1
        )
        
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        
        # Create initial version
        version1 = TemplateVersion(
            template_id=template.id,
            version=1,
            prompt="Original prompt",
            structure="Original structure",
            tone="Professional"
        )
        db_session.add(version1)
        db_session.commit()
        
        # Update prompt (should create new version)
        update_data = {"prompt": "New updated prompt"}
        response = client.put(
            f"/api/v1/templates/{template.id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["prompt"] == "New updated prompt"
        assert data["current_version"] == 2  # New version created
    
    def test_delete_template_success(self, client, auth_headers, db_session):
        """Test deleting a template and its versions."""
        from app.db.models import Template as TemplateModel
        
        template = TemplateModel(
            name="Template to Delete",
            category="Tutorial",
            prompt="Prompt",
            structure="Structure",
            tone="Professional",
            current_version=1
        )
        
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        template_id = template.id
        
        # Delete template
        response = client.delete(
            f"/api/v1/templates/{template_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify it's deleted
        response = client.get(
            f"/api/v1/templates/{template_id}",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_delete_nonexistent_template(self, client, auth_headers):
        """Test deleting a template that doesn't exist."""
        response = client.delete(
            "/api/v1/templates/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestTemplateFiltering:
    """Test cases for template filtering and search functionality."""
    
    def test_filter_by_category(self, client, auth_headers, db_session):
        """Test filtering templates by category."""
        from app.db.models import Template as TemplateModel
        
        # Create templates in different categories
        template1 = TemplateModel(
            name="Leadership Template",
            category="Thought Leadership",
            prompt="Prompt 1",
            structure="Structure 1",
            tone="Professional",
            current_version=1
        )
        template2 = TemplateModel(
            name="Story Template",
            category="Personal Story",
            prompt="Prompt 2",
            structure="Structure 2",
            tone="Casual",
            current_version=1
        )
        
        db_session.add_all([template1, template2])
        db_session.commit()
        
        # Filter by category
        response = client.get(
            "/api/v1/templates/",
            headers=auth_headers,
            params={"category": "Thought Leadership"}
        )
        
        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        assert len(items) >= 1
        assert all(t["category"] == "Thought Leadership" for t in items)
    
    def test_filter_by_tone(self, client, auth_headers, db_session):
        """Test filtering templates by tone."""
        from app.db.models import Template as TemplateModel
        
        template1 = TemplateModel(
            name="Professional Template",
            category="Thought Leadership",
            prompt="Prompt 1",
            structure="Structure 1",
            tone="Professional",
            current_version=1
        )
        template2 = TemplateModel(
            name="Casual Template",
            category="Personal Story",
            prompt="Prompt 2",
            structure="Structure 2",
            tone="Casual",
            current_version=1
        )
        
        db_session.add_all([template1, template2])
        db_session.commit()
        
        # Filter by tone
        response = client.get(
            "/api/v1/templates/",
            headers=auth_headers,
            params={"tone": "Professional"}
        )
        
        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        assert len(items) >= 1
        assert all(t["tone"] == "Professional" for t in items)
    
    def test_search_templates(self, client, auth_headers, db_session):
        """Test searching templates by text."""
        from app.db.models import Template as TemplateModel
        
        template = TemplateModel(
            name="Unique Innovation Template",
            category="Tutorial",
            prompt="A very unique prompt about innovation",
            structure="Introduction + Steps + Conclusion",
            tone="Professional",
            current_version=1
        )
        
        db_session.add(template)
        db_session.commit()
        
        # Search by keyword
        response = client.get(
            "/api/v1/templates/",
            headers=auth_headers,
            params={"search": "unique"}
        )
        
        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        assert len(items) >= 1
        assert any("unique" in t["name"].lower() or "unique" in t["prompt"].lower() for t in items)
    
    def test_pagination(self, client, auth_headers, db_session):
        """Test template pagination."""
        from app.db.models import Template as TemplateModel
        
        # Create multiple templates
        templates = [
            TemplateModel(
                name=f"Template {i}",
                category="Thought Leadership",
                prompt=f"Prompt {i}",
                structure=f"Structure {i}",
                tone="Professional",
                current_version=1
            )
            for i in range(15)
        ]
        
        db_session.add_all(templates)
        db_session.commit()
        
        # Get first page
        response = client.get(
            "/api/v1/templates/",
            headers=auth_headers,
            params={"skip": 0, "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 10


class TestTemplateVersioning:
    """Test cases for automatic template versioning."""
    
    def test_update_structure_creates_version(self, client, auth_headers, db_session):
        """Test that updating structure creates a new version."""
        from app.db.models import Template as TemplateModel, TemplateVersion
        
        template = TemplateModel(
            name="Test",
            category="Tutorial",
            prompt="Prompt",
            structure="Original",
            tone="Professional",
            current_version=1
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        
        # Create v1
        v1 = TemplateVersion(
            template_id=template.id,
            version=1,
            prompt="Prompt",
            structure="Original",
            tone="Professional"
        )
        db_session.add(v1)
        db_session.commit()
        
        # Update structure
        response = client.put(
            f"/api/v1/templates/{template.id}",
            headers=auth_headers,
            json={"structure": "Updated"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_version"] == 2
        assert data["structure"] == "Updated"
    
    def test_update_tone_creates_version(self, client, auth_headers, db_session):
        """Test that updating tone creates a new version."""
        from app.db.models import Template as TemplateModel, TemplateVersion
        
        template = TemplateModel(
            name="Test",
            category="Tutorial",
            prompt="Prompt",
            structure="Structure",
            tone="Professional",
            current_version=1
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        
        # Create v1
        v1 = TemplateVersion(
            template_id=template.id,
            version=1,
            prompt="Prompt",
            structure="Structure",
            tone="Professional"
        )
        db_session.add(v1)
        db_session.commit()
        
        # Update tone
        response = client.put(
            f"/api/v1/templates/{template.id}",
            headers=auth_headers,
            json={"tone": "Casual"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_version"] == 2
        assert data["tone"] == "Casual"
    
    def test_multiple_updates_increment_version(self, client, auth_headers, db_session):
        """Test that multiple updates properly increment version number."""
        template_data = {
            "name": "Multi-Version Template",
            "category": "Tutorial",
            "prompt": "v1 prompt",
            "structure": "v1 structure",
            "tone": "Professional"
        }
        
        response = client.post(
            "/api/v1/templates/",
            headers=auth_headers,
            json=template_data
        )
        template_id = response.json()["id"]
        
        # Update 1: Change prompt -> v2
        response = client.put(
            f"/api/v1/templates/{template_id}",
            headers=auth_headers,
            json={"prompt": "v2 prompt"}
        )
        assert response.json()["current_version"] == 2
        
        # Update 2: Change structure -> v3
        response = client.put(
            f"/api/v1/templates/{template_id}",
            headers=auth_headers,
            json={"structure": "v3 structure"}
        )
        assert response.json()["current_version"] == 3
        
        # Update 3: Change tone -> v4
        response = client.put(
            f"/api/v1/templates/{template_id}",
            headers=auth_headers,
            json={"tone": "Casual"}
        )
        assert response.json()["current_version"] == 4
        
        # Check version history
        response = client.get(
            f"/api/v1/templates/{template_id}/versions",
            headers=auth_headers
        )
        versions = response.json()
        assert len(versions) == 4
    
    def test_get_version_history(self, client, auth_headers, db_session):
        """Test retrieving version history for a template."""
        from app.db.models import Template as TemplateModel, TemplateVersion
        
        template = TemplateModel(
            name="Versioned Template",
            category="Thought Leadership",
            prompt="Current prompt",
            structure="Current structure",
            tone="Professional",
            current_version=3
        )
        
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        
        # Create version history
        version1 = TemplateVersion(
            template_id=template.id,
            version=1,
            prompt="First prompt",
            structure="First structure",
            tone="Professional"
        )
        version2 = TemplateVersion(
            template_id=template.id,
            version=2,
            prompt="Second prompt",
            structure="Second structure",
            tone="Conversational"
        )
        version3 = TemplateVersion(
            template_id=template.id,
            version=3,
            prompt="Current prompt",
            structure="Current structure",
            tone="Professional"
        )
        
        db_session.add_all([version1, version2, version3])
        db_session.commit()
        
        # Get version history
        response = client.get(
            f"/api/v1/templates/{template.id}/versions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        versions = response.json()
        assert len(versions) == 3
        assert versions[0]["version"] == 3  # Most recent first
        assert versions[1]["version"] == 2
        assert versions[2]["version"] == 1


class TestTemplateStatistics:
    """Test cases for template statistics endpoint."""
    
    def test_get_template_stats(self, client, auth_headers, db_session):
        """Test retrieving template statistics."""
        from app.db.models import Template as TemplateModel
        
        # Create diverse templates
        templates = [
            TemplateModel(
                name="Template 1",
                category="Thought Leadership",
                prompt="Prompt 1",
                structure="Structure 1",
                tone="Professional",
                current_version=1
            ),
            TemplateModel(
                name="Template 2",
                category="Thought Leadership",
                prompt="Prompt 2",
                structure="Structure 2",
                tone="Casual",
                current_version=1
            ),
            TemplateModel(
                name="Template 3",
                category="Personal Story",
                prompt="Prompt 3",
                structure="Structure 3",
                tone="Professional",
                current_version=1
            )
        ]
        
        db_session.add_all(templates)
        db_session.commit()
        
        # Get stats
        response = client.get(
            "/api/v1/templates/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        stats = response.json()
        assert "total_templates" in stats
        assert "templates_by_category" in stats
        assert "templates_by_tone" in stats
        assert stats["total_templates"] >= 3


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
