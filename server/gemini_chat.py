import os

from dotenv import load_dotenv
from google import genai
from gemini_tools import run_tool_cycle, tools_config


def main() -> int:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set in .env")
        return 1

    client = genai.Client(api_key=api_key)
    chat = client.chats.create(
        model="gemini-3.1-flash-lite-preview",
                config=tools_config(),
        )

    print("Gemini chat. Type /exit to quit.")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return 0

        if not user_input:
            continue
        if user_input.lower() in {"/exit", "/quit"}:
            print("Exiting.")
            return 0

        try:
            response = chat.send_message(user_input)
            response = run_tool_cycle(chat, response)
            print(f"Gemini: {response.text}")
        except Exception as exc:
            print(f"Error: {exc}")
            continue


if __name__ == "__main__":
    raise SystemExit(main())
