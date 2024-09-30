#!/bin/bash



docker run --network=image_search_default -v .:/app/:rw image-search:latest poetry run alembic revision --autogenerate