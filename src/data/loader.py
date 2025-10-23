"""Data loading utilities for Swiss CV Generator"""

import json
import csv
import os
from typing import List, Dict, Any


def load_cantons_json(path: str = 'data/cantons.json') -> List[Dict]:
    """Load cantons from JSON file"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Cantons data not found at {path}")
    
    with open(path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    # Handle both list and dict formats
    if isinstance(data, dict):
        return list(data.values())
    return data


def load_companies_json(path: str = 'data/companies.json') -> List[Dict]:
    """Load companies from JSON file"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Companies data not found at {path}")
    
    with open(path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    # Handle both list and dict formats
    if isinstance(data, dict):
        return list(data.values())
    return data if isinstance(data, list) else []


def load_occupations_json(path: str = 'data/occupations.json') -> List[Dict]:
    """Load occupations from JSON file"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Occupations data not found at {path}")
    
    with open(path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    # Handle both list and dict formats
    if isinstance(data, dict):
        return list(data.values())
    return data if isinstance(data, list) else []


def load_names_csv(path: str) -> List[str]:
    """Load names from CSV file"""
    if not os.path.exists(path):
        return []
    
    names = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Try multiple column name variations
                name = (row.get('name') or 
                       row.get('Name') or 
                       row.get('vorname') or 
                       row.get('Vorname') or 
                       row.get('first_name') or
                       next(iter(row.values())))
                if name:
                    names.append(name.strip())
    except Exception as e:
        print(f"Warning: Error loading names from {path}: {e}")
    
    return names


def load_surnames_csv(path: str = 'data/surnames.csv') -> List[str]:
    """Load surnames from CSV file"""
    if not os.path.exists(path):
        return []
    
    surnames = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Try multiple column name variations
                surname = (row.get('surname') or 
                          row.get('Surname') or 
                          row.get('last_name') or 
                          row.get('nachname') or 
                          row.get('Nachname') or
                          next(iter(row.values())))
                if surname:
                    surnames.append(surname.strip())
    except Exception as e:
        print(f"Warning: Error loading surnames from {path}: {e}")
    
    return surnames


# Legacy function names for backwards compatibility
def load_cantons_csv(*args, **kwargs):
    """Deprecated: Use load_cantons_json instead"""
    return load_cantons_json(*args, **kwargs)


def load_companies_csv(*args, **kwargs):
    """Deprecated: Use load_companies_json instead"""
    return load_companies_json(*args, **kwargs)
