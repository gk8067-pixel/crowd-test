.PHONY: help install dev migrate upgrade downgrade celery beat flower test clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Start development server"
	@echo "  make migrate      - Create new migration"
	@echo "  make upgrade      - Run database migrations"
	@echo "  make downgrade    - Rollback last migration"
	@echo "  make celery       - Start Celery worker"
	@echo "  make beat         - Start Celery beat"
	@echo "  make flower       - Start Flower monitoring"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean cache files"
	@echo "  make docker-up    - Start Docker services"
	@echo "  make docker-down  - Stop Docker services"

install:
	pip install -r requirements.txt

dev:
	uvicorn backend_main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic revision --autogenerate -m "$(msg)"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

celery:
	celery -A celery_worker worker --loglevel=info

beat:
	celery -A celery_worker beat --loglevel=info

celery-all:
	celery -A celery_worker worker --beat --loglevel=info

flower:
	celery -A celery_worker flower --port=5555

test:
	pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

docker-rebuild:
	docker-compose up -d --build