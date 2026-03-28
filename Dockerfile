FROM python:3.12-slim-bookworm

ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install uv binary
COPY --from=docker.io/astral/uv:0.9.28 /uv /uvx /bin/

WORKDIR /app


# copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

# install dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project


# copy project files
COPY . .

# install dependencies
# RUN uv sync --locked

# install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# run FastAPI dev server
CMD ["uv", "run", "firerisk-api"]
