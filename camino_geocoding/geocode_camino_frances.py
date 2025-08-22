#!/usr/bin/env python3
"""
Simple geocoding script for Camino Francés stages.
Adds longitude and latitude coordinates to each stop using Google Maps API.
"""

import json
import os
import time
import googlemaps
from typing import Dict, Any, Optional, Tuple

class CaminoGeocoder:
    """Simple geocoder for Camino Francés stops."""
    
    def __init__(self):
        """Initialize the geocoder with Google Maps API."""
        google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not google_api_key:
            raise Exception("GOOGLE_MAPS_API_KEY environment variable is required")
        
        try:
            self.google_client = googlemaps.Client(key=google_api_key)
            print("✅ Google Maps API client initialized successfully")
        except Exception as e:
            raise Exception(f"Failed to initialize Google Maps API: {e}")
        
        self.rate_limit_delay = 0.1  # 100ms between requests
    
    def geocode_stop(self, stop: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """
        Geocode a single stop using the format: "place_name, town, country"
        
        Args:
            stop: Dictionary containing stop information
            
        Returns:
            Tuple of (longitude, latitude) or None if not found
        """
        name = stop['name']
        province = stop['province']
        country = stop['country']
        
        # Create search query: "place_name, town, country"
        query = f"{name}, {province}, {country}"
        
        try:
            print(f"Geocoding: {query}")
            
            # Use region bias for better results
            region_bias = 'es' if country == 'Spain' else 'fr'
            
            result = self.google_client.geocode(
                query,
                region=region_bias,
                language='en'
            )
            
            if result and len(result) > 0:
                location = result[0]['geometry']['location']
                lng = location['lng']
                lat = location['lat']
                
                print(f"  ✅ Found coordinates: ({lng}, {lat})")
                return (lng, lat)
            else:
                print(f"  ❌ No results found for: {query}")
                return None
                
        except Exception as e:
            print(f"  ❌ Error geocoding '{query}': {e}")
            return None
    
    def process_camino_data(self, input_file: str, output_file: str) -> None:
        """
        Process the Camino Francés JSON file and add coordinates to all stops.
        
        Args:
            input_file: Path to input JSON file
            output_file: Path to output JSON file with coordinates
        """
        print(f"Loading data from: {input_file}")
        
        # Load the original data
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total_stops = 0
        geocoded_stops = 0
        
        # Process each stage
        for stage in data['stages']:
            print(f"\nProcessing Stage {stage['stage_number']}: {stage['stage_name']}")
            
            for stop in stage['stops']:
                total_stops += 1
                
                # Skip if coordinates already exist
                if 'long' in stop and 'lat' in stop and stop['long'] is not None and stop['lat'] is not None:
                    print(f"  ⏭️  Skipping {stop['name']} - coordinates already exist")
                    geocoded_stops += 1
                    continue
                
                # Geocode the stop
                coords = self.geocode_stop(stop)
                if coords:
                    stop['long'] = coords[0]
                    stop['lat'] = coords[1]
                    geocoded_stops += 1
                else:
                    # Set to null if geocoding failed
                    stop['long'] = None
                    stop['lat'] = None
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
        
        print(f"\n📊 Geocoding Summary:")
        print(f"  Total stops: {total_stops}")
        print(f"  Successfully geocoded: {geocoded_stops}")
        print(f"  Failed: {total_stops - geocoded_stops}")
        
        # Save the updated data
        print(f"\nSaving geocoded data to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("✅ Geocoding completed!")

def main():
    """Main function to run the Camino Francés geocoding."""
    input_file = "../camino_frances_stages.json"
    output_file = "camino_frances_geocoded.json"
    
    try:
        geocoder = CaminoGeocoder()
        geocoder.process_camino_data(input_file, output_file)
        
        print(f"\n🎯 Next steps:")
        print(f"  1. Review the geocoded data in: {output_file}")
        print(f"  2. Run the visualization script to create a map")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
