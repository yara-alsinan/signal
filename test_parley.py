"""Run locally to test MIT Parley. Never prints or saves the API key.

This script reads .env.local only when you run it. It sends the key solely as
the Authorization header to the fixed MIT endpoint, with redirects disabled.
It makes one short request, which may consume a small amount of Parley credit.
"""

import argparse
import json
import socket
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


ENDPOINT = "https://parley.api.mit.edu/v1/chat/completions"
MODEL = "claude-haiku-4-5"


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def load_local_key():
    """Read the confirmed local file without logging its contents."""
    path = Path(__file__).resolve().parent / ".env.local"
    if path.is_symlink():
        raise ValueError("The key file must be a regular local file.")
    try:
        contents = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValueError("The local key file was not found.") from None
    if contents.lstrip().startswith("{\\rtf"):
        raise ValueError("The key file is rich text. Save it as plain text locally.")
    lines = contents.splitlines()
    for line in lines:
        name, separator, value = line.strip().partition("=")
        if separator and name == "PARLEY_API_KEY":
            key = value.strip().strip("\"'")
            if not key or key == "PASTE_YOUR_KEY_HERE":
                raise ValueError("The local key file still needs your Parley key.")
            if any(character in key for character in ("\u201c", "\u201d", "\u2018", "\u2019")):
                raise ValueError("Remove curly quotation marks surrounding the key in the local file.")
            return key
    raise ValueError("PARLEY_API_KEY is missing from the local file.")


def main():
    parser = argparse.ArgumentParser(description="One-request MIT Parley connection test")
    parser.add_argument("--bearer", action="store_true", help="Test Bearer-prefixed authentication instead of the supplied raw-key example")
    args = parser.parse_args()
    try:
        key = load_local_key()
    except ValueError as error:
        print("Setup:", error)
        return 1
    except (OSError, UnicodeError):
        print("Setup: Unable to read the local plain-text key file. Do not share its contents.")
        return 1

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Reply with exactly: Signal connection successful."}],
        "max_tokens": 32,
    }
    # Default follows the user's Parley example. --bearer explicitly tests an
    # alternative format; it is not a claim that MIT requires that format.
    authorization = key
    if args.bearer and not key.lower().startswith("bearer "):
        authorization = "Bearer " + key
    request = Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": authorization, "Content-Type": "application/json"},
        method="POST",
    )
    print("Sending one short request to MIT Parley...")
    try:
        with build_opener(NoRedirects()).open(request, timeout=45) as response:
            data = json.load(response)
    except HTTPError as error:
        messages = {
            400: "The request format or model settings were rejected.",
            401: "Authentication failed. Check the key locally; do not paste it into chat.",
            403: "The account or key may not have access to this model.",
            402: "The account may need available credit or billing authorization.",
            429: "A rate limit or quota was reached. Check the Parley account dashboard.",
        }
        print("HTTP", error.code, messages.get(error.code, "Parley could not complete the request."))
        print("No raw error response, request headers, or key have been displayed or saved.")
        return 1
    except (URLError, TimeoutError, socket.timeout):
        print("Connection failed or timed out. Check your connection and MIT access requirements.")
        return 1
    except (ValueError, OSError):
        print("Parley returned an unreadable response. No raw response has been displayed.")
        return 1

    if not isinstance(data, dict):
        print("Unexpected response format. No raw response has been displayed.")
        return 1
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        print("No completion was returned. Check model access in Parley.")
        return 1
    message = choices[0].get("message", {})
    if not isinstance(message, dict) or not isinstance(message.get("content"), str) or not message["content"].strip():
        print("A response arrived, but it contained no readable text completion.")
        return 1
    print("SUCCESS: Parley returned a text completion.")
    print("Requested model:", MODEL)
    usage = data.get("usage", {})
    if isinstance(usage, dict):
        for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
            value = usage.get(field)
            if isinstance(value, int) and not isinstance(value, bool):
                print(field + ":", value)
    print("The key and raw response were not displayed or saved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
