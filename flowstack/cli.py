"""
FlowStack CLI

Command-line interface for FlowStack agent development.
Provides project scaffolding, testing, and deployment commands.
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
import json
import yaml
from typing import Dict, Any

from .deployment import DeploymentBuilder
from .agent import Agent


def init_project(project_name: str, path: str = None) -> None:
    """
    Initialize a new FlowStack project with standard structure.
    
    Args:
        project_name: Name of the project
        path: Optional path to create project in
    """
    # Determine project path
    if path:
        project_path = Path(path) / project_name
    else:
        project_path = Path.cwd() / project_name
    
    # Create project structure
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "tools").mkdir(exist_ok=True)
    
    # Create agent.yaml
    agent_config = {
        'name': project_name,
        'instructions': f"""You are a helpful AI assistant.

## Your Capabilities
- Answer questions accurately
- Help with various tasks
- Use available tools when needed

## Guidelines
- Be helpful and professional
- Provide clear explanations
- Ask for clarification when needed""",
        'model': 'claude-3-sonnet',
        'provider': 'bedrock',
        'temperature': 0.7,
        'tools': {
            'calculator': {
                'description': 'Perform mathematical calculations',
                'instructions': 'Use this for any math operations'
            }
        }
    }
    
    with open(project_path / "agent.yaml", 'w') as f:
        yaml.dump(agent_config, f, default_flow_style=False, sort_keys=False)
    
    # Create example tool
    calculator_code = '''"""
Calculator tool for mathematical operations
"""

def add(x: float, y: float) -> float:
    """Add two numbers"""
    return x + y

def subtract(x: float, y: float) -> float:
    """Subtract y from x"""
    return x - y

def multiply(x: float, y: float) -> float:
    """Multiply two numbers"""
    return x * y

def divide(x: float, y: float) -> float:
    """Divide x by y"""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y
'''
    
    with open(project_path / "tools" / "calculator.py", 'w') as f:
        f.write(calculator_code)
    
    # Create tools/__init__.py
    with open(project_path / "tools" / "__init__.py", 'w') as f:
        f.write("# FlowStack Tools\n")
    
    # Create requirements.txt
    with open(project_path / "requirements.txt", 'w') as f:
        f.write("flowstack>=1.1.0\n")
    
    # Create .env.example
    with open(project_path / ".env.example", 'w') as f:
        f.write("# FlowStack API Configuration\n")
        f.write("FLOWSTACK_API_KEY=fs_test_...\n")
        f.write("FLOWSTACK_API_URL=https://api.flowstack.fun\n")
    
    # Create .gitignore
    with open(project_path / ".gitignore", 'w') as f:
        f.write(".env\n")
        f.write("*.pyc\n")
        f.write("__pycache__/\n")
        f.write(".flowstack/\n")
        f.write("*.log\n")
    
    # Create README.md
    readme = f"""# {project_name}

A FlowStack AI agent project.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your API key:
   ```bash
   cp .env.example .env
   # Edit .env with your FlowStack API key
   ```

## Development

### Test tools locally:
```python
from tools.calculator import add
print(add(5, 3))  # Output: 8
```

### Deploy agent:
```python
from flowstack import Agent
import os

agent = Agent.from_yaml(
    "agent.yaml",
    api_key=os.environ.get("FLOWSTACK_API_KEY")
)

response = agent.deploy()
print(f"Deployed to: {{response['namespace']}}")
```

### Chat with agent:
```python
response = agent.chat("What is 5 plus 3?")
print(response)
```

## Project Structure

```
{project_name}/
├── tools/              # Tool functions
│   └── calculator.py   # Example calculator tools
├── agent.yaml         # Agent configuration
├── requirements.txt   # Python dependencies
└── .env              # Environment variables (create from .env.example)
```

## Tools

Add new tools by creating Python files in the `tools/` directory.
Each function in these files will be available as a tool to your agent.

## Configuration

Edit `agent.yaml` to customize:
- Agent name and instructions
- Model and provider settings
- Tool descriptions and metadata
"""
    
    with open(project_path / "README.md", 'w') as f:
        f.write(readme)
    
    print(f"✅ Created FlowStack project: {project_path}")
    print("\nNext steps:")
    print(f"  cd {project_name}")
    print("  pip install -r requirements.txt")
    print("  # Set your API key in .env")
    print("  flowstack build  # Verify compilation")


def build_project(project_path: str = None) -> Dict[str, Any]:
    """
    Build and validate a FlowStack project.
    
    Args:
        project_path: Path to project (default: current directory)
        
    Returns:
        Compiled deployment payload
    """
    if project_path is None:
        project_path = os.getcwd()
    
    project_path = Path(project_path)
    yaml_path = project_path / "agent.yaml"
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"No agent.yaml found in {project_path}")
    
    # Create builder (dummy API key for build only)
    builder = DeploymentBuilder("build_only", "https://api.flowstack.fun")
    
    # Compile project
    payload = builder.compile_from_yaml(str(yaml_path))
    
    # Validate payload
    builder.validate_payload(payload)
    
    # Display build results
    print("🔨 Build successful!\n")
    print(f"Agent: {payload['agents'][0]['name']}")
    print(f"Model: {payload['agents'][0].get('model', 'claude-3-sonnet')}")
    print(f"Tools: {len(payload['tools'])} functions")
    
    if payload['tools']:
        print("\nCompiled tools:")
        for tool_name in payload['tools']:
            tool = payload['tools'][tool_name]
            print(f"  - {tool_name}: {tool['description'][:50]}...")
    
    # Save build output
    build_dir = project_path / ".flowstack"
    build_dir.mkdir(exist_ok=True)
    
    with open(build_dir / "build.json", 'w') as f:
        json.dump(payload, f, indent=2)
    
    print(f"\n💾 Build output saved to .flowstack/build.json")
    
    return payload


def deploy_project(project_path: str = None, api_key: str = None) -> None:
    """
    Deploy a FlowStack project.
    
    Args:
        project_path: Path to project
        api_key: FlowStack API key
    """
    if project_path is None:
        project_path = os.getcwd()
    
    # Get API key
    if api_key is None:
        api_key = os.environ.get('FLOWSTACK_API_KEY')
        if not api_key:
            raise ValueError("No API key provided. Set FLOWSTACK_API_KEY environment variable.")
    
    # Build project first
    print("Building project...")
    payload = build_project(project_path)
    
    # Create agent and deploy
    print("\nDeploying to FlowStack...")
    agent = Agent.from_yaml(
        str(Path(project_path) / "agent.yaml"),
        api_key=api_key
    )
    
    result = agent.deploy()
    
    print(f"\n✅ Deployment successful!")
    print(f"Deployment ID: {result.get('deployment_id')}")
    print(f"Namespace: {result.get('namespace')}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='FlowStack CLI - AI Agent Development Framework'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize new project')
    init_parser.add_argument('name', help='Project name')
    init_parser.add_argument('--path', help='Path to create project in')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build and validate project')
    build_parser.add_argument('--path', help='Project path', default='.')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy project')
    deploy_parser.add_argument('--path', help='Project path', default='.')
    deploy_parser.add_argument('--api-key', help='FlowStack API key')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        init_project(args.name, args.path)
    elif args.command == 'build':
        build_project(args.path)
    elif args.command == 'deploy':
        deploy_project(args.path, args.api_key)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()