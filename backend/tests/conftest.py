"""Pytest configuration and shared fixtures for testing."""

import os
import sys
from typing import Generator, AsyncGenerator
from pathlib import Path
import tempfile

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.db.models import Base, User, Post
from app.db.session import get_db
from app.core.security import get_password_hash


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """Create a test user in the database."""
    user = User(
        email="testuser@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_post(db_session: Session, test_user: User) -> Post:
    """Create a test post in the database."""
    post = Post(
        user_id=test_user.id,
        post_type="Story",
        tone="professional",
        content="This is a test LinkedIn post about AI and technology.",
        status="published",
        reference_text="Some reference material for the post.",
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


@pytest.fixture(scope="function")
def auth_headers(client: TestClient, test_user: User) -> dict:
    """Get authentication headers for a test user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "testpassword123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_pdf_file() -> Generator[tuple[str, bytes], None, None]:
    """Create a sample PDF file for testing."""
    # Simple PDF structure (this is a minimal valid PDF)
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF Content) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
0000000304 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
396
%%EOF
"""
    yield ("test.pdf", pdf_content)


@pytest.fixture
def sample_txt_file() -> tuple[str, bytes]:
    """Create a sample text file for testing."""
    content = """This is a test text file.
It contains multiple lines of text.
This can be used as reference material for generating LinkedIn posts.
AI and machine learning are transforming the tech industry."""
    return ("test.txt", content.encode("utf-8"))


@pytest.fixture
def sample_markdown_file() -> tuple[str, bytes]:
    """Create a sample markdown file for testing."""
    content = """# Test Markdown File

## Section 1
This is a markdown file with **bold** and *italic* text.

## Section 2
- Point 1
- Point 2
- Point 3

This can be used as reference material."""
    return ("test.md", content.encode("utf-8"))


@pytest.fixture
def mock_llm_response() -> dict:
    """Mock response from LLM for post generation."""
    return {
        "post_content": """🚀 Exciting developments in AI!

After analyzing the latest trends, it's clear that machine learning is revolutionizing how we work.

Key insights:
✅ Automation is increasing productivity
✅ AI tools are becoming more accessible
✅ The future is collaborative

What's your take on AI in your industry? Let's discuss! 👇

#AI #MachineLearning #Technology #Innovation""",
        "key_points": [
            "AI is transforming industries",
            "Automation increases productivity",
            "Collaboration is key"
        ]
    }


@pytest.fixture
def mock_notification_service(monkeypatch):
    """Mock notification service to prevent actual sending."""
    class MockNotificationService:
        async def send_telegram(self, message: str) -> dict:
            return {"success": True, "message": "Mock Telegram sent"}
        
        async def send_email(self, to_email: str, subject: str, content: str) -> dict:
            return {"success": True, "message": "Mock Email sent"}
    
    return MockNotificationService()


# Test data constants
VALID_POST_TYPES = [
    "Story",
    "Listicle",
    "How-to Guide",
    "Case Study",
    "Opinion Piece",
    "Industry News",
    "Personal Achievement"
]

VALID_TONES = [
    "professional",
    "casual",
    "inspiring",
    "educational",
    "humorous",
    "thought-provoking"
]

SAMPLE_MESSAGES = [
    "Just completed a major project using AI",
    "Thoughts on the future of remote work",
    "5 tips for better time management",
    "Celebrating our team's achievement"
]


@pytest.fixture
def large_file_content() -> bytes:
    """Create content that exceeds the 10MB limit."""
    # Create 11MB of data
    return b"x" * (11 * 1024 * 1024)
