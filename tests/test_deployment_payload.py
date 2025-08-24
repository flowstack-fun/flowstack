"""
Test deployment payload generation to ensure it matches infrastructure expectations.
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flowstack.deployment import DeploymentBuilder
from flowstack.tools import tool, extract_tool_source, parse_tool_metadata


class TestDeploymentPayload(unittest.TestCase):
    """Test that deployment payloads match expected infrastructure format"""
    
    def setUp(self):
        """Set up test environment"""
        self.builder = DeploymentBuilder("test_api_key", "https://api.flowstack.fun")
        
    def test_basic_payload_structure(self):
        """Test basic payload has required top-level fields"""
        config = {
            'name': 'test-agent',
            'instructions': 'You are a test agent',
            'model': 'claude-3-sonnet',
            'temperature': 0.7
        }
        
        payload = self.builder.compile_deployment(config)
        
        # Check top-level structure
        self.assertIn('agents', payload)
        self.assertIn('tools', payload)
        self.assertIsInstance(payload['agents'], list)
        self.assertIsInstance(payload['tools'], dict)
        
    def test_agent_configuration(self):
        """Test agent configuration matches expected format"""
        config = {
            'name': 'test-agent',
            'instructions': 'You are a helpful assistant',
            'model': 'claude-3-sonnet',
            'temperature': 0.8,
            'provider': 'bedrock'
        }
        
        payload = self.builder.compile_deployment(config)
        
        # Check agent structure
        self.assertEqual(len(payload['agents']), 1)
        agent = payload['agents'][0]
        
        self.assertEqual(agent['name'], 'test-agent')
        self.assertEqual(agent['system_prompt'], 'You are a helpful assistant')
        self.assertEqual(agent['model'], 'claude-3-sonnet')
        self.assertEqual(agent['temperature'], 0.8)
        self.assertIn('tools', agent)
        self.assertIsInstance(agent['tools'], list)
        
    def test_tool_compilation(self):
        """Test tool extraction and compilation"""
        # Create test function
        def add(x: float, y: float) -> float:
            """Add two numbers together"""
            return x + y
        
        # Extract and parse
        source = extract_tool_source(add)
        metadata = parse_tool_metadata(add)
        
        # Check extraction
        self.assertIn('def add', source)
        self.assertIn('return x + y', source)
        
        # Check metadata
        self.assertEqual(metadata['name'], 'add')
        self.assertEqual(metadata['description'], 'Add two numbers together')
        self.assertIn('properties', metadata['parameters'])
        self.assertIn('x', metadata['parameters']['properties'])
        self.assertIn('y', metadata['parameters']['properties'])
        
    def test_full_deployment_payload(self):
        """Test complete deployment payload with tools"""
        # Create temp directory with tools
        with tempfile.TemporaryDirectory() as tmpdir:
            tools_dir = Path(tmpdir) / 'tools'
            tools_dir.mkdir()
            
            # Create tool file
            tool_code = '''
def multiply(x: float, y: float) -> float:
    """Multiply two numbers"""
    return x * y

def divide(x: float, y: float) -> float:
    """Divide x by y"""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y
'''
            with open(tools_dir / 'math.py', 'w') as f:
                f.write(tool_code)
            
            # Create configuration
            config = {
                'name': 'calculator',
                'instructions': 'You are a calculator',
                'model': 'claude-3-sonnet',
                'temperature': 0.5,
                'tools': {
                    'multiply': {
                        'description': 'Multiply numbers',
                        'instructions': 'Use for multiplication'
                    },
                    'divide': {
                        'description': 'Divide numbers',
                        'instructions': 'Check for zero division'
                    }
                }
            }
            
            # Compile deployment
            payload = self.builder.compile_deployment(config, str(tools_dir))
            
            # Validate payload
            self.assertTrue(self.builder.validate_payload(payload))
            
            # Check tools were compiled
            self.assertIn('multiply', payload['tools'])
            self.assertIn('divide', payload['tools'])
            
            # Check tool structure
            multiply_tool = payload['tools']['multiply']
            self.assertIn('serialized', multiply_tool)
            self.assertIn('description', multiply_tool)
            self.assertIn('parameters', multiply_tool)
            self.assertIn('def multiply', multiply_tool['serialized'])
            
            # Check agent has tool references
            agent = payload['agents'][0]
            self.assertIn('multiply', agent['tools'])
            self.assertIn('divide', agent['tools'])
    
    def test_yaml_configuration(self):
        """Test loading from YAML configuration"""
        yaml_content = """
name: test-agent
instructions: |
  You are a helpful assistant.
  Be concise and accurate.
model: claude-3-sonnet
provider: bedrock
temperature: 0.7
tools:
  calculator:
    description: Math operations
    instructions: Use for calculations
"""
        
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / 'agent.yaml'
            with open(yaml_path, 'w') as f:
                f.write(yaml_content)
            
            config = self.builder.load_yaml_config(str(yaml_path))
            
            self.assertEqual(config['name'], 'test-agent')
            self.assertIn('You are a helpful assistant', config['instructions'])
            self.assertEqual(config['model'], 'claude-3-sonnet')
            self.assertEqual(config['temperature'], 0.7)
    
    def test_payload_validation(self):
        """Test payload validation catches errors"""
        # Invalid payload - missing agents
        invalid_payload = {
            'tools': {}
        }
        
        with self.assertRaises(ValueError) as context:
            self.builder.validate_payload(invalid_payload)
        self.assertIn("missing 'agents'", str(context.exception).lower())
        
        # Invalid payload - agent missing name
        invalid_payload = {
            'agents': [{'system_prompt': 'test'}],
            'tools': {}
        }
        
        with self.assertRaises(ValueError) as context:
            self.builder.validate_payload(invalid_payload)
        self.assertIn("missing required field: name", str(context.exception).lower())
        
        # Invalid payload - tool missing serialized
        invalid_payload = {
            'agents': [{'name': 'test', 'system_prompt': 'test', 'tools': []}],
            'tools': {
                'test_tool': {
                    'description': 'test'
                }
            }
        }
        
        with self.assertRaises(ValueError) as context:
            self.builder.validate_payload(invalid_payload)
        self.assertIn("missing field: serialized", str(context.exception).lower())
    
    def test_expected_infrastructure_format(self):
        """Test that payload exactly matches infrastructure expectations"""
        # This is the format the deployment-manager Lambda expects
        expected_structure = {
            "agents": [{
                "name": "customer-support",
                "system_prompt": "You are a helpful assistant",
                "tools": ["add", "multiply"],
                "temperature": 0.7,
                "model": "claude-3-sonnet"
            }],
            "tools": {
                "add": {
                    "serialized": "def add(x, y): return x + y",
                    "description": "Add two numbers",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"}
                        },
                        "required": ["x", "y"]
                    }
                }
            }
        }
        
        # Validate this structure passes validation
        self.assertTrue(self.builder.validate_payload(expected_structure))


if __name__ == '__main__':
    unittest.main()