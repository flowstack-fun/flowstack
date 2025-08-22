# Core Concepts

Understanding the key concepts behind FlowStack will help you build better agents and make the most of the platform.

## Agent

An **Agent** is your AI assistant with custom capabilities and memory.

```python
from flowstack import Agent

agent = Agent(
    name="my-assistant",        # Unique identifier
    api_key="fs_your_key",      # Your FlowStack API key  
    provider="bedrock",         # AI provider (bedrock, openai, anthropic)
    model="claude-3-sonnet"     # Specific model to use
)
```

### What Makes an Agent Unique?

- **Tools**: Custom functions the agent can call
- **Memory**: Persistent storage via DataVault
- **Identity**: Each agent has its own namespace and endpoint
- **Behavior**: The agent learns to use tools to complete tasks

!!! example "Agent Personality"
    ```python
    agent = Agent(
        name="helpful-assistant",
        api_key="fs_...",
        system_prompt="You are a helpful customer service agent. Always be polite and try to solve problems using the available tools."
    )
    ```

## Tools

**Tools** are Python functions that give your agent capabilities beyond chat.

```python
@agent.tool
def get_weather(city: str) -> dict:
    """Get current weather for a city"""
    # Your implementation here
    return {"city": city, "temp": 72, "condition": "sunny"}

@agent.tool
def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email to a user"""
    # Integration with email service
    return {"sent": True, "message_id": "abc123"}
```

### Tool Guidelines

!!! success "Good Tools"
    - **Single purpose**: One tool = one clear function
    - **Clear docstrings**: The agent uses these to understand what the tool does
    - **Return structured data**: Dicts and lists work best
    - **Handle errors gracefully**: Return error messages, don't raise exceptions

!!! failure "Avoid"
    - **Complex multi-step tools**: Break them into smaller tools
    - **Missing docstrings**: The agent won't know what the tool does
    - **Side effects without returns**: Always return something meaningful

### Tool Examples by Use Case

=== "E-commerce"
    ```python
    @agent.tool
    def lookup_order(order_id: str) -> dict:
        """Get order details by ID"""
        pass
    
    @agent.tool
    def cancel_order(order_id: str) -> dict:
        """Cancel an order if cancellation is allowed"""
        pass
    
    @agent.tool
    def process_refund(order_id: str, amount: float) -> dict:
        """Process a refund for an order"""
        pass
    ```

=== "Customer Support"
    ```python
    @agent.tool
    def search_knowledge_base(query: str) -> list:
        """Search for relevant help articles"""
        pass
    
    @agent.tool
    def create_ticket(title: str, description: str, priority: str) -> dict:
        """Create a support ticket"""
        pass
    
    @agent.tool
    def escalate_to_human(reason: str) -> dict:
        """Escalate conversation to human agent"""
        pass
    ```

=== "Data Analysis"
    ```python
    @agent.tool
    def query_database(sql: str) -> list:
        """Execute a SQL query safely"""
        pass
    
    @agent.tool
    def generate_chart(data: list, chart_type: str) -> dict:
        """Create a chart from data"""
        pass
    
    @agent.tool
    def export_report(data: dict, format: str) -> dict:
        """Export data as PDF or Excel"""
        pass
    ```

## Deployment

**Deployment** transforms your local agent into a production API with one command.

```python
# Deploy your agent
endpoint = agent.deploy()
# Returns: https://api.flowstack.fun/agents/your-agent-name
```

### What Happens During Deployment?

1. **Code Packaging**: Your agent code and tools are packaged
2. **Infrastructure Setup**: Lambda functions, API Gateway, databases
3. **Endpoint Creation**: Your agent gets a unique HTTPS URL
4. **Health Checks**: We verify everything is working
5. **Go Live**: Your agent starts handling requests

### Deployment Environments

=== "Development"
    ```python
    agent.deploy(environment="dev")
    # → https://api.flowstack.fun/agents/your-agent-dev
    ```
    
    - Lower costs, higher limits for testing
    - Separate DataVault namespace
    - Faster iteration, more debugging info

=== "Production"
    ```python
    agent.deploy(environment="prod")
    # → https://api.flowstack.fun/agents/your-agent
    ```
    
    - Production SLA and monitoring
    - Optimized performance
    - Enhanced security and isolation

!!! tip "Deploy Early and Often"
    Deploy to dev environment frequently during development. Deploy to production when you're confident in your agent's behavior.

## DataVault

**DataVault** is persistent storage built into every agent. Think of it as a simple database that just works.

```python
# Store data
key = agent.vault.store('users', {
    'name': 'Alice',
    'preferences': {'theme': 'dark', 'notifications': True}
})

# Retrieve data
user = agent.vault.retrieve('users', key=key)

# Query data
recent_users = agent.vault.query('users', {
    'created_at': {'$gte': '2024-01-01'}
})
```

### DataVault Collections

Think of **collections** like database tables. Each agent can create multiple collections:

- `users` - User profiles and preferences
- `conversations` - Chat history and context
- `sessions` - Temporary session data
- `feedback` - User feedback and ratings
- `cache` - Temporary calculations or API responses

### When to Use DataVault

!!! success "Perfect For"
    - **User preferences and settings**
    - **Conversation history and context**
    - **Agent memory and learning**
    - **Application state between sessions**
    - **Caching expensive operations**

!!! warning "Not Designed For"
    - Large files or media (use cloud storage URLs)
    - Real-time updates (not a message queue)
    - Complex relational queries (use a proper database)
    - Secrets or API keys (use BYOK for credentials)

### DataVault Patterns

=== "User State"
    ```python
    @agent.tool
    def remember_preference(user_id: str, key: str, value: str):
        """Remember a user preference"""
        user = agent.vault.retrieve('users', key=user_id) or {}
        user.setdefault('preferences', {})[key] = value
        agent.vault.store('users', user, key=user_id)
        return f"I'll remember that you prefer {key}: {value}"
    
    @agent.tool
    def get_user_preference(user_id: str, key: str):
        """Get a user's preference"""
        user = agent.vault.retrieve('users', key=user_id) or {}
        return user.get('preferences', {}).get(key, "No preference set")
    ```

=== "Conversation Memory"
    ```python
    def store_conversation(user_id: str, messages: list):
        """Store conversation history"""
        agent.vault.store('conversations', {
            'user_id': user_id,
            'messages': messages,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_conversation_history(user_id: str, limit: int = 10):
        """Get recent conversations for context"""
        return agent.vault.query('conversations', 
            {'user_id': user_id},
            sort=[('timestamp', -1)],
            limit=limit
        )
    ```

=== "Agent Learning"
    ```python
    @agent.tool
    def learn_from_feedback(topic: str, feedback: str, helpful: bool):
        """Learn from user feedback"""
        learning_data = {
            'topic': topic,
            'feedback': feedback,
            'helpful': helpful,
            'timestamp': datetime.now().isoformat()
        }
        agent.vault.store('learning', learning_data)
        return "Thank you for the feedback! I'll use this to improve."
    
    def get_learned_patterns(topic: str):
        """Retrieve learning patterns for a topic"""
        return agent.vault.query('learning', {
            'topic': topic,
            'helpful': True
        })
    ```

## Sessions

A **session** is FlowStack's billing unit. One session = one conversation (multiple messages back and forth).

### Session Lifecycle

1. **Start**: First message from a user starts a session
2. **Continue**: Follow-up messages extend the same session  
3. **End**: Session ends after 30 minutes of inactivity
4. **Bill**: You're charged for one session regardless of message count

```python
# Check your usage
usage = agent.get_usage()
print(f"Sessions used: {usage.sessions_used}/{usage.sessions_limit}")
print(f"Usage percentage: {usage.usage_percentage:.1f}%")

# Check if you're near limits
if usage.is_near_limit:
    print("Warning: You're using 80%+ of your monthly sessions")

if not usage.can_make_requests:
    print("Session limit reached. Please upgrade your plan.")
```

### Session vs. Messages

!!! example "Session Counting"
    **One Session** includes:
    
    - User: "What's the weather?"
    - Agent: "I'll check that for you. Which city?"
    - User: "San Francisco"
    - Agent: "It's 72°F and sunny in San Francisco"
    - User: "Thanks!"
    - Agent: "You're welcome!"
    
    **Six messages = One session**

### Managing Session Costs

- **Batch interactions**: Handle multiple requests in one conversation
- **Use DataVault**: Store data instead of repeating context
- **BYOK for AI costs**: Use your own provider keys to avoid markup
- **Monitor usage**: Check `agent.get_usage()` regularly

## AI Providers

FlowStack supports multiple AI providers, giving you flexibility and control over costs.

### Managed Providers (FlowStack-hosted)

```python
agent = Agent(
    name="my-agent",
    api_key="fs_...",
    provider="bedrock",  # Managed by FlowStack
    model="claude-3-sonnet"
)
```

**Benefits**: No additional setup, optimized performance, included in session pricing.

**Available**: AWS Bedrock (Claude, Llama, Mistral models)

### BYOK Providers (Bring Your Own Keys)

```python
agent = Agent(
    name="my-agent", 
    api_key="fs_...",
    provider="openai",
    model="gpt-4",
    byok={"api_key": "sk-your-openai-key"}  # Your own key
)
```

**Benefits**: Direct billing from provider, no markup, full control.

**Supported**: OpenAI, Anthropic, Cohere, Mistral, Ollama, AWS Bedrock

### Provider Switching

```python
# Start with managed Bedrock
agent = Agent("flexible-agent", api_key="fs_...", provider="bedrock")

# Switch to your own OpenAI account
agent.set_provider("openai", byok={"api_key": "sk-..."})

# Or use Anthropic direct
agent.set_provider("anthropic", byok={"api_key": "sk-ant-..."})
```

## Security & Isolation

Every agent runs in its own secure environment:

### Agent Isolation
- **Separate containers**: Each agent runs in isolation
- **Namespaced data**: DataVault data is isolated per agent
- **API key authentication**: Only you can access your agents
- **Rate limiting**: Automatic protection against abuse

### Data Security
- **Encrypted at rest**: All DataVault data is encrypted
- **TLS in transit**: All API calls use HTTPS
- **No data sharing**: Agents can't access each other's data
- **Audit logs**: We track access for compliance

### Best Practices

!!! success "Do"
    - Use strong API keys and keep them secret
    - Validate inputs in your tools
    - Store sensitive data in your own systems, not DataVault
    - Use BYOK for sensitive AI processing
    - Monitor usage and set up alerts

!!! failure "Don't"
    - Hardcode API keys in your source code
    - Store passwords or secrets in DataVault
    - Allow unrestricted database access from tools
    - Share API keys between environments
    - Ignore usage alerts

---

Ready to see these concepts in action? Check out our [recipes](recipes/chatbot.md) for complete examples, or dive into the [DataVault guide](datavault.md) to learn about data persistence.