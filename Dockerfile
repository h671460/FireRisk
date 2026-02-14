FROM python:3.12-slim-bookworm

ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install uv binary
COPY --from=docker.io/astral/uv:0.9.28 /uv /uvx /bin/

WORKDIR /app

# copy project files
COPY . .

# install dependencies
RUN uv sync --locked

# run FastAPI dev server
CMD ["uv", "run", "fastapi", "dev", "src/firerisk/api/main.py", "--reload", "--host", "0.0.0.0", "--port", "8000"]
