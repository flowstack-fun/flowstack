# Migration Guide

## Migrating from CloudPickle to MCP

FlowStack has transitioned from CloudPickle serialization to MCP (Model Context Protocol) for improved security and multi-language support. This guide helps you migrate existing agents.

## What Changed?

### Before: CloudPickle Serialization
- Tools were serialized as Python objects
- Security risks from arbitrary code execution
- Python-only support
- Could work in REPL/Jupyter

### After: MCP Source Code
- Tools execute from source code
- Secure container isolation
- Multi-language support (Python + JavaScript)
- Must be in .py files

## Migration Steps

### Step 1: Move Tools to Files

#### Before (REPL/Jupyter)
```python
# In Jupyter or Python REPL
>>> from flowstack import Agent
>>> agent = Agent("my-agent", api_key="fs_...")
>>> 
>>> @agent.tool
>>> def process_data(data):
...     return {"processed": data}
>>> 
>>> agent.deploy()  # This no longer works!
```

#### After (File-based)
```python
# In a file: my_agent.py
from flowstack import Agent

agent = Agent("my-agent", api_key="fs_...")

@agent.tool
def process_data(data: dict) -> dict:
    """Process input data"""
    return {"processed": data}

if __name__ == "__main__":
    agent.deploy()  # This works!
```

### Step 2: Add Type Hints and Docstrings

#### Before
```python
@agent.tool
def calculate(x, y):
    return x + y
```

#### After
```python
@agent.tool
def calculate(x: float, y: float) -> float:
    """Add two numbers together"""
    return x + y
```

### Step 3: Make Tools Self-Contained

#### Before (Global Dependencies)
```python
import requests

API_KEY = "secret_key"
BASE_URL = "https://api.example.com"

@agent.tool
def fetch_data(endpoint):
    # Uses global variables
    response = requests.get(f"{BASE_URL}/{endpoint}", 
                           headers={"X-API-Key": API_KEY})
    return response.json()
```

#### After (Self-Contained)
```python
@agent.tool
def fetch_data(endpoint: str) -> dict:
    """Fetch data from API endpoint"""
    import requests
    
    # Use DataVault for config
    config = agent.vault.retrieve('config', key='api_settings') or {
        'base_url': 'https://api.example.com',
        'api_key': 'secret_key'
    }
    
    response = requests.get(
        f"{config['base_url']}/{endpoint}",
        headers={"X-API-Key": config['api_key']}
    )
    return response.json()
```

### Step 4: Handle Imports Inside Tools

#### Before
```python
import pandas as pd
import numpy as np

@agent.tool
def analyze_csv(file_path):
    df = pd.read_csv(file_path)
    return {"mean": np.mean(df.values)}
```

#### After
```python
@agent.tool
def analyze_csv(file_path: str) -> dict:
    """Analyze CSV file and return statistics"""
    import pandas as pd
    import numpy as np
    
    df = pd.read_csv(file_path)
    return {
        "mean": float(np.mean(df.values)),
        "rows": len(df),
        "columns": len(df.columns)
    }
```

### Step 5: Update Error Handling

#### Before (Exceptions)
```python
@agent.tool
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

#### After (Return Errors)
```python
@agent.tool
def divide(a: float, b: float) -> dict:
    """Divide two numbers safely"""
    if b == 0:
        return {
            "success": False,
            "error": "Cannot divide by zero"
        }
    return {
        "success": True,
        "result": a / b
    }
```

## Common Migration Issues

### Issue 1: "Cannot extract source code"

**Symptom:**
```
FlowStackError: Tool 'my_tool' cannot be used with MCP execution.
Reason: could not get source code
```

**Solution:**
Move your tool definitions to a .py file:

```bash
# Create a proper Python file
cat > agent.py << 'EOF'
from flowstack import Agent

agent = Agent("my-agent", api_key="fs_...")

@agent.tool
def my_tool(input: str) -> dict:
    """Tool description"""
    return {"result": input}

if __name__ == "__main__":
    endpoint = agent.deploy()
    print(f"Deployed to: {endpoint}")
EOF

# Run the file
python agent.py
```

### Issue 2: Missing Dependencies in MCP

**Symptom:**
```
ImportError: No module named 'custom_module'
```

**Solution:**
Use standard libraries or common packages:

```python
# ✅ These work in MCP
import json
import datetime
import requests
import numpy
import pandas

# ❌ Custom modules won't work
import my_custom_module  # Not available in MCP
```

### Issue 3: Global State Access

**Symptom:**
```
NameError: name 'global_var' is not defined
```

**Solution:**
Use DataVault for persistent state:

```python
# Instead of global variables
@agent.tool
def set_setting(key: str, value: str) -> dict:
    """Store a setting"""
    agent.vault.store('settings', {key: value}, key=key)
    return {"stored": True}

@agent.tool
def get_setting(key: str) -> dict:
    """Retrieve a setting"""
    value = agent.vault.retrieve('settings', key=key)
    return {"key": key, "value": value}
```

## Testing Your Migration

### 1. Test Locally First

```python
# my_agent.py
from flowstack import Agent

agent = Agent("test-agent", api_key="fs_...")

@agent.tool
def test_tool(input: str) -> dict:
    """Test tool for migration"""
    return {"echo": input, "status": "working"}

# Test before deploying
if __name__ == "__main__":
    # Local test
    result = test_tool("hello")
    print(f"Local test: {result}")
    
    # Chat test
    response = agent.chat("Use the test tool with input 'world'")
    print(f"Chat test: {response}")
    
    # Deploy if tests pass
    endpoint = agent.deploy()
    print(f"Deployed: {endpoint}")
```

### 2. Validate Tool Loading

```python
# Check that tools are properly registered
print(f"Registered tools: {list(agent.tools.keys())}")

# Verify tool metadata
for name, tool in agent.tools.items():
    print(f"Tool: {name}")
    print(f"  Language: {tool.get('language', 'python')}")
    print(f"  Serialization: {tool.get('serialization_method')}")
    print(f"  Has source: {'source_code' in tool or 'serialized_function' in tool}")
```

### 3. Test Deployment

```python
import requests

# After deployment, test the endpoint
endpoint = "https://api.flowstack.fun/agents/test-agent"

response = requests.post(
    f"{endpoint}/chat",
    headers={"X-API-Key": "fs_your_key"},
    json={"message": "Test the test_tool with input 'deployed'"}
)

print(response.json())
```

## Migration Checklist

- [ ] Move all tool definitions to .py files
- [ ] Add type hints to all parameters
- [ ] Add docstrings to all tools
- [ ] Make tools self-contained (no global state)
- [ ] Move imports inside tool functions
- [ ] Replace exceptions with error returns
- [ ] Test tools locally before deployment
- [ ] Verify tool registration
- [ ] Test deployed endpoint

## Benefits After Migration

### Security
- No arbitrary code execution
- Isolated container execution
- Source code auditing

### Reliability
- Consistent execution environment
- Better error handling
- Easier debugging

### Features
- Multi-language support (Python + JavaScript)
- Better performance
- Future-proof architecture

## Getting Help

If you encounter issues during migration:

1. Check error messages for specific problems
2. Review the [MCP Guide](mcp-guide.md) for details
3. See [Troubleshooting](deployment.md#troubleshooting)
4. Contact support at [flowstack.fun/support](https://flowstack.fun/support)

## Example: Complete Migration

### Original Agent (CloudPickle)
```python
# old_agent.py (or in Jupyter)
import requests
from flowstack import Agent

API_KEY = "my_api_key"
agent = Agent("weather-bot", api_key="fs_...")

@agent.tool
def get_weather(city):
    response = requests.get(f"https://api.weather.com/{city}",
                           headers={"X-API-Key": API_KEY})
    return response.json()

agent.deploy()  # Would fail now
```

### Migrated Agent (MCP)
```python
# new_agent.py
from flowstack import Agent

agent = Agent("weather-bot", api_key="fs_...")

@agent.tool
def get_weather(city: str) -> dict:
    """Get current weather for a city
    
    Args:
        city: City name (e.g., 'San Francisco')
    
    Returns:
        Weather data including temperature and conditions
    """
    import requests
    
    # Get API key from DataVault
    config = agent.vault.retrieve('config', key='weather_api') or {}
    api_key = config.get('api_key', 'default_key')
    
    try:
        response = requests.get(
            f"https://api.weather.com/{city}",
            headers={"X-API-Key": api_key},
            timeout=10
        )
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Failed to get weather: {str(e)}",
            "city": city
        }

if __name__ == "__main__":
    # Store API configuration
    agent.vault.store('config', {
        'api_key': 'your_weather_api_key'
    }, key='weather_api')
    
    # Test locally
    print("Testing locally...")
    result = get_weather("San Francisco")
    print(f"Local test: {result}")
    
    # Deploy
    print("Deploying...")
    endpoint = agent.deploy()
    print(f"Success! Deployed to: {endpoint}")
```

This migrated version:
- ✅ In a .py file
- ✅ Has type hints
- ✅ Has docstring
- ✅ Self-contained
- ✅ Handles errors gracefully
- ✅ Uses DataVault for config
- ✅ Ready for MCP execution

---

Migration complete! Your agents are now more secure, reliable, and ready for the future of FlowStack.