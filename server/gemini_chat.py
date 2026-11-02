"""Chat with Adiutor in the terminal (no web UI needed).

    python gemini_chat.py
"""

import asyncio
import os

from dotenv import load_dotenv
from google import genai

from db import init_db
from gemini_tools import stream_chat


async def main() -> int:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set in .env")
        return 1

    init_db()
    client = genai.Client(api_key=api_key)
    history: list[dict] = []

    print("Adiutor chat. Type /exit to quit.")
    while True:
        try:
            user_input = (await asyncio.to_thread(input, "You: ")).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return 0

        if not user_input:
            continue
        if user_input.lower() in {"/exit", "/quit"}:
            print("Exiting.")
            return 0

        answer = []
        print("Adiutor: ", end="", flush=True)
        try:
            async for event in stream_chat(client, user_input, history):
                if event["type"] == "text":
                    answer.append(event["delta"])
                    print(event["delta"], end="", flush=True)
                elif event["type"] == "tool":
                    print(f"\n  [{event['label']}]", flush=True)
            print()
        except Exception as exc:
            print(f"\nError: {exc}")
            continue

        history.append({"role": "user", "text": user_input})
        history.append({"role": "assistant", "text": "".join(answer)})


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
