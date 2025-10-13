import os

from openai import OpenAI


class SummaryGenerator:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def generate(self, persona, max_tokens: int = 150) -> str:
        prompt = (
            f"Write a concise {persona.primary_language} professional summary for a "
            f"{persona.occupation['title_de']} with {persona.years_experience} years' experience "
            f"in {persona.occupation['industry']} in Switzerland."
        )
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
