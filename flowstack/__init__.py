"""
FlowStack Python SDK

A clean, simple interface for AI agent development with built-in billing management.
Supports multiple AI providers through managed infrastructure or BYOK (Bring Your Own Key).
"""

from .agent import Agent, create_agent
from .models import Models
from .providers import Providers
from .billing import BillingManager
from .tools import tool
from .deployment import DeploymentBuilder
from .datavault import DataVault
from .exceptions import (
    FlowStackError, 
    AuthenticationError, 
    QuotaExceededError,
    InvalidProviderError,
    CredentialsRequiredError,
    TierLimitationError
)

__version__ = "1.1.0"
__all__ = [
    "Agent",
    "create_agent",
    "Models", 
    "Providers",
    "BillingManager",
    "DataVault",
    "tool",
    "DeploymentBuilder",
    "FlowStackError",
    "AuthenticationError", 
    "QuotaExceededError",
    "InvalidProviderError",
    "CredentialsRequiredError",
    "TierLimitationError"
]