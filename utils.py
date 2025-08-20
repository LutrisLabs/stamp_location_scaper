#!/usr/bin/env python3
"""
Utility functions for the Pilgrim Stamp Scraper.
Contains helper functions for URL handling, HTML parsing, and other utilities.
"""

import os
import time
from urllib.parse import urljoin, urlparse
from typing import List, Optional
import logging

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        directory_path: Path to the directory to ensure exists
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logging.info(f"Created directory: {directory_path}")

def construct_absolute_url(base_url: str, relative_url: str) -> str:
    """
    Construct an absolute URL from a base URL and relative URL.
    
    Args:
        base_url: Base URL to resolve relative URLs against
        relative_url: Relative URL to convert to absolute
        
    Returns:
        Absolute URL
    """
    return urljoin(base_url, relative_url)

def extract_town_name_from_url(url: str) -> str:
    """
    Extract town name from a category URL.
    
    Args:
        url: Category URL containing town information
        
    Returns:
        Town name extracted from the URL
    """
    try:
        # Parse the URL to extract the last part after 'category/'
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        
        # Find the index of 'category' and get the next part
        if 'category' in path_parts:
            category_index = path_parts.index('category')
            if category_index + 1 < len(path_parts):
                town_slug = path_parts[category_index + 1]
                # Convert slug to readable town name (replace hyphens with spaces, capitalize)
                town_name = town_slug.replace('-', ' ').replace('_', ' ').title()
                return town_name
        
        # Fallback: return the last part of the path
        if path_parts:
            last_part = path_parts[-1]
            return last_part.replace('-', ' ').replace('_', ' ').title()
        
        return "Unknown Town"
        
    except Exception as e:
        logging.error(f"Error extracting town name from URL {url}: {e}")
        return "Unknown Town"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe file system usage.
    
    Args:
        filename: Original filename to sanitize
        
    Returns:
        Sanitized filename safe for file system
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def rate_limit_delay(seconds: float = 1.0) -> None:
    """
    Implement rate limiting delay between requests.
    
    Args:
        seconds: Number of seconds to delay
    """
    time.sleep(seconds)

# Spanish to English category translation mapping
SPANISH_TO_ENGLISH_CATEGORIES = {
    # A.A.C.S. -> AACS
    'A.A.C.S.': 'AACS',
    
    # Albergues de peregrinos -> Pilgrim hostels
    'Albergues de peregrinos': 'Pilgrim hostels',
    
    # Ayuntamientos y Concejos -> Town Halls and Councils
    'Ayuntamientos y Concejos': 'Town Halls and Councils',
    
    # Bares y restaurantes -> Bars and restaurants
    'Bares y restaurantes': 'Bars and restaurants',
    
    # Colegios y Universidades -> Colleges and Universities
    'Colegios y Universidades': 'Colleges and Universities',
    
    # Catedrales -> Cathedrals
    'Catedrales': 'Cathedrals',
    
    # Conventos -> Convents
    'Conventos': 'Convents',
    
    # Empresas y compañías -> Companies and businesses
    'Empresas y compañías': 'Companies and businesses',
    
    # Hostelería -> Hospitality
    'Hostelería': 'Hospitality',
    
    # Iglesias de Santiago -> Churches of Santiago
    'Iglesias de Santiago': 'Churches of Santiago',
    
    # Iglesias y parroquias -> Churches and parishes
    'Iglesias y parroquias': 'Churches and parishes',
    
    # Locales comerciales -> Commercial premises
    'Locales comerciales': 'Commercial premises',
    
    # Monasterios -> Monasteries
    'Monasterios': 'Monasteries',
    
    # Museos -> Museums
    'Museos': 'Museums',
    
    # Oficinas de Turismo -> Tourist Offices
    'Oficinas de Turismo': 'Tourist Offices',
    
    # Personajes del Camino -> Characters of the Camino
    'Personajes del Camino': 'Characters of the Camino',
    
    # Policía y cuerpos de seguridad -> Police and security forces
    'Policía y cuerpos de seguridad': 'Police and security forces',
    
    # Additional categories that might appear in individual stamp pages
    'Auritz / Burguete': 'Auritz / Burguete',  # Place name, keep as is
    
    # Additional stable location/town tags to keep as-is
    'Roncesvalles / Orreaga': 'Roncesvalles / Orreaga',
    'Pamplona / Iruña': 'Pamplona / Iruña',
    'Villava / Atarrabia': 'Villava / Atarrabia',
    'Burlada / Burlata': 'Burlada / Burlata',
    'Cizur Mayor / Zizur Nagusi': 'Cizur Mayor / Zizur Nagusi',
    'Cizur Menor / Zizur Txikia': 'Cizur Menor / Zizur Txikia',
    'Larrasoaña / Larrasoaina': 'Larrasoaña / Larrasoaina',
    'Ilárraz / Ilarratz': 'Ilárraz / Ilarratz',
    'Zuriáin': 'Zuriáin',
    'Zabaldika': 'Zabaldika',
    'Zariquiegui': 'Zariquiegui',
    'Muruzabal': 'Muruzabal',
    'Viscarret-Guerendiain': 'Viscarret-Guerendiain',
    'Valle de Erro': 'Valle de Erro',
    'Akerreta': 'Akerreta',
    'Zubiri': 'Zubiri',
    'Burguete': 'Burguete',
    'Arre': 'Arre',
    'Obanos': 'Obanos',
    'Uterga': 'Uterga',
}

def translate_categories_to_english(spanish_categories: list) -> list:
    """
    Translate Spanish categories to English using smart detection.
    
    Args:
        spanish_categories: List of Spanish category strings
        
    Returns:
        List of English category strings
    """
    english_categories = []
    
    for category in spanish_categories:
        if category in SPANISH_TO_ENGLISH_CATEGORIES:
            # Known category - use translation
            english_categories.append(SPANISH_TO_ENGLISH_CATEGORIES[category])
        else:
            # Smart detection: if it's not a known category, it's likely a person name
            # or location that should be preserved as-is
            english_categories.append(category)
            
            # Categorize for better analytics
            category_type = categorize_unknown_category(category)
            logging.info(f"Auto-preserved {category_type}: '{category}'")
    
    return english_categories

def categorize_unknown_category(category: str) -> str:
    """
    Categorize an unknown category to help with analytics and future mapping decisions.
    
    Args:
        category: The unknown category string
        
    Returns:
        str: Category type ('person_name', 'location', 'business', 'other')
    """
    # Check if it looks like a person name (contains common name patterns)
    if any(pattern in category for pattern in [' ', '"', "'", 'de ', 'del ', 'la ', 'el ']):
        if any(word in category.lower() for word in ['juan', 'jose', 'maria', 'carlos', 'ana', 'luis', 'pedro', 'antonio']):
            return 'person_name'
        elif any(word in category.lower() for word in ['hotel', 'bar', 'restaurante', 'albergue', 'pension', 'cafe']):
            return 'business'
        elif any(word in category.lower() for word in ['calle', 'plaza', 'avenida', 'camino', 'ruta']):
            return 'location'
        else:
            return 'person_name'  # Default to person name for unknown patterns
    
    # Check if it looks like a location (single word, no spaces)
    elif len(category.split()) == 1 and not any(char in category for char in ['/', '-', '(', ')']):
        return 'location'
    
    # Check if it looks like a business name
    elif any(word in category.lower() for word in ['s.l.', 's.a.', 'coop', 'assoc', 'fund']):
        return 'business'
    
    else:
        return 'other'

def normalize_categories(categories):
    """
    Normalize categories to ensure they are always a clean list of strings.
    
    Args:
        categories: None, list, or str - the categories to normalize
        
    Returns:
        list[str]: Clean list of category strings
    """
    if categories is None:
        return []
    if isinstance(categories, list):
        return [c.strip() for c in categories if isinstance(c, str) and c.strip()]
    if isinstance(categories, str):
        parts = [p.strip() for p in categories.split(';') if p.strip()]
        return parts
    logging.warning(f"Unexpected categories type: {type(categories)}")
    return []

def validate_category_translations():
    """
    Validate that all Spanish categories have English translations.
    This function should be called during testing and can be used in production.
    
    Returns:
        bool: True if all categories have translations, False otherwise
    """
    # Get all unique Spanish categories from the mapping
    spanish_categories = set(SPANISH_TO_ENGLISH_CATEGORIES.keys())
    
    # Get all unique English categories from the mapping
    english_categories = set(SPANISH_TO_ENGLISH_CATEGORIES.values())
    
    # Check if we have the same number of categories
    if len(spanish_categories) != len(english_categories):
        logging.error(f"Category count mismatch: {len(spanish_categories)} Spanish vs {len(english_categories)} English")
        return False
    
    # Check for any missing translations
    missing_translations = []
    for spanish_cat in spanish_categories:
        if spanish_cat not in SPANISH_TO_ENGLISH_CATEGORIES:
            missing_translations.append(spanish_cat)
    
    if missing_translations:
        logging.error(f"Missing translations for categories: {missing_translations}")
        return False
    
    logging.info(f"✓ Category translation validation passed: {len(spanish_categories)} categories")
    return True
