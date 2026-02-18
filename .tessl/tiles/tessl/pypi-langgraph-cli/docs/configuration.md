# Configuration

Comprehensive configuration system for LangGraph CLI applications. Configuration is defined through `langgraph.json` files and validated using typed Python schemas.

## Capabilities

### Configuration Validation

Validate and normalize configuration data from dictionaries or JSON files.

```python { .api }
def validate_config(config: Config) -> Config
```

**Purpose**: Validate and normalize a configuration dictionary
**Parameters**:
- `config` (Config): Raw configuration dictionary to validate
**Returns**: Validated and normalized Config object
**Raises**: ValidationError for invalid configuration

```python { .api }
def validate_config_file(config_path: pathlib.Path) -> Config
```

**Purpose**: Load and validate configuration from JSON file
**Parameters**:
- `config_path` (pathlib.Path): Path to langgraph.json configuration file
**Returns**: Validated Config object
**Raises**: FileNotFoundError, JSONDecodeError, ValidationError

**Usage Examples:**

```python
from langgraph_cli.config import validate_config, validate_config_file
import pathlib

# Validate configuration dictionary
config_dict = {
    "dependencies": ["langchain_openai", "."],
    "graphs": {"my_graph": "./src/app.py:graph"},
    "python_version": "3.11"
}
validated_config = validate_config(config_dict)

# Validate configuration file
config_path = pathlib.Path("langgraph.json")
config = validate_config_file(config_path)
```

### Docker Generation

Generate Docker-related files from configuration.

```python { .api }
def config_to_docker(
    config: Config,
    platform: str = "linux/amd64",
    with_apt_package_cache: bool = False,
    tag: str = "latest"
) -> tuple[str, dict[str, str]]
```

**Purpose**: Generate Dockerfile content from configuration
**Parameters**:
- `config` (Config): Validated configuration object
- `platform` (str): Target platform for Docker build
- `with_apt_package_cache` (bool): Include apt package cache optimization
- `tag` (str): Docker image tag
**Returns**: Tuple of (dockerfile_content, build_contexts)

```python { .api }
def config_to_compose(
    config: Config,
    image: str,
    port: int = DEFAULT_PORT,
    docker_compose: Optional[pathlib.Path] = None,
    debugger_port: Optional[int] = None,
    debugger_base_url: Optional[str] = None,
    postgres_uri: Optional[str] = None
) -> str
```

**Purpose**: Generate Docker Compose YAML from configuration
**Parameters**:
- `config` (Config): Validated configuration object
- `image` (str): Docker image name to use
- `port` (int): Port to expose (default: 8123)
- `docker_compose` (Optional[pathlib.Path]): Additional compose file to merge
- `debugger_port` (Optional[int]): Port for debugger UI
- `debugger_base_url` (Optional[str]): Base URL for debugger
- `postgres_uri` (Optional[str]): PostgreSQL connection string
**Returns**: Docker Compose YAML content as string

**Usage Examples:**

```python
from langgraph_cli.config import config_to_docker, config_to_compose

# Generate Dockerfile
dockerfile_content, build_contexts = config_to_docker(
    config,
    platform="linux/amd64,linux/arm64",
    tag="my-app:latest"
)

# Generate Docker Compose
compose_yaml = config_to_compose(
    config,
    image="my-app:latest",
    port=8080,
    debugger_port=8081
)
```

### Image Management

Determine appropriate Docker images and tags from configuration.

```python { .api }
def default_base_image(config: Config) -> str
```

**Purpose**: Determine the appropriate base Docker image for a configuration
**Parameters**:
- `config` (Config): Configuration object
**Returns**: Docker base image name (e.g., "python:3.11-slim")

```python { .api }
def docker_tag(
    config: Config,
    image: Optional[str] = None,
    platform: Optional[str] = None
) -> str
```

**Purpose**: Generate appropriate Docker tag from configuration
**Parameters**:
- `config` (Config): Configuration object
- `image` (Optional[str]): Custom image name override
- `platform` (Optional[str]): Target platform specification
**Returns**: Full Docker image tag

**Usage Examples:**

```python
from langgraph_cli.config import default_base_image, docker_tag

# Get default base image
base_image = default_base_image(config)  # "python:3.11-slim"

# Generate Docker tag
tag = docker_tag(config, image="my-app", platform="linux/amd64")
```

## Configuration Schema

### Core Configuration

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

**Configuration Properties:**

- **python_version**: Python runtime version ("3.11", "3.12", "3.13")
- **node_version**: Node.js runtime version for JavaScript dependencies
- **api_version**: LangGraph API server version to use
- **base_image**: Custom Docker base image override
- **image_distro**: Linux distribution ("debian", "wolfi", "bullseye", "bookworm")
- **dependencies**: List of Python/Node.js packages to install
- **graphs**: Mapping of graph IDs to import paths (e.g., "./src/app.py:graph")
- **env**: Environment variables (file path string or dictionary)
- **dockerfile_lines**: Additional Docker instructions to include
- **pip_config_file**: Path to custom pip configuration file
- **pip_installer**: Package installer ("auto", "pip", "uv")
- **store**: Long-term memory store configuration
- **auth**: Custom authentication configuration
- **http**: HTTP server and routing configuration
- **checkpointer**: State checkpointing configuration
- **ui**: UI component definitions
- **keep_pkg_tools**: Retain packaging tools in final image

### Store Configuration

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

**Store Configuration:**

- **IndexConfig**: Vector search configuration
  - `dims`: Embedding vector dimensions (required)
  - `embed`: Embedding model reference (required, e.g., "openai:text-embedding-3-large")
  - `fields`: JSON fields to extract and embed (optional)
- **TTLConfig**: Time-to-live behavior
  - `refresh_on_read`: Refresh TTL on read operations
  - `default_ttl`: Default TTL in minutes for new items
  - `sweep_interval_minutes`: Cleanup interval for expired items

### Authentication Configuration

```python { .api }
class AuthConfig(TypedDict, total=False):
    path: str  # Required
    disable_studio_auth: bool
    openapi: SecurityConfig

class SecurityConfig(TypedDict, total=False):
    type: str
    scheme: str
    name: str
```

**Authentication Properties:**

- **path**: Path to Auth() class instance (required)
- **disable_studio_auth**: Disable LangSmith authentication for Studio integration
- **openapi**: OpenAPI security configuration for API documentation

### HTTP Configuration

```python { .api }
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

class CorsConfig(TypedDict, total=False):
    allow_origins: list[str]
    allow_methods: list[str]
    allow_headers: list[str]
    allow_credentials: bool
    max_age: int

class ConfigurableHeaderConfig(TypedDict, total=False):
    request: dict[str, str]
    response: dict[str, str]
```

**HTTP Configuration Properties:**

- **app**: Path to custom Starlette/FastAPI application
- **disable_***: Disable specific API route groups
- **cors**: Cross-Origin Resource Sharing configuration
- **configurable_headers**: Custom header handling for requests/responses
- **logging_headers**: Headers to include in access logs

### Checkpointer Configuration

```python { .api }
class CheckpointerConfig(TypedDict, total=False):
    ttl: ThreadTTLConfig

class ThreadTTLConfig(TypedDict, total=False):
    default_ttl: Optional[float]
    sweep_interval_minutes: Optional[int]
```

**Checkpointer Properties:**

- **ttl**: Time-to-live configuration for checkpointed conversation threads

## Configuration Examples

### Minimal Configuration

```json
{
  "dependencies": ["langchain_openai", "."],
  "graphs": {
    "main": "./src/graph.py:compiled_graph"
  }
}
```

### Complete Development Configuration

```json
{
  "python_version": "3.11",
  "dependencies": [
    "langchain_openai",
    "langchain_community",
    "."
  ],
  "graphs": {
    "chat_agent": "./src/agents/chat.py:agent",
    "rag_system": "./src/rag/pipeline.py:rag_graph"
  },
  "env": "./.env.development",
  "store": {
    "index": {
      "dims": 1536,
      "embed": "openai:text-embedding-3-small",
      "fields": ["content", "metadata.title"]
    },
    "ttl": {
      "default_ttl": 1440,
      "sweep_interval_minutes": 60
    }
  },
  "http": {
    "cors": {
      "allow_origins": ["http://localhost:3000"],
      "allow_credentials": true
    }
  }
}
```

### Production Configuration

```json
{
  "python_version": "3.12",
  "image_distro": "wolfi",
  "dependencies": [
    "langchain_openai==0.1.7",
    "langchain_community==0.2.1",
    "."
  ],
  "graphs": {
    "production_agent": "./src/production_graph.py:graph"
  },
  "env": {
    "LOG_LEVEL": "INFO",
    "ENVIRONMENT": "production"
  },
  "auth": {
    "path": "./src/auth.py:custom_auth"
  },
  "http": {
    "disable_meta": true,
    "cors": {
      "allow_origins": ["https://myapp.example.com"]
    }
  },
  "dockerfile_lines": [
    "RUN apt-get update && apt-get install -y curl",
    "COPY config/ /app/config/"
  ]
}
```

## Validation and Error Handling

The configuration system provides comprehensive validation:

- **Type checking**: All fields validated against TypedDict schemas
- **Required field validation**: Missing required fields raise ValidationError
- **Format validation**: Import paths, version strings, and URIs validated
- **Dependency validation**: Package specifications checked for format
- **Graph path validation**: Import paths verified for correct module:variable format

Common validation errors:

- **Invalid Python version**: Must be "3.11", "3.12", or "3.13"
- **Invalid graph path**: Must follow "module.path:variable" format
- **Missing embedding dimensions**: IndexConfig requires both `dims` and `embed`
- **Invalid dependency format**: Package specifications must be valid pip requirements