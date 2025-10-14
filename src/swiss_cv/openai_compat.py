# Compatibility shim to emulate a subset of openai.ChatCompletion.create()
# Delegates to swiss_cv.openai_wrapper.client.chat() for actual calls.
from typing import Any, Dict
from dataclasses import dataclass
import json

try:
    from .openai_wrapper import client as _client
except Exception:
    # fallback: try top-level import (for different PYTHONPATH setups)
    try:
        from swiss_cv.openai_wrapper import client as _client
    except Exception:
        _client = None

@dataclass
class _Choice:
    message: Dict[str, Any]

def _format_response(text: str):
    # Return a dict with choices[0].message.content shape
    return {'choices': [{'message': {'content': text}}]}

class ChatCompletion:
    @staticmethod
    def create(model=None, messages=None, temperature: float=0.7, max_tokens: int=256, **kwargs):
        if _client is None:
            raise RuntimeError('OpenAI client wrapper not available')
        # convert messages to text if provided as list of dicts
        if messages and isinstance(messages, list):
            # join user/system messages to a single prompt
            prompt = '\\n'.join([m.get('content','') for m in messages])
        else:
            prompt = str(messages)
        # delegate to wrapper.chat (which handles retries)
        text = _client.chat(messages=[{'role':'user','content':prompt}], temperature=temperature, max_tokens=max_tokens)
        return _format_response(text)
