uv-docker-example 

uv-docker-example
=================

An example project for using uv in Docker images, with a focus on best practices for developing with the project mounted in the local image.

See the [uv Docker integration guide](https://docs.astral.sh/uv/guides/integration/docker/) for more background.

Trying it out
-------------

A [run.sh](./run.sh) utility is provided for quickly building the image and starting a container. This script demonstrates best practices for developing using the container, using bind mounts for the project and virtual environment directories.

To build and run the web application in the container using docker run:

    $ ./run.sh
        

Then, check out [http://localhost:8000](http://localhost:8000) to see the website.

A Docker Compose configuration is also provided to demonstrate best practices for developing using the container with Docker Compose. Docker Compose is more complex than using docker run, but has more robust support for various workflows.

To build and run the web application using Docker Compose:

    $ docker compose up --watch
        

By default, the image is set up to start the web application. However, a command-line interface is provided for demonstration purposes as well.

To run the command-line entrypoint in the container:

    $ ./run.sh hello
        

Using run2.sh with Custom Tagging and Build Output
--------------------------------------------------

A modified script `run2.sh` is also provided, which extends the functionality of `run.sh` by allowing you to specify a custom image tag and see detailed build output. This script is useful when you want more control over the image tagging and need to debug the build process.

### Key Features of run2.sh:

*   **Custom Image Tagging:** You can specify an image tag as the first argument when running the script. This allows you to build and run images with meaningful names, making it easier to manage and reference them.
*   **Detailed Build Output:** The script removes the quiet mode (`-q`), so you can see detailed output from the docker build command, which is helpful for debugging build issues.
*   **Error Handling:** Checks if the build was successful before attempting to run the container, providing informative error messages.
*   **Argument Passing:** Allows you to pass additional commands or arguments to the container, enabling flexible usage.
*   **Interactive Mode Detection:** Automatically detects if the script is run in an interactive terminal and sets the Docker interactive options accordingly.

### How to Use run2.sh:

#### Build and Run with Default Tag:

    $ ./run2.sh
        

Then, check out [http://localhost:8000](http://localhost:8000) to see the website.

#### Build and Run with a Custom Tag:

    $ ./run2.sh my-custom-tag
        

This builds the Docker image with the tag `my-custom-tag` and runs the container using that image. Using custom tags allows you to manage different versions of your image and makes it easier to reference specific builds.

#### Benefits of Using Custom Tags:

*   **Image Management:** Custom tags help you keep track of different builds, especially when working on features or versions.
*   **Reusability:** You can run containers from previously built images without rebuilding them, saving time.
*   **Clarity:** Meaningful tags make it easier to understand which image you're working with.

#### Passing Commands to the Container:

    $ ./run2.sh my-custom-tag python app.py
        

This will execute `python app.py` inside the container.

#### Entering a Bash Shell in the Container:

    $ ./run2.sh my-custom-tag /bin/bash
        

This is useful for debugging or inspecting the container environment.

### Example Workflow Using run2.sh with Tags:

#### Build and Run the Application:

    $ ./run2.sh my-app-tag
        

This builds the image with tag `my-app-tag` and runs the container.

#### Make Changes to the Code:

Edit your application code locally. Since the project directory is mounted into the container, changes will be reflected without rebuilding the image.

#### Rebuild with a New Tag:

    $ ./run2.sh my-app-tag-v2
        

Now you have a new image tagged `my-app-tag-v2`.

#### Run Commands Inside the Container:

    $ ./run2.sh my-app-tag-v2 uv sync --frozen
        

This checks that the environment is up-to-date inside the container.

Understanding run2.sh Script:
-----------------------------

### Script Breakdown:

    #!/usr/bin/env sh
    
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
    echo "Running Docker container from image: $TAG"
    docker run \
        --rm \
        --volume "$(pwd)":/app \
        --volume /app/.venv \
        --publish 8000:8000 \
        $INTERACTIVE \
        "$TAG" \
        "$@"
        

### Key Points:

*   **Interactive Mode Detection:** The script checks if it's running in an interactive terminal and sets the `-it` option for `docker run` accordingly.
*   **Tag Assignment:** Uses the first argument as the image tag, or defaults to `my-default-tag` if none is provided. This allows for flexibility in naming your images.
*   **Conditional shift:** Adjusts the positional parameters only if an argument is provided, preventing errors when no tag is specified.
*   **Build Process:** Runs `docker build` with the specified tag and provides detailed output, aiding in debugging.
*   **Error Handling:** Exits the script if the build fails, ensuring that you don't attempt to run a container from a failed build.
*   **Running the Container:** Uses the tagged image to run the container and passes any additional arguments to the container.

Project Overview
----------------

### Dockerfile

The `Dockerfile` defines the image and includes:

*   Installation of uv
*   Installing the project dependencies and the project separately for optimal image build caching
*   Placing environment executables on the `PATH`
*   Running the web application

The `multistage.Dockerfile` example extends the `Dockerfile` example to use multistage builds to reduce the final size of the image.

### Dockerignore file

The `.dockerignore` file includes an entry for the `.venv` directory to ensure the `.venv` is not included in image builds. Note that the `.dockerignore` file is not applied to volume mounts during container runs.

### Run scripts

#### run.sh:

The `run.sh` script includes an example of invoking `docker run` for local development, mounting the source code for the project into the container so that edits are reflected immediately.

#### run2.sh:

The `run2.sh` script enhances `run.sh` by adding support for custom image tagging, detailed build output, and improved error handling. It is particularly useful when you need more control over the build and run process, such as when debugging or managing multiple image versions.

### Docker Compose file

The `compose.yml` file includes a Docker Compose definition for the web application. It includes a watch directive for Docker Compose, which is a best-practice method for updating the container on local changes.

### Application code

The Python application code for the project is at `src/uv_docker_example/__init__.py` — there's a command line entrypoint and a basic FastAPI application — both of which just display "hello world" output.

### Project definition

The project at `pyproject.toml` includes Ruff as an example development dependency, includes FastAPI as a dependency, and defines a `hello` entrypoint for the application.

Useful commands
---------------

To check that the environment is up-to-date after image builds using `run2.sh`:

    $ ./run2.sh my-custom-tag uv sync --frozen
    Audited 2 packages ...
        

To enter a bash shell in the container using `run2.sh`:

    $ ./run2.sh my-custom-tag /bin/bash
        

To build the image without running anything:

    $ docker build -t my-custom-tag .
        

To build the multistage image:

    $ docker build -t my-custom-tag -f multistage.Dockerfile .
        

Summary
-------

The `run2.sh` script provides enhanced functionality over the original `run.sh`, allowing for custom image tagging, detailed build outputs, and better error handling. It is especially useful for development workflows where you need more control and visibility over the Docker build and run processes.

### Benefits of Using run2.sh with Tags:

*   **Custom Tagging:** Helps manage and distinguish between different builds or versions of your application.
*   **Detailed Build Output:** Useful for debugging and ensuring the build process completes successfully.
*   **Flexibility:** Ability to pass commands or arguments to the container, enabling various workflows like running different services or scripts inside the container.

Feel free to use either script based on your requirements:

*   **Use run.sh** for quick development iterations with minimal configuration.
*   **Use run2.sh** when you need to specify custom image tags, debug build issues, or manage multiple image versions.

If you have any questions or need further assistance, please refer to the script comments or the Docker documentation.