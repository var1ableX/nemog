# CLI Commands

Core command-line interface providing all LangGraph development and deployment workflows. All commands support `--help` for detailed option information.

## Capabilities

### Project Creation

Create new LangGraph projects from predefined templates.

```bash { .api }
langgraph new [PATH] --template TEMPLATE_NAME
```

**Parameters:**
- `PATH` (optional): Directory path for new project
- `--template`: Template identifier (see Templates documentation)

**Usage Examples:**

```bash
# Create project in current directory with interactive template selection
langgraph new

# Create project in specific directory
langgraph new ./my-langgraph-app

# Create project with specific template
langgraph new my-project --template react-agent-python
```

### Development Server

Run LangGraph API server in development mode with hot reloading and debugging capabilities.

```bash { .api }
langgraph dev [OPTIONS]
```

**Key Options:**
- `--host TEXT`: Network interface to bind (default: 127.0.0.1)
- `--port INTEGER`: Port number (default: 2024)
- `--no-reload`: Disable automatic reloading
- `--config, -c FILE`: Configuration file path (default: langgraph.json)
- `--n-jobs-per-worker INTEGER`: Max concurrent jobs per worker
- `--no-browser`: Skip opening browser window
- `--debug-port INTEGER`: Enable remote debugging on port
- `--wait-for-client`: Wait for debugger connection
- `--studio-url TEXT`: LangGraph Studio URL
- `--allow-blocking`: Don't raise errors for blocking I/O
- `--tunnel`: Expose via public tunnel
- `--server-log-level TEXT`: API server log level (default: WARNING)

**Usage Examples:**

```bash
# Basic development server
langgraph dev

# Custom port and host
langgraph dev --host 0.0.0.0 --port 3000

# Development with debugging
langgraph dev --debug-port 5678 --wait-for-client

# Disable auto-reload and browser opening
langgraph dev --no-reload --no-browser
```

### Production Deployment

Launch LangGraph API server using Docker Compose for production deployment.

```bash { .api }
langgraph up [OPTIONS]
```

**Key Options:**
- `--port, -p INTEGER`: Port to expose (default: 8123)
- `--config, -c FILE`: Configuration file path (default: langgraph.json)
- `--docker-compose, -d FILE`: Additional docker-compose.yml file
- `--recreate/--no-recreate`: Container recreation control (default: no-recreate)
- `--pull/--no-pull`: Pull latest images (default: pull)
- `--watch`: Restart on file changes
- `--wait`: Wait for services to start
- `--verbose`: Show detailed server logs
- `--debugger-port INTEGER`: Serve debugger UI on port
- `--debugger-base-url TEXT`: URL for debugger to access API
- `--postgres-uri TEXT`: Custom PostgreSQL connection string
- `--api-version TEXT`: API server version to use
- `--image TEXT`: Pre-built Docker image to use
- `--base-image TEXT`: Base image for the server

**Usage Examples:**

```bash
# Basic production deployment
langgraph up

# Custom port and configuration
langgraph up --port 9000 --config my-config.json

# With additional services and debugging
langgraph up --docker-compose docker-compose.services.yml --debugger-port 8080

# Force recreate containers with verbose logging
langgraph up --recreate --verbose --wait
```

### Image Building

Build Docker images for LangGraph applications for deployment or distribution.

```bash { .api }
langgraph build -t IMAGE_TAG [OPTIONS] [DOCKER_BUILD_ARGS]...
```

**Key Options:**
- `--tag, -t TEXT`: Docker image tag (required)
- `--config, -c FILE`: Configuration file path (default: langgraph.json)
- `--pull/--no-pull`: Pull latest base images (default: pull)
- `--base-image TEXT`: Override base image
- `--api-version TEXT`: API server version
- `--install-command TEXT`: Custom install command
- `--build-command TEXT`: Custom build command

**Parameters:**
- `DOCKER_BUILD_ARGS`: Additional Docker build arguments (passed through)

**Usage Examples:**

```bash
# Basic image build
langgraph build -t my-app:latest

# Multi-platform build with custom base image
langgraph build -t my-app:v1.0 --base-image python:3.11-slim --platform linux/amd64,linux/arm64

# Build with custom configuration and no base image pull
langgraph build -t my-app:dev --config dev.json --no-pull

# Advanced build with Docker build args
langgraph build -t my-app:latest --build-arg HTTP_PROXY=http://proxy.example.com:8080
```

### File Generation

Generate Dockerfile and Docker Compose files for custom deployment workflows.

```bash { .api }
langgraph dockerfile SAVE_PATH [OPTIONS]
```

**Parameters:**
- `SAVE_PATH`: Path where Dockerfile will be saved (required)

**Key Options:**
- `--config, -c FILE`: Configuration file path (default: langgraph.json)
- `--add-docker-compose`: Generate docker-compose.yml and related files
- `--base-image TEXT`: Override base image
- `--api-version TEXT`: API server version

**Usage Examples:**

```bash
# Generate Dockerfile only
langgraph dockerfile ./Dockerfile

# Generate Dockerfile and Docker Compose files
langgraph dockerfile ./Dockerfile --add-docker-compose

# Generate with custom configuration and base image
langgraph dockerfile ./deploy/Dockerfile --config prod.json --base-image python:3.12-alpine
```

## Global Options

All commands support these global options:

- `--help`: Show help message and available options
- `--version`: Show CLI version information

## Configuration File

All commands default to using `langgraph.json` in the current directory. This file defines:

- **dependencies**: Python/Node.js packages required
- **graphs**: Mapping of graph IDs to import paths
- **env**: Environment variables (file path or dictionary)
- **python_version**: Python runtime version (3.11, 3.12, 3.13)

Example minimal configuration:

```json
{
  "dependencies": ["langchain_openai", "."],
  "graphs": {
    "my_graph": "./src/graph.py:compiled_graph"
  },
  "env": "./.env"
}
```

## Error Handling

The CLI provides detailed error messages for common issues:

- **Configuration validation errors**: Invalid langgraph.json format or missing required fields
- **Docker errors**: Missing Docker/Docker Compose or insufficient permissions
- **Port conflicts**: Port already in use for development or production servers
- **Template errors**: Invalid or missing template specifications
- **Build failures**: Docker build errors with context and suggestions

Use `--verbose` flag with applicable commands for additional debugging information.