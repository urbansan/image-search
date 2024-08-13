#!/bin/bash

docker run -v .:/app/:rw focal-test-base:latest pytest tests


