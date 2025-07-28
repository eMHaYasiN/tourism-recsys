.PHONY: help setup run test clean docker

help:
	@echo "Available commands:"
	@echo "  make setup   - Install dependencies"
	@echo "  make run     - Run API locally"
	@echo "  make test    - Run tests"
	@echo "  make docker  - Build Docker image"
	@echo "  make clean   - Clean up files"

setup:
	pip install -r requirements.txt

run:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

docker:
	docker build -t tourism-recsys:latest .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
