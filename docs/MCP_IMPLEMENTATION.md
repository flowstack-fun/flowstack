# FlowStack MCP Implementation Guide

## Overview

FlowStack now supports **multi-language tools** through MCP (Model Context Protocol) integration, enabling developers to write tools in both **Python** and **JavaScript** within the same agent.

## What's New

### 🚀 Multi-Language Support
- **Python tools**: Continue using your existing Python functions
- **JavaScript tools**: Write tools in JavaScript/TypeScript
- **Mixed workflows**: Combine tools from both languages in conversations

### ⚡ MCP Architecture
- **Container-based execution**: Reliable, scalable tool execution
- **Language isolation**: Python and JavaScript tools run in separate containers
- **Automatic routing**: Tools are automatically routed to the correct runtime

### 🔄 Seamless Migration
- **Backward compatibility**: Existing CloudPickle tools continue to work
- **Gradual migration**: Migrate tools at your own pace
- **Rollback support**: Safe migration with rollback capabilities

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FlowStack Agent                       │
├─────────────────────────────────────────────────────────────┤
│  Python SDK              │          JavaScript SDK          │
│  ┌─────────────────┐    │    ┌─────────────────────────┐   │
│  │ @agent.tool     │    │    │ agent.tool('name', {    │   │
│  │ def py_func():  │    │    │   handler: jsFunc       │   │
│  │   return "hi"   │    │    │ })                      │   │
│  └─────────────────┘    │    └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   Provider Router Function                   │
│                  (routes to MCP if tools)                   │
└─────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  MCP Orchestrator Function                   │
│         (manages container tasks and routes execution)       │
└─────────────────────────────────────────────────────────────┘
                                   │
                ┌─────────────────────────────────┐
                │                                 │
                ▼                                 ▼
┌─────────────────────────┐           ┌─────────────────────────┐
│   Python MCP Server     │           │    Node.js MCP Server   │
│    (Container Task)     │           │    (Container Task)    │
│                         │           │                         │
│  ┌─────────────────┐   │           │  ┌─────────────────┐    │
│  │   DataVault     │   │           │  │   DataVault     │    │
│  │   Context       │   │           │  │   Context       │    │
│  │   Injection     │   │           │  │   Injection     │    │
│  └─────────────────┘   │           │  └─────────────────┘    │
└─────────────────────────┘           └─────────────────────────┘
```

## Key Components

### 1. MCP Orchestrator
- **Location**: `lambda/mcp-orchestrator/`
- **Purpose**: Routes tool execution to appropriate container tasks
- **Features**: Task pooling, auto-scaling, health monitoring

### 2. MCP Servers
- **Python Server**: `mcp-servers/python/server.py`
- **Node.js Server**: `mcp-servers/node/server.js`
- **Execution**: Container tasks with DataVault access

### 3. Updated SDKs
- **Python SDK**: Enhanced with `language` parameter
- **JavaScript SDK**: New TypeScript SDK with dual-language support

### 4. Migration Tools
- **Migration Script**: `migration/cloudpickle_to_mcp.py`
- **Validation**: `migration/validate_mcp_migration.py`
- **Rollback**: Built-in rollback capabilities

## Quick Start

### Python SDK (Enhanced)

```python
from flowstack.agent import Agent, Providers, Models

agent = Agent(
    name='dual-language-agent',
    api_key='your-api-key',
    provider=Providers.BEDROCK,
    model=Models.CLAUDE_35_SONNET_BEDROCK
)

# Python tool (traditional)
@agent.tool
def analyze_data(data: list) -> dict:
    \"\"\"Analyze numerical data\"\"\"
    return {
        'count': len(data),
        'average': sum(data) / len(data),
        'max': max(data),
        'min': min(data)
    }

# JavaScript tool from Python SDK
@agent.tool(language='javascript', source_code='''
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}
''')
def format_currency():
    \"\"\"Format amount as currency\"\"\"
    pass

# Use both tools in conversation
response = agent.chat(\"\"\"
Analyze this data [100, 200, 300, 400, 500] and then 
format the average as USD currency.
\"\"\")
```

### JavaScript SDK (New)

```javascript
const { Agent, Providers, Models } = require('@flowstack/sdk');

const agent = new Agent({
    name: 'js-agent',
    apiKey: 'your-api-key'
});

// JavaScript tool (native)
agent.tool('processOrder', {
    description: 'Process e-commerce order',
    handler: (order) => {
        return {
            orderId: order.id,
            total: order.items.reduce((sum, item) => sum + item.price, 0),
            processedAt: new Date().toISOString()
        };
    }
});

// Python tool from JavaScript SDK  
agent.tool('calculateShipping', {
    description: 'Calculate shipping costs using Python',
    language: 'python',
    code: `
def calculateShipping(weight, distance):
    base_rate = 5.99
    weight_rate = weight * 0.50
    distance_rate = distance * 0.02
    return base_rate + weight_rate + distance_rate
    `
});

// Use mixed tools
const response = await agent.chat(
    'Process an order with 3 items at $10 each, then calculate shipping for 2lbs over 100 miles'
);
```

## Tool Development Guide

### Python Tools

#### Basic Python Tool
```python
@agent.tool
def simple_calculator(operation: str, a: float, b: float) -> dict:
    \"\"\"Perform basic math operations\"\"\"
    operations = {
        'add': a + b,
        'subtract': a - b,
        'multiply': a * b,
        'divide': a / b if b != 0 else 'Error: Division by zero'
    }
    
    return {
        'operation': operation,
        'operands': [a, b],
        'result': operations.get(operation, 'Unknown operation')
    }
```

#### Python Tool with DataVault
```python
@agent.tool
def save_user_preference(key: str, value: any) -> dict:
    \"\"\"Save user preference to persistent storage\"\"\"
    
    # DataVault is automatically injected as 'vault'
    success = vault.set(f"user_pref_{key}", {
        'value': value,
        'saved_at': time.time(),
        'version': 1
    })
    
    return {
        'success': success,
        'key': key,
        'message': f"Saved preference: {key}"
    }
```

#### Python Tool with External APIs
```python
@agent.tool
def fetch_weather(city: str) -> dict:
    \"\"\"Fetch weather data for a city\"\"\"
    import requests
    
    try:
        # Mock weather API (replace with real API)
        response = requests.get(f"https://api.weather.com/v1/current?city={city}")
        data = response.json()
        
        return {
            'city': city,
            'temperature': data.get('temperature'),
            'condition': data.get('condition'),
            'humidity': data.get('humidity'),
            'fetched_at': time.time()
        }
    except Exception as e:
        return {
            'error': str(e),
            'city': city
        }
```

### JavaScript Tools

#### Basic JavaScript Tool
```javascript
agent.tool('validateEmail', {
    description: 'Validate email address format',
    handler: (email) => {
        const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
        const isValid = emailRegex.test(email);
        
        return {
            email: email,
            valid: isValid,
            message: isValid ? 'Valid email format' : 'Invalid email format'
        };
    }
});
```

#### JavaScript Tool with Async Operations
```javascript
agent.tool('fetchApiData', {
    description: 'Fetch data from API endpoint',
    handler: async (url, options = {}) => {
        try {
            const response = await fetch(url, {
                method: options.method || 'GET',
                headers: {
                    'User-Agent': 'FlowStack-Agent/1.0',
                    ...options.headers
                },
                timeout: 10000
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            return {
                url: url,
                status: response.status,
                data: data,
                fetchedAt: new Date().toISOString()
            };
            
        } catch (error) {
            return {
                url: url,
                error: error.message,
                fetchedAt: new Date().toISOString()
            };
        }
    }
});
```

#### JavaScript Tool with DataVault
```javascript
agent.tool('trackUserAction', {
    description: 'Track user action in analytics',
    handler: async (action, metadata = {}) => {
        const vault = agent.getVault();
        
        try {
            // Get existing actions
            const existing = await vault.get('user_actions') || [];
            
            // Add new action
            const newAction = {
                action: action,
                metadata: metadata,
                timestamp: new Date().toISOString(),
                id: Math.random().toString(36).substr(2, 9)
            };
            
            existing.push(newAction);
            
            // Save back to vault
            const success = await vault.set('user_actions', existing);
            
            return {
                success: success,
                actionId: newAction.id,
                totalActions: existing.length
            };
            
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
});
```

## Advanced Patterns

### Multi-Step Workflows

```python
# Python data processing
@agent.tool
def process_sales_data(sales_records: list) -> dict:
    \"\"\"Process raw sales data\"\"\"
    total_sales = sum(record['amount'] for record in sales_records)
    return {
        'total_sales': total_sales,
        'record_count': len(sales_records),
        'average_sale': total_sales / len(sales_records)
    }

# JavaScript visualization  
@agent.tool(language='javascript', source_code='''
function generateSalesDashboard(salesData) {
    const { total_sales, record_count, average_sale } = salesData;
    
    return `
📊 Sales Dashboard
═════════════════
💰 Total Sales: $${total_sales.toFixed(2)}
📈 Average Sale: $${average_sale.toFixed(2)}
📋 Total Records: ${record_count}

Generated: ${new Date().toLocaleString()}
    `;
}
''')
def generate_sales_dashboard():
    pass

# Use in conversation
response = agent.chat(\"\"\"
Process this sales data and create a dashboard:
[
    {"amount": 150.50}, 
    {"amount": 200.00}, 
    {"amount": 75.25}
]
\"\"\")
```

### Error Handling Across Languages

```python
# Python tool with error handling
@agent.tool
def divide_safely(a: float, b: float) -> dict:
    \"\"\"Safely divide two numbers\"\"\"
    try:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        
        result = a / b
        return {
            'success': True,
            'result': result,
            'operation': f"{a} ÷ {b}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'operation': f"{a} ÷ {b}"
        }
```

```javascript
// JavaScript tool with error handling
agent.tool('parseJsonSafely', {
    description: 'Safely parse JSON string',
    handler: (jsonString) => {
        try {
            const parsed = JSON.parse(jsonString);
            
            return {
                success: true,
                data: parsed,
                type: Array.isArray(parsed) ? 'array' : typeof parsed
            };
            
        } catch (error) {
            return {
                success: false,
                error: error.message,
                input: jsonString.substring(0, 100) + (jsonString.length > 100 ? '...' : '')
            };
        }
    }
});
```

## Migration from CloudPickle

### Step 1: Identify Tools to Migrate

```bash
# Run migration assessment
python migration/cloudpickle_to_mcp.py --environment dev --dry-run
```

This shows:
- Number of CloudPickle tools found
- Which tools have extractable source code
- Which tools use DataVault
- Potential migration issues

### Step 2: Perform Migration

```bash
# Migrate all tools
python migration/cloudpickle_to_mcp.py --environment dev

# Or migrate specific tool
python migration/cloudpickle_to_mcp.py --environment dev --tool "namespace/tool_name"
```

### Step 3: Validate Migration

```bash
# Validate migrated tools
python migration/validate_mcp_migration.py --environment dev --output migration_report.json
```

### Step 4: Update Tool Usage (Optional)

After migration, you can enhance tools with explicit language specifications:

```python
# Before (CloudPickle)
@agent.tool
def old_tool():
    return "legacy"

# After (MCP-enhanced)
@agent.tool(language='python')  # Explicit language
def enhanced_tool(param: str) -> dict:
    \"\"\"Enhanced tool with better typing\"\"\"
    return {"result": param, "enhanced": True}
```

## Testing

### Running Tests

```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test category
python tests/run_all_tests.py --category integration

# Run JavaScript SDK tests
node tests/e2e/test_javascript_sdk.js
```

### Writing Tool Tests

```python
# Test Python tool
def test_my_python_tool():
    agent = create_test_agent()
    
    @agent.tool
    def test_tool(x: int) -> int:
        return x * 2
    
    response = agent.chat("Use test_tool with x=5")
    assert "10" in response

# Test JavaScript tool  
def test_my_js_tool():
    agent = create_test_agent()
    
    @agent.tool(language='javascript', source_code='''
    function doubler(x) { return x * 2; }
    ''')
    def js_doubler():
        pass
    
    response = agent.chat("Use doubler with x=5")
    assert "10" in response
```

## Performance Considerations

### Container Task Optimization

- **Free Tier**: Shared task pool (cost-efficient)
- **Paid Tiers**: Dedicated tasks (better performance)
- **Auto-scaling**: Tasks scale based on demand
- **Warm Pool**: Pre-warmed tasks for low latency

### Best Practices

1. **Tool Design**:
   - Keep tools focused and single-purpose
   - Use appropriate language for the task
   - Handle errors gracefully

2. **Performance**:
   - JavaScript tools typically start faster
   - Python tools better for data processing
   - Use DataVault for state persistence

3. **Debugging**:
   - Check execution logs for details
   - Use validation tools for migration issues
   - Test tools individually before deployment

## Troubleshooting

### Common Issues

#### 1. Tool Not Executing
```
Error: Tool 'my_tool' not found
```

**Solutions**:
- Verify tool is registered: `agent.tools` should contain tool
- Check tool name matches exactly
- Ensure MCP orchestrator is deployed

#### 2. JavaScript Syntax Errors
```
Error: Unexpected token in JavaScript code
```

**Solutions**:
- Validate JavaScript syntax
- Use proper function declarations
- Check for template string issues

#### 3. DataVault Access Failed
```
Error: DataVault get failed: Connection timeout
```

**Solutions**:
- Check MONGODB_URI environment variable
- Verify network connectivity
- Check DataVault namespace permissions

#### 4. MCP Task Creation Failed
```
Error: Failed to create MCP task
```

**Solutions**:
- Verify container cluster is running
- Check container task definitions exist
- Review permissions for container execution

### Getting Help

1. **Check logs**: Execution logs for detailed errors
2. **Run validation**: Use migration validation tools
3. **Test individually**: Test tools before deployment
4. **Review documentation**: Check this guide and examples

## What's Next

### Roadmap Features
- **More languages**: Go, Rust, Java support planned  
- **Tool marketplace**: Shared tool library
- **Visual tool builder**: GUI for non-technical users
- **Advanced workflows**: Complex multi-step automations

### Contributing
- Submit tool examples to the community
- Report issues and bugs  
- Suggest new language integrations
- Contribute to SDK improvements

---

**Ready to build multi-language AI agents?** Start with the examples above and explore the power of combining Python and JavaScript tools in your FlowStack agents!