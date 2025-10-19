import os
import json
from typing import Optional
from .sampler import sample_canton_language, sample_age_and_experience, sample_name, sample_phone, sample_email
from .text_utils import normalize_for_output
from .models_persona import SwissPersona, Experience
from .cache_openai import cache_response

# try openai wrapper
try:
    from swiss_cv.openai_wrapper import client as openai_client
except Exception:
    openai_client = None

@cache_response(ttl_seconds=60*60*24)
def _call_openai_structured(prompt: str):
    if openai_client is None:
        return None
    try:
        resp = openai_client.chat(messages=[{'role':'user','content':prompt}], temperature=0.6, max_tokens=350)
        # if resp is dict with choices
        if isinstance(resp, dict):
            choices = resp.get('choices') or []
            if choices:
                text = choices[0].get('message', {}).get('content') or choices[0].get('text')
                return text
        if isinstance(resp, str):
            return resp
    except Exception:
        return None
    return None

STRUCTURED_PROMPT_TEMPLATE = (
    "You are an assistant that produces a small CV summary for a Swiss professional.\n"
    "Return ONLY a JSON object with keys: summary (string), bullets (array of 3 short bullet strings), skills (array of short strings).\n"
    "Do not add any explanation, only the JSON.\n\n"
    "Input:\n{context}\n\nOutput:\n"
)

def generate_summary_with_ai_structured(persona: dict) -> Optional[dict]:
    if openai_client is None:
        return None
    context = "Age: {age}\\nCanton: {canton}\\nLanguage: {language}\\nOccupation: {occupation}\\nExperienceYears: {experience_years}".format(
        age=persona['age'],
        canton=persona['canton'],
        language=persona['language'],
        occupation=persona['occupation'],
        experience_years=persona['experience_years']
    )
    prompt = STRUCTURED_PROMPT_TEMPLATE.format(context=context)
    text = _call_openai_structured(prompt)
    if not text:
        return None

    # try to extract JSON from the response (some models wrap in markdown)
    try:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            j = json.loads(text[start:end+1])
            return j
    except Exception:
        try:
            return json.loads(text)
        except Exception:
            return None
    return None

def fallback_summary_structured(persona: dict) -> dict:
    s = {
        'summary': "Experienced {occupation} based in {canton}, {age} years old, with {years} years in the field.".format(
            occupation=persona.get('occupation','professional'),
            canton=persona['canton'],
            age=persona['age'],
            years=persona.get('experience_years',0)
        ),
        'bullets': [
            f"{persona.get('experience_years',0)} years experience in {persona.get('occupation','')}",
            "Team collaboration & project delivery",
            "Problem-solving and communication"
        ],
        'skills': ["Communication", "Problem solving", persona.get('occupation','General')]
    }
    return s

def generate_persona(occupation: str = 'technology') -> SwissPersona:
    canton, language = sample_canton_language()
    age, exp_years = sample_age_and_experience()
    first, last = sample_name(language)
    phone = sample_phone()
    email = sample_email(first, last, canton)

    persona_raw = {
        'first_name': first,
        'last_name': last,
        'age': age,
        'canton': canton,
        'language': language,
        'email': email,
        'phone': phone,
        'occupation': occupation,
        'experience_years': exp_years
    }

    # AI structured summary
    structured = generate_summary_with_ai_structured(persona_raw)
    if not structured:
        structured = fallback_summary_structured(persona_raw)

    persona_raw['summary'] = normalize_for_output(structured.get('summary',''))
    persona_raw['bullets'] = [normalize_for_output(b) for b in structured.get('bullets',[])]
    persona_raw['skills'] = [normalize_for_output(s) for s in structured.get('skills',[])]

    # experiences
    experiences = []
    current_year = 2025
    start_year = current_year - (persona_raw['experience_years'] or 0)
    experiences.append({
        'title': f"{occupation.title()} Specialist",
        'company': f"{occupation.title()} Solutions AG",
        'start_year': max(2000, start_year),
        'end_year': None,
        'description': persona_raw['bullets'][0] if persona_raw['bullets'] else ''
    })

    persona = SwissPersona(
        first_name = persona_raw['first_name'],
        last_name = persona_raw['last_name'],
        age = persona_raw['age'],
        canton = persona_raw['canton'],
        language = persona_raw['language'],
        email = persona_raw['email'],
        phone = persona_raw['phone'],
        summary = persona_raw['summary'],
        experiences = [Experience(**e) for e in experiences]
    )

    # attach extras bypassing pydantic __setattr__ validation
    object.__setattr__(persona, 'skills', persona_raw['skills'])
    object.__setattr__(persona, 'bullets', persona_raw['bullets'])

    return persona


