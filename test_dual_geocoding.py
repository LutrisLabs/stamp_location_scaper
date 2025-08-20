#!/usr/bin/env python3
"""
Test script for dual geocoding functionality.
Tests both Nominatim and Google Maps (if API key available).
"""

import os
import sys
from geocode_pilgrim_stamps import PilgrimStampGeocoder

def test_dual_geocoding():
    """Test the dual geocoding functionality."""
    print("🧪 Testing Dual Geocoding Functionality")
    print("=" * 50)
    
    # Initialize geocoder
    geocoder = PilgrimStampGeocoder()
    
    # Test cases
    test_cases = [
        ("Albergue de Villava", "Villava Atarrabia"),
        ("Catedral Metropolitana de Pamplona", "Pamplona Iruna"),
        ("Hotel Akerreta", "Akerreta"),
    ]
    
    print(f"Testing {len(test_cases)} locations...")
    print(f"Google Maps API available: {'Yes' if geocoder.google_client else 'No'}")
    print()
    
    for i, (place, town) in enumerate(test_cases, 1):
        print(f"--- Test {i}: {place} in {town} ---")
        
        result = geocoder.geocode_location(place, town)
        
        print(f"  Nominatim: {result['nominatim_coords']}")
        print(f"  Google Maps: {result['google_coords']}")
        print(f"  Final result: {result['final_coords']}")
        print(f"  Source: {result['geocoding_source']}")
        print(f"  Confidence: {result['confidence']}")
        print()
    
    print("✅ Dual geocoding test completed!")

if __name__ == "__main__":
    test_dual_geocoding()
