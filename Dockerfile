FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --extra prod 2>/dev/null || uv sync --no-dev --extra prod

# Copy project
COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uv run python manage.py migrate --noinput && uv run python manage.py create_initial_user && uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
