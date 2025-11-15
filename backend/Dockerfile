# Build stage - install dependencies
FROM python:3.13-slim-bookworm AS builder

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.4

# Copy dependency files only
COPY pyproject.toml poetry.lock ./

# Export dependencies to requirements.txt (Poetry not needed in final image)
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev


# Runtime stage - minimal final image
FROM python:3.13-slim-bookworm

WORKDIR /app

# Install runtime dependencies only
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY alembic.ini .
COPY alembic ./alembic
COPY scripts ./scripts

# Copy Firebase service account (required for push notifications)
COPY firebase-service-account.json .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]