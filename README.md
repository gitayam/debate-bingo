# Debate Bingo

A modern, interactive debate bingo application built with **Next.js 15**, **FastAPI**, and **PostgreSQL**. Originally inspired by a simple Streamlit app, this version provides a production-ready, scalable solution with real-time game state management.

## 🎯 Features

- **Interactive Bingo Cards**: 3×3 and 5×5 grid options
- **Real-time Updates**: Game state synchronized across sessions
- **Persistent Storage**: PostgreSQL database for game history
- **Modern UI**: Responsive design with dark mode support
- **Type Safety**: Full TypeScript implementation
- **RESTful API**: FastAPI backend with automatic OpenAPI documentation
- **Development Ready**: Docker setup for easy development

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM with migrations
- **Pydantic** - Data validation and serialization
- **PostgreSQL** - Primary database
- **Redis** - Session management and caching
- **Alembic** - Database migration management

### Frontend (Next.js 15)
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety throughout
- **Tailwind CSS v4** - Utility-first styling
- **Zustand** - Lightweight state management
- **TanStack Query** - Server state management
- **Responsive Design** - Mobile-first approach

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (recommended)
- **Node.js 18+** and **Python 3.11+** (for local development)

### Option 1: Docker (Recommended)

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd debate-bingo
   ./scripts/dev-setup.sh
   ```

2. **Start all services:**
   ```bash
   docker-compose up
   ```

3. **Access the application:**
   - Frontend: http://localhost:3745
   - Backend API: http://localhost:8745
   - API Documentation: http://localhost:8745/docs

### Option 2: Local Development

1. **Setup infrastructure:**
   ```bash
   docker-compose up -d postgres redis
   ```

2. **Backend setup:**
   ```bash
   cd backend
   pip install poetry
   poetry install
   poetry run alembic upgrade head
   poetry run python app/utils/init_db.py
   poetry run uvicorn app.main:app --reload --port 8745
   ```

3. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🎮 How to Play

1. **Start a New Game**: Choose your player name and grid size (3×3 or 5×5)
2. **Watch the Debate**: Click phrases when they occur during the debate
3. **Get BINGO**: Complete a row, column, or diagonal to win
4. **Track Progress**: View your timeline and game statistics

## 📁 Project Structure

```
debate-bingo/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── tests/              # Backend tests
│   ├── alembic/            # Database migrations
│   └── pyproject.toml      # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/            # Next.js App Router
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API services
│   │   ├── stores/         # Zustand stores
│   │   └── types/          # TypeScript types
│   └── package.json        # Node.js dependencies
├── scripts/                # Development scripts
├── docs/                   # Documentation
└── docker-compose.yml      # Docker services
```

## 🛠️ Development

### Backend Commands
```bash
cd backend

# Install dependencies
poetry install

# Run development server
poetry run uvicorn app.main:app --reload --port 8745

# Database migrations
poetry run alembic revision --autogenerate -m "Description"
poetry run alembic upgrade head

# Run tests
poetry run pytest

# Linting and formatting
poetry run black .
poetry run flake8 .
poetry run mypy .
```

### Frontend Commands
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Linting and type checking
npm run lint
npm run type-check
```

## 🗄️ Database Schema

### Core Tables
- **bingo_phrases** - All available bingo phrases
- **bingo_game_sessions** - Individual game instances
- **bingo_cards** - Card positions and states

### Key Features
- **Automatic timestamps** on all models
- **Foreign key relationships** for data integrity
- **Database migrations** with Alembic
- **Sample data initialization** with debate phrases

## 🔧 Configuration

### Environment Variables

**Backend** (`.env`):
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/debate_bingo_dev
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=["http://localhost:3745"]
```

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8745
```

## 📊 API Documentation

The FastAPI backend automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8745/docs
- **ReDoc**: http://localhost:8745/redoc

### Key Endpoints
- `GET /api/v1/bingo/phrases` - Get all bingo phrases
- `POST /api/v1/bingo/game` - Create new game session
- `GET /api/v1/bingo/game/{session_id}` - Get game state
- `PATCH /api/v1/bingo/game/{session_id}/position/{position}` - Update card

## 🧪 Testing

### Backend Testing
```bash
cd backend
poetry run pytest                    # Run all tests
poetry run pytest --cov             # With coverage
poetry run pytest tests/unit/       # Unit tests only
```

### Frontend Testing
```bash
cd frontend
npm test                            # Run all tests
npm run test:coverage               # With coverage
npm run test:ui                     # Interactive UI
```

## 🚢 Deployment

### Production Build
```bash
# Backend
cd backend
poetry export -f requirements.txt --output requirements.txt
docker build -f Dockerfile.prod -t debate-bingo-backend .

# Frontend
cd frontend
npm run build
docker build -f Dockerfile.prod -t debate-bingo-frontend .
```

### Environment Setup
- Configure production database and Redis
- Set secure `SECRET_KEY` and proper CORS origins
- Use environment-specific configuration files

## 🎨 Design System

### Colors
- **Primary**: Orange (#ED6C1A) - Main brand color
- **Gray Scale**: Tailwind's gray palette for UI elements
- **Status Colors**: Green (success), Red (error), Yellow (warning)

### Typography
- **Sans Serif**: Inter (body text, UI)
- **Display**: Playfair Display (headings, logo)

### Components
- **Cards**: Rounded corners with subtle shadows
- **Buttons**: Primary/secondary variants with hover states
- **Grid**: Responsive bingo grid with click animations

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards
- **Backend**: Black formatting, flake8 linting, mypy type checking
- **Frontend**: ESLint, Prettier, TypeScript strict mode
- **Commits**: Conventional commit messages
- **Tests**: Required for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original Streamlit implementation inspiration
- Political debate entertainment community
- Open source contributors

---

**Built with ❤️ for political debate entertainment**