# FlowStack Python SDK

A clean, simple SDK for building AI agents with automatic billing management and multi-provider support.

## Features

- **Multiple AI Providers**: Support for Amazon Bedrock, OpenAI, Anthropic, and more
- **Flexible Billing**: Use managed infrastructure or bring your own API keys
- **Clean Interface**: Simple, intuitive API without billing complexity
- **Automatic Usage Tracking**: Built-in session and cost management
- **Type Safety**: Full type hints for better development experience

## Quick Start

### Installation

```bash
pip install flowstack
```

### Basic Usage

```python
from flowstack import Agent, Models, Providers

# Create an agent (uses managed Bedrock by default)
agent = Agent(
    name="my-assistant",
    api_key="fs_your_api_key_here",
    model=Models.CLAUDE_35_SONNET
)

# Simple chat
response = agent.chat("Hello! How are you?")
print(response)

# Get usage statistics
usage = agent.get_usage()
print(f"Sessions used: {usage.sessions_used}/{usage.sessions_limit}")
```

### Using Your Own API Keys (BYOK)

```python
# Use your own OpenAI API key
agent = Agent(
    name="openai-agent",
    api_key="fs_your_api_key_here",
    provider=Providers.OPENAI,
    model="gpt-4o",
    byok={"api_key": "sk-your-openai-key"}
)

# Use your own AWS credentials for Bedrock
agent = Agent(
    name="bedrock-byok",
    api_key="fs_your_api_key_here",
    provider=Providers.BEDROCK,
    model=Models.CLAUDE_35_SONNET,
    byok={
        "aws_access_key": "AKIA...",
        "aws_secret_key": "your-secret",
        "region": "us-west-2"
    }
)

# Use Anthropic direct API
agent = Agent(
    name="anthropic-direct",
    api_key="fs_your_api_key_here", 
    provider=Providers.ANTHROPIC,
    model="claude-3-opus-20240229",
    byok={"api_key": "sk-ant-your-key"}
)
```

### Advanced Usage

```python
# Multi-turn conversation
agent = Agent(
    name="chat-agent",
    api_key="fs_your_api_key_here"
)

messages = [
    {"role": "user", "content": "What is 2+2?"},
    {"role": "assistant", "content": "2+2 equals 4."},
    {"role": "user", "content": "What about 2+3?"}
]

response = agent.invoke(messages, temperature=0.7, max_tokens=100)
```

### Usage Monitoring

```python
# Check usage limits
usage = agent.get_usage()

if usage.is_near_limit:
    print("Warning: Approaching usage limit!")

if not usage.can_make_requests:
    print("Usage limit reached. Please upgrade your plan.")

# Get tier information
tier_info = agent.get_tier_info()
print(f"Current tier: {tier_info['current_tier']}")
print(f"Can use managed models: {tier_info['can_use_managed']}")
```

## Supported Providers

### Amazon Bedrock (Managed or BYOK)
- **Anthropic**: Claude 3/3.5 (Haiku, Sonnet, Opus)
- **Meta**: Llama 3/3.1/3.2 models
- **Mistral**: 7B, Large, Mixtral
- **Amazon**: Titan models
- **Cohere**: Command R/R+
- **AI21**: Jamba models

### BYOK-Only Providers
- **OpenAI**: GPT-4, GPT-3.5
- **Anthropic Direct**: Claude API
- **Cohere**: Command models
- **MistralAI**: Direct API
- **Ollama**: Local models
- **AWS SageMaker**: Custom endpoints
- **Writer**: Enterprise models

## Error Handling

```python
from flowstack import Agent, FlowStackError, QuotaExceededError

try:
    agent = Agent(name="test", api_key="invalid")
    response = agent.chat("Hello")
except QuotaExceededError as e:
    print(f"Quota exceeded: {e}")
    print(f"Current usage: {e.details['current_usage']}")
except FlowStackError as e:
    print(f"FlowStack error: {e}")
```

## Billing

### Free Tier
- 25 agent sessions/month
- BYOK required for all providers
- No managed Bedrock access

### Paid Tiers
- **Starter ($29/month)**: 1,000 sessions, pay-as-you-go AI usage
- **Professional ($99/month)**: 10,000 sessions, optimized AI pricing  
- **Enterprise ($499+/month)**: 100K+ sessions, volume pricing

All billing is handled automatically - you only see your usage and current charges.

## Model Constants

```python
from flowstack import Models

# Anthropic Claude (via Bedrock)
Models.CLAUDE_35_SONNET
Models.CLAUDE_35_HAIKU
Models.CLAUDE_3_OPUS

# Meta Llama (via Bedrock)
Models.LLAMA_3_70B
Models.LLAMA_31_405B

# OpenAI (BYOK only)
Models.GPT_4O
Models.GPT_4_TURBO

# And many more...
```

## Provider Constants

```python
from flowstack import Providers

# Managed billing available
Providers.BEDROCK

# BYOK only
Providers.OPENAI
Providers.ANTHROPIC
Providers.COHERE
Providers.MISTRAL
Providers.OLLAMA
```

## Development

### Local Setup

```bash
git clone https://github.com/flowstack/python-sdk
cd python-sdk
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black flowstack/
flake8 flowstack/
```

## Support

- 📖 [Documentation](https://docs.flowstack.ai)
- 🐛 [Bug Reports](https://github.com/flowstack/python-sdk/issues)  
- 💬 [Discord Community](https://discord.gg/flowstack)
- 📧 [Email Support](mailto:support@flowstack.ai)

## License

MIT License - see [LICENSE](LICENSE) file for details.