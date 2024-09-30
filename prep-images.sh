#!/bin/bash


docker build -f Dockerfile -t image-search:latest . && \
docker build -f DockerfileTest -t test-image-search:latest .