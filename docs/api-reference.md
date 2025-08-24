# API Reference

Complete reference for the FlowStack Python SDK.

## Agent Class

::: flowstack.agent.Agent
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### Usage Examples

#### Basic Agent Creation

```python
from flowstack import Agent, Models, Providers

# Simple agent with defaults
agent = Agent(
    name="my-agent",
    api_key="fs_your_api_key_here"
)

# Agent with specific provider and model
agent = Agent(
    name="openai-agent", 
    api_key="fs_your_api_key_here",
    provider=Providers.OPENAI,
    model="gpt-4o",
    byok={"api_key": "sk-your-openai-key"}
)
```

#### Adding Tools

!!! important "Source Code Requirement"
    Tools must be defined in Python files (.py), not in interactive environments.
    FlowStack extracts source code for secure MCP execution.

```python
# In a file: my_agent.py
@agent.tool
def get_weather(city: str) -> dict:
    """Get current weather for a city"""
    # Your implementation here
    return {"city": city, "temperature": 72, "condition": "sunny"}

@agent.tool
def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email"""
    # Your implementation here
    return {"sent": True, "message_id": "abc123"}

# JavaScript tools (coming soon)
@agent.tool(language='javascript', source_code='''
function processData(data) {
    return data.map(x => x * 2);
}
''')
def process_data_js():
    pass  # Placeholder for JavaScript tool
```

#### Chat Interface

```python
# Simple chat
response = agent.chat("What's the weather in San Francisco?")
print(response)

# Chat with parameters
response = agent.chat(
    "Write a haiku about programming",
    temperature=0.8,
    max_tokens=100
)
```

#### Advanced Usage

```python
# Multi-turn conversation
messages = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."},
    {"role": "user", "content": "Show me an example"}
]

response = agent.invoke(messages, temperature=0.7)
```

### Methods

#### `__init__(name, api_key, provider=Providers.BEDROCK, model=Models.CLAUDE_35_SONNET, byok=None, base_url=None, **kwargs)`

Initialize a new FlowStack agent.

**Parameters:**

- `name` (str): Unique identifier for your agent
- `api_key` (str): Your FlowStack API key
- `provider` (str): AI provider to use (default: Providers.BEDROCK)
- `model` (str): Model to use (default: Models.CLAUDE_35_SONNET)  
- `byok` (dict, optional): Bring Your Own Key credentials
- `base_url` (str, optional): Custom API base URL
- `**kwargs`: Additional configuration options

**Example:**
```python
agent = Agent(
    name="customer-service",
    api_key="fs_abc123",
    provider=Providers.OPENAI,
    model="gpt-4o",
    byok={"api_key": "sk-xyz789"}
)
```

#### `chat(message, **kwargs) -> str`

Simple chat interface that returns just the text response.

**Parameters:**

- `message` (str): Your message to the agent
- `**kwargs`: Additional parameters (temperature, max_tokens, etc.)

**Returns:** `str` - The agent's response

**Example:**
```python
response = agent.chat("Hello! How are you?")
print(response)  # "Hello! I'm doing well, thank you for asking..."
```

#### `invoke(message, **kwargs) -> dict`

Advanced interface for full control over the conversation.

**Parameters:**

- `message` (str | list): Text message or list of message objects
- `**kwargs`: Additional parameters (temperature, max_tokens, etc.)

**Returns:** `dict` - Full response object with metadata

**Example:**
```python
# Simple message
response = agent.invoke("Tell me a joke")

# Multi-turn conversation
messages = [
    {"role": "user", "content": "What is AI?"},
    {"role": "assistant", "content": "AI stands for Artificial Intelligence..."},
    {"role": "user", "content": "Give me an example"}
]
response = agent.invoke(messages)
```

#### `deploy() -> str`

Deploy your agent to production.

!!! note "MCP Deployment"
    During deployment, FlowStack extracts your tools' source code and configures them for secure MCP (Model Context Protocol) execution in isolated containers.

**Returns:** `str` - Production endpoint URL

**Example:**
```python
endpoint = agent.deploy()
print(f"Agent deployed at: {endpoint}")
# Output: "Agent deployed at: https://api.flowstack.fun/agents/my-agent"
```

**Common Errors:**
- `"Cannot extract source code"`: Tools must be in .py files, not REPL/Jupyter
- `"Tool validation failed"`: Ensure tools have proper docstrings and type hints

#### `get_usage() -> UsageStats`

Get current usage statistics and limits.

**Returns:** `UsageStats` - Usage information object

**Example:**
```python
usage = agent.get_usage()
print(f"Sessions: {usage.sessions_used}/{usage.sessions_limit}")
print(f"Remaining: {usage.sessions_remaining}")
print(f"Usage: {usage.usage_percentage:.1f}%")

if usage.is_near_limit:
    print("Warning: Approaching usage limit!")
```

#### `set_provider(provider, byok=None)`

Switch to a different AI provider.

**Parameters:**

- `provider` (str): New provider to use
- `byok` (dict, optional): BYOK credentials if required

**Example:**
```python
# Switch to OpenAI
agent.set_provider(Providers.OPENAI, byok={"api_key": "sk-..."})

# Switch to Anthropic
agent.set_provider(Providers.ANTHROPIC, byok={"api_key": "sk-ant-..."})

# Switch back to managed Bedrock
agent.set_provider(Providers.BEDROCK)
```

#### `set_model(model)`

Change the model being used.

**Parameters:**

- `model` (str): New model to use

**Example:**
```python
agent.set_model("gpt-4o")
agent.set_model(Models.CLAUDE_35_HAIKU)
```

#### `get_tier_info() -> dict`

Get information about your current pricing tier.

**Returns:** `dict` - Tier information

**Example:**
```python
tier = agent.get_tier_info()
print(f"Current tier: {tier['current_tier']}")
print(f"Session limit: {tier['session_limit']}")
print(f"Can use managed models: {tier['can_use_managed']}")
```

#### `store_byok_credentials(provider, credentials) -> bool`

Store BYOK credentials for future use.

**Parameters:**

- `provider` (str): Provider name
- `credentials` (dict): Credential dictionary

**Returns:** `bool` - Success status

**Example:**
```python
success = agent.store_byok_credentials('openai', {
    'api_key': 'sk-your-openai-key'
})

if success:
    print("Credentials stored successfully")
```

### Properties

#### `vault`

Access to DataVault for persistent storage.

**Example:**
```python
# Store data
agent.vault.store('users', {'name': 'Alice', 'age': 30})

# Retrieve data
user = agent.vault.retrieve('users', key='user_123')

# Query data
adults = agent.vault.query('users', {'age': {'$gte': 18}})
```

## DataVault

The DataVault provides persistent storage for your agents.

### Core Methods

#### `store(collection, data, key=None) -> str`

Store data in a collection.

**Parameters:**

- `collection` (str): Collection name (like a database table)
- `data` (dict): Data to store
- `key` (str, optional): Custom key (auto-generated if not provided)

**Returns:** `str` - Key of stored item

**Example:**
```python
# Auto-generated key
key = agent.vault.store('products', {
    'name': 'Laptop',
    'price': 999.99,
    'category': 'electronics'
})

# Custom key
agent.vault.store('products', {
    'name': 'Mouse',
    'price': 29.99
}, key='mouse-001')
```

#### `retrieve(collection, key=None, filter=None) -> dict | list | None`

Retrieve data from a collection.

**Parameters:**

- `collection` (str): Collection name
- `key` (str, optional): Specific key to retrieve
- `filter` (dict, optional): Query filter for multiple items

**Returns:** Single item, list of items, or None

**Example:**
```python
# Get specific item
product = agent.vault.retrieve('products', key='mouse-001')

# Get all items in collection
all_products = agent.vault.retrieve('products')

# Query with filter
expensive_items = agent.vault.retrieve('products', filter={
    'price': {'$gte': 500}
})
```

#### `query(collection, filter) -> list`

Advanced querying with MongoDB-style filters.

**Parameters:**

- `collection` (str): Collection name
- `filter` (dict): Query filter using MongoDB syntax

**Returns:** `list` - List of matching items

**Example:**
```python
# Basic query
results = agent.vault.query('users', {'age': {'$gte': 18}})

# Complex query with multiple conditions
active_admins = agent.vault.query('users', {
    'role': 'admin',
    'active': True,
    'last_login': {'$gte': '2024-01-01'}
})

# Complex query
power_users = agent.vault.query('users', {
    '$or': [
        {'premium': True},
        {'login_count': {'$gte': 100}}
    ]
})
```

#### `update(collection, key, updates) -> bool`

Update an existing item.

**Parameters:**

- `collection` (str): Collection name
- `key` (str): Key of item to update
- `updates` (dict): Fields to update

**Returns:** `bool` - Success status

**Example:**
```python
success = agent.vault.update('products', 'mouse-001', {
    'price': 24.99,
    'sale': True
})
```

#### `delete(collection, key) -> bool`

Delete an item from a collection.

**Parameters:**

- `collection` (str): Collection name
- `key` (str): Key of item to delete

**Returns:** `bool` - Success status

**Example:**
```python
deleted = agent.vault.delete('products', 'mouse-001')
```

#### `count(collection, filter=None) -> int`

Count items in a collection.

**Parameters:**

- `collection` (str): Collection name
- `filter` (dict, optional): Query filter

**Returns:** `int` - Number of items

**Example:**
```python
total_users = agent.vault.count('users')
active_users = agent.vault.count('users', {'active': True})
```

#### `list_collections() -> list`

List all collections in your agent's namespace.

**Returns:** `list` - Collection names

**Example:**
```python
collections = agent.vault.list_collections()
print(f"Available collections: {collections}")
```

#### `clear(collection) -> bool`

Clear all items from a collection.

!!! warning "Destructive Operation"
    This permanently deletes all data in the collection.

**Parameters:**

- `collection` (str): Collection name

**Returns:** `bool` - Success status

**Example:**
```python
# Clear temporary cache
agent.vault.clear('temp_cache')
```

## UsageStats Class

::: flowstack.billing.UsageStats
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### Properties

#### `sessions_used`
Number of sessions used in current billing period.

#### `sessions_limit`  
Total session limit for current billing period.

#### `sessions_remaining`
Number of sessions remaining.

#### `current_charges`
Current charges for the billing period.

#### `tier`
Current pricing tier (free, starter, professional, enterprise).

#### `usage_percentage`
Usage as percentage of limit (0-100).

#### `is_near_limit`
True if usage is above 80% of limit.

#### `can_make_requests`
True if more requests can be made within limits.

### Example Usage

```python
usage = agent.get_usage()

print(f"Usage: {usage.sessions_used}/{usage.sessions_limit}")
print(f"Percentage: {usage.usage_percentage:.1f}%")
print(f"Current charges: ${usage.current_charges:.2f}")
print(f"Tier: {usage.tier}")

if usage.is_near_limit:
    print("⚠️ Warning: You're using 80%+ of your monthly sessions")
    
if not usage.can_make_requests:
    print("❌ Session limit reached. Please upgrade your plan.")
    
print(f"Sessions remaining: {usage.sessions_remaining}")
```

## Constants

### Models

```python
from flowstack import Models

# Anthropic Claude (via Bedrock)
Models.CLAUDE_35_SONNET      # claude-3-5-sonnet-20240620-v1:0
Models.CLAUDE_35_HAIKU       # claude-3-5-haiku-20240307-v1:0  
Models.CLAUDE_3_OPUS         # claude-3-opus-20240229-v1:0

# Meta Llama (via Bedrock)
Models.LLAMA_3_70B           # meta.llama3-70b-instruct-v1:0
Models.LLAMA_31_405B         # meta.llama3-1-405b-instruct-v1:0

# OpenAI (BYOK only)
Models.GPT_4O                # gpt-4o
Models.GPT_4_TURBO           # gpt-4-turbo
Models.GPT_35_TURBO          # gpt-3.5-turbo
```

### Providers

```python
from flowstack import Providers

# Managed billing available
Providers.BEDROCK            # Cloud AI services (managed or BYOK)

# BYOK only
Providers.OPENAI             # OpenAI API
Providers.ANTHROPIC          # Anthropic API  
Providers.COHERE             # Cohere API
Providers.MISTRAL            # Mistral AI API
Providers.OLLAMA             # Local Ollama
Providers.SAGEMAKER          # SageMaker endpoints
Providers.WRITER             # Writer API
```

## Exceptions

### FlowStackError

Base exception for all FlowStack SDK errors.

```python
from flowstack import FlowStackError

try:
    response = agent.chat("Hello")
except FlowStackError as e:
    print(f"FlowStack error: {e}")
```

### AuthenticationError

Raised when API key is invalid or missing.

```python
from flowstack import AuthenticationError

try:
    agent = Agent("test", api_key="invalid_key")
    response = agent.chat("Hello")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

### QuotaExceededError

Raised when usage limits are exceeded.

```python
from flowstack import QuotaExceededError

try:
    response = agent.chat("Hello")
except QuotaExceededError as e:
    print(f"Quota exceeded: {e}")
    print(f"Current usage: {e.details.get('current_usage')}")
    print(f"Limit: {e.details.get('limit')}")
```

### InvalidProviderError

Raised when an unsupported provider is specified.

```python
from flowstack import InvalidProviderError

try:
    agent.set_provider("unsupported_provider")
except InvalidProviderError as e:
    print(f"Invalid provider: {e}")
```

### CredentialsRequiredError

Raised when BYOK credentials are required but not provided.

```python
from flowstack import CredentialsRequiredError

try:
    agent = Agent("test", api_key="fs_...", provider="openai")  # Missing BYOK
except CredentialsRequiredError as e:
    print(f"Credentials required: {e}")
```

### TierLimitationError

Raised when trying to use features not available in current tier.

```python
from flowstack import TierLimitationError

try:
    response = agent.chat("Hello")  # Free tier trying to use managed models
except TierLimitationError as e:
    print(f"Tier limitation: {e}")
```

## Utility Functions

### create_agent()

Convenience function for quick agent creation.

```python
from flowstack import create_agent, Models, Providers

agent = create_agent(
    name="quick-agent",
    api_key="fs_your_key",
    provider=Providers.OPENAI,
    model=Models.GPT_4O,
    byok={"api_key": "sk-..."}
)
```

## Environment Variables

The SDK respects these environment variables:

- `FLOWSTACK_API_URL`: Custom API base URL (default: https://api.flowstack.fun)
- `FLOWSTACK_API_KEY`: Default API key (if not provided in constructor)

```bash
export FLOWSTACK_API_URL="https://api.flowstack.fun"
export FLOWSTACK_API_KEY="fs_your_api_key_here"
```

## Error Handling Best Practices

```python
from flowstack import (
    Agent, FlowStackError, AuthenticationError, 
    QuotaExceededError, CredentialsRequiredError
)

try:
    agent = Agent("my-agent", api_key="fs_...")
    
    # Check usage before making requests
    usage = agent.get_usage()
    if not usage.can_make_requests:
        print("Usage limit reached!")
        return
    
    response = agent.chat("Hello!")
    print(response)
    
except AuthenticationError:
    print("Invalid API key. Please check your credentials.")
    
except QuotaExceededError as e:
    print(f"Usage limit exceeded: {e}")
    print("Please upgrade your plan or wait for reset.")
    
except CredentialsRequiredError as e:
    print(f"BYOK credentials required: {e}")
    print("Please provide API keys for the selected provider.")
    
except FlowStackError as e:
    print(f"FlowStack error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

For more examples and detailed guides, see our [recipes](recipes/chatbot.md) and [concepts](concepts.md) documentation.