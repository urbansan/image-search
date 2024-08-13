FROM focal-test-base:latest

COPY . .

# Run Alembic migrations
# RUN alembic upgrade head

# Expose the port the FastAPI app runs on
EXPOSE 8000

# The command to run the FastAPI app is defined in docker-compose.yml