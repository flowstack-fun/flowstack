"""
FlowStack Deployment Module

Handles agent deployment, configuration parsing, and compilation.
"""

import os
import yaml
import json
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import logging

from .tools import (
    extract_tool_source,
    parse_tool_metadata,
    validate_tool_function,
    discover_tools
)

logger = logging.getLogger(__name__)


class DeploymentBuilder:
    """
    Builds deployment payloads for FlowStack agents.
    
    Compiles agent configuration and tools into the format
    expected by the FlowStack infrastructure.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.flowstack.fun"):
        """
        Initialize deployment builder.
        
        Args:
            api_key: FlowStack API key
            base_url: API base URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        
    def compile_from_yaml(self, yaml_path: str, tools_dir: str = None) -> Dict[str, Any]:
        """
        Compile deployment payload from agent.yaml configuration.
        
        Args:
            yaml_path: Path to agent.yaml file
            tools_dir: Directory containing tool functions (default: ./tools)
            
        Returns:
            Deployment payload ready for API
        """
        # Load YAML configuration
        config = self.load_yaml_config(yaml_path)
        
        # Determine tools directory
        if tools_dir is None:
            yaml_dir = os.path.dirname(yaml_path)
            tools_dir = os.path.join(yaml_dir, 'tools')
        
        # Compile and return payload
        return self.compile_deployment(config, tools_dir)
    
    def load_yaml_config(self, yaml_path: str) -> Dict[str, Any]:
        """
        Load and parse agent.yaml configuration.
        
        Args:
            yaml_path: Path to YAML file
            
        Returns:
            Parsed configuration dictionary
        """
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required = ['name', 'instructions']
        for field in required:
            if field not in config:
                raise ValueError(f"Missing required field in agent.yaml: {field}")
        
        return config
    
    def compile_deployment(self, config: Dict[str, Any], tools_dir: str = None) -> Dict[str, Any]:
        """
        Compile deployment payload from configuration and tools.
        
        Args:
            config: Agent configuration dictionary
            tools_dir: Directory containing tool functions
            
        Returns:
            Deployment payload matching infrastructure format
        """
        # Discover available tools
        discovered_tools = {}
        if tools_dir and os.path.exists(tools_dir):
            discovered_tools = discover_tools(tools_dir)
        
        # Build agent configuration
        agent_config = {
            "name": config['name'],
            "system_prompt": config['instructions'],
            "temperature": config.get('temperature', 0.7),
            "model": config.get('model', 'claude-3-sonnet')
        }
        
        # Process tools
        compiled_tools = {}
        tool_names = []
        
        # Get tool configuration from YAML
        tools_config = config.get('tools', {})
        
        # If tools_config is a list, convert to dict
        if isinstance(tools_config, list):
            tools_config = {tool: {} for tool in tools_config}
        
        # Compile each discovered tool
        for func_name, func in discovered_tools.items():
            # Check if this tool should be included
            # Include if: 1) No specific tools listed, or 2) Tool is in the list
            if not tools_config or func_name in tools_config:
                try:
                    # Validate tool
                    validate_tool_function(func)
                    
                    # Extract source and metadata
                    source = extract_tool_source(func)
                    metadata = parse_tool_metadata(func)
                    
                    # Get tool-specific config from YAML
                    tool_config = tools_config.get(func_name, {})
                    
                    # Override description if provided in YAML
                    if 'description' in tool_config:
                        metadata['description'] = tool_config['description']
                    
                    # Add instructions if provided
                    if 'instructions' in tool_config:
                        metadata['description'] += f"\n{tool_config['instructions']}"
                    
                    # Build tool entry
                    compiled_tools[func_name] = {
                        "serialized": source,
                        "description": metadata['description'],
                        "parameters": metadata['parameters']
                    }
                    
                    tool_names.append(func_name)
                    
                except Exception as e:
                    logger.warning(f"Skipping tool {func_name}: {e}")
        
        # Add tools list to agent config
        agent_config['tools'] = tool_names
        
        # Build final payload
        payload = {
            "agents": [agent_config],
            "tools": compiled_tools
        }
        
        return payload
    
    def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """
        Validate deployment payload matches expected format.
        
        Args:
            payload: Deployment payload to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If payload is invalid
        """
        # Check top-level structure
        if 'agents' not in payload:
            raise ValueError("Payload missing 'agents' field")
        if 'tools' not in payload:
            raise ValueError("Payload missing 'tools' field")
        
        # Validate agents
        if not isinstance(payload['agents'], list):
            raise ValueError("'agents' must be a list")
        
        for agent in payload['agents']:
            required = ['name', 'system_prompt', 'tools']
            for field in required:
                if field not in agent:
                    raise ValueError(f"Agent missing required field: {field}")
        
        # Validate tools
        if not isinstance(payload['tools'], dict):
            raise ValueError("'tools' must be a dictionary")
        
        for tool_name, tool_data in payload['tools'].items():
            required = ['serialized', 'description', 'parameters']
            for field in required:
                if field not in tool_data:
                    raise ValueError(f"Tool {tool_name} missing field: {field}")
        
        return True
    
    def compile_from_directory(self, project_dir: str) -> Dict[str, Any]:
        """
        Compile deployment from a project directory.
        
        Expects structure:
        project_dir/
        ├── agent.yaml
        └── tools/
            └── *.py
        
        Args:
            project_dir: Path to project directory
            
        Returns:
            Deployment payload
        """
        yaml_path = os.path.join(project_dir, 'agent.yaml')
        tools_dir = os.path.join(project_dir, 'tools')
        
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"No agent.yaml found in {project_dir}")
        
        return self.compile_from_yaml(yaml_path, tools_dir)


def parse_agent_yaml(yaml_content: str) -> Dict[str, Any]:
    """
    Parse agent configuration from YAML string.
    
    Args:
        yaml_content: YAML configuration string
        
    Returns:
        Parsed configuration dictionary
    """
    return yaml.safe_load(yaml_content)


def generate_deployment_json(payload: Dict[str, Any], output_path: str = None) -> str:
    """
    Generate deployment JSON for inspection/debugging.
    
    Args:
        payload: Deployment payload
        output_path: Optional path to save JSON
        
    Returns:
        JSON string
    """
    json_str = json.dumps(payload, indent=2)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(json_str)
    
    return json_str