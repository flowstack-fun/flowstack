# FlowStack Frontend Integration Guide

This guide provides the correct API endpoints for frontend integration with the FlowStack platform.

## ⚠️ Important: Endpoint Mapping

The FlowStack API **does not** use `/api/auth/*` endpoints. The correct endpoints are documented below.

## Base URL

- **Production/Development**: `https://api.flowstack.fun`

## Authentication & User Management Endpoints

### User Registration (Signup)
```javascript
// POST /customers
const response = await fetch('https://api.flowstack.fun/customers', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    name: 'John Doe' // optional
  })
});

// Response
{
  "customer_id": "uuid",
  "api_key": "fs_...",
  "tier": "free",
  "sessions_limit": 25,
  "message": "Account created! Please check your email to verify your account before using the API.",
  "email_verification_required": true
}
```

### Email Verification
```javascript
// GET /customers/verify?token=<verification_token>&customer_id=<customer_id>
const verificationUrl = `https://api.flowstack.fun/customers/verify?token=${token}&customer_id=${customerId}`;
// This is typically called from email link, returns HTML page
```

### Resend Email Verification
```javascript
// POST /customers/resend-verification
const response = await fetch('https://api.flowstack.fun/customers/resend-verification', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com'
  })
});
```

### Login (Currently Not Implemented)
```javascript
// POST /customers/login
// Note: This endpoint exists in the infrastructure but is not fully implemented
// Currently, FlowStack uses API keys for authentication rather than user sessions
```

### Get Customer Information
```javascript
// GET /customers/{customerId}
const response = await fetch(`https://api.flowstack.fun/customers/${customerId}`, {
  headers: {
    'X-API-Key': 'fs_your_api_key'
  }
});

// Response
{
  "customer_id": "uuid",
  "email": "user@example.com",
  "tier": "free",
  "sessions_used": 5,
  "sessions_limit": 25,
  "email_verified": true,
  "created_at": "2025-08-24T..."
}
```

## API Key Management

### Create Additional API Key
```javascript
// POST /customers/{customerId}/api-keys
const response = await fetch(`https://api.flowstack.fun/customers/${customerId}/api-keys`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'fs_your_api_key'
  },
  body: JSON.stringify({
    name: 'My App API Key' // optional name for the key
  })
});

// Response
{
  "api_key": "fs_new_key...",
  "name": "My App API Key",
  "created_at": "2025-08-24T..."
}
```

### Regenerate API Key
```javascript
// POST /customers/{customerId}/regenerate-key
const response = await fetch(`https://api.flowstack.fun/customers/${customerId}/regenerate-key`, {
  method: 'POST',
  headers: {
    'X-API-Key': 'fs_your_current_api_key'
  }
});
```

## BYOK (Bring Your Own Key) Management

### Store Provider Credentials
```javascript
// POST /customers/{customerId}/byok-credentials
const response = await fetch(`https://api.flowstack.fun/customers/${customerId}/byok-credentials`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'fs_your_api_key'
  },
  body: JSON.stringify({
    provider: 'openai', // or 'anthropic', 'bedrock'
    credentials: {
      api_key: 'your_openai_api_key'
    }
  })
});
```

## Agent & Tool Management

### Deploy Agent with Tools
```javascript
// POST /deployments
const response = await fetch('https://api.flowstack.fun/deployments', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'fs_your_api_key'
  },
  body: JSON.stringify({
    name: 'my-agent',
    tools: [
      {
        name: 'add_numbers',
        language: 'python',
        serialization_method: 'source_code',
        source_code: 'def add_numbers(x: int, y: int) -> int:\\n    return x + y',
        function_name: 'add_numbers',
        schema: {
          type: 'function',
          function: {
            name: 'add_numbers',
            parameters: {
              type: 'object',
              properties: {
                x: { type: 'integer' },
                y: { type: 'integer' }
              },
              required: ['x', 'y']
            }
          }
        }
      }
    ]
  })
});
```

### Invoke Agent
```javascript
// POST /agents/{agentName}/invoke
const response = await fetch(`https://api.flowstack.fun/agents/${agentName}/invoke`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'fs_your_api_key'
  },
  body: JSON.stringify({
    message: 'Add 5 and 3 using the add_numbers tool'
  })
});
```

## Usage & Billing

### Get Usage Statistics
```javascript
// GET /usage
const response = await fetch('https://api.flowstack.fun/usage', {
  headers: {
    'X-API-Key': 'fs_your_api_key'
  }
});

// Response
{
  "customer_id": "uuid",
  "tier": "free",
  "current_period": {
    "sessions_used": 5,
    "sessions_limit": 25,
    "reset_date": "2025-09-01T00:00:00Z"
  },
  "usage_history": [...]
}
```

### Get Tier Information
```javascript
// GET /tier-info
const response = await fetch('https://api.flowstack.fun/tier-info', {
  headers: {
    'X-API-Key': 'fs_your_api_key'
  }
});
```

## Error Handling

All endpoints return consistent error responses:

```javascript
// Error response format
{
  "error": "Error description"
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created (for signup, key creation)
- `400` - Bad Request (missing required fields)
- `401` - Unauthorized (invalid API key)
- `404` - Not Found (customer/resource not found)
- `429` - Rate Limited
- `500` - Internal Server Error

### CORS Support

All endpoints support CORS with the following headers:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS`
- `Access-Control-Allow-Headers: Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Requested-With,Accept,Origin`
- `Access-Control-Max-Age: 86400`

## Frontend Implementation Example

### React Hook for API Calls

```javascript
import { useState, useCallback } from 'react';

const useFlowStackAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const apiCall = useCallback(async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`https://api.flowstack.fun${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const signup = useCallback((email, name) => {
    return apiCall('/customers', {
      method: 'POST',
      body: JSON.stringify({ email, name }),
    });
  }, [apiCall]);

  const getCustomer = useCallback((customerId, apiKey) => {
    return apiCall(`/customers/${customerId}`, {
      headers: { 'X-API-Key': apiKey },
    });
  }, [apiCall]);

  return {
    loading,
    error,
    signup,
    getCustomer,
    apiCall,
  };
};

export default useFlowStackAPI;
```

## Authentication Flow

1. **Signup**: Call `POST /customers` with email
2. **Email Verification**: User clicks link in email, which calls `GET /customers/verify`
3. **Store API Key**: Save the API key from signup response for future requests
4. **Use API Key**: Include `X-API-Key` header in all authenticated requests

## Important Notes

- **No JWT/Session Management**: FlowStack uses API keys, not JWT tokens
- **Email Verification Required**: Users must verify email before using the API
- **Rate Limiting**: Free tier has 25 sessions per month
- **BYOK Optional**: Users can bring their own OpenAI/Anthropic keys for lower costs
- **All Tool Execution**: Goes through secure MCP (Model Context Protocol) containers

For more detailed technical documentation, see the infrastructure diagrams in `/internal/diagrams/`.