# MCP (Model Context Protocol) Guide

## Overview

FlowStack uses MCP (Model Context Protocol) for secure, isolated tool execution. This guide explains how MCP works and how to optimize your agents for it.

## What is MCP?

MCP is FlowStack's security and execution protocol that:

- **Isolates tool execution** in secure containers
- **Prevents cross-contamination** between tools and agents
- **Enables multi-language support** (Python and JavaScript)
- **Executes from source code**, not serialized objects

## Why MCP?

### Security First

Traditional approaches using serialized code (pickle, CloudPickle) pose security risks:
- Code injection vulnerabilities
- Arbitrary code execution
- Difficult to audit

MCP solves these by:
- Executing only verified source code
- Running tools in isolated containers
- Preventing access to other tools' environments

### Multi-Language Support

MCP enables tools in multiple languages within the same agent:

```python
# Python tool
@agent.tool
def analyze_data(data: list) -> dict:
    """Analyze data using Python libraries"""
    import numpy as np
    return {"mean": np.mean(data), "std": np.std(data)}

# JavaScript tool (coming soon)
@agent.tool(language='javascript', source_code='''
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}
''')
def validate_email_js():
    pass  # Placeholder
```

## MCP Requirements

### 1. File-Based Tools

!!! important "Critical Requirement"
    Tools MUST be defined in `.py` files, not in interactive environments.

**Why?** FlowStack needs to extract the actual source code of your functions.

```python
# ✅ GOOD: In a file my_agent.py
@agent.tool
def my_tool():
    return "This works!"

# ❌ BAD: In Python REPL or Jupyter
>>> @agent.tool
>>> def my_tool():
>>>     return "This won't work!"
```

### 2. Clean Dependencies

Tools should have clear, importable dependencies:

```python
# ✅ GOOD: Clear imports
@agent.tool
def fetch_data(url: str) -> dict:
    """Fetch data from URL"""
    import requests
    response = requests.get(url)
    return response.json()

# ❌ BAD: Hidden dependencies
@agent.tool
def process_data(data):
    """Process data"""
    # Assumes 'helper' is available somehow
    return helper.process(data)  # Will fail in MCP
```

### 3. Self-Contained Functions

Tools should be self-contained and not rely on global state:

```python
# ✅ GOOD: Self-contained
@agent.tool
def calculate_tax(amount: float, rate: float = 0.1) -> float:
    """Calculate tax on amount"""
    return amount * rate

# ❌ BAD: Relies on global state
TAX_RATE = 0.1  # Global variable

@agent.tool
def calculate_tax_bad(amount: float) -> float:
    """Calculate tax on amount"""
    return amount * TAX_RATE  # Won't have access to TAX_RATE
```

## MCP Execution Flow

### 1. Development Phase

```python
# You write tools in your .py file
@agent.tool
def get_user(user_id: str) -> dict:
    """Get user by ID"""
    # Your implementation
    return {"id": user_id, "name": "Alice"}
```

### 2. Deployment Phase

```python
# FlowStack extracts source code
agent.deploy()
# → Extracts: "def get_user(user_id: str) -> dict:..."
# → Validates function structure
# → Prepares for MCP execution
```

### 3. Runtime Phase

```
User Message → Agent → MCP Orchestrator → Container → Tool Execution
                            ↓
                    Isolated Environment
                    Security Boundaries
                    Resource Limits
```

### 4. Result Return

```
Tool Result → MCP Orchestrator → Agent → User Response
```

## Best Practices

### 1. Use Type Hints

Type hints help MCP understand your tools better:

```python
@agent.tool
def search_products(
    query: str,
    max_results: int = 10,
    category: str = None
) -> list[dict]:
    """Search for products"""
    # Implementation
    return results
```

### 2. Handle Errors Gracefully

Return error information instead of raising exceptions:

```python
@agent.tool
def divide_numbers(a: float, b: float) -> dict:
    """Divide two numbers"""
    if b == 0:
        return {"error": "Division by zero", "success": False}
    return {"result": a / b, "success": True}
```

### 3. Use DataVault for State

Instead of global variables, use DataVault:

```python
@agent.tool
def set_config(key: str, value: str) -> dict:
    """Store configuration"""
    agent.vault.store('config', {key: value}, key=key)
    return {"stored": True, "key": key}

@agent.tool
def get_config(key: str) -> dict:
    """Retrieve configuration"""
    value = agent.vault.retrieve('config', key=key)
    return {"key": key, "value": value}
```

### 4. Document Your Tools

Clear docstrings help the agent understand when to use each tool:

```python
@agent.tool
def weather_forecast(city: str, days: int = 7) -> dict:
    """
    Get weather forecast for a city.
    
    Args:
        city: City name (e.g., "San Francisco")
        days: Number of days to forecast (1-14)
    
    Returns:
        Dictionary with forecast data including temperature,
        conditions, and precipitation probability.
    """
    # Implementation
    return forecast_data
```

## Troubleshooting

### Error: "Cannot extract source code"

**Cause:** Tool defined in REPL/Jupyter/interactive mode

**Solution:** Move tools to a .py file:

```bash
# Create a file
cat > my_agent.py << 'EOF'
from flowstack import Agent

agent = Agent("my-agent", api_key="fs_...")

@agent.tool
def my_tool():
    return "Works!"

if __name__ == "__main__":
    agent.deploy()
EOF

# Run the file
python my_agent.py
```

### Error: "Tool validation failed"

**Cause:** Missing docstring or invalid function structure

**Solution:** Ensure proper function definition:

```python
# ✅ GOOD
@agent.tool
def my_tool(param: str) -> dict:
    """Clear description of what this tool does"""
    return {"result": param}

# ❌ BAD
@agent.tool
def my_tool(param):  # Missing type hints and docstring
    return param
```

### Error: "Import not found in MCP environment"

**Cause:** Using a module not available in MCP containers

**Solution:** Use standard library or common packages:

```python
# ✅ Standard libraries always available
import json, datetime, re, math, random

# ✅ Common packages usually available
import requests, numpy, pandas

# ❌ Custom or uncommon packages may not be available
import my_custom_module  # Won't work unless pre-installed
```

## Advanced MCP Features

### Container Resource Limits

Each tool execution has resource limits:
- **Memory**: 512MB default
- **CPU**: 1 vCPU
- **Timeout**: 30 seconds
- **Network**: Outbound only

### Security Boundaries

Tools cannot:
- Access other tools' data
- Modify system files
- Access environment variables (except approved ones)
- Make inbound network connections

### Performance Optimization

MCP uses several optimizations:
- **Container pooling**: Reuses containers for faster execution
- **Code caching**: Caches validated source code
- **Parallel execution**: Can run multiple tools simultaneously

## Migration from CloudPickle

If you have existing agents using CloudPickle:

### Before (CloudPickle)
```python
# Old approach - no longer supported
import cloudpickle

@agent.tool
def my_tool():
    return "data"

# This would serialize the function object
serialized = cloudpickle.dumps(my_tool)
```

### After (MCP Source Code)
```python
# New approach - required for MCP
# In a .py file
@agent.tool
def my_tool():
    """Tool description"""
    return {"data": "result"}

# FlowStack extracts source code automatically
agent.deploy()  # Handles everything
```

## Future Enhancements

### Coming Soon

1. **JavaScript/TypeScript tools**: Full support for JS/TS tools
2. **Custom containers**: Bring your own Docker containers
3. **Tool composition**: Tools calling other tools
4. **Streaming responses**: Real-time tool output
5. **File handling**: Direct file upload/download support

### In Development

- WebAssembly tool support
- GPU-accelerated tools
- Long-running background tools
- Tool versioning and rollback

## Summary

MCP makes FlowStack agents:
- **More secure**: Isolated execution, no code serialization
- **More reliable**: Consistent environment, clear boundaries
- **More capable**: Multi-language support, better debugging
- **More scalable**: Container pooling, parallel execution

Remember the key requirement: **Always define tools in .py files**, not in interactive environments!

---

Need help? Check our [troubleshooting guide](deployment.md#troubleshooting) or [contact support](https://flowstack.fun/support).