# Docker Integration

Automated Docker and Docker Compose integration for LangGraph applications. Provides capability detection, file generation, and orchestration support for development and production deployments.

## Capabilities

### Docker Capability Detection

Detect available Docker and Docker Compose features on the system.

```python { .api }
def check_capabilities(runner) -> DockerCapabilities
```

**Purpose**: Detect Docker and Docker Compose capabilities and versions
**Parameters**:
- `runner`: Execution runner context for subprocess commands
**Returns**: DockerCapabilities named tuple with detected features

```python { .api }
class DockerCapabilities(NamedTuple):
    docker: bool
    compose: bool
    buildx: bool
    version: str
```

**DockerCapabilities Properties:**
- **docker**: Docker CLI availability
- **compose**: Docker Compose availability (v2+ preferred)
- **buildx**: Docker Buildx multi-platform build support
- **version**: Docker version string

**Usage Examples:**

```python
from langgraph_cli.docker import check_capabilities
from langgraph_cli.exec import Runner

with Runner() as runner:
    caps = check_capabilities(runner)

    if caps.docker:
        print(f"Docker {caps.version} available")

    if caps.compose:
        print("Docker Compose available")

    if caps.buildx:
        print("Multi-platform builds supported")
```

### Docker Compose Generation

Generate Docker Compose YAML files from configuration and runtime parameters.

```python { .api }
def compose(
    capabilities: DockerCapabilities,
    image: str,
    config: Config,
    port: int = DEFAULT_PORT,
    docker_compose: Optional[pathlib.Path] = None,
    watch: bool = False,
    debugger_port: Optional[int] = None,
    debugger_base_url: Optional[str] = None,
    postgres_uri: Optional[str] = None
) -> str
```

**Purpose**: Generate complete Docker Compose YAML for LangGraph deployment
**Parameters**:
- `capabilities` (DockerCapabilities): Docker system capabilities
- `image` (str): Docker image name to deploy
- `config` (Config): LangGraph configuration object
- `port` (int): Host port to expose (default: 8123)
- `docker_compose` (Optional[pathlib.Path]): Additional compose file to merge
- `watch` (bool): Enable file watching for development
- `debugger_port` (Optional[int]): Port for debugger UI
- `debugger_base_url` (Optional[str]): Base URL for debugger API access
- `postgres_uri` (Optional[str]): Custom PostgreSQL connection string
**Returns**: Complete Docker Compose YAML as string

**Usage Examples:**

```python
from langgraph_cli.docker import compose, check_capabilities
from langgraph_cli.config import validate_config_file
from langgraph_cli.exec import Runner
import pathlib

# Load configuration and check capabilities
config = validate_config_file(pathlib.Path("langgraph.json"))

with Runner() as runner:
    capabilities = check_capabilities(runner)

    # Generate compose file for production
    compose_yaml = compose(
        capabilities=capabilities,
        image="my-app:latest",
        config=config,
        port=8080
    )

    # Generate compose file for development with debugging
    dev_compose_yaml = compose(
        capabilities=capabilities,
        image="my-app:dev",
        config=config,
        port=2024,
        watch=True,
        debugger_port=8081,
        debugger_base_url="http://localhost:2024"
    )

    # Generate with additional services
    full_compose_yaml = compose(
        capabilities=capabilities,
        image="my-app:latest",
        config=config,
        docker_compose=pathlib.Path("docker-compose.services.yml"),
        postgres_uri="postgresql://user:pass@postgres:5432/db"
    )
```

### YAML Utilities

Convert Python data structures to properly formatted YAML.

```python { .api }
def dict_to_yaml(d: dict, *, indent: int = 0) -> str
```

**Purpose**: Convert dictionary to YAML format with proper indentation
**Parameters**:
- `d` (dict): Dictionary to convert to YAML
- `indent` (int): Base indentation level (default: 0)
**Returns**: YAML string representation

**Usage Examples:**

```python
from langgraph_cli.docker import dict_to_yaml

# Convert configuration to YAML
config_dict = {
    "services": {
        "app": {
            "image": "my-app:latest",
            "ports": ["8080:8080"],
            "environment": {
                "LOG_LEVEL": "INFO"
            }
        }
    }
}

yaml_output = dict_to_yaml(config_dict)
print(yaml_output)
# Output:
# services:
#   app:
#     image: my-app:latest
#     ports:
#       - "8080:8080"
#     environment:
#       LOG_LEVEL: INFO
```

## Docker Compose Templates

The CLI generates different Docker Compose configurations based on use case:

### Basic Production Deployment

```yaml
version: '3.8'
services:
  langgraph-api:
    image: my-app:latest
    ports:
      - "8123:8000"
    environment:
      - PORT=8000
      - HOST=0.0.0.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Development with Debugging

```yaml
version: '3.8'
services:
  langgraph-api:
    image: my-app:dev
    ports:
      - "2024:8000"
      - "8081:8001"  # debugger port
    environment:
      - PORT=8000
      - HOST=0.0.0.0
      - DEBUGGER_PORT=8001
    volumes:
      - ./src:/app/src:ro  # watch mode
    develop:
      watch:
        - action: rebuild
          path: ./src
```

### Production with PostgreSQL

```yaml
version: '3.8'
services:
  langgraph-api:
    image: my-app:latest
    ports:
      - "8123:8000"
    environment:
      - PORT=8000
      - HOST=0.0.0.0
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/langgraph
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=langgraph
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

## Multi-Platform Support

Docker integration supports multi-platform builds using Docker Buildx:

### Platform Detection

The system automatically detects Buildx support and enables multi-platform builds when available:

```python
# Capability detection includes Buildx support
capabilities = check_capabilities(runner)
if capabilities.buildx:
    # Multi-platform builds available
    platforms = ["linux/amd64", "linux/arm64"]
```

### Build Commands

Generated Docker commands support platform specification:

```bash
# Single platform
docker build -t my-app:latest .

# Multi-platform with Buildx
docker buildx build --platform linux/amd64,linux/arm64 -t my-app:latest .
```

## File Generation Workflow

The CLI follows this workflow for Docker file generation:

1. **Capability Detection**: Check Docker, Compose, and Buildx availability
2. **Configuration Validation**: Validate langgraph.json configuration
3. **Dockerfile Generation**: Create Dockerfile from configuration and templates
4. **Compose Generation**: Create docker-compose.yml with services and networking
5. **Additional Files**: Generate .dockerignore, environment files, and health checks

### Generated Files

- **Dockerfile**: Multi-stage build with Python/Node.js setup
- **docker-compose.yml**: Service orchestration and networking
- **.dockerignore**: Optimized build context exclusions
- **docker-compose.override.yml**: Development-specific overrides (when applicable)

## Environment Integration

Docker containers are configured with proper environment variable handling:

### Configuration Sources

1. **langgraph.json env field**: File path or dictionary
2. **Command-line overrides**: Runtime environment variables
3. **Docker Compose environment**: Container-specific variables
4. **External .env files**: Mounted or copied environment files

### Variable Precedence

1. Command-line arguments (highest priority)
2. Docker Compose environment section
3. Container environment variables
4. Configuration file env dictionary
5. External .env files (lowest priority)

## Health Checks and Monitoring

Generated Docker configurations include health checks and monitoring:

### Application Health Checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

### Dependency Health Checks

```yaml
# PostgreSQL health check
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
  interval: 5s
  timeout: 5s
  retries: 5
```

### Resource Limits

Production configurations include resource constraints:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

## Error Handling

Docker integration provides detailed error handling:

- **Missing Docker**: Clear error message with installation instructions
- **Version compatibility**: Warnings for older Docker/Compose versions
- **Build failures**: Detailed build logs and troubleshooting steps
- **Network conflicts**: Port availability checking and suggestions
- **Image pull failures**: Registry authentication and connectivity guidance