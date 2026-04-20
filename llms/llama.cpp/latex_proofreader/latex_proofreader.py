#!/usr/bin/env python3

# /// script
# dependencies = [
#   "openai",
#   "rich",
# ]
# ///

import argparse
from typing import Optional
from openai import OpenAI
from pathlib import Path
import logging
import os
import sys

from progress import ProgressManager
import time

from file_manager import tool_list_files, LATEX_DIRECTORIES, LATEX_AUX_DIRECTORIES, LATEX_AUX_FILES, FILTER_DIRS
from log_manager import setup_logging
from tool import tool, build_tools, TOOL_REGISTRY
from llm import llm_plan


FILTER_DIRS = {"build", "dist"}

MAX_ITERATIONS = 10


def get_llm_response(client: OpenAI, tools, model: str, prompt: str):
    with ProgressManager() as pm:
        try:
            message = llm_plan(client, tools, model, prompt, pm=pm)
            return message
        except Exception as e:
            print(f"Error: {e}")
            return None


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="latex_proofreader (llama.cpp)")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.0.1"
    )
    parser.add_argument("-p", "--port", nargs="?", default=8080, help="webserver port (default: %(default)s, llama.cpp)")
    parser.add_argument("-m", "--model", help="loaded model")
    parser.add_argument("-ad", "--auxiliary_dir", default=[], nargs="*", help="other directories helpful to understand project")
    parser.add_argument("-af", "--auxiliary_file", default=[], nargs="*", help="other files helpful to understand project")
    parser.add_argument("src", default=os.getcwd(), help="latex directory (default: %(default)s)", nargs="?")
    parser.add_argument("command", default="check", help="command")
    parser.add_argument("--prompt", default="Check the files of this LaTeX project", help="prompt", nargs="?")

    # parse arguments
    args = parser.parse_args()
    logger.debug(args)

    # create local OpenAI client (api key must be set but will be ignored)
    client = OpenAI(
        base_url=f"http://localhost:{args.port}/v1",
        api_key="ignored-by-local-server",
    )
    model = args.model

    # TODO Add tool to list all LaTeX files in a directory
    latex_directories = [Path(args.src)]
    latex_directories_help = [*args.auxiliary_dir]
    latex_files_help = [*args.auxiliary_file]

    LATEX_DIRECTORIES.clear()
    LATEX_DIRECTORIES.extend(latex_directories)
    LATEX_AUX_DIRECTORIES.clear()
    LATEX_AUX_DIRECTORIES.extend(latex_directories_help)
    LATEX_AUX_FILES.clear()
    LATEX_AUX_FILES.extend(latex_files_help)

    # TODO Add tool to read/write LaTeX files
    # TODO Add prompt that grammar checks all files
    # TODO Add prompt that checks if the content makes sense
    # TODO Add tool that can provide additional resources like PDF files or HTML files for context (for better logic checks)
    # TODO Research OpenAI Response Format
    # TODO Make sure that the context is not overflowing

    tools = build_tools()
    logger.debug(tools)

    if args.command == "info":
        print(args)

        print("latex directories:")
        for latex_dir in latex_directories:
            print(f"- {latex_dir!r}")

        print("latex directories:")
        for latex_dir in latex_directories_help:
            print(f"- {latex_dir!r}")

        print("latex help files:")
        for latex_file in latex_files_help:
            print(f"- {latex_file!r}")

        print("tools:")
        for tool in tools:
            print(f"- {tool['function']['name']}: {tool['function']['description']}")

        print("tool_list_files:")
        print(LATEX_DIRECTORIES + LATEX_AUX_DIRECTORIES)
        print(tool_list_files())

    elif args.command == "check":
        message = get_llm_response(client, tools, model, args.prompt)
        print(message)
    else:
        print("Unsupported command!")



        console = Console()

        start = time.perf_counter()
        with Status("Main task...", spinner="dots") as main_status:
            time.sleep(1)

            with Status("Subtask A...", spinner="bouncingBar"):
                time.sleep(1)

            with Status("Subtask B...", spinner="bouncingBar"):
                time.sleep(1)

            main_status.update("Finalizing...")
            time.sleep(1)
        elapsed = time.perf_counter() - start
        console.print(f"[green]✔ Done in {elapsed:.2f}s[/green]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            transient=True,
        ) as progress:

            task = progress.add_task("Processing...", total=None)

            time.sleep(2.5)

            progress.stop_task(task)
        time.sleep(2.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(-1)
