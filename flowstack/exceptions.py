"""
FlowStack Exception Classes

Clean error handling for the FlowStack SDK.
"""

class FlowStackError(Exception):
    """Base exception for all FlowStack errors"""
    
    def __init__(self, message, error_code=None, details=None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

class AuthenticationError(FlowStackError):
    """Raised when API key is invalid or missing"""
    
    def __init__(self, message="Invalid API key"):
        super().__init__(message, error_code="AUTH_ERROR")

class QuotaExceededError(FlowStackError):
    """Raised when session or usage limits are exceeded"""
    
    def __init__(self, message="Usage quota exceeded", current_usage=None, limit=None):
        super().__init__(message, error_code="QUOTA_EXCEEDED")
        self.details = {
            "current_usage": current_usage,
            "limit": limit
        }

class InvalidProviderError(FlowStackError):
    """Raised when an unsupported provider is specified"""
    
    def __init__(self, provider):
        super().__init__(f"Unsupported provider: {provider}", error_code="INVALID_PROVIDER")
        self.provider = provider

class CredentialsRequiredError(FlowStackError):
    """Raised when BYOK credentials are required but not provided"""
    
    def __init__(self, provider, message=None):
        if not message:
            message = f"{provider} requires BYOK credentials"
        super().__init__(message, error_code="CREDENTIALS_REQUIRED")
        self.provider = provider

class ModelNotAvailableError(FlowStackError):
    """Raised when a model is not available for the selected provider"""
    
    def __init__(self, model, provider):
        super().__init__(f"Model {model} not available for provider {provider}", 
                        error_code="MODEL_NOT_AVAILABLE")
        self.model = model
        self.provider = provider

class BillingError(FlowStackError):
    """Raised when there are billing-related issues"""
    
    def __init__(self, message="Billing error occurred"):
        super().__init__(message, error_code="BILLING_ERROR")

class TierLimitationError(FlowStackError):
    """Raised when attempting to use features not available in current tier"""
    
    def __init__(self, feature, tier):
        super().__init__(f"Feature '{feature}' not available in {tier} tier", 
                        error_code="TIER_LIMITATION")
        self.feature = feature
        self.tier = tier