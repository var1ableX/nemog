# LangGraph CLI

A comprehensive command-line interface for LangGraph, providing tools to create, develop, and deploy LangGraph applications. The CLI enables complete development workflows from project scaffolding through Docker-based deployment, with configuration-driven development server capabilities and hot reloading support.

## Package Information

- **Package Name**: langgraph-cli
- **Package Type**: CLI tool
- **Language**: Python
- **Installation**: `pip install langgraph-cli`
- **Development Mode**: `pip install "langgraph-cli[inmem]"`

## Core Imports

```python
# The CLI is accessed via command line, not Python imports
# Main entry point is the 'langgraph' command
```

For programmatic access to configuration handling (requires `pip install langgraph-cli`):

```python
from langgraph_cli.config import Config, validate_config, validate_config_file
```

## Basic Usage

```bash
# Create a new project
langgraph new my-project --template react-agent-python

# Run development server with hot reloading
langgraph dev --port 2024 --config langgraph.json

# Launch production server with Docker
langgraph up --port 8123 --config langgraph.json

# Build Docker image for deployment
langgraph build --tag my-app:latest --config langgraph.json

# Generate deployment files
langgraph dockerfile ./Dockerfile --config langgraph.json
```

## Architecture

LangGraph CLI follows a configuration-driven architecture:

- **Configuration Schema**: Comprehensive TypedDict classes define all configuration options
- **Command System**: Click-based CLI with modular command organization
- **Docker Integration**: Automatic Dockerfile and Docker Compose generation
- **Template System**: Extensible project scaffolding with multiple pre-built templates
- **Development Server**: Hot reloading development environment with debugging support

The CLI bridges development and production workflows by providing unified configuration through `langgraph.json` files that drive both local development and production deployment.

## Capabilities

### CLI Commands

Core command-line interface for all LangGraph development and deployment workflows. Includes project creation, development server, production deployment, and Docker image building.

```bash { .api }
langgraph new [PATH] --template TEMPLATE_NAME
langgraph dev --host HOST --port PORT --config CONFIG
langgraph up --port PORT --config CONFIG --docker-compose COMPOSE_FILE
langgraph build --tag TAG --config CONFIG
langgraph dockerfile SAVE_PATH --config CONFIG
```

[CLI Commands](./cli-commands.md)

### Configuration Management

Comprehensive configuration system for defining project dependencies, graph definitions, environment variables, and deployment settings through typed configuration schemas.

```python { .api }
def validate_config(config: Config) -> Config: ...
def validate_config_file(config_path: pathlib.Path) -> Config: ...
def config_to_docker(...) -> tuple[str, dict[str, str]]: ...
def config_to_compose(...) -> str: ...
```

[Configuration](./configuration.md)

### Docker Integration

Automated Docker and Docker Compose file generation from configuration, supporting multi-platform builds, custom base images, and development/production workflows.

```python { .api }
def check_capabilities(runner) -> DockerCapabilities: ...
def compose(capabilities, ...) -> str: ...
def dict_to_yaml(d: dict, *, indent: int = 0) -> str: ...
```

[Docker Integration](./docker-integration.md)

### Template System

Project scaffolding system with multiple pre-built templates for common LangGraph patterns, enabling rapid project initialization with best practices.

```python { .api }
def create_new(path: Optional[str], template: Optional[str]) -> None: ...
```

Available templates:
- New LangGraph Project (minimal chatbot)
- ReAct Agent (extensible agent with tools)
- Memory Agent (cross-conversation memory)
- Retrieval Agent (RAG capabilities)
- Data-enrichment Agent (web search)

[Templates](./templates.md)

## Types

### Core Configuration Types

```python { .api }
class Config(TypedDict, total=False):
    python_version: str
    node_version: str
    api_version: str
    base_image: str
    image_distro: Distros
    dependencies: list[str]
    graphs: dict[str, str]
    env: Union[str, dict[str, str]]
    dockerfile_lines: list[str]
    pip_config_file: str
    pip_installer: str
    store: StoreConfig
    auth: AuthConfig
    http: HttpConfig
    checkpointer: CheckpointerConfig
    ui: dict[str, Any]
    keep_pkg_tools: bool
```

### Store Configuration Types

```python { .api }
class StoreConfig(TypedDict, total=False):
    index: IndexConfig
    ttl: TTLConfig

class IndexConfig(TypedDict, total=False):
    dims: int  # Required
    embed: str  # Required
    fields: Optional[list[str]]

class TTLConfig(TypedDict, total=False):
    refresh_on_read: bool
    default_ttl: Optional[float]
    sweep_interval_minutes: Optional[int]
```

### Authentication and HTTP Types

```python { .api }
class AuthConfig(TypedDict, total=False):
    path: str  # Required
    disable_studio_auth: bool
    openapi: SecurityConfig

class HttpConfig(TypedDict, total=False):
    app: str
    disable_assistants: bool
    disable_threads: bool
    disable_runs: bool
    disable_store: bool
    disable_mcp: bool
    disable_meta: bool
    cors: CorsConfig
    configurable_headers: ConfigurableHeaderConfig
    logging_headers: ConfigurableHeaderConfig

class CheckpointerConfig(TypedDict, total=False):
    ttl: ThreadTTLConfig
```

### Docker Integration Types

```python { .api }
class DockerCapabilities(NamedTuple):
    docker: bool
    compose: bool
    buildx: bool
    version: str

# Type aliases
Distros = Literal["debian", "wolfi", "bullseye", "bookworm"]
```

## Constants

```python { .api }
# Configuration defaults
DEFAULT_CONFIG = "langgraph.json"
DEFAULT_PORT = 8123

# Version constraints
MIN_PYTHON_VERSION = "3.11"
DEFAULT_PYTHON_VERSION = "3.11"
MIN_NODE_VERSION = "20"
DEFAULT_NODE_VERSION = "20"
DEFAULT_IMAGE_DISTRO = "debian"

# Package version (managed via version.py)
__version__ = "0.4.2"
```