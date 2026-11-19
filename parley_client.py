"""Minimal MIT-only transport. Key is loaded only when a user starts a live run."""

import json
import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

from test_parley import ENDPOINT, MODEL, NoRedirects, load_local_key


class ParleyError(Exception):
    pass


class ParleyClient:
    def __init__(self):
        # No credential is sent to prompts, printed, or written to an output file.
        key = load_local_key()
        self._authorization = key if key.lower().startswith("bearer ") else "Bearer " + key

    def complete(self, messages, tools, first=False):
        payload = {
            "model": MODEL, "messages": messages, "tools": tools,
            "tool_choice": "required" if first else "auto", "max_tokens": 1200,
        }
        request = Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"), method="POST",
                          headers={"Authorization": self._authorization, "Content-Type": "application/json"})
        try:
            with build_opener(NoRedirects()).open(request, timeout=60) as response:
                data = json.load(response)
        except HTTPError as error:
            raise ParleyError("Parley returned HTTP %s. No raw error or credentials displayed." % error.code) from None
        except (URLError, TimeoutError, socket.timeout, OSError):
            raise ParleyError("Parley connection failed or timed out. No automatic retry was made.") from None
        except ValueError:
            raise ParleyError("Parley returned an unreadable response.") from None
        if not isinstance(data, dict) or not data.get("choices"):
            raise ParleyError("Parley returned no completion. Tool-calling access may need checking.")
        return data
