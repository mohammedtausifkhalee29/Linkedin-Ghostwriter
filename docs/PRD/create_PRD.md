#### Feature 1: Create Post Mode (Manual Generation)

### Feature Name

Create Post Mode (Manual Generation)

### Feature Description

This feature enables users to manually generate a LinkedIn post by selecting a post type, defining their main message, and optionally uploading reference materials such as text, web links, or PDFs. It’s designed for professionals who want to create authentic, structured, and contextually relevant posts with minimal effort. Using Streamlit for the front-end and Pydantic.AI on the backend, the feature provides a clean, guided interface and ensures output consistency through structured prompts.

### User Stories

As a user, I want to select the post type and define my main message so that the AI can generate a post aligned with my intent.
As a user, I want to upload reference material (text, article link, or PDF) so that the AI can use context from real content to improve post quality.
As a user, I want to preview and edit the generated post before sending it, so that I can fine-tune tone and messaging.
As a user, I want to send the generated post to my Telegram or email or save it as a draft, so I can easily publish or reuse it later.

### Acceptance Criteria

User can select post type (e.g., Motivational, Case Study, How-To) and define a main message.
System allows text, URL, or PDF uploads; PDF content parsed using PyMuPDF or pytesseract.
Clicking “Generate Post” triggers Pydantic.AI to generate a post within 5 seconds.
User can preview, edit, regenerate, or discard the post.
User can send post via Telegram/email or save as draft (local JSON or SQLite).

### PRD Narrative

The “Create Post Mode” offers a structured and intuitive interface for content creation. It combines Streamlit’s simplicity with Pydantic.AI’s parsing and generation capabilities. Users define the message, context, and style; the AI agent generates a tailored post. The UI prioritizes clarity and speed: no clutter, single-column flow, and instant feedback loops for upload, generation, and preview actions. The backend manages content extraction, validation, and AI orchestration securely and efficiently.

### Step-by-Step Developer Tasks

## Frontend (Streamlit)

Create create_post.py page with input widgets:
Dropdown for post type
Text area for main message (max 250 chars)
File uploader (text, URL, or PDF)
Long-form context input (style, tone, target audience)
Generate button
Implement preview window to display AI-generated post.
Add buttons: “Regenerate,” “Edit,” “Send to Telegram,” “Send to Email,” “Save Draft.”
Handle file upload preview (show extracted text snippet).
Display errors (invalid input, large files, timeout).

## Backend (FastAPI)
Create /generate-post endpoint:
Accepts JSON payload (post_type, message, tone, reference_text)
Validates via Pydantic model
Calls Pydantic.AI for structured post generation.
Create /send-post endpoint for Telegram/email integration.
Implement /save-draft to persist post drafts (JSON/SQLite).
Implement file parsing utilities (PyMuPDF + pytesseract fallback).
Add error handling middleware for all endpoints.

## Pydantic.AI Integration
Define Pydantic schema for PostContext and GeneratedPost.
Prompt template ensures post follows structure: Hook → Story → Lesson → CTA.
Validate AI output against schema before sending to frontend.

## Testing
Unit tests for backend endpoints (mock Pydantic.AI and external services).
Integration test: upload → generate → preview → send.
UI smoke test for main user flow (Streamlit e2e test stub).

### Rules & Standards

## Design Principles

Simple, single-column layout with clear flow from inputs → generation → preview.
Minimal latency (<7s generation).
Accessible design: contrast-compliant, keyboard navigable.
Contextual help tooltips (e.g., “What’s a post type?”).

## Coding Standards

Language: Python 3.11+
Frameworks: Streamlit (frontend), FastAPI (backend), Pydantic.AI (AI orchestration)
Use async FastAPI routes.
Centralize AI calls in /services/ai_post_service.py.
Follow modular folder structure: /frontend, /backend, /utils.

## Formatting & Linting

Use black + isort + flake8.
Run mypy for type checks.
Enforce linting via pre-commit hook.

## File Handling

Limit upload size ≤10MB.
Allowed formats: .pdf, .txt, .md.
Use PyMuPDF for text extraction; pytesseract fallback for scanned PDFs.

## Security & Secrets

Store API keys, SMTP creds, Telegram token in .env.
Do not log raw inputs or AI outputs containing PII.
Enable CORS for trusted origins only.

## Testing & QA

Mock Pydantic.AI and Telegram APIs during tests.
Validate performance (<5s post generation).
Confirm successful delivery via both Telegram and email.

## Deliverables

Streamlit UI page (create_post.py)
FastAPI endpoints (/generate-post, /send-post, /save-draft)
Unit + Integration tests
.env.example with required vars

