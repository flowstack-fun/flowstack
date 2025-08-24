# FlowStack SDK

## From Local Agent to Production in 5 Minutes

Build your AI agent locally. Deploy with one command. Get a production endpoint instantly.

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } **5 Minutes to Production**

    ---

    Skip weeks of infrastructure setup. Build locally, deploy instantly.

    ```python
    result = agent.deploy()  # That's it
    ```

-   :material-database:{ .lg .middle } **Built-in Persistence**

    ---

    DataVault gives every agent MongoDB-backed storage with zero configuration.

    ```python
    vault.store('users', data)
    ```

-   :material-cash:{ .lg .middle } **Simple Billing**

    ---

    Pay per session (API call), not per token. No surprise bills.

    **Free**: 25 sessions/month | **Hobbyist**: $15/200 sessions

-   :material-cloud-upload:{ .lg .middle } **Auto-Scaling Infrastructure**

    ---

    We handle Lambda, containers, databases. You focus on agent logic.

    From 0 to 1000s of requests automatically.

</div>

## The Problem

You can build an AI agent locally in 10 minutes.  
Deploying it to production takes **10 days** of DevOps hell:

- ❌ Setting up AWS Lambda functions
- ❌ Configuring Docker containers
- ❌ Managing databases and persistence
- ❌ Setting up API gateways and load balancers
- ❌ Handling authentication and security
- ❌ Managing scaling and monitoring

## The FlowStack Solution

```python
from flowstack import Agent

# 1. Build your agent (YAML or code)
agent = Agent.from_yaml("agent.yaml", api_key="fs_...")
# Or define in code with instructions
agent = Agent(
    name="customer-helper",
    api_key="fs_...",
    instructions="You are a helpful support agent"
)

# 2. Test locally (works on your machine)
response = agent.chat("What's the status of order 12345?")
print(response)

# 3. Deploy to production (one command)
result = agent.deploy()
print(f"Deployed: {result['namespace']}")

# 4. Your agent is now live and accessible via API
```

**That's it.** Your agent is now running in production with:

✅ **HTTPS API endpoint** - Ready for production traffic  
✅ **Automatic scaling** - From 0 to thousands of requests  
✅ **Built-in persistence** - DataVault for storing data  
✅ **Security & isolation** - Each agent runs securely  
✅ **Monitoring & logs** - Track usage and debug issues  

## Who This Is For

### :material-account-hard-hat: Indie Developers & Hackers
You're building side projects, prototypes, or internal tools. **Pain point**: You can hack something locally, but deploying sucks.

!!! example "Weekend Project"
    Build a Slack bot, Discord assistant, or automation tool. Deploy Sunday night, use Monday morning.

### :material-rocket-launch: Startups Exploring AI
You don't want to spend weeks on infrastructure when testing ideas. **Value**: FlowStack = shortcut to shipping production-ready agents.

!!! example "MVP in Days"
    Test your AI product idea with real users. Iterate on features, not infrastructure.

### :material-cog-transfer: Automation Enthusiasts
You're already using Zapier or n8n. **Value**: Agents + persistence + real runtime → more powerful than simple automation.

!!! example "Zapier Killer"
    Build stateful workflows that remember context between runs. Handle complex decision trees.

## What We Handle (So You Don't Have To)

<div class="grid cards" markdown>

-   **:material-server: Infrastructure**
    
    Lambda functions, Docker containers, auto-scaling, load balancing

-   **:material-database-cog: Persistence**
    
    MongoDB-backed DataVault with namespaced, isolated storage

-   **:material-brain: AI Access**
    
    Managed Bedrock, OpenAI, Anthropic with simple provider switching

-   **:material-shield-check: Security**
    
    API authentication, request isolation, rate limiting, monitoring

-   **:material-chart-line: Monitoring**
    
    Usage tracking, error handling, debugging tools, real-time logs

-   **:material-cash-multiple: Billing**
    
    Transparent session-based pricing, usage tracking, no hidden fees

</div>

## Ready to Start?

<div class="grid cards" markdown>

-   :material-rocket:{ .lg .middle } **[5-Minute Quickstart](quickstart.md)**

    ---

    Build and deploy your first agent in under 5 minutes

-   :material-lightbulb:{ .lg .middle } **[Core Concepts](concepts.md)**

    ---

    Understand agents, deployment, DataVault, and sessions

-   :material-chef-hat:{ .lg .middle } **[Recipes & Examples](recipes/chatbot.md)**

    ---

    Real-world examples for chatbots, automation, and workflows

</div>

---

!!! quote "The Vision"
    **FlowStack is the Vercel for AI agents.** You build the logic, we handle everything else to make it production-ready. Skip the infrastructure grind — focus on what makes your agent unique.

[Get Started →](quickstart.md){ .md-button .md-button--primary }
