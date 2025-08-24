"""
AI Provider Constants

Supported AI providers and their configuration.
"""

class Providers:
    """Constants for all supported AI providers"""
    
    # Primary providers
    BEDROCK = "bedrock"           # Amazon Bedrock (managed or BYOK)
    OPENAI = "openai"             # OpenAI (BYOK only)
    ANTHROPIC = "anthropic"       # Anthropic direct API (BYOK only)
    COHERE = "cohere"             # Cohere (BYOK only)
    MISTRAL = "mistral"           # MistralAI (BYOK only)
    OLLAMA = "ollama"             # Local Ollama (BYOK only)
    SAGEMAKER = "sagemaker"       # AWS SageMaker (BYOK only)
    WRITER = "writer"             # Writer.com (BYOK only)
    LITELLM = "litellm"           # LiteLLM proxy (BYOK only)
    
    @classmethod
    def get_managed_providers(cls):
        """Get providers that support managed billing"""
        return [cls.BEDROCK]
    
    @classmethod
    def get_byok_only_providers(cls):
        """Get providers that require BYOK"""
        return [
            cls.OPENAI, cls.ANTHROPIC, cls.COHERE, cls.MISTRAL,
            cls.OLLAMA, cls.SAGEMAKER, cls.WRITER, cls.LITELLM
        ]
    
    @classmethod
    def get_all_providers(cls):
        """Get all supported providers"""
        return [
            cls.BEDROCK, cls.OPENAI, cls.ANTHROPIC, cls.COHERE,
            cls.MISTRAL, cls.OLLAMA, cls.SAGEMAKER, cls.WRITER, cls.LITELLM
        ]
    
    @classmethod
    def supports_managed_billing(cls, provider):
        """Check if provider supports managed billing"""
        return provider in cls.get_managed_providers()
    
    @classmethod
    def requires_byok(cls, provider):
        """Check if provider requires BYOK"""
        return provider in cls.get_byok_only_providers()