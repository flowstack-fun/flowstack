"""
FlowStack Agent

Clean, simple interface for AI agent development.
Supports multiple providers with automatic billing management.
"""

import requests
import json
from typing import Dict, Any, Optional, List, Union
from .models import Models
from .providers import Providers
from .billing import BillingManager, UsageStats
from .exceptions import (
    FlowStackError, AuthenticationError, QuotaExceededError,
    InvalidProviderError, CredentialsRequiredError, TierLimitationError
)

class Agent:
    """
    AI Agent with clean customer interface
    
    Handles multiple providers, billing, and BYOK scenarios
    without exposing internal markup or payment flow details
    """
    
    def __init__(
        self,
        name: str,
        api_key: str,
        provider: str = Providers.BEDROCK,
        model: str = Models.CLAUDE_35_SONNET,
        byok: Optional[Dict[str, str]] = None,
        base_url: str = None,
        **kwargs
    ):
        """
        Initialize FlowStack Agent
        
        Args:
            name: Agent name/identifier
            api_key: FlowStack API key
            provider: AI provider (bedrock, openai, anthropic, etc.)
            model: Model to use
            byok: Bring Your Own Key credentials (optional)
            base_url: API base URL (optional)
            **kwargs: Additional configuration
        """
        self.name = name
        self.api_key = api_key
        self.provider = provider
        self.model = model
        self.byok = byok or {}
        import os
        self.base_url = base_url or os.environ.get('FLOWSTACK_API_URL', "https://api.flowstack.fun")
        
        # Initialize billing manager
        self.billing = BillingManager(api_key, self.base_url)
        
        # Validate configuration
        self._validate_configuration()
        
        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        })
    
    def _validate_configuration(self):
        """Validate agent configuration"""
        
        # Check if provider is supported
        if self.provider not in Providers.get_all_providers():
            raise InvalidProviderError(self.provider)
        
        # Check if BYOK is required for this provider
        if Providers.requires_byok(self.provider) and not self.byok:
            raise CredentialsRequiredError(
                self.provider, 
                f"{self.provider} requires BYOK credentials. Please provide them in the 'byok' parameter."
            )
        
        # Validate BYOK credentials format
        if self.byok:
            self._validate_byok_credentials()
    
    def _validate_byok_credentials(self):
        """Validate BYOK credentials format"""
        
        required_fields = {
            Providers.BEDROCK: ["aws_access_key", "aws_secret_key"],
            Providers.OPENAI: ["api_key"],
            Providers.ANTHROPIC: ["api_key"],
            Providers.COHERE: ["api_key"],
            Providers.MISTRAL: ["api_key"],
            Providers.OLLAMA: ["host"],
            Providers.SAGEMAKER: ["endpoint_name", "region"],
            Providers.WRITER: ["api_key"]
        }
        
        if self.provider in required_fields:
            for field in required_fields[self.provider]:
                if field not in self.byok:
                    raise CredentialsRequiredError(
                        self.provider,
                        f"Missing required BYOK field '{field}' for {self.provider}"
                    )
    
    def invoke(
        self, 
        message: Union[str, List[Dict[str, str]]], 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a message to the AI model
        
        Args:
            message: Text message or list of message objects
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Model response
        """
        
        # Check if user can make requests
        can_proceed, reason = self.billing.can_make_request()
        if not can_proceed:
            raise QuotaExceededError(reason)
        
        # Prepare messages
        if isinstance(message, str):
            messages = [{"role": "user", "content": message}]
        else:
            messages = message
        
        # Prepare request
        request_data = {
            "provider": self.provider,
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        # Add BYOK credentials if provided
        if self.byok:
            request_data["byok_credentials"] = self.byok
        
        try:
            # Make API request
            response = self.session.post(
                f"{self.base_url}/invoke",
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                data = response.json()
                raise QuotaExceededError(
                    data.get("error", "Rate limit exceeded"),
                    current_usage=data.get("current_usage"),
                    limit=data.get("limit")
                )
            elif response.status_code == 403:
                data = response.json()
                if "free tier" in data.get("error", "").lower():
                    raise TierLimitationError("managed models", "free")
                raise FlowStackError(data.get("error", "Access denied"))
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise FlowStackError(f"Request failed: {e}")
        except json.JSONDecodeError:
            raise FlowStackError("Invalid response format")
    
    def chat(self, message: str, **kwargs) -> str:
        """
        Simple chat interface - returns just the text response
        
        Args:
            message: User message
            **kwargs: Additional parameters
        
        Returns:
            AI response text
        """
        response = self.invoke(message, **kwargs)
        
        # Extract text content from different response formats
        if "content" in response:
            if isinstance(response["content"], list):
                # Anthropic format
                return response["content"][0].get("text", str(response))
            else:
                return response["content"]
        elif "choices" in response:
            # OpenAI format
            return response["choices"][0]["message"]["content"]
        elif "text" in response:
            return response["text"]
        else:
            return str(response)
    
    def set_model(self, model: str):
        """Change the model being used"""
        self.model = model
    
    def set_provider(self, provider: str, byok: Optional[Dict[str, str]] = None):
        """
        Change the provider and optionally update BYOK credentials
        
        Args:
            provider: New provider to use
            byok: BYOK credentials (if required)
        """
        self.provider = provider
        if byok:
            self.byok = byok
        
        # Re-validate configuration
        self._validate_configuration()
    
    def get_usage(self) -> UsageStats:
        """Get current usage statistics"""
        stats_data = self.billing.get_usage_stats()
        return UsageStats(stats_data)
    
    def store_byok_credentials(self, provider: str, credentials: Dict[str, str]) -> bool:
        """
        Store BYOK credentials for future use
        
        Args:
            provider: Provider name
            credentials: Credential dictionary
        
        Returns:
            Success status
        """
        return self.billing.store_byok_credentials(provider, credentials)
    
    def get_tier_info(self) -> Dict[str, Any]:
        """Get information about current tier"""
        return self.billing.get_tier_info()
    
    def __str__(self) -> str:
        return f"FlowStack Agent '{self.name}' using {self.provider}/{self.model}"
    
    def __repr__(self) -> str:
        return f"Agent(name='{self.name}', provider='{self.provider}', model='{self.model}')"

# Convenience function for quick agent creation
def create_agent(
    name: str,
    api_key: str,
    provider: str = Providers.BEDROCK,
    model: str = Models.CLAUDE_35_SONNET,
    **kwargs
) -> Agent:
    """
    Create an agent with minimal configuration
    
    Args:
        name: Agent name
        api_key: FlowStack API key
        provider: AI provider
        model: Model to use
        **kwargs: Additional configuration
    
    Returns:
        Configured Agent instance
    """
    return Agent(
        name=name,
        api_key=api_key,
        provider=provider,
        model=model,
        **kwargs
    )