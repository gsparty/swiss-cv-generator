# src/swiss_cv/text_utils.py
from ftfy import fix_text

def normalize_for_output(s: str) -> str:
    if not s:
        return s
    return fix_text(s)
