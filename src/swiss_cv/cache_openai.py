import os, hashlib, json, functools
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache', 'openai')

def _key_for(*args, **kwargs):
    s = json.dumps({'args':args,'kwargs':kwargs}, sort_keys=True, default=str)
    return hashlib.sha256(s.encode('utf8')).hexdigest()

def cache_response(ttl_seconds=86400):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            os.makedirs(CACHE_DIR, exist_ok=True)
            key = _key_for(*args, **kwargs)
            path = os.path.join(CACHE_DIR, key + '.json')
            if os.path.exists(path):
                try:
                    with open(path,'r',encoding='utf8') as f:
                        return json.load(f)
                except Exception:
                    pass
            res = func(*args, **kwargs)
            try:
                with open(path,'w',encoding='utf8') as f:
                    json.dump(res, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            return res
        return wrapper
    return deco
