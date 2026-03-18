#!/usr/bin/env python3
"""CLI tool for interacting with Gandalf challenge API."""

import argparse
import json
import os
import sys
from datetime import datetime

import requests

API_URL = "https://gandalf-api.lakera.ai/api/send-message"
DEFAULT_DEFENDER = "gandalf-the-white"
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gandalf_log.json")
COOKIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.json")

HEADERS = {
    "accept": "application/json",
    "origin": "https://gandalf.lakera.ai",
    "referer": "https://gandalf.lakera.ai/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
}


def load_cookies():
    """Load cookies from cookies.json if it exists."""
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE) as f:
            return json.load(f)
    return {}


def send_message(prompt, defender=DEFAULT_DEFENDER, cookies=None):
    """Send a prompt to the Gandalf API and return the response."""
    data = {
        "defender": defender,
        "prompt": prompt,
    }
    resp = requests.post(
        API_URL,
        data=data,
        headers=HEADERS,
        cookies=cookies or {},
    )
    resp.raise_for_status()
    response = resp.json()
    log_interaction(prompt, response, defender)
    return response


def log_interaction(prompt, response, defender):
    """Append interaction to the log file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "defender": defender,
        "prompt": prompt,
        "response": response,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Gandalf Challenge CLI")
    parser.add_argument("prompt", nargs="?", help="Prompt to send (or use interactive mode)")
    parser.add_argument("-d", "--defender", default=DEFAULT_DEFENDER, help=f"Defender name (default: {DEFAULT_DEFENDER})")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--no-log", action="store_true", help="Disable logging")
    args = parser.parse_args()

    cookies = load_cookies()

    if args.interactive:
        print("Gandalf CLI - Interactive Mode (Ctrl+C to exit)")
        print(f"Defender: {args.defender}")
        print(f"Logging to: {LOG_FILE}")
        print("-" * 50)
        while True:
            try:
                prompt = input("\n> ").strip()
                if not prompt:
                    continue
                response = send_message(prompt, args.defender, cookies)
                answer = response.get("answer", "No answer")
                print(f"\nGandalf: {answer}")
            except KeyboardInterrupt:
                print("\nBye!")
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
    elif args.prompt:
        response = send_message(args.prompt, args.defender, cookies)
        answer = response.get("answer", "No answer")
        print(answer)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
