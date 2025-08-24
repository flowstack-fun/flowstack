# FlowStack MCP Implementation Guide

## Overview

FlowStack uses **MCP (Model Context Protocol)** for secure, isolated tool execution. Tools are extracted as source code and executed in containerized environments.

## Key Features

### 🚀 Source Code Extraction
- **Python tools**: Define tools as functions in .py files
- **Source extraction**: Uses `inspect.getsource()` instead of serialization
- **YAML configuration**: Define agents and tools declaratively

### ⚡ MCP Architecture
- **Container-based execution**: Reliable, scalable tool execution in ECS Fargate
- **Isolated execution**: Each tool runs in a secure container
- **Automatic routing**: Tools are automatically routed to MCP runtime

### 🔄 Development Workflow
- **Local development**: Write and test tools as normal Python functions
- **Deployment**: FlowStack extracts source and deploys to infrastructure
- **No serialization**: Tools are stored as source code, not pickled objects

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FlowStack Agent                       │
├─────────────────────────────────────────────────────────────┤
│                         Python SDK                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ from flowstack import tool                          │   │
│  │                                                     │   │
│  │ @tool                                               │   │
│  │ def my_function():                                  │   │
│  │     return "result"                                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   Deployment Manager                         │
│              (extracts source, stores in DynamoDB)          │
└─────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Executor Lambda                      │
│          (creates MCP proxy functions for tools)            │
└─────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  MCP Orchestrator Function                   │
│         (manages container tasks and routes execution)       │
└─────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     ECS Fargate Tasks                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Python MCP Server Container              │   │
│  │         (executes Python tools in isolation)        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Tool Implementation Examples

### Python Tools with @tool Decorator

```python
from flowstack import Agent, tool

agent = Agent(
    name="data-processor",
    api_key="your-api-key",
    instructions="You are a data analysis assistant"
)

# Define tool with decorator
@tool
def analyze_data(data: list) -> dict:
    """Analyze numerical data"""
    return {
        'count': len(data),
        'average': sum(data) / len(data) if data else 0,
        'max': max(data) if data else None,
        'min': min(data) if data else None
    }

# Add tool to agent
agent.add_tool(analyze_data)

# Deploy agent
result = agent.deploy()
print(f"Deployed: {result['namespace']}")
```

### Tools in Separate Files (Recommended)

Project structure:
```
my-agent/
├── agent.yaml
└── tools/
    ├── math_tools.py
    └── data_tools.py
```

`agent.yaml`:
```yaml
name: data-processor
instructions: |
  You are a data analysis assistant.
  Help users analyze and process data.
model: claude-3-sonnet
temperature: 0.7
tools:
  analyze_data:
    description: Analyze numerical data
  calculate_statistics:
    description: Calculate advanced statistics
```

`tools/data_tools.py`:
```python
def analyze_data(data: list) -> dict:
    """Analyze numerical data"""
    return {
        'count': len(data),
        'average': sum(data) / len(data) if data else 0,
        'max': max(data) if data else None,
        'min': min(data) if data else None
    }

def calculate_statistics(data: list) -> dict:
    """Calculate advanced statistics"""
    import statistics
    return {
        'mean': statistics.mean(data),
        'median': statistics.median(data),
        'stdev': statistics.stdev(data) if len(data) > 1 else 0
    }
```

Deploy:
```python
from flowstack import Agent

agent = Agent.from_yaml("agent.yaml", api_key="your-api-key")
result = agent.deploy()
```

## MCP Execution Flow

1. **Tool Definition**: Developer defines tools as Python functions
2. **Source Extraction**: SDK extracts source using `inspect.getsource()`
3. **Deployment**: Source code stored in DynamoDB with agent config
4. **Agent Invocation**: When agent needs a tool, creates MCP proxy
5. **MCP Orchestration**: Proxy calls MCP orchestrator Lambda
6. **Container Execution**: Tool executes in isolated ECS container
7. **Result Return**: Result passed back through chain to agent

## DataVault Integration

Tools can access DataVault for persistent storage:

```python
from flowstack import tool, DataVault

# Initialize DataVault
vault = DataVault(api_key="your-api-key")

@tool
def save_user_preference(key: str, value: str) -> dict:
    """Save user preference to DataVault"""
    success = vault.store('preferences', {
        'key': key,
        'value': value,
        'timestamp': '2024-01-01T00:00:00Z'
    })
    
    return {
        'saved': success,
        'message': f"Preference {key} saved"
    }

@tool
def get_user_preference(key: str) -> dict:
    """Retrieve user preference from DataVault"""
    prefs = vault.retrieve('preferences', filter={'key': key})
    
    if prefs:
        return prefs[0]
    else:
        return {'error': 'Preference not found'}
```

## Best Practices

### Tool Design
- **Single Responsibility**: Each tool should do one thing well
- **Clear Documentation**: Use descriptive docstrings
- **Type Hints**: Always include type hints for parameters
- **Error Handling**: Handle errors gracefully within tools
- **Stateless**: Tools should be stateless (use DataVault for state)

### Security Considerations
- **No Secrets in Code**: Never hardcode API keys or secrets
- **Input Validation**: Validate all tool inputs
- **Safe Operations**: Avoid operations that could harm the system
- **Isolated Execution**: Tools run in isolated containers

### Performance Optimization
- **Lightweight Tools**: Keep tools focused and fast
- **Batch Operations**: Design tools to handle batch operations
- **Caching**: Use DataVault for caching expensive operations
- **Async Support**: Long-running operations should be async

## Migration from CloudPickle

If you have existing agents using CloudPickle serialization:

1. **Extract tool code** into separate functions
2. **Add @tool decorator** or place in tools/ directory
3. **Update agent configuration** to use new tools
4. **Test locally** before deployment
5. **Deploy** using new MCP system

Old (CloudPickle):
```python
# This approach is deprecated
agent.add_tool(my_function)  # Function was pickled
```

New (MCP):
```python
# Tools are extracted as source code
@tool
def my_function():
    return "result"

agent.add_tool(my_function)  # Source extracted
```

## Troubleshooting

### Common Issues

**"Cannot extract source code"**
- Ensure tools are defined in .py files, not REPL/Jupyter
- Check that functions are not lambdas or nested functions

**"Tool validation failed"**
- Add proper docstrings to your tools
- Include type hints for all parameters
- Ensure function has a return statement

**"MCP execution timeout"**
- Tools have a 30-second timeout
- Break long operations into smaller tools
- Use async patterns for long-running operations

## Summary

FlowStack's MCP implementation provides:
- **Secure execution** in isolated containers
- **Source-based deployment** (no serialization)
- **Simple development** with Python functions
- **Scalable infrastructure** with auto-scaling
- **Built-in persistence** with DataVault integration

Tools are just Python functions that get deployed to a robust, managed infrastructure.