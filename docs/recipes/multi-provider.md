# Recipe: Multi-Provider Setup

Switch between AI providers to optimize costs, capabilities, and performance for different use cases.

!!! tip "Perfect for Cost Optimization"
    This recipe shows how to use different AI providers strategically - managed Bedrock for reliability, your own OpenAI for cost control, and Anthropic for specific capabilities.

## What You'll Build

A smart agent that can:

- 🔄 **Switch providers dynamically** based on task requirements
- 💰 **Optimize costs** by using the right provider for each job
- 🚀 **Maximize capabilities** by leveraging each provider's strengths
- 📊 **Track usage and costs** across all providers
- 🔧 **Handle provider failures** with automatic fallbacks
- ⚖️ **Load balance** across multiple providers

## The Complete Code

```python title="multi_provider_agent.py"
from flowstack import Agent, tool, DataVault
from datetime import datetime, timedelta
import json

# Initialize the multi-provider agent with default provider
agent = Agent(
    name="smart-multi-provider",
    api_key="fs_your_api_key_here",
    provider="bedrock",  # Default to managed Bedrock
    model="claude-3-5-sonnet-20241022",
    instructions="""You are a smart assistant that can use multiple AI providers optimally. 
    You should:
    - Choose the best provider for each task based on requirements
    - Consider cost, speed, and capability trade-offs
    - Track usage across providers for optimization
    - Handle provider failures gracefully with fallbacks
    """
)

# Initialize DataVault for persistent storage
vault = DataVault(api_key="fs_your_api_key_here")

# Define provider configurations
PROVIDER_CONFIGS = {
    'bedrock_managed': {
        'provider': 'bedrock',
        'model': 'claude-3-5-sonnet-20241022',
        'byok': None,  # Managed by FlowStack
        'cost_per_session': 'managed',  # Included in FlowStack pricing
        'strengths': ['reliability', 'no_setup', 'managed_billing'],
        'best_for': ['production', 'customer_facing', 'critical_tasks']
    },
    'openai_byok': {
        'provider': 'openai',
        'model': 'gpt-4o',
        'byok': {'api_key': 'sk-your-openai-key'},  # Your own key
        'cost_per_session': 'variable',  # Direct OpenAI billing
        'strengths': ['cost_control', 'latest_models', 'function_calling'],
        'best_for': ['development', 'high_volume', 'cost_optimization']
    },
    'anthropic_byok': {
        'provider': 'anthropic',
        'model': 'claude-3-opus-20240229',
        'byok': {'api_key': 'sk-ant-your-anthropic-key'},
        'cost_per_session': 'variable',
        'strengths': ['reasoning', 'safety', 'long_context'],
        'best_for': ['complex_analysis', 'research', 'content_generation']
    },
    'openai_fast': {
        'provider': 'openai',
        'model': 'gpt-3.5-turbo',
        'byok': {'api_key': 'sk-your-openai-key'},
        'cost_per_session': 'low',
        'strengths': ['speed', 'low_cost', 'good_performance'],
        'best_for': ['simple_tasks', 'high_frequency', 'testing']
    }
}

# Tool 1: Smart Provider Selection
@tool
def select_optimal_provider(task_description: str, requirements: dict = None) -> dict:
    """Intelligently select the best provider for a given task"""
    
    requirements = requirements or {}
    
    # Analyze task requirements
    task_analysis = analyze_task_requirements(task_description, requirements)
    
    # Score each provider for this task
    provider_scores = {}
    for provider_name, config in PROVIDER_CONFIGS.items():
        score = calculate_provider_score(task_analysis, config)
        provider_scores[provider_name] = score
    
    # Select best provider
    best_provider = max(provider_scores.items(), key=lambda x: x[1])
    selected_config = PROVIDER_CONFIGS[best_provider[0]]
    
    # Switch to selected provider
    switch_result = switch_provider(best_provider[0])
    
    return {
        'task_description': task_description,
        'selected_provider': best_provider[0],
        'provider_config': selected_config,
        'selection_score': best_provider[1],
        'all_scores': provider_scores,
        'task_analysis': task_analysis,
        'switch_successful': switch_result['success']
    }

def analyze_task_requirements(task_description: str, requirements: dict) -> dict:
    """Analyze task to determine requirements"""
    
    task_lower = task_description.lower()
    analysis = {
        'complexity': 'medium',
        'speed_priority': 'medium',
        'cost_priority': 'medium',
        'reliability_priority': 'high',
        'task_type': 'general'
    }
    
    # Complexity analysis
    complex_indicators = ['analyze', 'research', 'complex', 'detailed', 'comprehensive']
    simple_indicators = ['simple', 'quick', 'basic', 'summarize']
    
    if any(indicator in task_lower for indicator in complex_indicators):
        analysis['complexity'] = 'high'
    elif any(indicator in task_lower for indicator in simple_indicators):
        analysis['complexity'] = 'low'
    
    # Speed priority analysis
    if any(word in task_lower for word in ['urgent', 'quick', 'fast', 'immediate']):
        analysis['speed_priority'] = 'high'
    elif any(word in task_lower for word in ['detailed', 'thorough', 'comprehensive']):
        analysis['speed_priority'] = 'low'
    
    # Cost priority from requirements
    if requirements.get('cost_sensitive', False):
        analysis['cost_priority'] = 'high'
    elif requirements.get('premium_quality', False):
        analysis['cost_priority'] = 'low'
    
    # Task type classification
    if any(word in task_lower for word in ['code', 'programming', 'function']):
        analysis['task_type'] = 'coding'
    elif any(word in task_lower for word in ['write', 'content', 'article', 'blog']):
        analysis['task_type'] = 'content_creation'
    elif any(word in task_lower for word in ['analyze', 'research', 'study']):
        analysis['task_type'] = 'analysis'
    elif any(word in task_lower for word in ['chat', 'conversation', 'help']):
        analysis['task_type'] = 'conversation'
    
    return analysis

def calculate_provider_score(task_analysis: dict, provider_config: dict) -> float:
    """Calculate how well a provider matches task requirements"""
    
    score = 0.0
    
    # Base score for all providers
    score += 50
    
    # Complexity matching
    if task_analysis['complexity'] == 'high':
        if 'reasoning' in provider_config['strengths']:
            score += 20
        if provider_config['model'] in ['claude-3-opus-20240229', 'gpt-4o']:
            score += 15
    elif task_analysis['complexity'] == 'low':
        if 'speed' in provider_config['strengths']:
            score += 15
        if provider_config['model'] == 'gpt-3.5-turbo':
            score += 10
    
    # Cost considerations
    if task_analysis['cost_priority'] == 'high':
        if provider_config['cost_per_session'] == 'low':
            score += 20
        elif provider_config['cost_per_session'] == 'variable':
            score += 10
        elif provider_config['cost_per_session'] == 'managed':
            score -= 5
    
    # Speed considerations
    if task_analysis['speed_priority'] == 'high':
        if 'speed' in provider_config['strengths']:
            score += 15
        if provider_config['model'] == 'gpt-3.5-turbo':
            score += 10
    
    # Reliability considerations
    if task_analysis['reliability_priority'] == 'high':
        if 'reliability' in provider_config['strengths']:
            score += 15
        if provider_config['provider'] == Providers.BEDROCK:
            score += 10
    
    # Task type specific bonuses
    task_type = task_analysis['task_type']
    if task_type == 'coding' and 'function_calling' in provider_config['strengths']:
        score += 15
    elif task_type == 'content_creation' and 'long_context' in provider_config['strengths']:
        score += 15
    elif task_type == 'analysis' and 'reasoning' in provider_config['strengths']:
        score += 15
    
    return score

@tool
def switch_provider(provider_name: str) -> dict:
    """Switch to a different provider configuration"""
    
    if provider_name not in PROVIDER_CONFIGS:
        return {
            'success': False,
            'error': f'Unknown provider configuration: {provider_name}',
            'available_providers': list(PROVIDER_CONFIGS.keys())
        }
    
    config = PROVIDER_CONFIGS[provider_name]
    
    try:
        # Switch the agent to the new provider
        agent.set_provider(
            provider=config['provider'],
            byok=config['byok']
        )
        agent.set_model(config['model'])
        
        # Log the switch
        switch_log = {
            'switched_to': provider_name,
            'provider': config['provider'],
            'model': config['model'],
            'timestamp': datetime.now().isoformat(),
            'has_byok': config['byok'] is not None
        }
        
        vault.store('provider_switches', switch_log)
        
        return {
            'success': True,
            'switched_to': provider_name,
            'provider': config['provider'],
            'model': config['model'],
            'strengths': config['strengths'],
            'cost_model': config['cost_per_session']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'attempted_provider': provider_name
        }

# Tool 2: Cost Tracking and Optimization
@tool
def track_provider_usage(provider_name: str, task_description: str, session_cost: float = None) -> dict:
    """Track usage and costs across providers"""
    
    usage_record = {
        'provider_name': provider_name,
        'provider': PROVIDER_CONFIGS[provider_name]['provider'],
        'model': PROVIDER_CONFIGS[provider_name]['model'],
        'task_description': task_description,
        'session_cost': session_cost,
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().date().isoformat()
    }
    
    vault.store('provider_usage', usage_record)
    
    # Calculate daily and monthly usage
    today = datetime.now().date().isoformat()
    month_start = datetime.now().replace(day=1).date().isoformat()
    
    daily_usage = vault.query('provider_usage', {
        'date': today,
        'provider_name': provider_name
    })
    
    monthly_usage = vault.query('provider_usage', {
        'date': {'$gte': month_start},
        'provider_name': provider_name
    })
    
    return {
        'recorded': True,
        'provider_name': provider_name,
        'task_description': task_description,
        'daily_sessions': len(daily_usage),
        'monthly_sessions': len(monthly_usage),
        'estimated_monthly_cost': estimate_monthly_cost(monthly_usage, provider_name)
    }

def estimate_monthly_cost(usage_records: list, provider_name: str) -> dict:
    """Estimate monthly cost for a provider"""
    
    config = PROVIDER_CONFIGS[provider_name]
    
    if config['cost_per_session'] == 'managed':
        # Managed pricing - included in FlowStack subscription
        return {
            'type': 'managed',
            'sessions': len(usage_records),
            'estimated_cost': 'included_in_subscription',
            'note': 'Covered by FlowStack session pricing'
        }
    
    elif config['cost_per_session'] == 'low':
        # Estimate for GPT-3.5-turbo or similar
        estimated_cost = len(usage_records) * 0.05  # $0.05 per session estimate
        return {
            'type': 'byok_low_cost',
            'sessions': len(usage_records),
            'estimated_cost': round(estimated_cost, 2),
            'cost_per_session': 0.05
        }
    
    elif config['cost_per_session'] == 'variable':
        # Higher-end models - estimate based on model
        if 'gpt-4' in config['model']:
            cost_per_session = 0.25
        elif 'claude-3-opus' in config['model']:
            cost_per_session = 0.30
        else:
            cost_per_session = 0.15
        
        estimated_cost = len(usage_records) * cost_per_session
        return {
            'type': 'byok_variable',
            'sessions': len(usage_records),
            'estimated_cost': round(estimated_cost, 2),
            'cost_per_session': cost_per_session
        }
    
    return {
        'type': 'unknown',
        'sessions': len(usage_records),
        'estimated_cost': 'unable_to_estimate'
    }

@tool
def get_cost_optimization_recommendations() -> dict:
    """Analyze usage patterns and recommend cost optimizations"""
    
    # Get usage from last 30 days
    thirty_days_ago = (datetime.now() - timedelta(days=30)).date().isoformat()
    
    all_usage = vault.query('provider_usage', {
        'date': {'$gte': thirty_days_ago}
    })
    
    if not all_usage:
        return {
            'message': 'No usage data available for optimization analysis',
            'recommendations': []
        }
    
    # Analyze usage by provider
    provider_usage = {}
    for record in all_usage:
        provider = record['provider_name']
        if provider not in provider_usage:
            provider_usage[provider] = []
        provider_usage[provider].append(record)
    
    recommendations = []
    
    # Check for high-cost provider overuse
    for provider_name, usage_records in provider_usage.items():
        config = PROVIDER_CONFIGS[provider_name]
        
        if len(usage_records) > 100 and config['cost_per_session'] == 'variable':
            # High usage of expensive provider
            recommendations.append({
                'type': 'cost_reduction',
                'priority': 'high',
                'message': f'High usage of {provider_name} ({len(usage_records)} sessions). Consider using cheaper alternatives for simple tasks.',
                'suggestion': 'Use gpt-3.5-turbo for simple tasks, reserve expensive models for complex work',
                'potential_savings': estimate_potential_savings(usage_records, provider_name)
            })
        
        if config['cost_per_session'] == 'managed' and len(usage_records) < 10:
            # Low usage of managed provider
            recommendations.append({
                'type': 'efficiency',
                'priority': 'medium',
                'message': f'Low usage of managed {provider_name} ({len(usage_records)} sessions). You\'re paying for FlowStack sessions anyway.',
                'suggestion': 'Consider using managed Bedrock more for reliability and simplicity'
            })
    
    # Check for task-provider mismatches
    task_analysis = analyze_task_provider_matching(all_usage)
    if task_analysis['mismatches']:
        recommendations.append({
            'type': 'optimization',
            'priority': 'medium',
            'message': 'Some tasks may be using suboptimal providers',
            'mismatches': task_analysis['mismatches'][:3],  # Top 3 mismatches
            'suggestion': 'Use automatic provider selection for better optimization'
        })
    
    return {
        'analysis_period_days': 30,
        'total_sessions': len(all_usage),
        'providers_used': list(provider_usage.keys()),
        'recommendations': recommendations,
        'monthly_cost_estimate': calculate_total_monthly_cost(provider_usage)
    }

def estimate_potential_savings(usage_records: list, current_provider: str) -> dict:
    """Estimate potential savings by switching providers for some tasks"""
    
    # Simulate switching 50% of simple tasks to cheaper provider
    simple_tasks = 0
    for record in usage_records:
        task = record.get('task_description', '').lower()
        if any(word in task for word in ['simple', 'quick', 'basic', 'summarize']):
            simple_tasks += 1
    
    switchable_sessions = simple_tasks // 2  # Conservative estimate
    
    current_config = PROVIDER_CONFIGS[current_provider]
    if current_config['cost_per_session'] == 'variable':
        current_cost_per_session = 0.25 if 'gpt-4' in current_config['model'] else 0.15
        cheap_cost_per_session = 0.05  # GPT-3.5-turbo estimate
        
        monthly_savings = switchable_sessions * (current_cost_per_session - cheap_cost_per_session)
        
        return {
            'switchable_sessions': switchable_sessions,
            'monthly_savings': round(monthly_savings, 2),
            'annual_savings': round(monthly_savings * 12, 2)
        }
    
    return {'monthly_savings': 0, 'reason': 'already_using_managed_or_cheap_provider'}

def analyze_task_provider_matching(usage_records: list) -> dict:
    """Analyze if tasks are using optimal providers"""
    
    mismatches = []
    
    for record in usage_records:
        task = record.get('task_description', '')
        provider_name = record['provider_name']
        
        # Analyze what would be optimal for this task
        task_analysis = analyze_task_requirements(task, {})
        optimal_provider = None
        best_score = 0
        
        for p_name, config in PROVIDER_CONFIGS.items():
            score = calculate_provider_score(task_analysis, config)
            if score > best_score:
                best_score = score
                optimal_provider = p_name
        
        # Check if current provider is significantly suboptimal
        current_score = calculate_provider_score(task_analysis, PROVIDER_CONFIGS[provider_name])
        
        if optimal_provider != provider_name and (best_score - current_score) > 15:
            mismatches.append({
                'task': task[:100],  # Truncate long tasks
                'current_provider': provider_name,
                'optimal_provider': optimal_provider,
                'score_difference': round(best_score - current_score, 1)
            })
    
    return {
        'total_tasks_analyzed': len(usage_records),
        'mismatches_found': len(mismatches),
        'mismatches': sorted(mismatches, key=lambda x: x['score_difference'], reverse=True)
    }

# Tool 3: Provider Health and Fallback
@tool
def check_provider_health() -> dict:
    """Check health of all configured providers"""
    
    health_status = {}
    
    for provider_name, config in PROVIDER_CONFIGS.items():
        try:
            # Temporarily switch to provider and test
            original_provider = agent.provider
            original_model = agent.model
            
            agent.set_provider(config['provider'], config['byok'])
            agent.set_model(config['model'])
            
            # Quick health check
            start_time = datetime.now()
            test_response = agent.chat("Test message - please respond with 'OK'")
            response_time = (datetime.now() - start_time).total_seconds()
            
            health_status[provider_name] = {
                'status': 'healthy',
                'response_time_seconds': round(response_time, 2),
                'test_successful': 'OK' in test_response or 'ok' in test_response.lower(),
                'last_checked': datetime.now().isoformat()
            }
            
            # Restore original provider
            agent.set_provider(original_provider)
            agent.set_model(original_model)
            
        except Exception as e:
            health_status[provider_name] = {
                'status': 'unhealthy',
                'error': str(e),
                'last_checked': datetime.now().isoformat()
            }
    
    # Store health check results
    health_record = {
        'timestamp': datetime.now().isoformat(),
        'provider_health': health_status,
        'healthy_providers': [p for p, status in health_status.items() if status['status'] == 'healthy'],
        'unhealthy_providers': [p for p, status in health_status.items() if status['status'] == 'unhealthy']
    }
    
    vault.store('provider_health_checks', health_record)
    
    return health_record

@tool
def execute_with_fallback(task: str, preferred_provider: str = None, max_retries: int = 3) -> dict:
    """Execute a task with automatic provider fallback on failure"""
    
    # Determine provider order
    if preferred_provider and preferred_provider in PROVIDER_CONFIGS:
        provider_order = [preferred_provider]
        # Add other providers as fallbacks
        provider_order.extend([p for p in PROVIDER_CONFIGS.keys() if p != preferred_provider])
    else:
        # Use all providers in order of reliability
        provider_order = ['bedrock_managed', 'openai_byok', 'anthropic_byok', 'openai_fast']
    
    attempts = []
    
    for attempt, provider_name in enumerate(provider_order):
        if attempt >= max_retries:
            break
        
        try:
            # Switch to provider
            switch_result = switch_provider(provider_name)
            
            if not switch_result['success']:
                attempts.append({
                    'provider': provider_name,
                    'attempt': attempt + 1,
                    'result': 'failed_to_switch',
                    'error': switch_result.get('error')
                })
                continue
            
            # Execute task
            start_time = datetime.now()
            response = agent.chat(task)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Success!
            attempts.append({
                'provider': provider_name,
                'attempt': attempt + 1,
                'result': 'success',
                'execution_time_seconds': round(execution_time, 2)
            })
            
            # Track successful usage
            track_provider_usage(provider_name, task)
            
            return {
                'success': True,
                'response': response,
                'provider_used': provider_name,
                'attempts': attempts,
                'total_attempts': len(attempts)
            }
            
        except Exception as e:
            attempts.append({
                'provider': provider_name,
                'attempt': attempt + 1,
                'result': 'failed',
                'error': str(e)
            })
            continue
    
    # All providers failed
    return {
        'success': False,
        'error': 'All providers failed',
        'attempts': attempts,
        'total_attempts': len(attempts)
    }

# Tool 4: Load Balancing
@tool
def distribute_load_across_providers(tasks: list, strategy: str = 'round_robin') -> dict:
    """Distribute multiple tasks across providers for load balancing"""
    
    if strategy == 'round_robin':
        # Simple round-robin distribution
        provider_names = list(PROVIDER_CONFIGS.keys())
        task_assignments = []
        
        for i, task in enumerate(tasks):
            provider = provider_names[i % len(provider_names)]
            task_assignments.append({
                'task_id': i,
                'task': task,
                'assigned_provider': provider
            })
    
    elif strategy == 'optimal':
        # Assign each task to its optimal provider
        task_assignments = []
        
        for i, task in enumerate(tasks):
            optimal_result = select_optimal_provider(task)
            task_assignments.append({
                'task_id': i,
                'task': task,
                'assigned_provider': optimal_result['selected_provider'],
                'selection_score': optimal_result['selection_score']
            })
    
    elif strategy == 'cost_optimized':
        # Prioritize cheaper providers
        cheap_providers = [p for p, config in PROVIDER_CONFIGS.items() 
                          if config['cost_per_session'] in ['low', 'managed']]
        expensive_providers = [p for p, config in PROVIDER_CONFIGS.items() 
                              if config['cost_per_session'] == 'variable']
        
        task_assignments = []
        
        for i, task in enumerate(tasks):
            # Use cheap providers for simple tasks, expensive for complex
            task_analysis = analyze_task_requirements(task, {})
            
            if task_analysis['complexity'] == 'low':
                provider = cheap_providers[i % len(cheap_providers)]
            else:
                provider = expensive_providers[i % len(expensive_providers)]
            
            task_assignments.append({
                'task_id': i,
                'task': task,
                'assigned_provider': provider,
                'reason': f"task_complexity_{task_analysis['complexity']}"
            })
    
    return {
        'strategy': strategy,
        'total_tasks': len(tasks),
        'task_assignments': task_assignments,
        'provider_distribution': calculate_provider_distribution(task_assignments)
    }

def calculate_provider_distribution(task_assignments: list) -> dict:
    """Calculate how tasks are distributed across providers"""
    
    distribution = {}
    for assignment in task_assignments:
        provider = assignment['assigned_provider']
        distribution[provider] = distribution.get(provider, 0) + 1
    
    return distribution

# Test the multi-provider agent
def test_multi_provider():
    """Test the multi-provider agent with different scenarios"""
    print("🔄 Testing Multi-Provider Agent")
    print("=" * 50)
    
    # Test 1: Provider selection for different task types
    print("\n1. Testing smart provider selection...")
    
    test_tasks = [
        "Write a simple summary of this text",
        "Analyze the complex implications of quantum computing on cryptography",
        "Quick help with basic Python syntax",
        "Detailed research report on climate change impacts"
    ]
    
    for task in test_tasks:
        response = agent.chat(f"Select optimal provider for: {task}")
        print(f"Task: {task[:50]}...")
        print(f"Selection: {response}")
        print()
    
    # Test 2: Cost tracking
    print("\n2. Testing cost tracking...")
    response = agent.chat("Track usage for openai_fast provider for the task: basic math calculation")
    print(f"Cost Tracking: {response}")
    
    # Test 3: Health check
    print("\n3. Testing provider health...")
    response = agent.chat("Check the health of all providers")
    print(f"Health Check: {response}")
    
    # Test 4: Fallback execution
    print("\n4. Testing fallback execution...")
    response = agent.chat("Execute with fallback: What is 2+2? (prefer anthropic_byok)")
    print(f"Fallback Execution: {response}")
    
    print("\n✅ Multi-provider testing complete!")

# Deploy the multi-provider agent
def deploy_multi_provider():
    """Deploy the multi-provider agent to production"""
    print("\n🚀 Deploying multi-provider agent...")
    
    result = agent.deploy()
    
    print(f"✅ Multi-provider agent deployed!")
    print(f"Deployment ID: {result['deployment_id']}")
    print(f"Namespace: {result['namespace']}")
    print(f"API Endpoint: https://api.flowstack.fun/agents/{result['namespace']}/invoke")
    
    print("\n🔄 Your agent now supports:")
    print("• Automatic provider selection based on task requirements")
    print("• Cost tracking and optimization recommendations")
    print("• Provider health monitoring and fallback")
    print("• Load balancing across multiple providers")
    print("• Real-time provider switching")
    
    return result

if __name__ == "__main__":
    # Run tests
    test_multi_provider()
    
    # Deploy
    deploy_choice = input("\nDeploy multi-provider agent? (y/N): ")
    if deploy_choice.lower() == 'y':
        deploy_multi_provider()
```

## Provider Strategy Examples

### Cost-Optimized Setup

```python title="cost_optimized_config.py"
# Configuration optimized for minimal costs
COST_OPTIMIZED_CONFIGS = {
    'ultra_cheap': {
        'provider': Providers.OPENAI,
        'model': 'gpt-3.5-turbo',
        'byok': {'api_key': 'sk-your-openai-key'},
        'use_for': ['simple_tasks', 'high_volume', 'testing']
    },
    'balanced': {
        'provider': Providers.BEDROCK,
        'model': Models.CLAUDE_35_HAIKU,  # Fastest/cheapest Claude
        'byok': None,  # Managed
        'use_for': ['production', 'customer_facing']
    },
    'premium_only_when_needed': {
        'provider': Providers.ANTHROPIC,
        'model': 'claude-3-opus-20240229',
        'byok': {'api_key': 'sk-ant-your-key'},
        'use_for': ['complex_analysis', 'critical_decisions']
    }
}

def setup_cost_optimized_agent():
    """Setup agent with cost optimization as primary goal"""
    
    agent = Agent(
        name="cost-optimized-assistant",
        api_key="fs_your_api_key",
        provider=Providers.OPENAI,  # Start with cheapest
        model="gpt-3.5-turbo",
        byok={'api_key': 'sk-your-openai-key'}
    )
    
    @tool
    def smart_cost_routing(task: str, max_cost_per_session: float = 0.10):
        """Route tasks based on cost constraints"""
        
        # Estimate task complexity
        complexity = estimate_task_complexity(task)
        
        if complexity == 'simple' and max_cost_per_session >= 0.05:
            return switch_to_provider('ultra_cheap')
        elif complexity == 'medium' and max_cost_per_session >= 0.15:
            return switch_to_provider('balanced')
        elif complexity == 'complex' and max_cost_per_session >= 0.30:
            return switch_to_provider('premium_only_when_needed')
        else:
            return {'error': 'Task too expensive for budget', 'max_budget': max_cost_per_session}
    
    return agent
```

### Performance-Optimized Setup

```python title="performance_optimized_config.py"
# Configuration optimized for speed and reliability
PERFORMANCE_CONFIGS = {
    'ultra_fast': {
        'provider': Providers.OPENAI,
        'model': 'gpt-3.5-turbo',
        'byok': {'api_key': 'sk-your-openai-key'},
        'expected_response_time': 2.0,  # seconds
        'use_for': ['real_time', 'chat', 'quick_responses']
    },
    'balanced_performance': {
        'provider': Providers.BEDROCK,
        'model': Models.CLAUDE_35_SONNET,
        'byok': None,
        'expected_response_time': 4.0,
        'use_for': ['production', 'balanced_tasks']
    },
    'high_quality': {
        'provider': Providers.ANTHROPIC,
        'model': 'claude-3-opus-20240229',
        'byok': {'api_key': 'sk-ant-your-key'},
        'expected_response_time': 8.0,
        'use_for': ['quality_critical', 'complex_reasoning']
    }
}

@tool
def performance_based_routing(task: str, max_response_time: float = 5.0):
    """Route based on performance requirements"""
    
    # Select fastest provider that meets quality needs
    task_quality_needs = assess_quality_requirements(task)
    
    suitable_providers = []
    for name, config in PERFORMANCE_CONFIGS.items():
        if (config['expected_response_time'] <= max_response_time and
            meets_quality_threshold(task_quality_needs, config)):
            suitable_providers.append((name, config))
    
    if suitable_providers:
        # Choose fastest suitable provider
        best_provider = min(suitable_providers, key=lambda x: x[1]['expected_response_time'])
        return switch_to_provider(best_provider[0])
    else:
        return {'error': 'No provider meets performance requirements'}
```

### Capability-Optimized Setup

```python title="capability_optimized_config.py"
# Configuration optimized for specific capabilities
CAPABILITY_CONFIGS = {
    'code_specialist': {
        'provider': Providers.OPENAI,
        'model': 'gpt-4o',
        'byok': {'api_key': 'sk-your-openai-key'},
        'capabilities': ['function_calling', 'code_generation', 'debugging'],
        'use_for': ['programming', 'api_integration', 'technical_tasks']
    },
    'reasoning_expert': {
        'provider': Providers.ANTHROPIC,
        'model': 'claude-3-opus-20240229',
        'byok': {'api_key': 'sk-ant-your-key'},
        'capabilities': ['deep_reasoning', 'analysis', 'research', 'long_context'],
        'use_for': ['research', 'analysis', 'complex_problem_solving']
    },
    'reliable_workhorse': {
        'provider': Providers.BEDROCK,
        'model': Models.CLAUDE_35_SONNET,
        'byok': None,
        'capabilities': ['reliability', 'consistency', 'safety'],
        'use_for': ['production', 'customer_facing', 'business_critical']
    }
}

@tool
def capability_based_routing(task: str, required_capabilities: list):
    """Route based on required capabilities"""
    
    best_match = None
    best_score = 0
    
    for name, config in CAPABILITY_CONFIGS.items():
        # Calculate capability match score
        matched_caps = set(required_capabilities) & set(config['capabilities'])
        score = len(matched_caps) / len(required_capabilities)
        
        if score > best_score:
            best_score = score
            best_match = name
    
    if best_match and best_score >= 0.5:  # At least 50% capability match
        return switch_to_provider(best_match)
    else:
        return {'error': 'No provider has required capabilities', 'required': required_capabilities}
```

## Monitoring and Analytics

### Usage Dashboard

```python
@tool
def get_multi_provider_dashboard(days: int = 7) -> dict:
    """Get comprehensive dashboard of multi-provider usage"""
    
    cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
    
    # Get all usage data
    usage_data = vault.query('provider_usage', {
        'date': {'$gte': cutoff_date}
    })
    
    # Get provider switches
    switches = vault.query('provider_switches', {
        'timestamp': {'$gte': cutoff_date + 'T00:00:00'}
    })
    
    # Get health checks
    health_checks = vault.query('provider_health_checks', {
        'timestamp': {'$gte': cutoff_date + 'T00:00:00'}
    })
    
    # Calculate metrics
    provider_stats = {}
    for record in usage_data:
        provider = record['provider_name']
        if provider not in provider_stats:
            provider_stats[provider] = {
                'session_count': 0,
                'total_cost_estimate': 0,
                'avg_response_time': 0,
                'success_rate': 100
            }
        provider_stats[provider]['session_count'] += 1
    
    # Calculate cost estimates
    for provider, stats in provider_stats.items():
        cost_estimate = estimate_monthly_cost(
            [r for r in usage_data if r['provider_name'] == provider],
            provider
        )
        stats['cost_estimate'] = cost_estimate
    
    return {
        'period_days': days,
        'total_sessions': len(usage_data),
        'providers_used': len(provider_stats),
        'provider_stats': provider_stats,
        'total_switches': len(switches),
        'health_checks_performed': len(health_checks),
        'cost_optimization_score': calculate_optimization_score(usage_data)
    }

def calculate_optimization_score(usage_data: list) -> float:
    """Calculate how well the system is optimized (0-100)"""
    
    if not usage_data:
        return 0
    
    score = 50  # Base score
    
    # Check for appropriate provider usage
    task_provider_matches = 0
    total_tasks = len(usage_data)
    
    for record in usage_data:
        task = record.get('task_description', '')
        provider = record['provider_name']
        
        # Simple heuristic: check if provider choice makes sense
        task_analysis = analyze_task_requirements(task, {})
        
        if task_analysis['complexity'] == 'low' and 'fast' in PROVIDER_CONFIGS[provider]['strengths']:
            task_provider_matches += 1
        elif task_analysis['complexity'] == 'high' and 'reasoning' in PROVIDER_CONFIGS[provider]['strengths']:
            task_provider_matches += 1
        elif task_analysis['complexity'] == 'medium':
            task_provider_matches += 0.5
    
    # Adjust score based on matching
    match_rate = task_provider_matches / total_tasks
    score += (match_rate * 50)  # Up to 50 points for good matching
    
    return min(round(score, 1), 100)
```

## Next Steps

<div class="grid cards" markdown>

-   :material-memory:{ .lg .middle } **[Stateful Agent](stateful-agent.md)**

    ---

    Combine multi-provider capabilities with learning and memory

-   :material-robot-excited:{ .lg .middle } **[Chatbot Agent](chatbot.md)**

    ---

    Build chatbots that can switch providers based on conversation needs

-   :material-cog-transfer:{ .lg .middle } **[Automation Agent](automation-agent.md)**

    ---

    Create workflows that use different providers for different steps

</div>

---

!!! success "You Built a Multi-Provider System!"
    You've created an intelligent system that optimally routes tasks across multiple AI providers, balancing cost, performance, and capabilities. This gives you the flexibility to optimize for any scenario.

Your multi-provider agent now has:
✅ **Smart Routing** - Automatically selects the best provider for each task  
✅ **Cost Optimization** - Minimizes expenses while maintaining quality  
✅ **Fallback Handling** - Automatically switches providers on failures  
✅ **Load Balancing** - Distributes work across multiple providers  
✅ **Health Monitoring** - Tracks provider performance and availability  
✅ **Usage Analytics** - Detailed insights into costs and optimization opportunities  