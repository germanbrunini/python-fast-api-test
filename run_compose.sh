#!/usr/bin/env sh

# Build and run the Docker image with a specified tag.

# Determine if the script is running in an interactive terminal
if [ -t 1 ]; then
    INTERACTIVE="-it"
else
    INTERACTIVE=""
fi

# Default values
TAG="my-default-tag"
COMPOSE_FLAG="false"

# Parse arguments
while [ "$#" -gt 0 ]; do
    case "$1" in
        compose=*)
            COMPOSE_FLAG="${1#*=}"
            ;;
        *)
            TAG="$1"
            ;;
    esac
    shift
done

echo "TAG is: $TAG"
echo "COMPOSE_FLAG is: $COMPOSE_FLAG"
echo "INTERACTIVE is: $INTERACTIVE"

# Build the Docker image with the specified tag
echo "Building Docker image with tag: $TAG"
docker build -t "$TAG" .

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "Docker image build failed."
    exit 1
fi

# Decide whether to run docker compose or docker run
if [ "$COMPOSE_FLAG" = "true" ]; then
    echo "Running Docker Compose"
    docker compose up
else
    # Run the Docker container using the tagged image
    echo "Running Docker container from image: $TAG"
    docker run \
        --rm \
        --volume "$(pwd)":/app \
        --volume /app/.venv \
        --publish 8000:8000 \
        $INTERACTIVE \
        "$TAG"
fi
