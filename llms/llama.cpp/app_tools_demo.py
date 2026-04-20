#!/usr/bin/env python3

# /// script
# dependencies = [
#   "openai",
# ]
# ///


import argparse
import json
import inspect
from typing import get_type_hints
from typing import Optional
from openai import OpenAI


# > Boilerplate code for easy conversion from function to tool definition
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
# < Boilerplate code


TOOL_REGISTRY = []

def tool(func):
    """
    Marks a function as an LLM tool and registers it.
    """
    TOOL_REGISTRY.append(func)
    return func


@tool
def tool_reverse_text(text: str) -> str:
    """
    Reverse a string
    """
    return text[::-1]

@tool
def tool_read_markdown_todo_file(text: str) -> str:
    """
    Read TODOs from a Markdown file
    """
    with open("todos.md", "r", encoding="utf-8") as f:
        return f.readlines()

@tool
def tool_write_markdown_todo_file(text: str) -> str:
    """
    Write TODOs to a Markdown file (use a list with '- [ ]' and '- [x]' and add '# TODOs' as heading)
    """
    with open("todos.md", "w", encoding="utf-8") as f:
        f.writelines(text)


def build_tools():
    return [generate_tool_schema(f) for f in TOOL_REGISTRY]


def run_tool_call(tool_call):
    tool_map = {f.__name__: f for f in TOOL_REGISTRY}
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    return tool_map[name](**args)


def get_llm_response(client: OpenAI, tools, model: str, prompt: str, system_prompt: Optional[str] = None):
    MAX_ITERATIONS = 4

    try:
        messages = [
            {"role": "system", "content": system_prompt or "Use tools when helpful."},
            {"role": "user", "content": prompt},
        ]

        for i in range(MAX_ITERATIONS):
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                temperature=0.7,
            )

            message = response.choices[0].message

            # If no tool call → we're done
            if not message.tool_calls:
                return message.content

            # Append assistant message (with tool call)
            messages.append(message)

            # Execute ALL tool calls (not just first)
            for tool_call in message.tool_calls:
                print(f"[iter {i}] tool call: {tool_call.function.name}({tool_call.function.arguments})")

                try:
                    result = run_tool_call(tool_call)
                except Exception as e:
                    result = f"Error executing tool: {e}"

                # Append tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })

        # If loop exits → max iterations reached
        return "Max iterations reached without final response."

    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="app_tools_demo (llama.cpp)")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.0.1"
    )
    parser.add_argument("-p", "--port", nargs="?", default=8080, help="webserver port (default: %(default)s, llama.cpp)")
    parser.add_argument("-m", "--model", required=True, help="loaded model")
    parser.add_argument("--system", help="system prompt")
    parser.add_argument("prompt", help="prompt")

    args = parser.parse_args()
    print(args)

    client = OpenAI(
        base_url=f"http://localhost:{args.port}/v1",
        api_key="ignored-by-local-server",
    )

    tools = build_tools()
    print("tools:")
    for tool in tools:
        print(f"- {tool["function"]["name"]}: {tool["function"]["description"]}")

    response = get_llm_response(client, tools, args.model, args.prompt, args.system)
    print(response)


if __name__ == "__main__":
    main()