import inspect
import json
from typing import get_type_hints


def python_type_to_json_type(py_type):
    mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
    }
    return mapping.get(py_type, "string")


def generate_tool_schema(func):
    sig = inspect.signature(func)
    hints = get_type_hints(func)

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        py_type = hints.get(name, str)

        properties[name] = {
            "type": python_type_to_json_type(py_type)
        }

        if param.default is inspect.Parameter.empty:
            required.append(name)

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


TOOL_REGISTRY = []


def tool(func):
    """
    Marks a function as an LLM tool and registers it.
    """
    TOOL_REGISTRY.append(func)
    return func


def build_tools():
    return [generate_tool_schema(f) for f in TOOL_REGISTRY]


def run_tool_call(tool_call):
    tool_map = {f.__name__: f for f in TOOL_REGISTRY}
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    return tool_map[name](**args)
