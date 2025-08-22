# FlowStack SDK

**From local agent to production in 5 minutes.**

FlowStack is the simplest way to build and deploy AI agents. Write Python tools, test locally, deploy instantly. No infrastructure, no DevOps, no complexity.

## 🚀 Why FlowStack?

**Think Vercel for AI agents.** You focus on agent logic, we handle everything else.

- ✅ **Write tools in Python** - Natural @agent.tool decorator
- ✅ **Deploy in one command** - `agent.deploy()` and you're live
- ✅ **Instant production API** - Get HTTPS endpoints immediately  
- ✅ **Built-in memory** - DataVault for persistent agent state
- ✅ **Multi-provider support** - Switch between OpenAI, Claude, Llama seamlessly

## 🎯 Perfect For

- **🥷 Indie developers** - Build weekend projects that scale
- **🚀 Startups** - Rapid prototyping without infrastructure overhead
- **🤖 Automation enthusiasts** - Replace Zapier with custom AI logic

## ⚡ Quick Start

### 1. Install & Deploy in 5 Minutes

```bash
# Install
pip install flowstack

# Get your API key from flowstack.fun
export FLOWSTACK_API_KEY="fs_..."
```

### 2. Build Your First Agent

```python
from flowstack import Agent

# Create agent with tools
agent = Agent("customer-helper")

@agent.tool
def lookup_order(order_id: str) -> dict:
    """Look up customer order status"""
    # Your business logic here
    return {"status": "shipped", "tracking": "UPS123456789"}

@agent.tool  
def update_address(order_id: str, new_address: str) -> str:
    """Update shipping address for an order"""
    # Your business logic here
    return f"Address updated for order {order_id}"

# Test locally
response = agent.chat("What's the status of order #12345?")
print(response)  # Agent calls lookup_order() automatically
```

### 3. Deploy to Production

```python
# Deploy with one command
endpoint = agent.deploy()
print(f"🎉 Your agent is live at: {endpoint}")

# Now available as REST API:
# POST https://your-agent.flowstack.fun/chat
# {"message": "What's the status of order #12345?"}
```

## 🧠 Persistent Memory with DataVault

Agents remember context across conversations:

```python
@agent.tool
def save_preference(user_id: str, preference: str) -> str:
    """Save user preference"""
    agent.vault.store('preferences', {
        'user_id': user_id, 
        'preference': preference
    })
    return "Preference saved!"

@agent.tool
def get_recommendations(user_id: str) -> list:
    """Get personalized recommendations"""
    prefs = agent.vault.query('preferences', {'user_id': user_id})
    # Use preferences to customize recommendations
    return ["item1", "item2", "item3"]
```

## 🔄 Multi-Provider Flexibility

Switch AI providers without changing code:

```python
# Use managed Bedrock (included in pricing)
agent = Agent("my-agent", model="claude-3-sonnet")

# Or bring your own OpenAI key  
agent = Agent("my-agent", 
    provider="openai",
    model="gpt-4o", 
    byok={"api_key": "sk-your-key"}
)

# Same tools, same deployment, different AI provider
```

## 📊 Real-World Examples

### Slack Customer Support Bot
```python
agent = Agent("support-bot")

@agent.tool
def search_knowledge_base(query: str) -> str:
    # Search your docs/FAQ
    return search_results

@agent.tool  
def create_ticket(issue: str, priority: str) -> str:
    # Create Zendesk/Jira ticket
    return ticket_id

# Deploy and connect to Slack webhook
endpoint = agent.deploy()
```

### E-commerce Order Assistant
```python
agent = Agent("order-assistant")

@agent.tool
def check_inventory(product_id: str) -> dict:
    # Check your inventory system
    return {"in_stock": True, "quantity": 50}

@agent.tool
def process_return(order_id: str, reason: str) -> str:
    # Handle return logic
    return "Return processed"

# Deploy and embed in your website
endpoint = agent.deploy()
```

### Content Creation Workflow  
```python
agent = Agent("content-creator")

@agent.tool
def research_topic(topic: str) -> str:
    # Research from multiple sources
    return research_summary

@agent.tool
def publish_to_cms(title: str, content: str) -> str:
    # Publish to WordPress/Contentful
    return "Published successfully"

# Deploy and trigger via webhook
endpoint = agent.deploy()
```

## 💰 Simple Pricing

**Session-based pricing.** One conversation = one session, regardless of message count.

- **Free**: 25 sessions/month
- **Starter**: $29/month, 1,000 sessions  
- **Professional**: $99/month, 10,000 sessions
- **Enterprise**: $499+/month, 100,000+ sessions

## 📚 Learn More

- **📖 [Documentation](https://flowstack-fun.github.io/flowstack/)** - Complete guides and examples
- **🚀 [5-Minute Tutorial](https://flowstack-fun.github.io/flowstack/quickstart/)** - Get started immediately
- **🧠 [DataVault Guide](https://flowstack-fun.github.io/flowstack/datavault/)** - Persistent agent memory
- **🍳 [Recipe Collection](https://flowstack-fun.github.io/flowstack/recipes/chatbot/)** - Real-world examples

## 🛠️ Development

```bash
# Local development
git clone https://github.com/flowstack-fun/flowstack.git
cd flowstack
pip install -e .

# Run tests  
pytest tests/

# Build docs
mkdocs serve
```

## 🤝 Support

- **🐛 Issues**: [GitHub Issues](https://github.com/flowstack-fun/flowstack/issues)
- **💬 Community**: [Discord](https://discord.gg/flowstack) 
- **📧 Email**: [support@flowstack.fun](mailto:support@flowstack.fun)
- **🐦 Updates**: [@flowstack](https://twitter.com/flowstack)

---

**Built for developers who ship fast.** 🚢

*Stop building infrastructure. Start building agents.*