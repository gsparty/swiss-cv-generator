import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json

try:
    import openai
except Exception:
    openai = None

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(["html", "xml"]))


class OpenAITextGenerator:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled and (openai is not None) and bool(os.getenv("OPENAI_API_KEY"))
        if self.enabled:
            openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate_summary(self, persona, max_tokens: int = 150) -> str:
        # Try LLM when configured, else fallback to simple template text
        if self.enabled:
            try:
                # Keep prompt small & safe
                prompt = f"Write a short professional CV summary in {persona.language} for this persona: {json.dumps(persona.dict(), ensure_ascii=False)}"
                resp = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                )
                text = resp["choices"][0]["message"]["content"].strip()
                return text
            except Exception as e:
                # don't fail: fallback
                print("OpenAI generation failed, falling back to template:", e)
        # fallback simple summary
        return f"{persona.name} mit {persona.years_experience} Jahren Erfahrung als {persona.title}."
