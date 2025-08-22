"""
AI Model Constants

Pre-defined model IDs for easy selection across all supported providers.
"""

class Models:
    """Constants for all supported AI models"""
    
    # Anthropic Claude Models (via Bedrock) - Latest & Greatest
    CLAUDE_OPUS_4_1 = "anthropic.claude-opus-4-1-20250805-v1:0"  # Most capable
    CLAUDE_37_SONNET = "anthropic.claude-3-7-sonnet-20250219-v1:0"  # Latest Sonnet
    CLAUDE_SONNET_4 = "anthropic.claude-sonnet-4-20250514-v1:0"  # Sonnet 4
    CLAUDE_35_SONNET_V2 = "anthropic.claude-3-5-sonnet-20241022-v2:0"  # Flagship
    CLAUDE_35_SONNET = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    CLAUDE_35_HAIKU = "anthropic.claude-3-5-haiku-20241022-v1:0"  # Fast & efficient
    CLAUDE_3_OPUS = "anthropic.claude-3-opus-20240229-v1:0"
    CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
    # Legacy Claude
    CLAUDE_V2_1 = "anthropic.claude-v2:1"
    CLAUDE_V2 = "anthropic.claude-v2"
    CLAUDE_INSTANT = "anthropic.claude-instant-v1"
    
    # Amazon Nova Models (NEW!) - Amazon's newest models
    NOVA_PREMIER = "amazon.nova-premier-v1:0"  # Most capable
    NOVA_PRO = "amazon.nova-pro-v1:0"  # Balanced performance
    NOVA_LITE = "amazon.nova-lite-v1:0"  # Fast
    NOVA_MICRO = "amazon.nova-micro-v1:0"  # Ultra-fast
    
    # Meta Llama Models (via Bedrock) - Including Llama 4!
    LLAMA4_MAVERICK_17B = "meta.llama4-maverick-17b-instruct-v1:0"  # Llama 4!
    LLAMA4_SCOUT_17B = "meta.llama4-scout-17b-instruct-v1:0"  # Llama 4!
    LLAMA33_70B = "meta.llama3-3-70b-instruct-v1:0"  # Latest 3.3
    LLAMA32_90B = "meta.llama3-2-90b-instruct-v1:0"  # Largest 3.2
    LLAMA32_11B = "meta.llama3-2-11b-instruct-v1:0"
    LLAMA32_3B = "meta.llama3-2-3b-instruct-v1:0"
    LLAMA32_1B = "meta.llama3-2-1b-instruct-v1:0"
    LLAMA31_405B = "meta.llama3-1-405b-instruct-v1:0"  # Massive
    LLAMA31_70B = "meta.llama3-1-70b-instruct-v1:0"
    LLAMA31_8B = "meta.llama3-1-8b-instruct-v1:0"
    LLAMA3_70B = "meta.llama3-70b-instruct-v1:0"
    LLAMA3_8B = "meta.llama3-8b-instruct-v1:0"
    
    # Mistral Models (via Bedrock)
    PIXTRAL_LARGE = "mistral.pixtral-large-2502-v1:0"  # Latest multimodal
    MISTRAL_LARGE_2407 = "mistral.mistral-large-2407-v1:0"  # Flagship
    MISTRAL_LARGE_2402 = "mistral.mistral-large-2402-v1:0"
    MISTRAL_7B = "mistral.mistral-7b-instruct-v0:2"
    MIXTRAL_8X7B = "mistral.mixtral-8x7b-instruct-v0:1"
    
    # Amazon Titan Models
    TITAN_PREMIER = "amazon.titan-text-premier-v1:0"
    TITAN_EXPRESS = "amazon.titan-text-express-v1"
    TITAN_LITE = "amazon.titan-text-lite-v1"
    
    # Cohere Models (via Bedrock)
    COMMAND_R_PLUS = "cohere.command-r-plus-v1:0"
    COMMAND_R = "cohere.command-r-v1:0"
    
    # AI21 Models (via Bedrock)
    JAMBA_15_LARGE = "ai21.jamba-1-5-large-v1:0"
    JAMBA_15_MINI = "ai21.jamba-1-5-mini-v1:0"
    
    # OpenAI Models (BYOK only)
    GPT_4O = "gpt-4o"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_35_TURBO = "gpt-3.5-turbo"
    
    # Anthropic Direct API Models (BYOK only)
    CLAUDE_DIRECT_OPUS = "claude-3-opus-20240229"
    CLAUDE_DIRECT_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_DIRECT_HAIKU = "claude-3-haiku-20240307"
    
    @classmethod
    def get_bedrock_models(cls):
        """Get all models available via Amazon Bedrock (40+ models!)"""
        return [
            # Latest Anthropic Claude models
            cls.CLAUDE_OPUS_4_1, cls.CLAUDE_37_SONNET, cls.CLAUDE_SONNET_4,
            cls.CLAUDE_35_SONNET_V2, cls.CLAUDE_35_SONNET, cls.CLAUDE_35_HAIKU,
            cls.CLAUDE_3_OPUS, cls.CLAUDE_3_SONNET, cls.CLAUDE_3_HAIKU,
            cls.CLAUDE_V2_1, cls.CLAUDE_V2, cls.CLAUDE_INSTANT,
            
            # Amazon Nova models (newest!)
            cls.NOVA_PREMIER, cls.NOVA_PRO, cls.NOVA_LITE, cls.NOVA_MICRO,
            
            # Meta Llama models (including Llama 4!)
            cls.LLAMA4_MAVERICK_17B, cls.LLAMA4_SCOUT_17B,
            cls.LLAMA33_70B, cls.LLAMA32_90B, cls.LLAMA32_11B, cls.LLAMA32_3B, cls.LLAMA32_1B,
            cls.LLAMA31_405B, cls.LLAMA31_70B, cls.LLAMA31_8B,
            cls.LLAMA3_70B, cls.LLAMA3_8B,
            
            # Mistral models
            cls.PIXTRAL_LARGE, cls.MISTRAL_LARGE_2407, cls.MISTRAL_LARGE_2402,
            cls.MISTRAL_7B, cls.MIXTRAL_8X7B,
            
            # Amazon Titan models
            cls.TITAN_PREMIER, cls.TITAN_EXPRESS, cls.TITAN_LITE,
            
            # Other providers
            cls.COMMAND_R_PLUS, cls.COMMAND_R,
            cls.JAMBA_15_LARGE, cls.JAMBA_15_MINI
        ]
    
    @classmethod
    def get_openai_models(cls):
        """Get all OpenAI models (BYOK only)"""
        return [cls.GPT_4O, cls.GPT_4_TURBO, cls.GPT_35_TURBO]
    
    @classmethod
    def get_anthropic_direct_models(cls):
        """Get Anthropic direct API models (BYOK only)"""
        return [cls.CLAUDE_DIRECT_OPUS, cls.CLAUDE_DIRECT_SONNET, cls.CLAUDE_DIRECT_HAIKU]