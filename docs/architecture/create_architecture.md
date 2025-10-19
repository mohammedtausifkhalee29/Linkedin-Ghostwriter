# Comprehensive Feature Architecture: Create Post Mode (Manual Generation)

This document provides a complete blueprint for implementing the "Create Post Mode (Manual Generation)" feature. It is designed to be so detailed and thorough that a coding assistant can implement the entire feature without requiring any additional information or clarification.

## 1. Feature Overview

- **Feature Name**: Create Post Mode (Manual Generation)
- **Feature Description**: This feature enables users to manually generate a LinkedIn post by selecting a post type, defining their main message, and optionally uploading reference materials such as text, web links, or PDFs. It’s designed for professionals who want to create authentic, structured, and contextually relevant posts with minimal effort. Using Streamlit for the front-end and Pydantic.AI on the backend, the feature provides a clean, guided interface and ensures output consistency through structured prompts.
- **User Stories**:
  - As a user, I want to select the post type and define my main message so that the AI can generate a post aligned with my intent.
  - As a user, I want to upload reference material (text, article link, or PDF) so that the AI can use context from real content to improve post quality.
  - As a user, I want to preview and edit the generated post before sending it, so that I can fine-tune tone and messaging.
  - As a user, I want to send the generated post to my Telegram or email or save it as a draft, so I can easily publish or reuse it later.
- **Acceptance Criteria**:
  - User can select post type (e.g., Motivational, Case Study, How-To) and define a main message.
  - System allows text, URL, or PDF uploads; PDF content parsed using PyMuPDF or pytesseract.
  - Clicking “Generate Post” triggers Pydantic.AI to generate a post within 5 seconds.
  - User can preview, edit, regenerate, or discard the post.
  - User can send post via Telegram/email or save as draft (local JSON or SQLite).
- **Dependencies**:
  - Existing authentication service for user identification.
  - Notification service for sending posts to Telegram/email.
  - Pydantic.AI for post generation.
## 2. Architecture Diagrams

### System Architecture Diagram
```mermaid
graph TD
    subgraph Frontend (Streamlit)
        A[1_Create_Post.py] --&gt;|HTTP Request| B{api_client.py}
    end

    subgraph Backend (FastAPI)
        B --&gt;|/api/v1/posts/generate| C[posts.py]
        C --&gt;|Generate Post| D[post_generator.py]
        D --&gt;|Pydantic.AI| E[AI Service]
        C --&gt;|Save Post| F[models.py]
        F --&gt;|SQLAlchemy| G[Database (SQLite)]
    end

    subgraph External Services
        E --&gt;|LLM API| H[OpenAI/Anthropic]
        C --&gt;|Send Notification| I[notification_service.py]
        I --&gt;|Telegram/Email API| J[Notification APIs]
    end
```

### Data Flow Diagram
```mermaid
graph TD
    A[User Inputs] --&gt; B[Streamlit UI]
    B --&gt;|Post Data| C[FastAPI Backend]
    C --&gt;|Structured Prompt| D[Pydantic.AI]
    D --&gt;|Generated Post| C
    C --&gt;|Save to DB| E[Database]
    C --&gt;|Send to User| B
    B --&gt;|Display Post| A
```

### Component Hierarchy Diagram
```mermaid
graph TD
    A[app.py] --&gt; B[1_Create_Post.py]
    B --&gt; C[layout.py]
    B --&gt; D[api_client.py]
```

### API Flow Diagram
```mermaid
sequenceDiagram
    participant Frontend
    participant Backend
    participant PydanticAI
    participant Database

    Frontend-&gt;&gt;Backend: POST /api/v1/posts/generate
    Backend-&gt;&gt;PydanticAI: generate_post(data)
    PydanticAI--&gt;&gt;Backend: GeneratedPost
    Backend-&gt;&gt;Database: save_post(post)
    Database--&gt;&gt;Backend: Post ID
    Backend--&gt;&gt;Frontend: {post: GeneratedPost}
```
## 3. Database Architecture

### Schema Changes

The existing `posts` table will be modified to include `status` and `reference_text` columns to support drafts and reference material.

**Modified `posts` Table:**
```sql
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    template_id INTEGER, -- Can be NULL if generated in Create Post Mode
    generation_mode TEXT NOT NULL, -- 'manual' or 'auto'
    status TEXT NOT NULL DEFAULT 'published', -- 'draft' or 'published'
    reference_text TEXT, -- To store extracted text from uploads
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (template_id) REFERENCES templates (id)
);
```

### Data Models

**Post Interface (TypeScript/Pydantic):**
```typescript
interface Post {
  id: number;
  user_id: number;
  content: string;
  template_id?: number | null;
  generation_mode: 'manual' | 'auto';
  status: 'draft' | 'published';
  reference_text?: string | null;
  created_at: string;
}
```

### Relationships

- **`posts.user_id`**: Foreign key to `users.id`.
- **`posts.template_id`**: Foreign key to `templates.id` (nullable).

### Indexes

- An index should be created on the `status` column for efficient querying of drafts.
```sql
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
```

### Migrations

1.  Add the `status` column to the `posts` table with a default value of `'published'`.
2.  Add the `reference_text` column to the `posts` table (nullable).
3.  Create a new index on the `status` column.
## 4. API Architecture

### Endpoint Definitions

#### 1. Generate Post
- **Endpoint**: `POST /api/v1/posts/generate`
- **Description**: Generates a LinkedIn post based on user inputs.
- **Authentication**: Required (JWT-based)
- **Request Body**:
  ```typescript
  interface GeneratePostRequest {
    post_type: string;
    message: string;
    tone: string;
    reference_text?: string;
  }
  ```
- **Response Body**:
  ```typescript
  interface GeneratePostResponse {
    post: {
      content: string;
    };
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid input data.
  - `401 Unauthorized`: Invalid or missing token.
  - `500 Internal Server Error`: AI service failure.

#### 2. Send Post
- **Endpoint**: `POST /api/v1/posts/send`
- **Description**: Sends a generated post to Telegram or email.
- **Authentication**: Required (JWT-based)
- **Request Body**:
  ```typescript
  interface SendPostRequest {
    post_content: string;
    channel: 'telegram' | 'email';
  }
  ```
- **Response Body**:
  ```typescript
  interface SendPostResponse {
    status: 'success';
    message: string;
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid channel or content.
  - `401 Unauthorized`: Invalid or missing token.
  - `500 Internal Server Error`: Notification service failure.

#### 3. Save Draft
- **Endpoint**: `POST /api/v1/posts/draft`
- **Description**: Saves a generated post as a draft.
- **Authentication**: Required (JWT-based)
- **Request Body**:
  ```typescript
  interface SaveDraftRequest {
    content: string;
    reference_text?: string;
  }
  ```
- **Response Body**:
  ```typescript
  interface SaveDraftResponse {
    status: 'success';
    draft_id: number;
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid content.
  - `401 Unauthorized`: Invalid or missing token.
  - `500 Internal Server Error`: Database error.
## 5. Frontend Architecture

### Component Specifications

#### 1. `CreatePostPage`
- **Purpose**: Main component for the "Create Post" feature.
- **Props**: None
- **State**:
  - `postType`: string
  - `mainMessage`: string
  - `referenceFile`: File | null
  - `longFormContext`: string
  - `generatedPost`: string
  - `isLoading`: boolean
  - `error`: string | null
- **Event Handlers**:
  - `handleGeneratePost()`: Calls the API to generate a post.
  - `handleSendPost(channel: 'telegram' | 'email')`: Sends the post.
  - `handleSaveDraft()`: Saves the post as a draft.
  - `handleFileUpload(file: File)`: Handles file uploads.

### Page Components

- **`1_Create_Post.py`**: The main page file for this feature.

### Routing

- The page will be accessible at the `/Create_Post` route.

### State Management

- State will be managed locally within the `CreatePostPage` component using Streamlit's session state.

### Form Handling

- Form inputs will be validated on the frontend before making API calls.
- Error messages will be displayed to the user for invalid inputs.
## 6. Security Architecture

### Authentication Requirements

- All API endpoints for this feature must be protected and require a valid JWT token.
- The frontend will store the JWT token in the session state and include it in the `Authorization` header of all API requests.

### Authorization Rules

- Users can only access their own generated posts and drafts.
- Role-based access control is not required for this feature.

### Data Validation

- All user inputs will be validated on both the frontend and backend.
- The backend will use Pydantic models to validate the structure and data types of API request bodies.
- File uploads will be validated for size and type.

### Audit Logging

- The following actions will be logged for security purposes:
  - User login attempts (success and failure).
  - Post generation requests.
  - Post send requests.
## 7. Integration Points

### Existing App Integration

- **Authentication**: Integrates with the existing JWT-based authentication system.
- **Notification Service**: Uses the existing `notification_service.py` to send posts via Telegram and email.
- **Database**: Uses the existing database session management to interact with the database.

### Third-party Services

- **Pydantic.AI**: Integrates with Pydantic.AI for post generation.
- **OpenAI/Anthropic**: The AI service will make API calls to these services for LLM-based text generation.

### Event Handling

- This feature does not emit or consume any events.
## 8. Implementation Specifications

### File Structure

- **Frontend**:
  - `frontend/pages/1_Create_Post.py`: Main UI for the feature.
- **Backend**:
  - `backend/app/api/v1/endpoints/posts.py`: API endpoints for posts.
  - `backend/app/schemas/post.py`: Pydantic schemas for posts.
  - `backend/app/services/post_generator.py`: Service for generating posts.

### Naming Conventions

- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Components**: `PascalCase`

### Code Organization

- Code will be organized into modules and services based on functionality.
- Business logic will be kept in the services layer, separate from the API endpoints.

### Type Definitions

- All functions and variables will be type-hinted using Python's `typing` module.
- Pydantic models will be used for data validation and serialization.

### Constants

- API keys and other secrets will be stored in a `.env` file.
- Configuration values will be managed by the `config.py` module.
## 9. Testing Requirements

### Unit Tests

- **Backend**:
  - Test the `/generate-post` endpoint with valid and invalid inputs.
  - Test the `/send-post` endpoint with valid and invalid inputs.
  - Test the `/save-draft` endpoint with valid and invalid inputs.
  - Test the `post_generator` service, mocking the Pydantic.AI client.
- **Frontend**:
  - Unit tests are not applicable for Streamlit components.

### Integration Tests

- Test the entire flow of generating a post, from the frontend to the backend and back.
- Test the integration with the notification service.
- Test the integration with the database.

### E2E Tests

- Test the user flow of creating a post, from filling out the form to seeing the generated post.
- Test the file upload functionality.
- Test the error handling and display of error messages.
## 10. Performance Considerations

### Optimization Requirements

- The post generation process should take less than 7 seconds.
- The frontend should be responsive and provide a smooth user experience.

### Caching Strategy

- Caching is not required for this feature.

### Database Queries

- Database queries will be optimized for performance.
- Indexes will be used on frequently queried columns.