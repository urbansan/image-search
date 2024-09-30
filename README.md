# Image Search Engine

## Intro

This project is a PoC for a scalable image search web service. It comprises of:
0. UI: Swagger/OpenAPI built in FastAPI:)
1. Nginx reverse proxy as an entry point
2. 2 (or more) FastAPI services
3. MySQL service
4. Redis service with Redisearch
5. RabbitMQ broker to offload computation from the FastAPI apps
6. Taskiq async workers which process images

## How to Run

To run the project locally, follow these steps:

1. Run the default docker-compose.yaml:
   ```bash
   docker compose up --build
   ```
   wait for all services to get up and all migrations to be applied

   
2. Goto the address in your browser:
    ```bash
    localhost:8000/docs
   ```
   
## How to Test

Tests require services: Redis and Mysql.

1. Prepare Images:
   ```bash
   ./prep-images.sh
   ```

2. Tests require services: Redis and Mysql. All DB migrations and Redisearch indices are defined in the docker-compose files
   ```bash
   docker compose -f docker-compose-test.yaml up --build
   ```

3. Run tests
    ```bash
    ./run-tests.sh
   ```
   
## Base Python stack
1. Alembic for migrations. Migrations are applied when running docker-compose files. To add a revision run
   ```bash 
   ./add-db-revision.sh
   ```
2. Taskiq for MQ workers.
3. SqlAlchemy CORE for async programming with DB.
4. Pytest for testing.
5. Isort, ruff, black, mypy for quality tools.
6. Poetry for managing packages.
7. Pydantic-settings for environment variables management.
8. Polyfactory for test object generation (although not yet used).

Disclaimer: No logging was used, because it was not required for such a small app:)