# FlowStack Client-Side Authentication Implementation Guide

## Overview
FlowStack now supports dual authentication:
- **JWT Authentication**: For web dashboard access (session-based)
- **API Key Authentication**: For developer API/SDK usage (persistent)

**Important**: Email verification is now **strictly enforced**. Users must verify their email before either authentication method works.

## Authentication Flow

### 1. User Registration (Signup)

```javascript
// POST https://api.flowstack.fun/customers
const signup = async (email, name, password) => {
  const response = await fetch('https://api.flowstack.fun/customers', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      name,
      password  // NEW: Optional password for dashboard access
    })
  });
  
  const data = await response.json();
  // Response:
  // {
  //   "customer_id": "uuid",
  //   "api_key": "fs_...",
  //   "tier": "free",
  //   "sessions_limit": 25,
  //   "message": "Account created! You must verify your email before using the API.",
  //   "email_verification_required": true,
  //   "api_key_active": false,  // Won't work until verified
  //   "password_set": true       // Indicates if password was set
  // }
  
  return data;
};
```

### 2. Email Verification (Required!)

User receives email with verification link. After clicking:
- Account status changes to `active`
- API key becomes functional
- User can login with password (if set)

### 3. Login (For Dashboard Access)

```javascript
// POST https://api.flowstack.fun/customers/login
const login = async (email, password) => {
  const response = await fetch('https://api.flowstack.fun/customers/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password
    })
  });
  
  if (response.status === 401) {
    throw new Error('Invalid email or password');
  }
  
  if (response.status === 404) {
    throw new Error('User not found. Please sign up first.');
  }
  
  const data = await response.json();
  // Response:
  // {
  //   "access_token": "eyJ...",
  //   "id_token": "eyJ...",
  //   "refresh_token": "eyJ...",
  //   "expires_in": 3600,
  //   "customer": {
  //     "customer_id": "uuid",
  //     "email": "user@example.com",
  //     "tier": "free",
  //     "email_verified": true
  //   }
  // }
  
  // Store tokens securely
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  localStorage.setItem('token_expires', Date.now() + data.expires_in * 1000);
  
  return data;
};
```

### 4. Token Refresh

```javascript
// POST https://api.flowstack.fun/customers/refresh
const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('https://api.flowstack.fun/customers/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh_token: refreshToken
    })
  });
  
  if (response.status === 401) {
    // Refresh token expired, redirect to login
    redirectToLogin();
    return;
  }
  
  const data = await response.json();
  // Response:
  // {
  //   "access_token": "eyJ...",
  //   "id_token": "eyJ...",
  //   "expires_in": 3600
  // }
  
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('token_expires', Date.now() + data.expires_in * 1000);
  
  return data;
};
```

### 5. Password Reset Flow

```javascript
// Step 1: Request reset code
const forgotPassword = async (email) => {
  const response = await fetch('https://api.flowstack.fun/customers/forgot-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email })
  });
  
  const data = await response.json();
  // Always returns success for security (doesn't reveal if email exists)
  return data;
};

// Step 2: Reset with code
const resetPassword = async (email, code, newPassword) => {
  const response = await fetch('https://api.flowstack.fun/customers/reset-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      code,
      new_password: newPassword
    })
  });
  
  if (response.status === 400) {
    throw new Error('Invalid or expired reset code');
  }
  
  const data = await response.json();
  return data;
};
```

## Making Authenticated API Calls

### Using JWT Token (Dashboard/Web App)

```javascript
const makeAuthenticatedCall = async (endpoint, options = {}) => {
  // Check if token needs refresh
  const tokenExpires = localStorage.getItem('token_expires');
  if (Date.now() > tokenExpires - 60000) { // Refresh 1 min before expiry
    await refreshAccessToken();
  }
  
  const accessToken = localStorage.getItem('access_token');
  
  const response = await fetch(`https://api.flowstack.fun${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    }
  });
  
  if (response.status === 401) {
    // Token expired, try refresh
    await refreshAccessToken();
    // Retry request
    return makeAuthenticatedCall(endpoint, options);
  }
  
  return response;
};

// Example usage
const usage = await makeAuthenticatedCall('/usage');
const data = await usage.json();
```

### Using API Key (Developer SDK)

```javascript
const makeApiCall = async (endpoint, options = {}) => {
  const apiKey = process.env.FLOWSTACK_API_KEY; // Store securely
  
  const response = await fetch(`https://api.flowstack.fun${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      'X-API-Key': apiKey,
      'Content-Type': 'application/json',
    }
  });
  
  if (response.status === 403) {
    throw new Error('Email verification required or API key invalid');
  }
  
  return response;
};
```

## React Implementation Example

```jsx
// AuthContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');
    const tokenExpires = localStorage.getItem('token_expires');
    
    if (accessToken && Date.now() < tokenExpires) {
      // Parse user from id_token or fetch user info
      const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
      setUser(userData);
    }
    setLoading(false);
  }, []);

  const signup = async (email, name, password) => {
    const response = await fetch('https://api.flowstack.fun/customers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name, password })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Signup failed');
    }
    
    const data = await response.json();
    // Store API key for developer use
    localStorage.setItem('api_key', data.api_key);
    
    return data;
  };

  const login = async (email, password) => {
    const response = await fetch('https://api.flowstack.fun/customers/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Login failed');
    }
    
    const data = await response.json();
    
    // Store tokens
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('id_token', data.id_token);
    localStorage.setItem('token_expires', Date.now() + data.expires_in * 1000);
    localStorage.setItem('user_data', JSON.stringify(data.customer));
    
    setUser(data.customer);
    return data;
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('id_token');
    localStorage.removeItem('token_expires');
    localStorage.removeItem('user_data');
    setUser(null);
  };

  const value = {
    user,
    signup,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// ProtectedRoute.js
import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

export const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  
  return children;
};
```

## Important Notes

### Email Verification is Mandatory
- **API Keys**: Won't work until email is verified
- **Login**: Will fail if email not verified
- **Error Message**: "Email verification required. Please check your email and verify your account."

### Dual Authentication Strategy
- **Dashboard/Web**: Use JWT tokens (expire after 1 hour)
- **API/SDK**: Use API keys (never expire, but require email verification)
- **Both**: Require email verification first

### Security Best Practices
1. **Store tokens securely**: Use httpOnly cookies in production
2. **Refresh proactively**: Refresh tokens before they expire
3. **Handle errors gracefully**: Redirect to login on 401
4. **Never expose API keys**: Keep them server-side or in environment variables

### Error Handling

```javascript
// Centralized error handler
const handleApiError = (error, response) => {
  switch (response.status) {
    case 401:
      // Unauthorized - token expired or invalid
      return refreshTokenAndRetry();
    case 403:
      // Forbidden - email not verified
      return showEmailVerificationPrompt();
    case 404:
      // Not found
      return showNotFoundError();
    case 429:
      // Rate limited
      return showRateLimitError();
    default:
      return showGenericError(error);
  }
};
```

## Testing Your Implementation

1. **Test Signup Flow**:
   - Create account with password
   - Verify email verification is sent
   - Confirm API key doesn't work before verification

2. **Test Email Verification**:
   - Click verification link
   - Confirm account becomes active
   - Test API key now works

3. **Test Login Flow**:
   - Login with email/password
   - Verify JWT tokens received
   - Test authenticated API calls

4. **Test Token Refresh**:
   - Wait for token to near expiry
   - Verify auto-refresh works
   - Confirm API calls continue working

5. **Test Password Reset**:
   - Request reset code
   - Enter code and new password
   - Login with new password

## Migration for Existing Users

Existing users without passwords need to:
1. Request password reset
2. Set a new password
3. Login with new password

Or continue using API keys for programmatic access (after email verification).