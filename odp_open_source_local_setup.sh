#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# ==============================================================================
# Configuration Options
# ==============================================================================
# Define base paths
DEPLOY_BASE="${DEPLOY_BASE:-$HOME/odp-local-setup}"
SETUP_PATH="${SETUP_PATH:-$DEPLOY_BASE/opendatapipeline}"

# Frontend Build Variables
REACT_APP_SERVER_ENVIRONMENT="${REACT_APP_SERVER_ENVIRONMENT:-dev}"
# Note: (Optional) Ask the administrator for the REACT_APP_CLIENT_ID if Google OAuth is required
REACT_APP_CLIENT_ID="${REACT_APP_CLIENT_ID:-}"

# Minimum required versions
MIN_DOCKER_VERSION="24"
MIN_NODE_VERSION="18"

# ==============================================================================
# Helper Functions
# ==============================================================================
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ==============================================================================
# Prerequisite Checks
# ==============================================================================
echo_info "Verifying prerequisites..."

# 1. Check if running from root of cloned repository
if [ ! -d "client" ] || [ ! -d "docker" ] || [ ! -d "opendatapipeline" ]; then
    echo_error "Please run this script from the root of the cloned OpenDataPipeline repository."
    exit 1
fi

# 2. Check Docker
if ! command -v docker >/dev/null 2>&1; then
    echo_error "Docker is not installed. Please install Docker v${MIN_DOCKER_VERSION}+ and try again."
    exit 1
fi

docker_version=$(docker --version | grep -oE '[0-9]+' | head -1)
if [ "$docker_version" -lt "$MIN_DOCKER_VERSION" ]; then
    echo_error "Docker version is too old. Found v${docker_version}, but v${MIN_DOCKER_VERSION}+ is required."
    exit 1
fi
echo_info "Docker check passed (v${docker_version})."

# 3. Check Node.js
if ! command -v node >/dev/null 2>&1; then
    echo_error "Node.js is not installed. Please install Node.js v${MIN_NODE_VERSION}+ and try again."
    exit 1
fi

# node --version outputs something like v18.19.0, we just want the major number
node_version=$(node --version | grep -oE '[0-9]+' | head -1)
if [ "$node_version" -lt "$MIN_NODE_VERSION" ]; then
    echo_error "Node.js version is too old. Found v${node_version}, but v${MIN_NODE_VERSION}+ is required."
    exit 1
fi
echo_info "Node.js check passed (v${node_version})."

# 4. Check npm
if ! command -v npm >/dev/null 2>&1; then
    echo_error "npm is not installed. Please install npm and try again."
    exit 1
fi

# ==============================================================================
# 1. Build the Frontend (FE)
# ==============================================================================
echo_info "Building the Frontend (FE)..."
pushd client > /dev/null

export REACT_APP_SERVER_ENVIRONMENT
export REACT_APP_CLIENT_ID

echo_info "Installing npm dependencies (this may take a while)..."
npm install --force

echo_info "Running frontend build..."
CI=false npm run build

popd > /dev/null
echo_info "Frontend build completed successfully."

# ==============================================================================
# 2. Configure Environment Variables
# ==============================================================================
echo_info "Configuring Environment Variables..."
if [ ! -f "docker/.env" ]; then
    if [ -f "docker/.env.example" ]; then
        cp docker/.env.example docker/.env
        echo_info "Copied docker/.env.example to docker/.env"
    else
        echo_error "docker/.env.example not found. Please ensure it exists."
        exit 1
    fi
else
    echo_warn "docker/.env already exists, skipping copy."
fi

# ==============================================================================
# 3. Assemble the Environment
# ==============================================================================
echo_info "Assembling the environment at ${SETUP_PATH}..."
mkdir -p "$SETUP_PATH"

# Copy shared dependencies to base folder
echo_info "Copying shared dependencies..."
mkdir -p "$DEPLOY_BASE/odp_code_context" "$DEPLOY_BASE/audit_tracker" "$DEPLOY_BASE/core"
cp -r odp_code_context/. "$DEPLOY_BASE/odp_code_context/"
cp -r audit_tracker/. "$DEPLOY_BASE/audit_tracker/"
cp -r core/. "$DEPLOY_BASE/core/"

# Copy application components to setup path
echo_info "Copying application components..."
mkdir -p "$SETUP_PATH/opendatapipeline_src" "$SETUP_PATH/airflow" "$SETUP_PATH/spark_server_app" "$SETUP_PATH/dlt_server_app" "$SETUP_PATH/hadoop_local" "$SETUP_PATH/inbuilt_modules" "$SETUP_PATH/opendatapipeline"
cp -r opendatapipeline/src/. "$SETUP_PATH/opendatapipeline_src/"
cp opendatapipeline/requirements.txt "$SETUP_PATH/opendatapipeline_src/requirements.txt"
cp opendatapipeline/pyproject.toml "$SETUP_PATH/opendatapipeline_src/pyproject.toml"
cp opendatapipeline/setup.cfg "$SETUP_PATH/opendatapipeline_src/setup.cfg"
cp opendatapipeline/setup.py "$SETUP_PATH/opendatapipeline_src/setup.py"
cp -r airflow/. "$SETUP_PATH/airflow/"
cp -r spark_server_app/. "$SETUP_PATH/spark_server_app/"
cp -r dlt_server_app/. "$SETUP_PATH/dlt_server_app/"
cp -r opendatapipeline/hadoop_local/. "$SETUP_PATH/hadoop_local/"
cp -r opendatapipeline/inbuilt_modules/. "$SETUP_PATH/inbuilt_modules/"
cp -r docker/opendatapipeline/. "$SETUP_PATH/opendatapipeline/"

# Copy Frontend (FE) build and templates
echo_info "Copying Frontend build and templates..."
mkdir -p "$SETUP_PATH/opendatapipeline_src/api/static/react"
cp -r client/build/. "$SETUP_PATH/opendatapipeline_src/api/static/react/"
cp -r templates/. "$SETUP_PATH/opendatapipeline_src/api/templates/"

# Copy configuration and Docker files
echo_info "Copying configuration and Docker files..."
cp docker/.env "$SETUP_PATH/.env"
cp docker/docker-compose.yml "$SETUP_PATH/docker-compose.yml"
cp docker/airflow_docker.Dockerfile "$SETUP_PATH/airflow_docker.Dockerfile"

# Create necessary data directories for Docker volumes
echo_info "Creating data directories..."
mkdir -p "$SETUP_PATH/askondata/data/mongo/primary"
mkdir -p "$SETUP_PATH/askondata/data/mongo/secondary"
mkdir -p "$SETUP_PATH/askondata/data/mongo/tertiary"
mkdir -p "$SETUP_PATH/askondata/data/postgres"
mkdir -p "$SETUP_PATH/askondata/data/ollama"
mkdir -p "$SETUP_PATH/askondata/data/airflow/dags"
mkdir -p "$SETUP_PATH/opendatapipeline/logs/airflow"
mkdir -p "$SETUP_PATH/opendatapipeline/logs/spark"

# Prepare Airflow DAGs directory structure
echo_info "Preparing Airflow DAGs directory..."
cp -r airflow/dags/. "$SETUP_PATH/askondata/data/airflow/dags/"

# Prepare Spark configuration
echo_info "Preparing Spark configuration for environment: ${REACT_APP_SERVER_ENVIRONMENT}"
cp "$SETUP_PATH/opendatapipeline/config/spark/${REACT_APP_SERVER_ENVIRONMENT}/spark-defaults.conf" "$SETUP_PATH/opendatapipeline/config/spark/spark-defaults.conf"

# ==============================================================================
# 4. Build and Start Services
# ==============================================================================
echo_info "Building and starting Docker Compose services..."
pushd "$SETUP_PATH" > /dev/null

echo_info "Building docker images (--no-cache)..."
export SPARK_PROFILE=""
docker compose --profile dev build --no-cache

echo_info "Starting containers..."
docker compose --profile dev up -d

popd > /dev/null

echo_info "============================================================"
echo_info "Setup completed successfully!"
echo_info "The environment has been set up at: ${SETUP_PATH}"
echo_info "Monitor the container health status by running: watch docker ps"
echo_info "Once all containers are healthy, access the app at: https://localhost"
echo_info "============================================================"
