# Templates

Project scaffolding system for LangGraph applications. Provides multiple pre-built templates covering common LangGraph patterns and use cases, enabling rapid project initialization with best practices.

## Capabilities

### Project Creation

Create new LangGraph projects from predefined templates with proper structure and configuration.

```python { .api }
def create_new(path: Optional[str], template: Optional[str]) -> None
```

**Purpose**: Create a new LangGraph project from a template
**Parameters**:
- `path` (Optional[str]): Directory path for the new project (current directory if None)
- `template` (Optional[str]): Template identifier (interactive selection if None)
**Returns**: None (creates files and directories)
**Raises**: TemplateError for invalid templates, FileExistsError for existing directories

**Usage Examples:**

```python
from langgraph_cli.templates import create_new

# Interactive template selection in current directory
create_new(None, None)

# Create project with specific template
create_new("my-agent-app", "react-agent-python")

# Create in custom directory with interactive selection
create_new("./projects/new-bot", None)
```

## Available Templates

### New LangGraph Project

**Template ID**: `new-langgraph-project`
**Description**: Minimal chatbot with memory
**Use Case**: Basic conversational AI applications with persistent memory

**Features**:
- Simple chat interface with conversation memory
- Basic message handling and response generation
- Configuration for common LLM providers
- Development server setup
- Basic testing structure

**Generated Structure**:
```
my-project/
├── langgraph.json          # LangGraph configuration
├── pyproject.toml          # Python project configuration
├── .env.example           # Environment variables template
├── src/
│   ├── __init__.py
│   ├── graph.py           # Main conversation graph
│   └── nodes/             # Graph node implementations
│       ├── __init__.py
│       └── chat.py
├── tests/
│   ├── __init__.py
│   └── test_graph.py
└── README.md
```

### ReAct Agent

**Template ID**: `react-agent-python`
**Description**: Extensible agent with tools
**Use Case**: Reasoning and acting agents that can use external tools

**Features**:
- ReAct (Reasoning + Acting) pattern implementation
- Tool integration framework
- Extensible tool registry
- Error handling and retry logic
- Comprehensive logging and observability

**Generated Structure**:
```
react-agent/
├── langgraph.json
├── pyproject.toml
├── .env.example
├── src/
│   ├── __init__.py
│   ├── agent.py           # Main ReAct agent
│   ├── tools/             # Tool implementations
│   │   ├── __init__.py
│   │   ├── base.py        # Base tool interface
│   │   ├── web_search.py  # Web search tool
│   │   └── calculator.py  # Math operations
│   └── prompts/
│       ├── __init__.py
│       └── react.py       # ReAct prompting logic
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   └── test_tools.py
└── README.md
```

### Memory Agent

**Template ID**: `memory-agent-python`
**Description**: ReAct agent with cross-conversation memory
**Use Case**: Agents that remember information across multiple conversations

**Features**:
- ReAct pattern with persistent memory
- Long-term memory storage and retrieval
- Context management across sessions
- Memory indexing and search
- Conversation history management

**Generated Structure**:
```
memory-agent/
├── langgraph.json
├── pyproject.toml
├── .env.example
├── src/
│   ├── __init__.py
│   ├── agent.py           # Memory-enabled ReAct agent
│   ├── memory/            # Memory management
│   │   ├── __init__.py
│   │   ├── store.py       # Memory storage interface
│   │   └── retrieval.py   # Memory retrieval logic
│   ├── tools/             # Agent tools
│   │   ├── __init__.py
│   │   └── base.py
│   └── prompts/
│       ├── __init__.py
│       └── memory.py      # Memory-aware prompts
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   └── test_memory.py
└── README.md
```

### Retrieval Agent

**Template ID**: `retrieval-agent-python`
**Description**: Agent with RAG (Retrieval-Augmented Generation) capabilities
**Use Case**: Agents that can search and reference external knowledge bases

**Features**:
- RAG implementation with vector search
- Document ingestion and indexing
- Semantic search and retrieval
- Context-aware response generation
- Support for multiple document formats

**Generated Structure**:
```
retrieval-agent/
├── langgraph.json
├── pyproject.toml
├── .env.example
├── src/
│   ├── __init__.py
│   ├── agent.py           # RAG-enabled agent
│   ├── retrieval/         # RAG implementation
│   │   ├── __init__.py
│   │   ├── embeddings.py  # Embedding generation
│   │   ├── vectorstore.py # Vector storage
│   │   └── retriever.py   # Search and retrieval
│   ├── ingestion/         # Document processing
│   │   ├── __init__.py
│   │   ├── loader.py      # Document loaders
│   │   └── processor.py   # Text processing
│   └── prompts/
│       ├── __init__.py
│       └── rag.py         # RAG-specific prompts
├── data/                  # Sample documents
│   └── sample.txt
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_retrieval.py
│   └── test_ingestion.py
└── README.md
```

### Data-Enrichment Agent

**Template ID**: `data-enrichment-python`
**Description**: Web search and data organization agent
**Use Case**: Agents that gather, process, and organize information from web sources

**Features**:
- Web search integration
- Data extraction and cleaning
- Information organization and categorization
- Multi-source data aggregation
- Structured output generation

**Generated Structure**:
```
data-enrichment/
├── langgraph.json
├── pyproject.toml
├── .env.example
├── src/
│   ├── __init__.py
│   ├── agent.py           # Data enrichment agent
│   ├── search/            # Web search capabilities
│   │   ├── __init__.py
│   │   ├── web_search.py  # Search implementation
│   │   └── extractors.py  # Data extraction
│   ├── processing/        # Data processing
│   │   ├── __init__.py
│   │   ├── cleaner.py     # Data cleaning
│   │   └── organizer.py   # Information organization
│   ├── output/            # Output formatting
│   │   ├── __init__.py
│   │   └── formatters.py  # Structured output
│   └── prompts/
│       ├── __init__.py
│       └── enrichment.py  # Data enrichment prompts
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_search.py
│   └── test_processing.py
└── README.md
```

## Template Selection

### Interactive Selection

When no template is specified, the CLI provides an interactive selection interface:

```bash
$ langgraph new my-project

? Select a template:
❯ New LangGraph Project - Minimal chatbot with memory
  ReAct Agent - Extensible agent with tools
  Memory Agent - ReAct agent with cross-conversation memory
  Retrieval Agent - Agent with RAG capabilities
  Data-enrichment Agent - Web search and data organization
```

### Direct Template Usage

Templates can be specified directly:

```bash
# Create ReAct agent
langgraph new react-bot --template react-agent-python

# Create retrieval agent in specific directory
langgraph new ./agents/rag-bot --template retrieval-agent-python
```

## Template Configuration

The template system uses several constants for management:

```python { .api }
# Template definitions with URLs for Python and JavaScript versions
TEMPLATES: dict[str, dict[str, str]] = {
    "New LangGraph Project": {
        "description": "A simple, minimal chatbot with memory.",
        "python": "https://github.com/langchain-ai/new-langgraph-project/archive/refs/heads/main.zip",
        "js": "https://github.com/langchain-ai/new-langgraphjs-project/archive/refs/heads/main.zip",
    },
    "ReAct Agent": {
        "description": "A simple agent that can be flexibly extended to many tools.",
        "python": "https://github.com/langchain-ai/react-agent/archive/refs/heads/main.zip",
        "js": "https://github.com/langchain-ai/react-agent-js/archive/refs/heads/main.zip",
    },
    # Additional templates...
}

# Template identifier mapping for CLI usage
TEMPLATE_ID_TO_CONFIG: dict[str, tuple[str, str, str]]
TEMPLATE_IDS: list[str]

# Help string for CLI template selection
TEMPLATE_HELP_STRING: str
```

## Template Help

The CLI provides detailed template information:

```python
# Template help string with descriptions
TEMPLATE_HELP_STRING = """
Available templates:

  new-langgraph-project     Minimal chatbot with memory
  react-agent-python        Extensible agent with tools
  memory-agent-python       ReAct agent with cross-conversation memory
  retrieval-agent-python    Agent with RAG capabilities
  data-enrichment-python    Web search and data organization

Use 'langgraph new --template TEMPLATE_NAME' to create a project.
"""
```

## Template Components

Each template includes:

### Core Files

- **langgraph.json**: LangGraph configuration with appropriate dependencies
- **pyproject.toml**: Python project configuration with required packages
- **.env.example**: Environment variables template with provider APIs
- **README.md**: Template-specific setup and usage instructions

### Source Code Structure

- **Main agent/graph file**: Core application logic
- **Node implementations**: Modular graph node functions
- **Tool implementations**: External tool integrations
- **Prompt templates**: LLM prompt engineering
- **Configuration modules**: Settings and configuration management

### Testing Framework

- **Unit tests**: Component-level testing
- **Integration tests**: End-to-end workflow testing
- **Test fixtures**: Sample data and mock objects
- **Test configuration**: Testing-specific settings

### Documentation

- **README**: Quick start and overview
- **Code comments**: Inline documentation
- **Configuration examples**: Sample configurations
- **Deployment guides**: Production deployment instructions

## Customization

Templates serve as starting points and can be customized:

### Configuration Customization

Modify `langgraph.json` for:
- Different Python versions
- Additional dependencies
- Custom environment variables
- Production deployment settings

### Code Customization

Templates provide extensible architectures:
- Add new tools to ReAct agents
- Implement custom memory backends
- Add document loaders to retrieval agents
- Extend data processing pipelines

### Deployment Customization

Each template includes deployment options:
- Docker configuration
- Environment-specific settings
- CI/CD pipeline examples
- Monitoring and logging setup

## Best Practices

Templates follow LangGraph best practices:

### Code Organization

- Clear separation of concerns
- Modular node implementations
- Reusable components
- Consistent naming conventions

### Configuration Management

- Environment-based configuration
- Secure secret handling
- Flexible deployment options
- Development/production separation

### Testing Strategy

- Comprehensive test coverage
- Mock external dependencies
- Integration test patterns
- Performance testing examples

### Error Handling

- Graceful failure handling
- Informative error messages
- Recovery mechanisms
- Logging and observability