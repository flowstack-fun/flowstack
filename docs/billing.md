# Billing & Usage

FlowStack uses simple, transparent pricing based on sessions. No complex token counting, no surprise bills.

## How Billing Works

### Session-Based Pricing

A **session** is one conversation with your agent, regardless of how many messages are exchanged:

!!! example "What Counts as One Session"
    **Single Session Example:**
    
    - User: "Hello, can you help me?"
    - Agent: "Of course! What do you need help with?"
    - User: "I need to analyze this data..."
    - Agent: "I'll analyze that data for you. Here are the results..."
    - User: "Thanks! Can you also create a chart?"
    - Agent: "Absolutely! Here's your chart..."
    
    **6 messages = 1 session**

### Session Lifecycle

- **Session starts** with the first message from a user
- **Session continues** with follow-up messages in the same conversation  
- **Session ends** after 30 minutes of inactivity
- **New session begins** with the next message after timeout

## Pricing Tiers

<div class="grid cards" markdown>

-   :material-currency-usd-off:{ .lg .middle } **Free Tier**

    ---

    **$0/month**
    
    - 25 sessions/month
    - BYOK required for all providers
    - No managed Bedrock access
    - Community support

-   :material-rocket-launch:{ .lg .middle } **Starter**

    ---

    **$29/month**
    
    - 1,000 sessions/month
    - Managed Bedrock included
    - BYOK optional for cost savings
    - Email support

-   :material-office-building:{ .lg .middle } **Professional**

    ---

    **$99/month**
    
    - 10,000 sessions/month
    - Optimized AI pricing
    - Priority support
    - Advanced analytics

-   :material-domain:{ .lg .middle } **Enterprise**

    ---

    **$499+/month**
    
    - 100,000+ sessions/month
    - Volume pricing discounts
    - Custom infrastructure
    - Dedicated support

</div>

## Understanding Costs

### Managed vs BYOK

FlowStack offers two pricing models:

#### Managed Infrastructure
```python
# Managed Bedrock - included in session pricing
agent = Agent(
    name="managed-agent",
    api_key="fs_...",
    provider="bedrock",  # Managed by FlowStack
    model="claude-3-sonnet"
)
```

**Benefits:**
- ✅ No additional AI costs
- ✅ Optimized performance  
- ✅ Simplified billing
- ✅ Enterprise SLA

#### Bring Your Own Keys (BYOK)
```python
# BYOK - you pay AI provider directly
agent = Agent(
    name="byok-agent",
    api_key="fs_...",
    provider="openai",
    model="gpt-4o",
    byok={"api_key": "sk-your-openai-key"}  # Your key
)
```

**Benefits:**
- ✅ Direct AI provider billing
- ✅ No markup on AI costs
- ✅ Full control over AI spending
- ✅ Access to latest models

### Cost Comparison Examples

#### Simple Chatbot (1,000 sessions/month)

=== "Managed (Starter Plan)"
    
    **FlowStack:** $29/month
    
    **AI Costs:** Included
    
    **Total:** $29/month
    
    ✅ Predictable costs  
    ✅ No usage spikes  
    ✅ Enterprise reliability

=== "BYOK (Free + OpenAI)"
    
    **FlowStack:** $0/month (if under 25 sessions) or $29/month
    
    **OpenAI GPT-4:** ~$75/month (estimated)
    
    **Total:** $75-104/month
    
    ✅ Latest OpenAI models  
    ✅ Direct provider billing  
    ❌ Higher total cost

=== "BYOK (Starter + GPT-3.5)"
    
    **FlowStack:** $29/month
    
    **OpenAI GPT-3.5:** ~$15/month (estimated)
    
    **Total:** $44/month
    
    ✅ Lower AI costs  
    ✅ Good performance  
    ⚠️ Less capable model

#### High-Volume Application (10,000 sessions/month)

=== "Professional Plan"
    
    **FlowStack:** $99/month
    
    **AI Costs:** Included
    
    **Total:** $99/month
    
    ✅ Best value for high volume  
    ✅ Optimized infrastructure  
    ✅ Priority support

=== "BYOK Alternative"
    
    **FlowStack:** $99/month
    
    **AI Provider:** $300-800/month (estimated)
    
    **Total:** $399-899/month
    
    ✅ Access to any model  
    ❌ Much higher costs  
    ❌ Complex billing management

## Usage Tracking

### Check Your Usage

```python
from flowstack import Agent

agent = Agent("my-agent", api_key="fs_...")

# Get current usage
usage = agent.get_usage()

print(f"Sessions used: {usage.sessions_used}")
print(f"Sessions limit: {usage.sessions_limit}")
print(f"Sessions remaining: {usage.sessions_remaining}")
print(f"Usage percentage: {usage.usage_percentage:.1f}%")
print(f"Current charges: ${usage.current_charges:.2f}")
```

### Usage Alerts

```python
# Check if approaching limits
usage = agent.get_usage()

if usage.is_near_limit:
    print("⚠️ Warning: You're using 80%+ of your monthly sessions")
    
if not usage.can_make_requests:
    print("❌ Session limit reached. Please upgrade your plan.")
    
# Get tier information
tier_info = agent.get_tier_info()
print(f"Current tier: {tier_info['current_tier']}")
print(f"Can use managed models: {tier_info['can_use_managed']}")
```

### Usage Patterns

```python
# Track usage over time
@agent.tool
def track_usage_patterns() -> dict:
    """Track and analyze usage patterns"""
    
    usage = agent.get_usage()
    
    # Store usage snapshot
    agent.vault.store('usage_history', {
        'timestamp': datetime.now().isoformat(),
        'sessions_used': usage.sessions_used,
        'sessions_limit': usage.sessions_limit,
        'usage_percentage': usage.usage_percentage,
        'tier': usage.tier
    })
    
    # Get usage history for analysis
    history = agent.vault.query('usage_history', 
        sort=[('timestamp', -1)], 
        limit=30  # Last 30 data points
    )
    
    # Calculate trends
    if len(history) >= 2:
        recent_usage = history[0]['usage_percentage']
        previous_usage = history[1]['usage_percentage']
        trend = recent_usage - previous_usage
    else:
        trend = 0
    
    return {
        'current_usage': usage.usage_percentage,
        'trend': trend,
        'sessions_remaining': usage.sessions_remaining,
        'days_left_in_period': calculate_days_remaining(),
        'projected_usage': project_monthly_usage(history)
    }
```

## Cost Optimization Strategies

### 1. Choose the Right Provider

```python
# Cost optimization based on task complexity
def optimize_provider_for_cost(task: str):
    """Choose provider based on cost and task complexity"""
    
    complexity = analyze_task_complexity(task)
    
    if complexity == "simple":
        # Use cheapest option for simple tasks
        agent.set_provider("openai", byok={"api_key": "sk-..."})
        agent.set_model("gpt-3.5-turbo")  # ~$0.002 per 1K tokens
        
    elif complexity == "medium":
        # Use managed Bedrock for balanced cost/performance
        agent.set_provider("bedrock")  # Included in FlowStack pricing
        agent.set_model("claude-3-sonnet")
        
    else:  # complex
        # Use best model for complex tasks
        agent.set_provider("anthropic", byok={"api_key": "sk-ant-..."})
        agent.set_model("claude-3-opus")  # Most capable, higher cost
```

### 2. Implement Smart Caching

```python
@agent.tool
def cached_expensive_operation(query: str) -> dict:
    """Cache expensive operations to reduce costs"""
    
    # Generate cache key
    cache_key = f"expensive_op_{hash(query)}"
    
    # Check cache first
    cached_result = agent.vault.retrieve('cache', key=cache_key)
    
    if cached_result and not is_expired(cached_result):
        return {
            "result": cached_result['data'],
            "cached": True,
            "cost_saved": True
        }
    
    # Perform expensive operation
    result = expensive_operation(query)
    
    # Cache result for 1 hour
    agent.vault.store('cache', {
        'data': result,
        'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
    }, key=cache_key)
    
    return {
        "result": result,
        "cached": False,
        "cost_saved": False
    }
```

### 3. Batch Similar Requests

```python
@agent.tool
def batch_processing(requests: list) -> dict:
    """Process multiple similar requests in one session"""
    
    results = []
    
    # Process all requests in a single conversation
    batch_prompt = "Process these requests:\n"
    for i, request in enumerate(requests):
        batch_prompt += f"{i+1}. {request}\n"
    
    # Single AI call for multiple requests
    response = agent.chat(batch_prompt)
    
    # Parse batch response
    parsed_results = parse_batch_response(response, len(requests))
    
    return {
        "results": parsed_results,
        "requests_processed": len(requests),
        "sessions_used": 1,  # Only one session for multiple requests
        "cost_efficiency": f"Processed {len(requests)} requests in 1 session"
    }
```

### 4. Monitor and Optimize

```python
@agent.tool
def cost_analysis() -> dict:
    """Analyze costs and suggest optimizations"""
    
    # Get usage data
    usage = agent.get_usage()
    
    # Analyze provider usage patterns
    provider_usage = agent.vault.query('provider_switches', 
        sort=[('timestamp', -1)], 
        limit=100
    )
    
    # Calculate cost breakdown
    managed_sessions = len([p for p in provider_usage if p.get('provider') == 'bedrock'])
    byok_sessions = len(provider_usage) - managed_sessions
    
    recommendations = []
    
    # Recommend based on usage patterns
    if byok_sessions > managed_sessions and usage.tier in ['starter', 'professional']:
        recommendations.append({
            'type': 'cost_reduction',
            'message': 'You use BYOK frequently. Consider Professional plan for better managed pricing.',
            'potential_savings': calculate_managed_savings(byok_sessions)
        })
    
    if usage.usage_percentage < 50 and usage.tier != 'free':
        recommendations.append({
            'type': 'plan_optimization',
            'message': 'You use less than 50% of your sessions. Consider downgrading.',
            'potential_savings': calculate_downgrade_savings(usage.tier)
        })
    
    return {
        'current_tier': usage.tier,
        'usage_percentage': usage.usage_percentage,
        'managed_sessions': managed_sessions,
        'byok_sessions': byok_sessions,
        'recommendations': recommendations,
        'monthly_cost_estimate': estimate_monthly_cost(usage)
    }
```

## Billing FAQ

### When are sessions counted?

Sessions are counted when your agent processes a message, not when tools are called or data is stored.

```python
# This counts as 1 session
response = agent.chat("Hello, help me with a task")

# Even if the agent calls multiple tools
@agent.tool  
def tool1(): pass

@agent.tool
def tool2(): pass

# And accesses DataVault multiple times
agent.vault.store('data', {...})
agent.vault.retrieve('data', key='...')
```

### How do conversations work?

A conversation continues until there's 30 minutes of inactivity:

```python
# Session 1 starts
agent.chat("Hello")  

# 10 minutes later - still session 1
agent.chat("Can you help me?")

# 5 minutes later - still session 1  
agent.chat("Thanks!")

# 35 minutes later - session 2 starts
agent.chat("New question")
```

### What happens when I exceed limits?

When you reach your session limit:

1. **Graceful degradation** - Existing conversations can finish
2. **New sessions blocked** - New conversations return quota exceeded error
3. **Tools still work** - Agent tools and DataVault remain accessible
4. **Automatic reset** - Limits reset at the start of your next billing cycle

```python
try:
    response = agent.chat("Hello")
except QuotaExceededError as e:
    print(f"Quota exceeded: {e}")
    print(f"Current usage: {e.details['current_usage']}")
    print(f"Limit: {e.details['limit']}")
    print("Please upgrade your plan or wait for reset.")
```

### How do refunds work?

- **Unused sessions don't roll over** - Use them or lose them each month
- **Downgrades apply next cycle** - Immediate downgrades aren't prorated  
- **Upgrades are immediate** - Extra sessions available instantly
- **Cancellations effective at period end** - Service continues until renewal date

### Can I monitor costs in real-time?

Yes! FlowStack provides real-time usage tracking:

```python
# Real-time usage monitoring
usage = agent.get_usage()
print(f"Sessions used today: {usage.sessions_used}")
print(f"Estimated monthly cost: ${estimate_monthly_cost(usage)}")

# Set up usage alerts
if usage.usage_percentage > 80:
    send_slack_alert(f"⚠️ Usage at {usage.usage_percentage}%")
```

## Managing Costs

### Set Usage Alerts

```python
@agent.tool
def setup_usage_alerts(alert_thresholds: list = [75, 90, 95]) -> dict:
    """Set up automated usage alerts"""
    
    usage = agent.get_usage()
    
    alerts_triggered = []
    
    for threshold in alert_thresholds:
        if usage.usage_percentage >= threshold:
            alert = {
                'threshold': threshold,
                'current_usage': usage.usage_percentage,
                'sessions_remaining': usage.sessions_remaining,
                'message': f'Usage alert: {usage.usage_percentage}% of monthly limit reached'
            }
            alerts_triggered.append(alert)
            
            # Send alert (integrate with your notification system)
            send_usage_alert(alert)
    
    return {
        'current_usage': usage.usage_percentage,
        'alerts_triggered': alerts_triggered,
        'next_reset': get_next_billing_cycle_date()
    }
```

### Budget Management

```python
@agent.tool
def budget_guard(max_monthly_cost: float) -> dict:
    """Prevent exceeding monthly budget"""
    
    usage = agent.get_usage()
    estimated_cost = estimate_monthly_cost(usage)
    
    if estimated_cost > max_monthly_cost:
        return {
            'error': 'Budget exceeded',
            'estimated_monthly_cost': estimated_cost,
            'budget_limit': max_monthly_cost,
            'recommendation': 'Consider optimizing usage or increasing budget'
        }
    
    return {
        'budget_status': 'within_limits',
        'estimated_monthly_cost': estimated_cost,
        'budget_limit': max_monthly_cost,
        'budget_remaining': max_monthly_cost - estimated_cost
    }
```

---

Questions about billing? Check our [API reference](api-reference.md) for usage tracking methods or see [production tips](production.md) for cost optimization strategies.