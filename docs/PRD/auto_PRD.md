#### Feature 2: Auto Post Mode (Template-Driven Generation)


### Feature Name

Auto Post Mode (Template-Driven Generation)

### Feature Description

This feature allows users to generate LinkedIn posts automatically by selecting from predefined templates. Each template provides a post structure and tone suitable for common categories like Motivational, Case Study, Build in Public, or How-To posts. Users input a main message or upload reference material, and Pydantic.AI populates the chosen template with contextually relevant, ready-to-publish content. It’s designed to save time and maintain consistency for professionals who post regularly.

### User Stories

As a user, I want to browse and select from predefined post templates, so I can generate posts quickly without manually structuring content.
As a user, I want to define a main message and optionally upload reference material, so the AI can personalize the post with my specific context.
As a user, I want to preview the AI-generated post before sending or editing it, so I can ensure tone and messaging fit my style.
As a user, I want to send the generated post to my Telegram or email, or save it as a draft, so I can easily review or publish later.

### Acceptance Criteria

User can view available templates categorized by post type and preview their structure before selection.
User can input a main message (≤250 chars) and upload optional reference material (text, link, or PDF).
Clicking “Generate” triggers Pydantic.AI to fill the selected template with user inputs, returning a post within 5 seconds.
Generated post follows template structure (Hook → Insight → Lesson → CTA).
User can send, save, or regenerate the post.
Errors (invalid inputs, template missing, file errors) are displayed clearly in Streamlit.

### PRD Narrative

Auto Post Mode enables faster, template-driven post creation for busy professionals. Instead of starting from scratch, users choose a category and provide minimal input. The backend retrieves the relevant template, integrates user context, and calls Pydantic.AI to produce a structured post draft. The UI focuses on clarity and speed — a three-step flow: Select Template → Add Message → Generate & Review. The system handles parsing, validation, and delivery securely through Streamlit and FastAPI.

### Step-by-Step Developer Tasks

## Frontend (Streamlit)

Create auto_post.py page with inputs:
Template selection dropdown (grouped by category)
Text field for main message
File uploader for optional reference (text/link/PDF)
Tone & voice selector dropdown (Conversational, Formal, Friendly, etc.)
Generate button
Display template structure preview once selected.
Render generated post in preview window with edit/regenerate options.
Add “Send via Telegram,” “Send via Email,” and “Save Draft” actions.
Show validation errors and confirmation messages in UI.

## Backend (FastAPI)

Create /templates endpoint to return all available templates from database or JSON.
Create /generate-auto-post endpoint:
Accepts payload: template_id, message, tone, reference_text.
Validates input using Pydantic model.
Retrieves template structure from backend storage.
Calls Pydantic.AI to populate placeholders and generate post.
Implement /send-post endpoint (reusable from Feature 1) for Telegram/email.
Implement /save-draft to persist generated posts with metadata (template, timestamp).
Add /upload-reference utility for parsing text or PDFs with PyMuPDF + pytesseract fallback.

## Template Management

Store templates in structured JSON/SQLite:
 {
  "id": "temp_001",
  "type": "Case Study",
  "structure": ["Hook", "Challenge", "Solution", "Outcome", "CTA"],
  "tone": "Professional",
  "example": "How I improved X metric using Y framework..."
}
Backend retrieves templates by category/type for frontend rendering.

## Testing

Unit tests for /templates and /generate-auto-post endpoints (mock Pydantic.AI).
Integration tests for end-to-end post generation and delivery.
UI smoke test to validate template selection → post generation flow.

### Rules & Standards

## Design Principles

Keep UI flow linear: Template → Message → Generate → Preview.
Fast interaction: <5 seconds generation latency.
Accessible and minimal interface with clear icons and text labels.
Consistent preview formatting for all post types.

## Coding Standards

Language: Python 3.11+
Frameworks: Streamlit (frontend), FastAPI (backend), Pydantic.AI (AI logic).
Modular design: /backend/routes, /backend/services, /frontend/pages.
Use async/await for API calls.
Templates and drafts stored in /data directory with clear naming.

## Formatting & Linting

Apply black, flake8, isort.
Run mypy for type hints.
Enforce pre-commit hooks for code hygiene.

## File Handling

Upload limit: ≤10MB.
Supported formats: .pdf, .txt, .md.
Auto-parse PDFs using PyMuPDF; use pytesseract for image-based text.

## Security & Secrets

Store API keys and tokens in .env.
Protect template data endpoints from unauthorized writes.
Sanitize user inputs and escape HTML before rendering.

## Testing & QA

Mock Pydantic.AI in test mode.
Verify template integrity (placeholders resolved correctly).
Validate successful post generation for all categories.

## Deliverables

Streamlit UI page (auto_post.py)
FastAPI endpoints (/templates, /generate-auto-post, /send-post, /save-draft)
Template JSON schema and example set
Unit and integration tests
.env.example for environment setup


