"""
FlowStack Tool Support

Provides decorators and utilities for working with FlowStack tools.
Tools are Python functions that can be executed by AI agents.
"""

import inspect
import typing
from typing import Callable, Any, Dict, Optional, get_type_hints
import ast
import json


def tool(func: Callable = None, *, description: str = None) -> Callable:
    """
    Decorator to mark a function as a FlowStack tool.
    
    This decorator is optional - the SDK can discover all functions
    in a tools directory. Use it when you want to explicitly mark
    functions or add metadata.
    
    Args:
        func: The function to decorate
        description: Optional description override
        
    Returns:
        The decorated function with metadata attached
        
    Example:
        @tool(description="Adds two numbers together")
        def add(x: float, y: float) -> float:
            return x + y
    """
    def decorator(f: Callable) -> Callable:
        # Attach metadata to the function
        f._is_flowstack_tool = True
        f._tool_description = description
        return f
    
    if func is None:
        # Called with arguments: @tool(description="...")
        return decorator
    else:
        # Called without arguments: @tool
        return decorator(func)


def extract_tool_source(func: Callable) -> str:
    """
    Extract the source code of a function using inspect.
    
    Args:
        func: The function to extract
        
    Returns:
        The source code as a string
        
    Raises:
        ValueError: If source cannot be extracted
    """
    try:
        source = inspect.getsource(func)
        # Remove any decorators from the source
        lines = source.split('\n')
        
        # Find the first line that starts with 'def'
        def_index = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                def_index = i
                break
        
        # Return source from the def line onwards
        return '\n'.join(lines[def_index:])
    except (TypeError, OSError) as e:
        raise ValueError(f"Cannot extract source for function {func.__name__}: {e}")


def parse_tool_metadata(func: Callable) -> Dict[str, Any]:
    """
    Extract metadata from a function including description and parameters.
    
    Args:
        func: The function to analyze
        
    Returns:
        Dictionary containing:
        - name: Function name
        - description: From docstring or decorator
        - parameters: JSON schema of parameters
    """
    # Get function name
    name = func.__name__
    
    # Get description from decorator or docstring
    description = getattr(func, '_tool_description', None)
    if not description:
        description = inspect.getdoc(func) or f"Function {name}"
    
    # Get type hints
    type_hints = get_type_hints(func)
    
    # Build parameter schema
    signature = inspect.signature(func)
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    for param_name, param in signature.parameters.items():
        if param_name == 'self':
            continue
            
        # Get type from hints or default to string
        param_type = type_hints.get(param_name, str)
        
        # Convert Python type to JSON schema type
        json_type = python_type_to_json_schema(param_type)
        
        parameters["properties"][param_name] = json_type
        
        # Mark as required if no default value
        if param.default == inspect.Parameter.empty:
            parameters["required"].append(param_name)
    
    return {
        "name": name,
        "description": description,
        "parameters": parameters
    }


def python_type_to_json_schema(python_type: type) -> Dict[str, str]:
    """
    Convert Python type to JSON schema type.
    
    Args:
        python_type: Python type hint
        
    Returns:
        JSON schema type definition
    """
    type_mapping = {
        int: {"type": "integer"},
        float: {"type": "number"},
        str: {"type": "string"},
        bool: {"type": "boolean"},
        list: {"type": "array"},
        dict: {"type": "object"},
        type(None): {"type": "null"}
    }
    
    # Handle Optional types
    origin = typing.get_origin(python_type)
    if origin is typing.Union:
        args = typing.get_args(python_type)
        # Check if it's Optional (Union with None)
        if type(None) in args:
            # Get the non-None type
            non_none_types = [t for t in args if t != type(None)]
            if len(non_none_types) == 1:
                schema = python_type_to_json_schema(non_none_types[0])
                # Don't mark as required in parent schema
                return schema
    
    # Handle List, Dict generics
    if origin is list:
        return {"type": "array"}
    if origin is dict:
        return {"type": "object"}
    
    # Default mapping
    return type_mapping.get(python_type, {"type": "string"})


def validate_tool_function(func: Callable) -> bool:
    """
    Validate that a function can be used as a FlowStack tool.
    
    Args:
        func: Function to validate
        
    Returns:
        True if valid, raises ValueError otherwise
    """
    # Check it's a function
    if not callable(func):
        raise ValueError(f"{func} is not callable")
    
    # Check we can extract source
    try:
        source = extract_tool_source(func)
        if not source:
            raise ValueError(f"Empty source for {func.__name__}")
    except Exception as e:
        raise ValueError(f"Cannot extract source for {func.__name__}: {e}")
    
    # Check for dangerous operations
    forbidden = ['exec', 'eval', '__import__', 'compile', 'open']
    source_lower = source.lower()
    for forbidden_func in forbidden:
        if forbidden_func in source_lower:
            raise ValueError(f"Function {func.__name__} contains forbidden operation: {forbidden_func}")
    
    # Parse to check syntax
    try:
        ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax in {func.__name__}: {e}")
    
    return True


def discover_tools(directory: str) -> Dict[str, Callable]:
    """
    Discover all tool functions in a directory.
    
    Args:
        directory: Path to directory containing Python files
        
    Returns:
        Dictionary mapping function names to functions
    """
    import os
    import importlib.util
    
    tools = {}
    
    # Scan directory for Python files
    for filename in os.listdir(directory):
        if filename.endswith('.py') and not filename.startswith('_'):
            filepath = os.path.join(directory, filename)
            module_name = filename[:-3]  # Remove .py
            
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find all functions in module
                for name, obj in inspect.getmembers(module):
                    if inspect.isfunction(obj) and not name.startswith('_'):
                        # Only include functions defined in this module
                        if obj.__module__ == module_name:
                            tools[name] = obj
    
    return tools