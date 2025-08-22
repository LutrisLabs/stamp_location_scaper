#!/usr/bin/env python3
"""
Script to fix incorrect geocoding coordinates in the Camino Francés data.
Updates specific stops with manually verified correct coordinates.
"""

import json

def fix_coordinates():
    """Fix the incorrect coordinates with manually verified correct ones."""
    
    # Load the geocoded data
    with open('camino_frances_geocoded.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Define the corrections: stop_name -> (lat, long)
    corrections = {
        "La Laguna": (42.70126950462187, -7.021868063322811),
        "Linares": (42.69913272721601, -7.073770644328744),
        "A Balsa": (42.766042678503005, -7.2537276139561895),
        "Marzan": (42.76879522844872, -7.476308531127457),
        "Vilacha": (42.79547043777973, -7.603233068665937),
        "O Hospital": (42.840954441423214, -7.734579480863954),
        "Lestedo": (42.872145522854524, -7.814158843458301),
        "Casanova": (42.87874591813561, -7.928150317049294),
        "A Brea": (42.91860389918316, -8.305194057330725),
        "A Rua": (42.914572344387096, -8.350234844778358),
        "San Bol": (42.32365504328446, -3.990781695387196)
    }
    
    print("🔧 Fixing incorrect coordinates...")
    
    # Track which corrections were made
    corrections_made = []
    
    # Process each stage
    for stage in data['stages']:
        for stop in stage['stops']:
            stop_name = stop['name']
            
            if stop_name in corrections:
                old_lat = stop['lat']
                old_long = stop['long']
                new_lat, new_long = corrections[stop_name]
                
                # Update coordinates
                stop['lat'] = new_lat
                stop['long'] = new_long
                
                corrections_made.append({
                    'name': stop_name,
                    'stage': stage['stage_number'],
                    'old_coords': f"({old_lat}, {old_long})",
                    'new_coords': f"({new_lat}, {new_long})"
                })
                
                print(f"✅ Fixed {stop_name} (Stage {stage['stage_number']})")
                print(f"   Old: {old_lat}, {old_long}")
                print(f"   New: {new_lat}, {new_long}")
    
    # Save the corrected data
    output_file = 'camino_frances_geocoded_corrected.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Summary of corrections:")
    print(f"   Total corrections made: {len(corrections_made)}")
    print(f"   Corrected data saved to: {output_file}")
    
    # Print all corrections made
    for correction in corrections_made:
        print(f"   • {correction['name']} (Stage {correction['stage']}): {correction['old_coords']} → {correction['new_coords']}")
    
    return corrections_made

if __name__ == "__main__":
    fix_coordinates()
