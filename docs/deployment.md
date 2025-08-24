# Deployment Guide

Turn your local agent into a production API with one command. FlowStack handles all the infrastructure complexity for you.

## Quick Deployment

```python
from flowstack import Agent

# Build your agent
agent = Agent("my-agent", api_key="fs_...")

@agent.tool
def my_function():
    """My custom tool"""
    return {"result": "success"}

# Deploy to production
endpoint = agent.deploy()
print(f"Live at: {endpoint}")
# → https://api.flowstack.fun/agents/my-agent
```

That's it! Your agent is now running in production.

## What Happens During Deployment

When you call `agent.deploy()`, FlowStack automatically:

### 1. **Source Code Extraction** ⚡
- Extracts your tools' source code from .py files
- Validates that tools can be executed securely
- Prepares tools for MCP execution

!!! important "Source Code Requirement"
    Tools must be defined in Python files (.py), not in interactive environments.
    FlowStack extracts the actual source code for secure execution via MCP.

### 2. **MCP Configuration** 🔒
- Configures tools for Model Context Protocol (MCP) execution
- Sets up isolated container environments
- Establishes secure communication channels

### 3. **Infrastructure Provisioning** 🏗️
- Spins up serverless functions with your agent
- Configures API endpoints for HTTP access
- Sets up load balancing and auto-scaling
- Creates monitoring and logging

### 4. **Data Setup** 💾
- Provisions your DataVault namespace
- Sets up database connections and permissions
- Configures data isolation and security

### 5. **Security Configuration** 🔒
- Applies API key authentication
- Sets up rate limiting and abuse protection
- Configures HTTPS and network security
- Implements request isolation
- Enables MCP security boundaries

### 6. **Health Checks** ✅
- Verifies your agent starts correctly
- Tests tool functionality
- Validates API responses
- Confirms monitoring is working
- Checks MCP orchestration

### 7. **Endpoint Creation** 🌐
- Assigns your unique API endpoint
- Configures routing and load balancing
- Sets up global edge caching
- Makes your agent accessible worldwide

## Deployment Environments

### Deployment Infrastructure

Your agent runs on FlowStack's managed infrastructure:

**Features:**
- ✅ Automatic scaling based on traffic
- ✅ Global edge caching for low latency
- ✅ Built-in monitoring and alerting
- ✅ Secure MCP tool execution
- ✅ Isolated namespaces per customer

**Response Details:**
```python
result = agent.deploy()

# Access deployment details
deployment_id = result['deployment_id']
namespace = result['namespace']

# Your agent is now available at:
# POST https://api.flowstack.fun/agents/{namespace}/invoke
```

## What You Get

### Instant API Endpoint

Your agent becomes accessible via HTTPS API:

```bash
# Chat with your agent
curl -X POST https://api.flowstack.fun/agents/my-agent/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fs_your_api_key" \
  -d '{"message": "Hello!"}'
```

### Automatic Scaling

FlowStack handles traffic from 0 to thousands of requests:

- **Cold Start Optimization**: Minimized startup time
- **Auto-Scaling**: Scales up/down based on demand
- **Load Balancing**: Distributes requests efficiently
- **Global Edge**: Served from locations worldwide

### Built-in Monitoring

Track your agent's performance in real-time:

```python
# Get deployment health
health = agent.get_deployment_health()
print(f"Status: {health['status']}")
print(f"Uptime: {health['uptime_percentage']}%")
print(f"Response time: {health['avg_response_time_ms']}ms")
```

### DataVault Integration

Your persistent storage is automatically configured:

```python
# Works immediately after deployment
@agent.tool
def store_user_data(user_id: str, data: dict):
    """Store user data in DataVault"""
    agent.vault.store('users', data, key=user_id)
    return {"stored": True}
```

## Deployment Options

### Basic Deployment

```python
# Simplest deployment
endpoint = agent.deploy()
```

### Advanced Deployment

```python
# Deployment with configuration
endpoint = agent.deploy(
    environment="prod",           # prod or dev
    region="us-east-1",          # AWS region
    timeout=30,                  # Function timeout in seconds
    memory=512,                  # Memory allocation in MB
    description="My production agent",
    tags={"team": "ai", "project": "customer-service"}
)
```

### Invoking Your Deployed Agent

```python
# After deployment, you can invoke your agent
result = agent.deploy()
namespace = result['namespace']

# Use the agent
response = agent.chat("Hello!")
```

## API Endpoints

After deployment, your agent provides several endpoints:

### Invoke Endpoint

**POST** `/agents/{namespace}/invoke`

Send messages to your agent:

```bash
curl -X POST https://api.flowstack.fun/agents/my-agent/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fs_your_api_key" \
  -d '{
    "message": "What can you help me with?",
    "context": {"user_id": "user123"},
    "temperature": 0.7
  }'
```

**Response:**
```json
{
  "message": "I can help you with...",
  "agent": "my-agent",
  "timestamp": "2024-01-15T10:30:00Z",
  "session_id": "sess_abc123"
}
```

### Invoke Endpoint

**POST** `/agents/{agent-name}/invoke`

Advanced interface with full message control:

```bash
curl -X POST https://api.flowstack.fun/agents/my-agent/invoke \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fs_your_api_key" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi! How can I help?"},
      {"role": "user", "content": "What time is it?"}
    ],
    "temperature": 0.8,
    "max_tokens": 150
  }'
```

### Health Endpoint

**GET** `/agents/{agent-name}/health`

Check agent health and status:

```bash
curl https://api.flowstack.fun/agents/my-agent/health \
  -H "X-API-Key: fs_your_api_key"
```

**Response:**
```json
{
  "status": "healthy",
  "uptime": "99.9%",
  "avg_response_time_ms": 245,
  "last_deployed": "2024-01-15T08:00:00Z",
  "version": "1.2.0"
}
```

### Usage Endpoint

**GET** `/agents/{agent-name}/usage`

Get usage statistics:

```bash
curl https://api.flowstack.fun/agents/my-agent/usage \
  -H "X-API-Key: fs_your_api_key"
```

## Managing Deployments

### Update Deployment

Deploy changes to your existing agent:

```python
# Update with new code
agent.deploy()  # Updates existing deployment

# Force new deployment
agent.deploy(force_update=True)
```

### Rollback Deployment

Revert to a previous version:

```python
# Rollback to previous version
agent.rollback()

# Rollback to specific version
agent.rollback(version="1.1.0")
```

### Delete Deployment

Remove your agent from production:

```python
# Delete deployment (keeps data)
agent.undeploy()

# Delete everything including data
agent.undeploy(delete_data=True)
```

## Configuration Best Practices

### Environment Variables

Use environment variables for configuration:

```python
import os

agent = Agent(
    name="my-agent",
    api_key=os.getenv("FLOWSTACK_API_KEY"),
    provider=os.getenv("AI_PROVIDER", "bedrock"),
    model=os.getenv("AI_MODEL", "claude-3-sonnet")
)
```

### Error Handling

Implement robust error handling for production:

```python
@agent.tool
def robust_function(data: str) -> dict:
    """Example of robust error handling"""
    try:
        # Your logic here
        result = process_data(data)
        return {"success": True, "result": result}
    
    except ValueError as e:
        return {"success": False, "error": "Invalid data format", "details": str(e)}
    
    except Exception as e:
        # Log error for debugging
        print(f"Unexpected error: {e}")
        return {"success": False, "error": "Internal error", "retry": True}
```

### Input Validation

Validate inputs in your tools:

```python
@agent.tool
def validate_inputs(email: str, age: int) -> dict:
    """Example of input validation"""
    
    # Validate email format
    if "@" not in email or "." not in email:
        return {"error": "Invalid email format"}
    
    # Validate age range
    if not 0 <= age <= 150:
        return {"error": "Age must be between 0 and 150"}
    
    # Process valid inputs
    return {"email": email, "age": age, "valid": True}
```

### Resource Management

Use DataVault efficiently:

```python
@agent.tool
def efficient_data_handling(user_id: str) -> dict:
    """Example of efficient data handling"""
    
    # Check if data exists before creating
    existing_data = agent.vault.retrieve('users', key=user_id)
    
    if existing_data:
        # Update existing data
        agent.vault.update('users', user_id, {
            'last_seen': datetime.now().isoformat()
        })
        return {"action": "updated", "user_id": user_id}
    else:
        # Create new data
        agent.vault.store('users', {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }, key=user_id)
        return {"action": "created", "user_id": user_id}
```

## Performance Optimization

### Response Time

Optimize for faster responses:

```python
# Use faster models for simple tasks
if task_complexity == "simple":
    agent.set_model("claude-3-haiku")  # Faster model
else:
    agent.set_model("claude-3-sonnet")  # More capable model
```

### Memory Usage

Efficient memory management:

```python
@agent.tool
def memory_efficient_processing(large_data: list) -> dict:
    """Process large data efficiently"""
    
    # Process in chunks instead of all at once
    chunk_size = 100
    results = []
    
    for i in range(0, len(large_data), chunk_size):
        chunk = large_data[i:i + chunk_size]
        chunk_result = process_chunk(chunk)
        results.append(chunk_result)
    
    return {"processed_chunks": len(results), "total_items": len(large_data)}
```

### Caching

Use DataVault for caching:

```python
@agent.tool
def cached_expensive_operation(query: str) -> dict:
    """Cache expensive operations"""
    
    # Check cache first
    cache_key = f"cache_{hash(query)}"
    cached_result = agent.vault.retrieve('cache', key=cache_key)
    
    if cached_result:
        return {"result": cached_result, "from_cache": True}
    
    # Perform expensive operation
    result = expensive_operation(query)
    
    # Cache result with expiration
    agent.vault.store('cache', {
        'result': result,
        'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
    }, key=cache_key)
    
    return {"result": result, "from_cache": False}
```

## Troubleshooting

### Common Deployment Issues

#### 1. Source Extraction Errors

**Problem:** "Cannot extract source code" or "Tool must be in .py file"

**Solution:** Ensure tools are defined in Python files, not REPL/Jupyter

```python
# BAD: Defining in REPL or Jupyter
>>> @agent.tool
>>> def my_tool():
>>>     return "Won't work"

# GOOD: In a file my_agent.py
@agent.tool
def my_tool():
    return "Works!"
```

#### 2. Import Errors

**Problem:** Module not found errors after deployment

**Solution:** Ensure all dependencies are importable

```python
# Test imports before deployment
try:
    import requests
    import pandas as pd
    from my_custom_module import my_function
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
```

#### 3. Tool Function Errors

**Problem:** Tools fail during deployment

**Solution:** Test tools locally first

```python
# Test your tools before deployment
@agent.tool
def test_tool() -> dict:
    """Test tool functionality"""
    return {"status": "working"}

# Test locally
result = test_tool()
print(f"Tool test result: {result}")
```

#### 4. Timeout Issues

**Problem:** Deployment times out

**Solution:** Optimize code and increase timeout

```python
# Deploy with longer timeout
endpoint = agent.deploy(timeout=60)  # 60 seconds
```

#### 5. Memory Issues

**Problem:** Out of memory errors

**Solution:** Increase memory allocation

```python
# Deploy with more memory
endpoint = agent.deploy(memory=1024)  # 1GB memory
```

### Debugging Production Issues

#### 1. Check Logs

```python
# Get deployment logs
logs = agent.get_logs(lines=100)
for log in logs:
    print(f"{log['timestamp']}: {log['message']}")
```

#### 2. Monitor Health

```python
# Check agent health
health = agent.get_deployment_health()
if health['status'] != 'healthy':
    print(f"⚠️ Agent unhealthy: {health}")
```

#### 3. Test Endpoint

```python
# Test your deployed agent
try:
    response = agent.chat("Health check")
    print(f"✅ Agent responding: {response}")
except Exception as e:
    print(f"❌ Agent not responding: {e}")
```

---

Ready to deploy your agent? Start with the [quickstart guide](quickstart.md) or check out our [recipes](recipes/chatbot.md) for complete examples!