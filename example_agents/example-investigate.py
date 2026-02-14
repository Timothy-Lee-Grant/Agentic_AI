#!/usr/bin/env python3
"""
Minimal agent demo with a single "secret message" tool.
Run: python3 agent.py
"""

import json
import shlex
import subprocess
from typing import Any, Dict, Optional

# ---------- Simple secret-store tool ----------
class SecretStore:
    def __init__(self):
        self._secret: Optional[str] = None

    def set_secret(self, message: str) -> str:
        self._secret = message
        return "Secret saved."

    def get_secret(self) -> str:
        if self._secret is None:
            return "No secret stored."
        return self._secret

# ---------- Model interface (pluggable) ----------
def call_model(prompt: str) -> str:
    """
    MODEL HOOK - Replace or extend this with a real Ollama call.

    1) Current demo: a tiny deterministic "mock model" that returns predictable JSON
       so you can try the agent/tool workflow without any external dependencies.

    2) Example Ollama integration (commented, adapt to your setup):
       import subprocess, shlex
       cmd = f'ollama generate llama2 --prompt {shlex.quote(prompt)} --json'
       output = subprocess.check_output(shlex.split(cmd), text=True)
       return output

    IMPORTANT: When you plug in a real LLM, instruct it to ONLY reply with a JSON
    object with fields: {"tool": "<tool_name>", "args": {...}} (no extra text).
    """

    # ---- MOCK BEHAVIOR (simple rule-based): ----
    # If prompt contains "store" or "set secret", choose set_secret.
    prompt_low = prompt.lower()
    if "set secret" in prompt_low or "store secret" in prompt_low or "save secret" in prompt_low:
        # ask for a secret message via structured JSON
        return json.dumps({"tool": "set_secret", "args": {"message": "this is a demo secret"}})
    if "get secret" in prompt_low or "reveal secret" in prompt_low or "what is the secret" in prompt_low:
        return json.dumps({"tool": "get_secret", "args": {}})
    # Fallback: ask to get the secret
    return json.dumps({"tool": "get_secret", "args": {}})

# ---------- Agent core ----------
class Agent:
    def __init__(self, model_fn):
        self.model_fn = model_fn
        self.store = SecretStore()
        # tool mapping
        self.tools = {
            "set_secret": self._tool_set_secret,
            "get_secret": self._tool_get_secret,
        }

    # Tool wrappers:
    def _tool_set_secret(self, args: Dict[str, Any]) -> Dict[str, Any]:
        message = args.get("message")
        if message is None:
            return {"ok": False, "result": "Missing 'message' argument"}
        result = self.store.set_secret(str(message))
        return {"ok": True, "result": result}

    def _tool_get_secret(self, args: Dict[str, Any]) -> Dict[str, Any]:
        result = self.store.get_secret()
        return {"ok": True, "result": result}

    def run_once(self, user_instruction: str) -> Dict[str, Any]:
        """
        Perform one agent cycle:
        - Build a prompt describing the tools & last observation.
        - Ask model for action (must be strict JSON).
        - Execute tool and return result.
        """
        tool_list = [{"name": name, "args": list(fn.__code__.co_varnames)[:]} for name, fn in self.tools.items()]
        prompt = (
            "You are an agent controller. You MUST reply ONLY with a JSON object "
            'of the form {"tool": "<tool_name>", "args": {...}} and nothing else.\n\n'
            "Available tools:\n"
            "- set_secret: stores a secret message. args: {message: string}\n"
            "- get_secret: returns the stored secret. args: {}\n\n"
            f"User instruction: {user_instruction}\n\n"
            "Respond with the tool call to accomplish the user's instruction."
        )

        model_response = self.model_fn(prompt)
        # If model returns a JSON string, parse it
        try:
            action = json.loads(model_response)
        except json.JSONDecodeError:
            return {"ok": False, "error": "Model response was not valid JSON", "raw": model_response}

        tool = action.get("tool")
        args = action.get("args", {})

        if tool not in self.tools:
            return {"ok": False, "error": f"Unknown tool '{tool}'", "action": action}

        # Execute tool
        try:
            tool_result = self.tools[tool](args)
            return {"ok": True, "action": action, "tool_result": tool_result}
        except Exception as e:
            return {"ok": False, "error": f"Tool execution raised: {e}", "action": action}

# ---------- Simple CLI to try it ----------
def main():
    agent = Agent(call_model)

    print("Tiny agent demo with secret-store tool.")
    print("Examples you can type:\n - set secret to <your message>\n - get secret\n - reveal secret\n - quit\n")

    while True:
        user = input(">>> ").strip()
        if user in ("quit", "exit"):
            break
        result = agent.run_once(user)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
