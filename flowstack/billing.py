"""
Billing Management

Clean interface for tracking usage and managing billing without exposing internal details.
"""

import requests
from typing import Dict, Any, Optional
from .exceptions import FlowStackError, AuthenticationError

class BillingManager:
    """
    Manages usage tracking and billing information
    Provides clean customer interface without exposing markup details
    """
    
    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        import os
        self.base_url = base_url or os.environ.get('FLOWSTACK_API_URL', "https://api.flowstack.fun")
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get current usage statistics
        Returns clean usage information without internal billing details
        """
        try:
            response = self.session.get(f"{self.base_url}/usage")
            response.raise_for_status()
            
            data = response.json()
            
            # Extract data from the nested structure
            current_period = data.get("current_period", {})
            
            return {
                "sessions_used": current_period.get("sessions_used", 0),
                "sessions_limit": current_period.get("sessions_limit", 0),
                "sessions_remaining": current_period.get("sessions_remaining", 0),
                "current_charges": data.get("current_charges", 0.0),
                "tier": data.get("tier", "free")
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            raise FlowStackError(f"Failed to get usage stats: {e}")
        except Exception as e:
            raise FlowStackError(f"Error getting usage stats: {e}")
    
    def get_billing_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent billing history
        Returns clean billing information without internal markup details
        """
        try:
            response = self.session.get(f"{self.base_url}/api/billing/history", 
                                      params={"limit": limit})
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            raise FlowStackError(f"Failed to get billing history: {e}")
        except Exception as e:
            raise FlowStackError(f"Error getting billing history: {e}")
    
    def can_make_request(self) -> tuple[bool, str]:
        """
        Check if user can make a request (within limits)
        Returns (can_proceed, reason)
        """
        try:
            stats = self.get_usage_stats()
            
            # Check session limits
            if stats["sessions_used"] >= stats["sessions_limit"]:
                return False, f"Monthly session limit reached ({stats['sessions_limit']}). Please upgrade your plan."
            
            return True, "OK"
            
        except Exception as e:
            return False, f"Error checking limits: {e}"
    
    def store_byok_credentials(self, provider: str, credentials: Dict[str, str]) -> bool:
        """
        Store BYOK credentials for a provider
        Credentials are encrypted and stored securely
        """
        try:
            response = self.session.post(f"{self.base_url}/api/byok-credentials", 
                                       json={
                                           "provider": provider,
                                           "credentials": credentials
                                       })
            response.raise_for_status()
            
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif e.response.status_code == 400:
                error_data = e.response.json()
                raise FlowStackError(f"Invalid credentials: {error_data.get('error', 'Unknown error')}")
            raise FlowStackError(f"Failed to store credentials: {e}")
        except Exception as e:
            raise FlowStackError(f"Error storing credentials: {e}")
    
    def get_tier_info(self) -> Dict[str, Any]:
        """
        Get information about current tier and upgrade options
        Returns clean tier information without markup details
        """
        try:
            response = self.session.get(f"{self.base_url}/tier-info")
            response.raise_for_status()
            
            data = response.json()
            
            # Clean response without internal details
            return {
                "current_tier": data.get("tier", "free"),
                "session_limit": data.get("session_limit", 0),
                "can_use_managed": data.get("can_use_managed", False),
                "upgrade_available": data.get("tier") != "enterprise"
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            raise FlowStackError(f"Failed to get tier info: {e}")
        except Exception as e:
            raise FlowStackError(f"Error getting tier info: {e}")

class UsageStats:
    """
    Clean representation of usage statistics
    Hides internal billing calculations from customer
    """
    
    def __init__(self, data: Dict[str, Any]):
        self.sessions_used = data.get("sessions_used", 0)
        self.sessions_limit = data.get("sessions_limit", 0)
        self.sessions_remaining = data.get("sessions_remaining", 0)
        self.current_charges = data.get("current_charges", 0.0)
        self.tier = data.get("tier", "free")
    
    @property
    def usage_percentage(self) -> float:
        """Get usage as percentage of limit"""
        if self.sessions_limit == 0:
            return 0.0
        return (self.sessions_used / self.sessions_limit) * 100
    
    @property
    def is_near_limit(self) -> bool:
        """Check if usage is near the limit (>80%)"""
        return self.usage_percentage > 80
    
    @property
    def can_make_requests(self) -> bool:
        """Check if more requests can be made"""
        return self.sessions_used < self.sessions_limit
    
    def __str__(self) -> str:
        return f"Usage: {self.sessions_used}/{self.sessions_limit} sessions ({self.usage_percentage:.1f}%)"