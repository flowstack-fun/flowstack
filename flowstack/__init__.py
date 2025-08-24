"""
FlowStack Python SDK

A clean, simple interface for AI agent development with built-in billing management.
Supports multiple AI providers through managed infrastructure or BYOK (Bring Your Own Key).
"""

from .agent import Agent
from .models import Models
from .providers import Providers
from .billing import BillingManager
from .exceptions import FlowStackError, AuthenticationError, QuotaExceededError

__version__ = "1.0.0"
__all__ = [
    "Agent",
    "Models", 
    "Providers",
    "BillingManager",
    "FlowStackError",
    "AuthenticationError", 
    "QuotaExceededError"
]