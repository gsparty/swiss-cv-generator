import os
import time
import openai
from typing import Optional

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def call_openai_chat(system: str, user_prompt: str, model: str = 'gpt-4', max_retries:int=4, delay:float=1.0) -> Optional[str]:
    \"\"\"Simple wrapper with exponential backoff. Returns text or None on final failure.\"\"\"
    if not openai.api_key:
        return None
    attempt = 0
    while attempt <= max_retries:
        try:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': user_prompt}
                ],
                temperature=0.6,
                max_tokens=400
            )
            return resp.choices[0].message.content.strip()
        except openai.error.RateLimitError as e:
            wait = delay * (2 ** attempt)
            time.sleep(wait)
            attempt += 1
            continue
        except openai.error.OpenAIError:
            # Generic failure - attempt limited retries
            wait = delay * (2 ** attempt)
            time.sleep(wait)
            attempt += 1
            continue
    return None
