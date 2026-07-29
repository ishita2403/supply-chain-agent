# src/supply_chain_agent/reasoning/llm_client.py

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"
REQUEST_TIMEOUT_SECONDS = 15  # fail fast rather than hang a request indefinitely


def call_ollama(prompt: str) -> str | None:
    """
    Calls the local Ollama server. Returns None on ANY failure (not running,
    not installed, timeout, unexpected response) -- callers MUST treat None
    as 'fall back to template', never as an error to propagate/crash on.
    This is a deliberate resilience boundary: LLM unavailability should
    never take down the core explanation feature (Section 2.2).
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip() or None
    except (requests.RequestException, ValueError):
        return None