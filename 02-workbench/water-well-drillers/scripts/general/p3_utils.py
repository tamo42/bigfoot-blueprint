import os
import re

def get_workspace_root():
    """
    Returns the absolute path to the workspace root (nhq-bigfoot-blueprint).
    Since this file is located at 02-workbench/water-well-drillers/scripts/general/utils.py,
    the root is 5 parent directories up.
    """
    current_file = os.path.abspath(__file__)
    # 02-workbench/water-well-drillers/scripts/general/utils.py -> general
    d1 = os.path.dirname(current_file)
    # general -> scripts
    d2 = os.path.dirname(d1)
    # scripts -> water-well-drillers
    d3 = os.path.dirname(d2)
    # water-well-drillers -> 02-workbench
    d4 = os.path.dirname(d3)
    # 02-workbench -> workspace root
    root = os.path.dirname(d4)
    return root

def resolve_path(relative_path_from_root):
    """
    Resolves a path relative to the workspace root.
    """
    return os.path.normpath(os.path.join(get_workspace_root(), relative_path_from_root))

def slugify(text):
    """
    Converts string to a clean slug.
    """
    if not text:
        return ""
    text = str(text).lower().strip()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^\w\-]+', '', text)
    text = re.sub(r'\-\-+', '-', text)
    return text.strip('-')


def clean_phone_number(phone_number):
    """
    Sanitizes phone numbers and formats them as (XXX) XXX-XXXX.
    """
    if not phone_number:
        return ""
    digits = re.sub(r'[^\d]', '', str(phone_number))
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return phone_number # return original if unable to format standard 10 digit

def load_env_api_key():
    """
    Finds and loads the GOOGLE_PLACES_API_KEY from the .env file at the workspace root.
    """
    env_path = resolve_path(".env")
    if not os.path.exists(env_path):
        return None
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('GOOGLE_PLACES_API_KEY='):
                return line.split('=', 1)[1].strip()
    return None

def get_places_cache_path():
    """
    Returns the absolute path to the Places API cache file.
    """
    return resolve_path("cache/places_cache.json")

def get_db_path(state):
    """
    Returns the absolute path to the SQLite database for the specified state.
    """
    db_name = f"{state.lower()}_wells.sqlite"
    return resolve_path(f"02-workbench/water-well-drillers/data/{db_name}")

def get_unified_db_path():
    """
    Returns the absolute path to the unified consolidated SQLite database.
    """
    return resolve_path("02-workbench/water-well-drillers/data/water_well_directory.sqlite")

