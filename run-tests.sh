#!/bin/bash


exit_code=0

scripts=(
  "pytest tests"
  "black --check image_search tests"
  "isort --check image_search tests"
  "ruff check image_search tests"
  "mypy image_search"
)

for script in "${scripts[@]}"; do
  echo "Running Test >>> "$script
  docker run --network=image_search_default \
  -v .:/app/:rw \
  --env MYSQL_ROOT_PASSWORD=rootpassword \
  --env MYSQL_DATABASE=mydatabase \
  --env MYSQL_USER=myuser \
  --env MYSQL_PASSWORD=mypassword \
  --env MYSQL_HOST=mysql-image-search-test \
  --env MYSQL_PORT=3306 \
  --env REDIS_HOST=redis-image-search-test \
  --env REDIS_PORT=6379 \
  test-image-search:latest poetry run $script

  script_exit_code=$?
  if [ $script_exit_code -ne 0 ]; then
      exit_code=$script_exit_code

  fi
done

exit $exit_code




