# LinkedIn Ghostwriter

An AI-powered LinkedIn post generator that helps you create engaging content effortlessly.

## 🚀 Features

- **✨ Create Post Mode**: Generate custom LinkedIn posts with AI assistance
- **🤖 Auto Post Mode**: Use pre-built templates for quick post generation
- **📚 Post History**: Track and manage all your generated posts
- **📱 Multi-channel Delivery**: Send posts via Telegram or Email
- **🎯 Multiple Templates**: Case studies, build-in-public updates, personal stories, and more

## 🏗️ Architecture

This project follows a modern, decoupled architecture:

- **Frontend**: Streamlit (Python-based web interface)
- **Backend**: FastAPI (High-performance Python API)
- **Database**: SQLite (can be upgraded to PostgreSQL)
- **AI Engine**: Pydantic AI with OpenAI/Anthropic models

## 📋 Prerequisites

- Python 3.10 or higher
- OpenAI API key (or other LLM provider)
- (Optional) Telegram Bot Token
- (Optional) SMTP credentials for email

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Linkedin Ghostwriter"
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cd ..
   cp .env.example .env
   # Edit .env and fill in your API keys and configuration
   ```

5. **Initialize the database**
   ```bash
   cd backend
   python -c "from app.db.models import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"
   # Or run the SQL schema directly:
   sqlite3 ../database/ghostwriter.db < ../database/schema.sql
   ```

## 🚀 Running the Application

### Start the Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Start the Frontend (Terminal 2)
```bash
cd frontend
source venv/bin/activate  # On Windows: venv\Scripts\activate
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration and security
│   │   ├── db/             # Database models and sessions
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry point
│   └── tests/              # Backend tests
├── frontend/               # Streamlit frontend
│   ├── pages/              # Application pages
│   ├── components/         # Reusable UI components
│   ├── utils/              # Utility functions
│   └── app.py              # Frontend entry point
├── database/               # Database files and schema
├── docs/                   # Documentation
└── .env.example            # Environment variables template
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend
The frontend can be tested manually through the Streamlit interface.

## 🔧 Configuration

Key configuration options in `.env`:

- `SECRET_KEY`: JWT secret key for authentication
- `OPENAI_API_KEY`: Your OpenAI API key
- `LLM_MODEL`: The LLM model to use (e.g., gpt-4)
- `TELEGRAM_BOT_TOKEN`: Telegram bot token for notifications
- `SMTP_*`: Email configuration for notifications

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Streamlit for the amazing UI library
- Pydantic AI for structured LLM interactions
- OpenAI for the powerful language models

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ using Python, FastAPI, and Streamlit**
