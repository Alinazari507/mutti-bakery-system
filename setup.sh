#!/bin/bash

set -euo pipefail

APP_NAME="muttis-bakery"
BASE_DIR="$(pwd)/${APP_NAME}"
LOG_FILE="${BASE_DIR}/logs/setup.log"

echo "Setting up unified Mutti's Bakery project structure..."

mkdir -p "${BASE_DIR}/src"
mkdir -p "${BASE_DIR}/data"
mkdir -p "${BASE_DIR}/logs"

touch "${BASE_DIR}/src/__init__.py"
touch "${BASE_DIR}/src/main.py"
touch "${BASE_DIR}/src/auth.py"
touch "${BASE_DIR}/src/ingredient.py"
touch "${BASE_DIR}/src/recipe.py"
touch "${BASE_DIR}/src/cache.py"
touch "${BASE_DIR}/src/break_glass.py"
touch "${BASE_DIR}/data/recipes.json"
touch "${BASE_DIR}/data/conversions.json"
touch "${BASE_DIR}/logs/app.log"

echo "Project structure initialized successfully."