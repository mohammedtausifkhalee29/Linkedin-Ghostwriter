### Feature 4: Template & Context Management

### Feature Name

Template & Context Management

### Feature Description

This feature enables the management of post templates, context data, and draft history within the LinkedIn Ghostwriter application. It allows admins to create and maintain reusable post templates categorized by type and tone, while users can access these templates, view their structure, and reuse past generated posts or drafts. The feature also includes prompt versioning to track template performance and maintain iteration history. It helps users generate posts faster and ensures consistency in writing style and message tone.

### User Stories

As an admin, I want to add, edit, and delete templates categorized by type, so that users have relevant options for generating posts.
As a user, I want to browse, preview, and select templates, so that I can easily choose the right structure for my post.
As a user, I want to save and view my previously generated posts and drafts, so that I can reuse or repurpose them later.
As an admin, I want to manage prompt versions, so I can analyze template performance and revert to previous configurations if needed.

### Acceptance Criteria

Templates can be created, updated, and deleted via admin interface or CLI.
Templates are categorized by type and include metadata (name, tone, structure, example).
Users can browse available templates and preview structure before selecting one.
Generated posts and drafts are stored with metadata (template used, timestamp, tone).
Prompt versioning maintains changelog with version ID, date, and author.
Validation errors (missing fields, duplicates) are displayed clearly.

### PRD Narrative

Template & Context Management provides the structural backbone of the LinkedIn Ghostwriter. It ensures templates and historical posts are centrally managed, versioned, and reusable. Templates are stored as structured JSON or in a lightweight SQLite DB for MVP. Users can easily browse templates, view structure previews, and manage their generated post history. Admins can add new templates or modify existing ones while maintaining version control. The system focuses on modularity, traceability, and long-term scalability.

### Step-by-Step Developer Tasks

## Backend (FastAPI)

Template CRUD Endpoints
/templates — GET: List all templates with filters (type, tone).
/templates — POST: Create new template (admin only).
/templates/{id} — PUT: Update existing template.
/templates/{id} — DELETE: Remove template.
Validate inputs using Pydantic models.
Prompt Versioning
Add table/model TemplateVersion with fields: template_id, version, changes, created_at.
Create /template-versions/{id} to retrieve version history.
Maintain automatic version bump on template updates.
Post & Draft Management
/posts — GET: Retrieve all generated/saved posts for a user.
/posts — POST: Save generated post with metadata (template, tone, timestamp).
/posts/{id} — DELETE: Delete or archive draft.
Persist to SQLite or local JSON for MVP.
Template Storage
Store templates in /data/templates.json for MVP with structure:
 {
  "id": "temp_01",
  "type": "Motivational",
  "tone": "Conversational",
  "structure": ["Hook", "Insight", "Lesson", "CTA"],
  "example": "How I overcame..."
}


Error Handling
Validate for duplicates, missing fields, or invalid structure arrays.
Standardize error responses (error_code, message, details).
Logging
Log template CRUD operations and version changes.
Log post creation and retrieval actions for auditing.

## Frontend (Streamlit)

Template Library Page
Display categorized templates with preview (name, tone, structure).
Allow selection → preview → use flow.
Add “View Versions” (admin-only) modal to see version history.
Post History Page
List previously generated posts with columns: Date, Template, Tone, Action.
Actions: View | Edit | Reuse | Delete.
Admin Section
Enable Add/Edit/Delete templates and auto-versioning.
Input validation on all fields.
Error & Success Handling
Show status messages for CRUD operations and drafts.
Clear feedback on version rollback success.

## Testing

Unit tests for all backend endpoints (template CRUD, versions, posts).
Integration test for template → generation → save → reuse flow.
UI smoke test to verify template preview and draft management.

### Rules & Standards

## Design Principles

Organized, two-tab layout: “Templates” and “My Posts.”
Maintain clarity: simple card-based template previews.
Instant feedback for CRUD actions.
Version control designed for traceability and rollback.

## Coding Standards

Language: Python 3.11+
Frameworks: FastAPI (backend), Streamlit (frontend), SQLite or JSON for persistence.
Pydantic for schema validation.
Use async endpoints for CRUD operations.
Centralize DB logic under /services/template_service.py.

## Formatting & Linting

Use black, isort, flake8.
Apply mypy type checking.
Enforce code review for new templates or schema changes.

## File Handling

Store templates in /data directory.
Limit JSON file size to <5MB for MVP.
Auto-backup templates on every CRUD operation.

## Security & Secrets

Admin routes protected with API key auth (from .env).
Sanitize user inputs to prevent injection.
No external data sharing or telemetry in MVP.

## Testing & QA

Verify CRUD, versioning, and draft persistence.
Validate that rollback creates new version entry.
Confirm data consistency between templates and posts.
Performance target: <2s for template list load.

## Deliverables

FastAPI endpoints for templates, versions, and drafts.
Streamlit UI for template library and post history.
SQLite/JSON persistence.
Unit, integration, and UI smoke tests.
.env.example with admin key and storage paths.

