# Comprehensive Feature Architecture: Auto Post Mode (Template-Driven Generation)

This document provides a complete blueprint for implementing the "Auto Post Mode (Template-Driven Generation)" feature. It is designed to be so detailed and thorough that a coding assistant can implement the entire feature without requiring any additional information or clarification.

## 1. Feature Overview

- **Feature Name**: Auto Post Mode (Template-Driven Generation)
- **Feature Description**: This feature allows users to generate LinkedIn posts automatically by selecting from predefined templates. Each template provides a post structure and tone suitable for common categories like Motivational, Case Study, Build in Public, or How-To posts. Users input a main message or upload reference material, and Pydantic.AI populates the chosen template with contextually relevant, ready-to-publish content. It’s designed to save time and maintain consistency for professionals who post regularly.
- **User Stories**:
  - As a user, I want to browse and select from predefined post templates, so I can generate posts quickly without manually structuring content.
  - As a user, I want to define a main message and optionally upload reference material, so the AI can personalize the post with my specific context.
  - As a user, I want to preview the AI-generated post before sending or editing it, so I can ensure tone and messaging fit my style.
  - As a user, I want to send the generated post to my Telegram or email, or save it as a draft, so I can easily review or publish later.
- **Acceptance Criteria**:
  - User can view available templates categorized by post type and preview their structure before selection.
  - User can input a main message (≤250 chars) and upload optional reference material (text, link, or PDF).
  - Clicking “Generate” triggers Pydantic.AI to fill the selected template with user inputs, returning a post within 5 seconds.
  - Generated post follows template structure (Hook → Insight → Lesson → CTA).
  - User can send, save, or regenerate the post.
  - Errors (invalid inputs, template missing, file errors) are displayed clearly in Streamlit.
- **Dependencies**:
  - Existing authentication service for user identification.
  - Notification service for sending posts to Telegram/email.
  - Pydantic.AI for post generation.
  - Database for storing and retrieving templates.
## 2. Architecture Diagrams

### System Architecture Diagram
```mermaid
graph TD
    subgraph Frontend (Streamlit)
        A[2_Auto_Post.py] --&gt;|HTTP Request| B{api_client.py}
    end

    subgraph Backend (FastAPI)
        B --&gt;|/api/v1/templates| C[templates.py]
        C --&gt;|Get Templates| D[models.py]
        D --&gt;|SQLAlchemy| E[Database (SQLite)]
        B --&gt;|/api/v1/posts/generate-auto| F[posts.py]
        F --&gt;|Generate Post| G[post_generator.py]
        G --&gt;|Pydantic.AI| H[AI Service]
        F --&gt;|Save Post| D
    end

    subgraph External Services
        H --&gt;|LLM API| I[OpenAI/Anthropic]
        F --&gt;|Send Notification| J[notification_service.py]
        J --&gt;|Telegram/Email API| K[Notification APIs]
    end
```

### Data Flow Diagram
```mermaid
graph TD
    A[User Selects Template] --&gt; B[Streamlit UI]
    B --&gt;|Template ID & Inputs| C[FastAPI Backend]
    C --&gt;|Get Template & Inputs| D[Pydantic.AI]
    D --&gt;|Generated Post| C
    C --&gt;|Save to DB| E[Database]
    C --&gt;|Send to User| B
    B --&gt;|Display Post| A
```

### Component Hierarchy Diagram
```mermaid
graph TD
    A[app.py] --&gt; B[2_Auto_Post.py]
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

    Frontend-&gt;&gt;Backend: GET /api/v1/templates
    Backend-&gt;&gt;Database: get_templates()
    Database--&gt;&gt;Backend: [Template]
    Backend--&gt;&gt;Frontend: {templates: [Template]}

    Frontend-&gt;&gt;Backend: POST /api/v1/posts/generate-auto
    Backend-&gt;&gt;Database: get_template(id)
    Database--&gt;&gt;Backend: Template
    Backend-&gt;&gt;PydanticAI: generate_post(template, data)
    PydanticAI--&gt;&gt;Backend: GeneratedPost
    Backend-&gt;&gt;Database: save_post(post)
    Database--&gt;&gt;Backend: Post ID
    Backend--&gt;&gt;Frontend: {post: GeneratedPost}
```
## 3. Database Architecture

### Schema Changes

No schema changes are required for this feature. The existing `templates` and `posts` tables will be used.

### Data Models

**Template Interface (TypeScript/Pydantic):**
```typescript
interface Template {
  id: number;
  name: string;
  category: string;
  structure: string;
  prompt: string;
  created_at: string;
}
```

### Relationships

- **`posts.template_id`**: Foreign key to `templates.id`.

### Indexes

- No new indexes are required for this feature.
## 4. API Architecture

### Endpoint Definitions

#### 1. Get Templates
- **Endpoint**: `GET /api/v1/templates`
- **Description**: Retrieves a list of all available post templates.
- **Authentication**: Required (JWT-based)
- **Request Body**: None
- **Response Body**:
  ```typescript
  interface GetTemplatesResponse {
    templates: Template[];
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Invalid or missing token.
  - `500 Internal Server Error`: Database error.

#### 2. Generate Auto Post
- **Endpoint**: `POST /api/v1/posts/generate-auto`
- **Description**: Generates a LinkedIn post based on a selected template and user inputs.
- **Authentication**: Required (JWT-based)
- **Request Body**:
  ```typescript
  interface GenerateAutoPostRequest {
    template_id: number;
    message: string;
    tone: string;
    reference_text?: string;
  }
  ```
- **Response Body**:
  ```typescript
  interface GenerateAutoPostResponse {
    post: {
      content: string;
    };
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Invalid input data.
  - `401 Unauthorized`: Invalid or missing token.
  - `404 Not Found`: Template not found.
  - `500 Internal Server Error`: AI service failure.
## 5. Frontend Architecture

### Component Specifications

#### 1. `AutoPostPage`
- **Purpose**: Main component for the "Auto Post" feature.
- **Props**: None
- **State**:
  - `templates`: Template[]
  - `selectedTemplate`: Template | null
  - `mainMessage`: string
  - `referenceFile`: File | null
  - `tone`: string
  - `generatedPost`: string
  - `isLoading`: boolean
  - `error`: string | null
- **Event Handlers**:
  - `handleGetTemplates()`: Fetches the list of templates from the API.
  - `handleGeneratePost()`: Calls the API to generate a post.
  - `handleSendPost(channel: 'telegram' | 'email')`: Sends the post.
  - `handleSaveDraft()`: Saves the post as a draft.
  - `handleFileUpload(file: File)`: Handles file uploads.

### Page Components

- **`2_Auto_Post.py`**: The main page file for this feature.

### Routing

- The page will be accessible at the `/Auto_Post` route.

### State Management

- State will be managed locally within the `AutoPostPage` component using Streamlit's session state.

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
  - `frontend/pages/2_Auto_Post.py`: Main UI for the feature.
- **Backend**:
  - `backend/app/api/v1/endpoints/posts.py`: API endpoints for posts.
  - `backend/app/api/v1/endpoints/templates.py`: API endpoints for templates.
  - `backend/app/schemas/post.py`: Pydantic schemas for posts.
  - `backend/app/schemas/template.py`: Pydantic schemas for templates.
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
  - Test the `/templates` endpoint to ensure it returns the correct list of templates.
  - Test the `/generate-auto-post` endpoint with valid and invalid inputs.
  - Test the `post_generator` service, mocking the Pydantic.AI client.
- **Frontend**:
  - Unit tests are not applicable for Streamlit components.

### Integration Tests

- Test the entire flow of generating a post, from selecting a template to seeing the generated post.
- Test the integration with the notification service.
- Test the integration with the database.

### E2E Tests

- Test the user flow of creating a post in auto mode, from selecting a template to generating and sending the post.
- Test the file upload functionality.
- Test the error handling and display of error messages.
## 10. Performance Considerations

### Optimization Requirements

- The post generation process should take less than 7 seconds.
- The frontend should be responsive and provide a smooth user experience.

### Caching Strategy

- The `/templates` endpoint can be cached to reduce database load.

### Database Queries

- Database queries will be optimized for performance.
- Indexes will be used on frequently queried columns.