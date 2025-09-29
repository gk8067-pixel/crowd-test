#!/bin/bash

echo "==================================="
echo "Survey System - Quick Start Script"
echo "==================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

# Check Python version
echo "Checking Python version..."
python3 --version

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until PGPASSWORD=password psql -h localhost -U postgres -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL is up!"

# Create database if not exists
echo "Creating database..."
PGPASSWORD=password psql -h localhost -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'survey_db'" | grep -q 1 || PGPASSWORD=password psql -h localhost -U postgres -c "CREATE DATABASE survey_db"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start services in background
echo "Starting backend server..."
uvicorn backend_main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting Celery worker..."
celery -A celery_worker worker --loglevel=info &
CELERY_PID=$!

echo "Starting Celery beat..."
celery -A celery_worker beat --loglevel=info &
BEAT_PID=$!

# Setup frontend
if [ -d "frontend" ]; then
    echo "Setting up frontend..."
    cd frontend
    
    if [ ! -f .env.local ]; then
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
    fi
    
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    echo "Starting frontend server..."
    npm run dev &
    FRONTEND_PID=$!
    cd ..
fi

echo ""
echo "==================================="
echo "All services started successfully!"
echo "==================================="
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo "==================================="

# Wait for Ctrl+C
trap "echo 'Stopping services...'; kill $BACKEND_PID $CELERY_PID $BEAT_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait