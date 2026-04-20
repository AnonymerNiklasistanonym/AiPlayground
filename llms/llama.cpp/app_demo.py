#!/usr/bin/env python3

# /// script
# dependencies = [
#   "openai",
# ]
# ///

import argparse
from typing import Optional
from openai import OpenAI


def get_llm_response(client: OpenAI, model: str, prompt: str, system_prompt: Optional[str]=None):
    try:
        # The client methods match the standard OpenAI library calls
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt or "instead of giving empty responses return prompt was too short"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            #max_tokens=150,
        )
        # Extract the content from the structured response
        generated_text = response.choices[0].message.content
        return generated_text
    except IndexError:
        print("Error: No choices found in the response.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the response: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="app_demo (llama.cpp)")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.0.1"
    )
    parser.add_argument("-p", "--port", nargs="?", default=8080, help="webserver port (default: %(default)s, llama.cpp)")
    parser.add_argument("-m", "--model", required=True, help="loaded model")
    parser.add_argument("--system", help="system prompt")
    parser.add_argument("prompt", help="prompt")

    # parse arguments
    args = parser.parse_args()
    print(args)

    # create local OpenAI client (api key must be set but will be ignored)
    client = OpenAI(
        base_url=f"http://localhost:{args.port}/v1",
        api_key="ignored-by-local-server",
    )

    response = get_llm_response(client, args.model, args.prompt, args.system)
    print(response)


if __name__ == "__main__":
    main()
