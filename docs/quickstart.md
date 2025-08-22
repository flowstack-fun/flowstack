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

Create a file called `my_agent.py`:

```python title="my_agent.py"
from flowstack import Agent

# Initialize your agent
agent = Agent(
    name="customer-helper",
    api_key="fs_your_api_key_here"  # Replace with your actual key
)

# Add a tool - this is what makes your agent useful
@agent.tool
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

@agent.tool  
def store_feedback(order_id: str, feedback: str) -> dict:
    """Store customer feedback for an order"""
    # Use DataVault to persist feedback
    feedback_data = {
        "order_id": order_id,
        "feedback": feedback,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    # Store in DataVault (built-in persistence)
    feedback_key = agent.vault.store('feedback', feedback_data)
    return {"message": "Feedback saved", "id": feedback_key}

# Test your agent locally first
if __name__ == "__main__":
    print("🤖 Testing customer helper agent...")
    
    # Test order lookup
    response1 = agent.chat("What's the status of order 12345?")
    print(f"Order Status: {response1}")
    
    # Test feedback storage
    response2 = agent.chat("I want to leave feedback for order 12345: Great service!")
    print(f"Feedback: {response2}")
    
    print("\n✅ Local testing complete!")
```

## Step 4: Test Locally

Run your agent to make sure it works:

```bash
python my_agent.py
```

You should see output like:

```
🤖 Testing customer helper agent...
Order Status: I found order 12345! It has shipped with tracking number UPS123456789 and should arrive tomorrow.
Feedback: Thank you for your feedback! I've saved your comment about great service for order 12345.

✅ Local testing complete!
```

!!! success "It Works!"
    Your agent is now running locally with tools and DataVault persistence. Next, let's make it live!

## Step 5: Deploy to Production

Add this to the bottom of your `my_agent.py` file:

```python title="my_agent.py" hl_lines="3-6"
# ... your existing code above ...

# Deploy to production
if __name__ == "__main__":
    # Test locally first (existing code)
    # ... 
    
    # Deploy to production
    print("\n🚀 Deploying to production...")
    endpoint = agent.deploy()
    print(f"✅ Agent deployed successfully!")
    print(f"Production endpoint: {endpoint}")
    print(f"Chat endpoint: {endpoint}/chat")
```

Run the deployment:

```bash
python my_agent.py
```

You'll see:

```
🚀 Deploying to production...
✅ Agent deployed successfully!
Production endpoint: https://api.flowstack.fun/agents/customer-helper
Chat endpoint: https://api.flowstack.fun/agents/customer-helper/chat
```

## Step 6: Test Your Live Agent

Your agent is now running in production! Test it with curl:

=== "Test Order Lookup"

    ```bash
    curl -X POST https://api.flowstack.fun/agents/customer-helper/chat \
      -H "Content-Type: application/json" \
      -H "X-API-Key: fs_your_api_key_here" \
      -d '{
        "message": "Check the status of order 67890"
      }'
    ```

=== "Test Feedback Storage"

    ```bash
    curl -X POST https://api.flowstack.fun/agents/customer-helper/chat \
      -H "Content-Type: application/json" \
      -H "X-API-Key: fs_your_api_key_here" \
      -d '{
        "message": "I want to give feedback for order 12345: Fast delivery!"
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