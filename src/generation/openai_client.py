# src/generation/openai_client.py
"""
OpenAI wrapper that supports both:
 - modern openai >= 1.0.0 API (from openai import OpenAI; client.chat.create(...))
 - legacy openai 0.28.x API (openai.ChatCompletion.create(...))

It uses a simple exponential backoff for transient errors and falls back
to the available API so the codebase can run with either client installed.
"""

from typing import Optional
import time
import random
import logging

LOGGER = logging.getLogger(__name__)

MAX_RETRIES = 4
BASE_BACKOFF_SECONDS = 1.0

def _sleep_with_backoff(attempt: int) -> None:
    # exponential backoff with jitter
    backoff = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
    jitter = random.uniform(0, backoff * 0.2)
    sleep_for = backoff + jitter
    LOGGER.debug("Backoff: sleeping %.2fs (attempt %d)", sleep_for, attempt)
    time.sleep(sleep_for)

def _is_transient_error(exc: Exception) -> bool:
    # Best-effort detection: many OpenAI transient errors mention 'Rate' or 'timeout' or 'temporar'
    msg = str(exc).lower()
    return any(k in msg for k in ("rate", "timeout", "temporar", "429", "timed out", "connection"))

def call_openai_chat(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 400, temperature: float = 0.7) -> str:
    """
    Call the OpenAI chat completion API in a way that supports both
    the modern and legacy openai Python clients.

    Returns the assistant's content (string) on success, otherwise raises.
    """
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    # 1) Prefer the modern client if available (openai>=1.0.0)
    try:
        try:
            from openai import OpenAI  # type: ignore
            client = OpenAI()
            LOGGER.debug("Using modern OpenAI client (openai>=1.0)")
            def _req():
                resp = client.chat.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                # modern response: resp.choices[0].message.content
                # guard for possible differences
                try:
                    return resp.choices[0].message.content
                except Exception:
                    # some versions return dict-like object
                    return resp["choices"][0]["message"]["content"]
        except Exception as exc_modern:
            # If modern client import or call setup fails, fallback to legacy
            LOGGER.debug("Modern openai client not available or failed to initialize: %s", exc_modern)
            raise

        # attempt with backoff
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return _req()
            except Exception as e:
                LOGGER.warning("OpenAI modern client call attempt %d failed: %s", attempt, e)
                if attempt == MAX_RETRIES or not _is_transient_error(e):
                    raise
                _sleep_with_backoff(attempt)

    except Exception:
        # 2) Fallback: try legacy openai client typical for 0.28.x
        try:
            import openai  # type: ignore
            LOGGER.debug("Falling back to legacy openai.ChatCompletion (0.28.x compatible)")
            def _legacy_req():
                resp = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                # legacy response: resp.choices[0].message.content or resp.choices[0].text
                c = resp.choices[0]
                # new-ish older variant:
                if hasattr(c, "message"):
                    return c.message["content"] if isinstance(c.message, dict) else c.message.content
                # very old variant:
                if hasattr(c, "text"):
                    return c.text
                # try dict access:
                return resp["choices"][0].get("message", {}).get("content") or resp["choices"][0].get("text")

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    return _legacy_req()
                except Exception as e:
                    LOGGER.warning("OpenAI legacy client call attempt %d failed: %s", attempt, e)
                    if attempt == MAX_RETRIES or not _is_transient_error(e):
                        raise
                    _sleep_with_backoff(attempt)

        except Exception as final_exc:
            # Provide a clear error that the caller can display
            LOGGER.exception("No working OpenAI client available or all attempts failed.")
            raise RuntimeError("OpenAI call failed (no client available or all retries exhausted) -> " + str(final_exc)) from final_exc
