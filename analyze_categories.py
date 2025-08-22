#!/usr/bin/env python3
"""
Analyze Categories Script

This script analyzes the english_categories column to understand
what should be kept as pure categories vs what should be removed.
"""

import pandas as pd
from collections import Counter

def analyze_categories():
    """Analyze the english_categories column"""
    print("=== ANALYSIS OF ENGLISH_CATEGORIES COLUMN ===")
    
    # Load the data
    df = pd.read_csv('clean_output_stamps_final_for_geosjon.csv')
    print(f"Total rows: {len(df)}")
    print(f"Unique values count: {df['english_categories'].nunique()}")
    
    # Extract all parts from the categories
    all_parts = []
    for val in df['english_categories'].dropna():
        parts = str(val).split('; ')
        all_parts.extend([part.strip() for part in parts])
    
    # Count occurrences
    part_counts = Counter(all_parts)
    
    print("\n=== ALL PARTS FOUND (with counts) ===")
    for part, count in part_counts.most_common():
        print(f"  {part}: {count}")
    
    # Identify what appears to be collaborators/names
    print("\n=== IDENTIFIED COLLABORATORS/NAMES ===")
    collaborators = []
    for part, count in part_counts.items():
        if any(name in part for name in ['Josep María Hernández', 'Íñigo Cía', 'Guido Haesaert', 'Jesús Campos', 'Raúl Oter', 'Roberto Daga', 'Pilar Guerrero']):
            collaborators.append((part, count))
    
    for name, count in collaborators:
        print(f"  {name}: {count}")
    
    # Identify what appears to be town names
    print("\n=== IDENTIFIED TOWN NAMES ===")
    towns = []
    for part, count in part_counts.items():
        if any(town in part for town in ['Sarria', 'Rabanal del Camino', 'Pedrouzo', 'Vega de Valcarce', 'Pamplona', 'Melide', 'Portomarín', 'Santiago de Compostela', 'León', 'Sahagún de Campos', 'Arzúa', 'Triacastela', 'Castrojeriz', 'Frómista', 'Logroño', 'Furelos', 'Muruzabal', 'Obanos']):
            towns.append((part, count))
    
    for town, count in towns:
        print(f"  {town}: {count}")
    
    # Identify what appears to be pure categories
    print("\n=== IDENTIFIED PURE CATEGORIES ===")
    pure_categories = []
    for part, count in part_counts.items():
        if part not in [item[0] for item in collaborators] and part not in [item[0] for item in towns]:
            pure_categories.append((part, count))
    
    for category, count in pure_categories:
        print(f"  {category}: {count}")

if __name__ == "__main__":
    analyze_categories()
