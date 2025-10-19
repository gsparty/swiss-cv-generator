from typing import Dict

SUMMARY_TEMPLATES = {
    'de': """Schreibe eine prägnante, professionelle Zusammenfassung (3–4 Sätze) auf Deutsch für eine/n {title} aus {canton} mit {experience} Jahren Berufserfahrung. Betone relevante technische Fähigkeiten und berufliche Erfolge.""",
    'fr': """Rédige un résumé professionnel concis (3–4 phrases) en français pour/un {title} de {canton} avec {experience} années d'expérience. Mets en avant les compétences techniques et les réalisations clés.""",
    'it': """Scrivi un riassunto professionale conciso (3–4 frasi) in italiano per un/una {title} da {canton} con {experience} anni di esperienza. Metti in evidenza le competenze tecniche e i risultati professionali."""
}

SKILLS_TEMPLATES = {
    'de': """Nenne 6–8 zentrale Fähigkeiten (technische und Soft Skills) passend für eine/n {title} mit {experience} Jahren Erfahrung in {industry}.""",
    'fr': """Liste 6–8 compétences clés (techniques et transversales) pour un/une {title} avec {experience} ans d'expérience dans {industry}.""",
    'it': """Elenca 6–8 competenze chiave (tecniche e trasversali) per un/una {title} con {experience} anni di esperienza in {industry}."""
}

def build_summary_prompt(persona) -> Dict[str,str]:
    tmpl = SUMMARY_TEMPLATES.get(persona.language.value, SUMMARY_TEMPLATES['de'])
    return {
        'system': 'You are a concise professional CV writer. Keep tone professional and neutral.',
        'user': tmpl.format(title=persona.current_title, canton=persona.canton, experience=int(persona.experience_years))
    }

def build_skills_prompt(persona) -> Dict[str,str]:
    tmpl = SKILLS_TEMPLATES.get(persona.language.value, SKILLS_TEMPLATES['de'])
    return {
        'system': 'You are an expert HR specialist who lists relevant skills for CVs.',
        'user': tmpl.format(title=persona.current_title, experience=int(persona.experience_years), industry=persona.industry)
    }


