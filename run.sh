#!/usr/bin/env sh

# Build and run the Docker image with a specified tag.

# Determine if the script is running in an interactive terminal
if [ -t 1 ]; then
    INTERACTIVE="-it"
else
    INTERACTIVE=""
fi

# Assign the first argument as the image tag, or use default
if [ "$#" -ge 1 ]; then
    TAG="$1"
    shift
else
    TAG="my-default-tag"
fi

echo "TAG is: $TAG"
echo "INTERACTIVE is: $INTERACTIVE"

# Build the Docker image with the specified tag
echo "Building Docker image with tag: $TAG"
docker build -t "$TAG" .

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "Docker image build failed."
    exit 1
fi

# Run the Docker container using the tagged image
if [ "$#" -gt 0 ]; then
    ARGS="$@"
else
    ARGS=""
fi

echo "Running Docker container from image: $TAG"
docker run \
    --rm \
    --volume "$(pwd)":/app \
    --volume /app/.venv \
    --publish 8000:8000 \
    $INTERACTIVE \
    "$TAG" \
    $ARGS