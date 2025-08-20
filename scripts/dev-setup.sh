#!/bin/bash

# Development setup script for Debate Bingo

set -e

echo "🎯 Setting up Debate Bingo development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start infrastructure services
echo "📦 Starting infrastructure services (PostgreSQL, Redis)..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Setup backend
echo "🐍 Setting up backend..."
cd backend

# Install dependencies if not already installed
if [ ! -d ".venv" ]; then
    echo "Installing Python dependencies..."
    pip install poetry
    poetry install
fi

# Run database migrations
echo "Running database migrations..."
poetry run alembic upgrade head

# Initialize database with sample data
echo "Initializing database with bingo phrases..."
poetry run python app/utils/init_db.py

cd ..

# Setup frontend
echo "⚛️  Setting up frontend..."
cd frontend

# Install dependencies if not already installed
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

cd ..

echo "✅ Development environment setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   Backend:  cd backend && poetry run uvicorn app.main:app --reload"
echo "   Frontend: cd frontend && npm run dev"
echo ""
echo "   Or use Docker: docker-compose up"
echo ""
echo "📱 Application URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"