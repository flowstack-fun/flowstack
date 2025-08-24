# 5-Minute Quickstart

Get your first agent from local development to production in under 5 minutes.

## Step 1: Install FlowStack SDK

```bash
pip install flowstack
```

!!! tip "Virtual Environment Recommended"
    ```bash
    python -m venv flowstack-env
    source flowstack-env/bin/activate  # On Windows: flowstack-env\Scripts\activate
    pip install flowstack
    ```

## Step 2: Get Your API Key

1. Go to [flowstack.fun](https://flowstack.fun)
2. Register your account (email verification required)
3. Copy your API key starting with `fs_`

!!! note "Free Tier"
    New accounts get 25 free sessions per month. Perfect for testing!

## Step 3: Build Your First Agent

!!! important "File Requirement"
    Tools must be defined in `.py` files (not in REPL, Jupyter, or command line).
    FlowStack needs to extract source code for secure MCP execution.

### Method 1: YAML Configuration (Recommended)

Create a project structure:
```
my-agent/
├── agent.yaml
└── tools/
    └── orders.py
```

Create `agent.yaml`:
```yaml title="agent.yaml"
name: customer-helper
instructions: |
  You are a helpful customer service agent.
  Help customers with their orders and feedback.
model: claude-3-sonnet
provider: bedrock
temperature: 0.7
tools:
  lookup_order:
    description: Look up order status
  store_feedback:
    description: Store customer feedback
```

Create `tools/orders.py`:
```python title="tools/orders.py"
def lookup_order(order_id: str) -> dict:
    """Look up order status by ID"""
    # In a real app, this would query your database
    # For now, let's simulate some order data
    orders = {
        "12345": {"status": "shipped", "tracking": "UPS123456789", "eta": "Tomorrow"},
        "67890": {"status": "processing", "tracking": None, "eta": "2-3 days"},
        "99999": {"status": "delivered", "tracking": "FEDEX987654321", "eta": "Completed"}
    }
    
    order = orders.get(order_id)
    if order:
        return order
    else:
        return {"error": f"Order {order_id} not found"}

def store_feedback(order_id: str, feedback: str) -> dict:
    """Store customer feedback for an order"""
    # In production, you'd store this in a database
    feedback_data = {
        "order_id": order_id,
        "feedback": feedback,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    # For now, just return success
    return {"message": "Feedback saved", "data": feedback_data}

```

### Method 2: Python Code with Decorator

Create `my_agent.py`:
```python title="my_agent.py"
from flowstack import Agent, tool

agent = Agent(
    name="customer-helper",
    api_key="fs_your_api_key_here",
    instructions="You are a helpful customer service agent."
)

@tool
def lookup_order(order_id: str) -> dict:
    """Look up order status by ID"""
    orders = {
        "12345": {"status": "shipped", "tracking": "UPS123456789"},
        "67890": {"status": "processing", "eta": "2-3 days"}
    }
    return orders.get(order_id, {"error": "Order not found"})

# Add tool to agent
agent.add_tool(lookup_order)
```

## Step 4: Test Locally

### For YAML approach:
```python title="test_agent.py"
from flowstack import Agent

agent = Agent.from_yaml("agent.yaml", api_key="fs_your_api_key_here")

# Test locally
response = agent.chat("What's the status of order 12345?")
print(response)
```

### For code approach:
```bash
python my_agent.py
```

!!! success "It Works!"
    Your agent is now running locally with tools and DataVault persistence. Next, let's make it live!

!!! tip "Troubleshooting: 'Cannot extract source' error"
    If you see an error about source extraction, make sure:
    1. Your tools are defined in a .py file (not interactive Python)
    2. The file is saved before running
    3. You're running the file with `python my_agent.py`, not copying into REPL

## Step 5: Deploy to Production

FlowStack extracts your tool source code and configures them for secure MCP execution.

### Deploy with YAML:
```python title="deploy.py"
from flowstack import Agent

agent = Agent.from_yaml("agent.yaml", api_key="fs_your_api_key_here")

print("🚀 Deploying to production...")
result = agent.deploy()
print(f"✅ Deployment successful!")
print(f"Deployment ID: {result['deployment_id']}")
print(f"Namespace: {result['namespace']}")
```

### Deploy with code:
```python
# Add to your my_agent.py
result = agent.deploy()
print(f"Deployed with ID: {result['deployment_id']}")
```

You'll see:

```
🚀 Deploying to production...
✅ Deployment successful!
Deployment ID: dep_abc123xyz
Namespace: ns_cust456_789def
```

## Step 6: Test Your Live Agent

Your agent is now deployed! To invoke it, use the namespace returned from deployment:

```python
# After deployment, you can invoke your agent
response = agent.chat("Check the status of order 67890")
print(response)
```

Or via API:

```bash
curl -X POST https://api.flowstack.fun/agents/{namespace}/invoke \
  -H "Content-Type: application/json" \
  -H "X-API-Key: fs_your_api_key_here" \
  -d '{
    "message": "Check the status of order 67890"
  }'
    ```

=== "Python Client"

    ```python
    import requests
    
    response = requests.post(
        "https://api.flowstack.fun/agents/customer-helper/chat",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": "fs_your_api_key_here"
        },
        json={"message": "What's the status of order 99999?"}
    )
    
    print(response.json())
    ```

## 🎉 Congratulations!

You just built and deployed a production AI agent in under 5 minutes! Your agent:

✅ **Has custom tools** - `lookup_order()` and `store_feedback()`  
✅ **Secure tool execution** - Tools run in isolated MCP containers  
✅ **Uses persistent storage** - DataVault automatically stores feedback  
✅ **Runs in production** - Live HTTPS endpoint ready for real traffic  
✅ **Scales automatically** - From 0 to thousands of requests  
✅ **Handles authentication** - Secured with your API key  

## What Happens Next?

<div class="grid cards" markdown>

-   :material-database:{ .lg .middle } **[Learn DataVault](datavault.md)**

    ---

    Understand how to store and query data in your agents

-   :material-cog:{ .lg .middle } **[Core Concepts](concepts.md)**

    ---

    Learn about agents, tools, deployment, and sessions

-   :material-chef-hat:{ .lg .middle } **[See More Examples](recipes/chatbot.md)**

    ---

    Chatbots, automation agents, and advanced patterns

-   :material-monitor-dashboard:{ .lg .middle } **[Monitor Usage](billing.md)**

    ---

    Track your usage, understand billing, and upgrade plans

</div>

## Check Your Usage

See how many sessions you've used:

```python
usage = agent.get_usage()
print(f"Sessions used: {usage.sessions_used}/{usage.sessions_limit}")
print(f"Sessions remaining: {usage.sessions_remaining}")
```

## Common Next Steps

### Add More Tools
```python
@agent.tool
def cancel_order(order_id: str) -> dict:
    """Cancel an order if possible"""
    # Your cancellation logic here
    pass

@agent.tool
def track_shipment(tracking_number: str) -> dict:
    """Get detailed tracking information"""
    # Integration with shipping APIs
    pass
```

### Store More Data
```python
# Store user preferences
agent.vault.store('users', {
    'user_id': 'user_123',
    'preferences': {'notifications': True, 'language': 'en'}
})

# Store conversation history
agent.vault.store('conversations', {
    'user_id': 'user_123',
    'messages': [...],
    'timestamp': datetime.now()
})
```

### Switch AI Providers
```python
# Use your own OpenAI key (no markup)
agent = Agent(
    name="my-agent",
    api_key="fs_...",
    provider="openai",
    model="gpt-4",
    byok={"api_key": "sk-your-openai-key"}
)
```

Ready to build something amazing? Check out our [recipes](recipes/chatbot.md) for inspiration!