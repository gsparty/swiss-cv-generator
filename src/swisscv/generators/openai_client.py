import os
def call_openai(prompt: str, model: str = "gpt-4o-mini"):
    """
    Minimal OpenAI wrapper with graceful fallback.
    If OPENAI_API_KEY is not set or an error occurs, returns a short German fallback summary.
    """
    fallback = "Erfahrener Profi mit relevanter Erfahrung und starken technischen Fähigkeiten."
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return fallback
    try:
        import openai
        openai.api_key = api_key
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role":"user","content":prompt}],
            max_tokens=200
        )
        return resp.choices[0].message.get("content","").strip() or fallback
    except Exception:
        return fallback


