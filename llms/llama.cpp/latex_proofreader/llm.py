from pathlib import Path
from typing import Optional
from openai import OpenAI
import logging
from rich.console import Console
from rich.status import Status

from tool import tool, run_tool_call

ROOT_DIR = Path(__file__).parent
PROMPT_PLAN = ROOT_DIR / "prompts" / "plan.md"
PROMPT_CHECK = ROOT_DIR / "prompts" / "check.md"

CLIENT: Optional[OpenAI] = None
TOOLS = []
MODEL: Optional[str] = None
PM = None

MAX_ITERATIONS_CHECK = 10
MAX_ITERATIONS_PLAN = 100

logger = logging.getLogger(__name__)


@tool
def tool_delegate_file_check(file: str, prompt: str) -> str:
    """
    Delegate the file check to another agent given the file path and a crafted prompt for the agent
    """
    llm_check(CLIENT, TOOLS, MODEL, prompt, file, PM)


def llm_check(client: OpenAI, tools, model: str, prompt: str, file: str, pm):
    """Plan execution"""
    logger.debug(f"llm_check: {prompt!r} ({file=!r}, {model=!r})")
    with pm.task(f"llm_check: {file.split('/')[-1]!r}"):

        with open(PROMPT_CHECK) as f:
            prompt_check = f.read()

        messages = [
            {"role": "system", "content": prompt_check},
            {"role": "user", "content": prompt + f"\n\nFile: {file}"},
        ]

        for i in range(MAX_ITERATIONS_CHECK):
            with pm.task(f"Query {model} [{i}]"):
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=tools,
                    temperature=0.7,
                )

            message = response.choices[0].message
            logger.debug(f"[iter {i}] message: {message!r}")

            # If no tool call → we're done
            if not message.tool_calls:
                return message.content

            # Append assistant message (with tool call)
            messages.append(message)

            # Execute ALL tool calls
            for tool_call in message.tool_calls:
                logger.debug(f"[iter {i}] tool call: {tool_call.function.name}({tool_call.function.arguments})")
                with pm.task(f"Tool Call: {tool_call.function.name}()"):
                    try:
                        result = run_tool_call(tool_call)
                    except Exception as e:
                        result = f"Error executing tool: {e}"
                logger.debug(f"[iter {i}] tool call result: {result!r}")

                # Append tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })

            if i == MAX_ITERATIONS_CHECK - 2:
                messages.append({
                    "role": "user",
                    "content": "This is the last try, come to a conclusion.",
                })

    # If loop exits → max iterations reached
    return f"[{file}] Max iterations ({MAX_ITERATIONS_CHECK}) reached without final response."


def llm_plan(client: OpenAI, tools, model: str, prompt: str, pm):
    """Plan execution"""
    logger.debug(f"llm_plan: {prompt!r} ({model=!r})")
    with pm.task(f"llm_plan: {prompt!r} ({model=!r})"):

        global CLIENT
        CLIENT = client
        global TOOLS
        TOOLS = tools
        global MODEL
        MODEL = model
        global PM
        PM = pm

        with open(PROMPT_PLAN) as f:
            prompt_plan = f.read()
        with open(PROMPT_CHECK) as f:
            prompt_check = f.read()

        messages = [
            {"role": "system", "content": prompt_plan},
            {"role": "user", "content": f"This is the system prompt that each agent already gets:\n\n{prompt_check}"},
            {"role": "user", "content": prompt},
        ]

        for i in range(MAX_ITERATIONS_PLAN):
            with pm.task(f"Query {model} [{i}]"):
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=tools,
                    temperature=0.7,
                )

            message = response.choices[0].message
            logger.debug(f"[iter {i}] message: {message!r}")

            # If no tool call → we're done
            if not message.tool_calls:
                return message.content

            # Append assistant message (with tool call)
            messages.append(message)

            # Execute ALL tool calls (not just first)
            for tool_call in message.tool_calls:
                logger.debug(f"[iter {i}] tool call: {tool_call.function.name}({tool_call.function.arguments})")
                with pm.task(f"Tool Call: {tool_call.function.name}()"):
                    try:
                        result = run_tool_call(tool_call)
                    except Exception as e:
                        result = f"Error executing tool: {e}"
                logger.debug(f"[iter {i}] tool call result: {result!r}")

                # Append tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })


            if i == MAX_ITERATIONS_PLAN - 2:
                messages.append({
                    "role": "user",
                    "content": "This is the last try, come to a conclusion.",
                })

    # If loop exits → max iterations reached
    return f"Max iterations ({MAX_ITERATIONS_PLAN}) reached without final response."
