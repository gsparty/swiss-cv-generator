"""OpenAI client for Swiss CV Generator"""

import os
import json
from pathlib import Path
import hashlib

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Cache directory
CACHE_DIR = Path('src/cache/openai')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_key(system_msg, user_msg, model="gpt-4o-mini"):
    """Generate cache key from messages"""
    combined = f"{model}:{system_msg}:{user_msg}"
    return hashlib.sha256(combined.encode()).hexdigest()

def get_cached_response(cache_key):
    """Get cached OpenAI response"""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f).get('response')
        except:
            return None
    return None

def save_cached_response(cache_key, response):
    """Save OpenAI response to cache"""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({'response': response}, f)
    except:
        pass

def call_openai_chat(system_message, user_message, model="gpt-4o-mini", temperature=0.7, max_tokens=500):
    """
    Call OpenAI Chat API (v1.0+ compatible)
    
    Args:
        system_message: System prompt
        user_message: User prompt
        model: Model name (default: gpt-4o-mini)
        temperature: Temperature (0-2)
        max_tokens: Max tokens in response
        
    Returns:
        Generated text response
    """
    
    # Check cache first
    cache_key = get_cache_key(system_message, user_message, model)
    cached = get_cached_response(cache_key)
    if cached:
        print(f"  📦 Using cached response")
        return cached
    
    # If OpenAI not available, use fallback
    if not OPENAI_AVAILABLE:
        return get_fallback_response(system_message, user_message)
    
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("  ⚠️  No OPENAI_API_KEY set, using fallback")
            return get_fallback_response(system_message, user_message)
        
        # Modern OpenAI v1.0+ API
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=30
        )
        
        result = response.choices[0].message.content.strip()
        save_cached_response(cache_key, result)
        return result
        
    except Exception as e:
        print(f"  ⚠️  OpenAI call failed: {str(e)[:100]}")
        return get_fallback_response(system_message, user_message)

def get_fallback_response(system_message, user_message):
    """Fallback response when OpenAI is unavailable"""
    if "summary" in user_message.lower():
        return (
            "Erfahrener Fachmann mit umfangreicher Expertise in Software-Entwicklung, "
            "Projektmanagement und agilen Methoden. Nachgewiesener Erfolg bei der "
            "Implementierung innovativer Lösungen und der Leitung hochperformanter Teams."
        )
    elif "responsibilities" in user_message.lower() or "aufgaben" in user_message.lower():
        return (
            "- Softwareentwicklung und -wartung\n"
            "- Projektleitung und Koordination\n"
            "- Teamkollaboration und Mentoring\n"
            "- Technische Dokumentation"
        )
    else:
        return "Professioneller mit fundierten Kenntnissen und praktischer Erfahrung."
