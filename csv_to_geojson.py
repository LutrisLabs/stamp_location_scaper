#!/usr/bin/env python3
"""
CSV to GeoJSON Converter

This script converts the cleaned pilgrim stamps CSV file to GeoJSON format
for use in mapping applications.
"""

import pandas as pd
import json
import argparse
import sys
from pathlib import Path

def load_csv_data(csv_path):
    """Load and validate the CSV data"""
    print(f"Loading CSV data from: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded {len(df)} stamps from CSV")
        
        # Check for required columns
        required_columns = ['place', 'town', 'latitude', 'longitude']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Error: Missing required columns: {missing_columns}")
            sys.exit(1)
        
        # Check for valid coordinates
        invalid_coords = df[
            (df['latitude'].isna()) | 
            (df['longitude'].isna()) |
            (df['latitude'] == 0) | 
            (df['longitude'] == 0)
        ]
        
        if len(invalid_coords) > 0:
            print(f"⚠️  Warning: {len(invalid_coords)} stamps have invalid coordinates")
        
        return df
        
    except FileNotFoundError:
        print(f"❌ Error: CSV file '{csv_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading CSV data: {e}")
        sys.exit(1)

def clean_and_prepare_data(df):
    """Clean and prepare the data for GeoJSON conversion"""
    print("Cleaning and preparing data...")
    
    # Remove rows with invalid coordinates
    df_clean = df.dropna(subset=['latitude', 'longitude'])
    df_clean = df_clean[(df_clean['latitude'] != 0) & (df_clean['longitude'] != 0)]
    
    # Fill missing values with defaults
    df_clean['country'] = df_clean.get('country', 'Spain')
    
    # Use english_categories if available, fallback to english_category
    if 'english_categories' in df_clean.columns:
        df_clean['english_category'] = df_clean['english_categories']
    elif 'english_category' in df_clean.columns:
        df_clean['english_category'] = df_clean['english_category']
    else:
        df_clean['english_category'] = 'Unknown'
    
    # Define the main categories to keep (based on analyze_categories.py output)
    main_categories = {
        'Pilgrim hostels': 'Pilgrim hostels',
        'Bars and restaurants': 'Bars and restaurants',
        'Hospitality': 'Hospitality',
        'Churches and parishes': 'Churches and parishes',
        'Commercial premises': 'Commercial premises',
        'AACS': 'AACS',
        'Town Halls and Councils': 'Town Halls and Councils',
        'Tourist Offices': 'Tourist Offices',
        'Characters of the Camino': 'Characters of the Camino',
        'Museums': 'Museums',
        'Churches of Santiago': 'Churches of Santiago',
        'Cathedrals': 'Cathedrals',
        'Convents': 'Convents',
        'Monasteries': 'Monasteries',
        'Companies and businesses': 'Companies and businesses',
        'Colleges and Universities': 'Colleges and Universities',
        'Police and security forces': 'Police and security forces'
    }
    
    # Function to map categories to main categories
    def map_to_main_category(category):
        if pd.isna(category):
            return 'Other'
        
        category_str = str(category).strip()
        
        # Direct matches
        if category_str in main_categories:
            return main_categories[category_str]
        
        # Check if any main category is contained in the category string
        for main_cat in main_categories.keys():
            if main_cat.lower() in category_str.lower():
                return main_categories[main_cat]
        
        # Check for specific patterns
        if any(word in category_str.lower() for word in ['hostel', 'albergue', 'refuge']):
            return 'Pilgrim hostels'
        elif any(word in category_str.lower() for word in ['bar', 'restaurant', 'café', 'cafe']):
            return 'Bars and restaurants'
        elif any(word in category_str.lower() for word in ['hotel', 'pensión', 'pension', 'hostal']):
            return 'Hospitality'
        elif any(word in category_str.lower() for word in ['church', 'iglesia', 'parish', 'parroquia']):
            return 'Churches and parishes'
        elif any(word in category_str.lower() for word in ['cathedral', 'catedral']):
            return 'Cathedrals'
        elif any(word in category_str.lower() for word in ['convent', 'convento']):
            return 'Convents'
        elif any(word in category_str.lower() for word in ['monastery', 'monasterio']):
            return 'Monasteries'
        elif any(word in category_str.lower() for word in ['museum', 'museo']):
            return 'Museums'
        elif any(word in category_str.lower() for word in ['tourist', 'turismo', 'office', 'oficina']):
            return 'Tourist Offices'
        elif any(word in category_str.lower() for word in ['town hall', 'ayuntamiento', 'council', 'consejo']):
            return 'Town Halls and Councils'
        elif any(word in category_str.lower() for word in ['police', 'policía', 'guardia', 'security']):
            return 'Police and security forces'
        elif any(word in category_str.lower() for word in ['university', 'universidad', 'college', 'colegio']):
            return 'Colleges and Universities'
        elif any(word in category_str.lower() for word in ['company', 'empresa', 'business', 'negocio']):
            return 'Companies and businesses'
        elif any(word in category_str.lower() for word in ['aacs']):
            return 'AACS'
        elif any(word in category_str.lower() for word in ['character', 'personaje']):
            return 'Characters of the Camino'
        elif any(word in category_str.lower() for word in ['santiago']):
            return 'Churches of Santiago'
        elif any(word in category_str.lower() for word in ['commercial', 'comercio', 'shop', 'tienda']):
            return 'Commercial premises'
        
        return 'Other'
    
    # Apply category mapping
    df_clean['english_category'] = df_clean['english_category'].apply(map_to_main_category)
    
    # Clean up text fields
    df_clean['place'] = df_clean['place'].fillna('Unknown Place')
    df_clean['town'] = df_clean['town'].fillna('Unknown Town')
    
    print(f"✓ Cleaned data: {len(df_clean)} valid stamps")
    
    # Show category distribution after mapping
    category_counts = df_clean['english_category'].value_counts()
    print(f"\nCategory distribution after mapping:")
    for category, count in category_counts.items():
        print(f"  {category}: {count}")
    
    return df_clean

def create_geojson_features(df):
    """Convert DataFrame rows to GeoJSON features"""
    print("Creating GeoJSON features...")
    
    features = []
    
    for idx, row in df.iterrows():
        # Create feature geometry
        geometry = {
            "type": "Point",
            "coordinates": [float(row['longitude']), float(row['latitude'])]
        }
        
        # Create feature properties - only keep essential ones
        properties = {
            "place_name": str(row['place']),
            "town_name": str(row['town']),
            "country_name": str(row['country']),
            "stamp_category": str(row['english_category'])
        }
        
        # Create feature
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
        
        features.append(feature)
    
    print(f"✓ Created {len(features)} GeoJSON features")
    return features

def create_geojson_collection(features, metadata=None):
    """Create a complete GeoJSON FeatureCollection"""
    print("Creating GeoJSON collection...")
    
    if metadata is None:
        metadata = {
            "name": "Camino Francés Pilgrim Stamps",
            "description": "Geocoded locations of pilgrim stamps along the Camino Francés",
            "created": pd.Timestamp.now().isoformat(),
            "source": "Manual review and Google geocoding",
            "total_stamps": len(features)
        }
    
    geojson = {
        "type": "FeatureCollection",
        "metadata": metadata,
        "features": features
    }
    
    print("✓ GeoJSON collection created")
    return geojson

def save_geojson(geojson, output_path):
    """Save GeoJSON to file"""
    print(f"Saving GeoJSON to: {output_path}")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)
        
        print(f"✓ GeoJSON saved successfully")
        
        # Get file size
        file_size = Path(output_path).stat().st_size
        print(f"📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
    except Exception as e:
        print(f"❌ Error saving GeoJSON: {e}")
        sys.exit(1)

def create_summary_report(df, geojson_path):
    """Create a summary report of the conversion"""
    print("\n" + "=" * 50)
    print("📊 CONVERSION SUMMARY")
    print("=" * 50)
    
    print(f"Total stamps processed: {len(df)}")
    print(f"Valid coordinates: {len(df)}")
    print(f"Output file: {geojson_path}")
    
    # Main categories breakdown (now much cleaner)
    if 'english_category' in df.columns:
        categories = df['english_category'].value_counts()
        print(f"\nMain categories breakdown:")
        for category, count in categories.items():
            print(f"  {category}: {count}")
    
    # Route breakdown
    if 'route' in df.columns:
        routes = df['route'].value_counts()
        print(f"\nRoutes breakdown:")
        for route, count in routes.items():
            print(f"  {route}: {count}")
    
    # Coordinate bounds
    lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
    lon_min, lon_max = df['longitude'].min(), df['longitude'].max()
    print(f"\nGeographic bounds:")
    print(f"  Latitude: {lat_min:.6f} to {lat_max:.6f}")
    print(f"  Longitude: {lon_min:.6f} to {lon_max:.6f}")

def main():
    """Main function"""
    print("CSV to GeoJSON Converter")
    print("=" * 40)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Convert pilgrim stamps CSV to GeoJSON format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Use default input/output files
  %(prog)s -i input.csv -o output.geojson    # Specify custom files
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        default='clean_output_stamps_final_for_geosjon.csv',
        help='Input CSV file path (default: clean_output_stamps_final_for_geosjon.csv)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='pilgrim_stamps.geojson',
        help='Output GeoJSON file path (default: pilgrim_stamps.geojson)'
    )
    
    args = parser.parse_args()
    
    # Load CSV data
    df = load_csv_data(args.input)
    
    # Clean and prepare data
    df_clean = clean_and_prepare_data(df)
    
    # Create GeoJSON features
    features = create_geojson_features(df_clean)
    
    # Create GeoJSON collection
    metadata = {
        "name": "Camino Francés Pilgrim Stamps",
        "description": "Geocoded locations of pilgrim stamps along the Camino Francés pilgrimage route",
        "created": pd.Timestamp.now().isoformat(),
        "source": "Manual review and Google geocoding",
        "total_stamps": len(features),
        "input_file": args.input,
        "conversion_tool": "csv_to_geojson.py"
    }
    
    geojson = create_geojson_collection(features, metadata)
    
    # Save GeoJSON file
    save_geojson(geojson, args.output)
    
    # Create summary report
    create_summary_report(df_clean, args.output)
    
    print("\n✅ Conversion completed successfully!")

if __name__ == "__main__":
    main()
