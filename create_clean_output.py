#!/usr/bin/env python3
"""
Clean Output Creator

This script processes the reviewed coordinates from the manual research
and creates clean output files with corrected stamp positions.
It also handles new stamps and copies stamp images.
"""

import pandas as pd
import numpy as np
import folium
import re
import warnings
import shutil
import os
warnings.filterwarnings('ignore')

def load_reviewed_data(filepath):
    """Load and process the reviewed Excel file"""
    print("Loading reviewed data...")
    
    # Load the reviewed file
    df = pd.read_excel(filepath)
    
    # Clean up column names and remove duplicates
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Remove rows with 'CLOSED' in Google_coords
    closed_count = len(df[df['Google_coords'] == 'CLOSED'])
    df = df[df['Google_coords'] != 'CLOSED'].copy()
    
    print(f"✓ Loaded {len(df)} reviewed stamps (removed {closed_count} CLOSED entries)")
    
    return df

def copy_stamp_images(df, stamp_images_folder):
    """Copy stamp images to the stamp_images folder"""
    print("Copying stamp images...")
    
    # Filter for new stamps (those with English_category)
    new_stamps = df[df['English_category'].notna()].copy()
    
    if len(new_stamps) == 0:
        print("No new stamps with images found")
        return
    
    # Create stamp_images folder if it doesn't exist
    os.makedirs(stamp_images_folder, exist_ok=True)
    
    copied_count = 0
    for idx, stamp in new_stamps.iterrows():
        stamp_path = stamp['Stamp_download_path']
        
        if pd.isna(stamp_path) or stamp_path == '':
            continue
            
        # Clean the path (remove trailing spaces and normalize)
        stamp_path = str(stamp_path).strip()
        
        # Extract filename from path
        filename = os.path.basename(stamp_path)
        
        # Create destination path
        dest_path = os.path.join(stamp_images_folder, filename)
        
        try:
            # Copy the image file
            shutil.copy2(stamp_path, dest_path)
            copied_count += 1
            print(f"  ✓ Copied: {filename}")
        except Exception as e:
            print(f"  ❌ Error copying {filename}: {e}")
    
    print(f"✓ Copied {copied_count} stamp images to {stamp_images_folder}")

def parse_google_coordinates(coord_string):
    """Parse Google coordinates string into lat, lon"""
    try:
        # Extract numbers from string like "42.80844559731623, -7.614917734223901"
        coords = re.findall(r'-?\d+\.\d+', coord_string)
        if len(coords) >= 2:
            lat = float(coords[0])
            lon = float(coords[1])
            return lat, lon
        else:
            print(f"Warning: Could not parse coordinates: {coord_string}")
            return None, None
    except Exception as e:
        print(f"Error parsing coordinates '{coord_string}': {e}")
        return None, None

def process_reviewed_coordinates(df):
    """Process the Google_coords column into separate lat/lon columns"""
    print("Processing Google coordinates...")
    
    # Parse coordinates
    coords_list = []
    for idx, row in df.iterrows():
        lat, lon = parse_google_coordinates(row['Google_coords'])
        coords_list.append({
            'place': row['Place Name'],
            'town': row['Town'],
            'new_lat': lat,
            'new_lon': lon,
            'old_lat': row['Current Latitude'],
            'old_lon': row['Current Longitude'],
            'distance_km': row['Distance from Trail (km)'],
            'english_category': row.get('English_category', None),
            'stamp_download_path': row.get('Stamp_download_path', None)
        })
    
    coords_df = pd.DataFrame(coords_list)
    
    # Remove any rows where coordinates couldn't be parsed
    coords_df = coords_df.dropna(subset=['new_lat', 'new_lon'])
    
    print(f"✓ Processed {len(coords_df)} valid coordinate sets")
    return coords_df

def update_original_stamps(original_csv_path, corrected_coords_df, closed_stamps_df):
    """Update the original stamps CSV with corrected coordinates and remove closed stamps"""
    print("Updating original stamps data...")
    
    # Load original stamps
    original_df = pd.read_csv(original_csv_path)
    print(f"✓ Loaded {len(original_df)} original stamps")
    
    # Create a copy for updating
    updated_df = original_df.copy()
    
    # Update coordinates for corrected stamps
    updates_count = 0
    for _, corrected in corrected_coords_df.iterrows():
        # Find matching stamp in original data
        mask = (updated_df['place'] == corrected['place']) & (updated_df['town'] == corrected['town'])
        
        if mask.any():
            updated_df.loc[mask, 'latitude'] = corrected['new_lat']
            updated_df.loc[mask, 'longitude'] = corrected['new_lon']
            updates_count += 1
        else:
            print(f"Warning: Could not find stamp '{corrected['place']}' in {corrected['town']}")
    
    # Remove closed stamps
    closed_count = 0
    for _, closed_stamp in closed_stamps_df.iterrows():
        mask = (updated_df['place'] == closed_stamp['Place Name']) & (updated_df['town'] == closed_stamp['Town'])
        if mask.any():
            updated_df = updated_df[~mask]
            closed_count += 1
    
    print(f"✓ Updated coordinates for {updates_count} stamps")
    print(f"✓ Removed {closed_count} closed stamps")
    print(f"✓ Final dataset: {len(updated_df)} stamps")
    
    return updated_df

def add_new_stamps(updated_df, corrected_coords_df):
    """Add new stamps that weren't in the original dataset"""
    print("Adding new stamps...")
    
    # Filter for new stamps (those with English_category)
    new_stamps = corrected_coords_df[corrected_coords_df['english_category'].notna()].copy()
    
    if len(new_stamps) == 0:
        print("No new stamps to add")
        return updated_df
    
    # Create new rows for new stamps
    new_rows = []
    for _, new_stamp in new_stamps.iterrows():
        new_row = {
            'place': new_stamp['place'],
            'town': new_stamp['town'],
            'latitude': new_stamp['new_lat'],
            'longitude': new_stamp['new_lon'],
            'category': new_stamp['english_category'],
            'country': 'Spain',  # Default for Camino Francés
            'region': 'Camino Francés'
        }
        new_rows.append(new_row)
    
    # Add new rows to the dataframe
    new_df = pd.DataFrame(new_rows)
    updated_df = pd.concat([updated_df, new_df], ignore_index=True)
    
    print(f"✓ Added {len(new_stamps)} new stamps")
    print(f"✓ Final dataset: {len(updated_df)} stamps")
    
    return updated_df

def create_clean_output_files(updated_df, corrected_coords_df):
    """Create clean output files in CSV and Excel formats"""
    print("Creating clean output files...")
    
    # CSV output
    csv_filename = 'clean_output_stamps.csv'
    updated_df.to_csv(csv_filename, index=False)
    print(f"✓ CSV file saved: {csv_filename}")
    
    # Excel output with formatting
    excel_filename = 'clean_output_stamps.xlsx'
    
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        # Main stamps data
        updated_df.to_excel(writer, sheet_name='All Stamps', index=False)
        
        # Summary of corrections
        summary_data = []
        for _, corrected in corrected_coords_df.iterrows():
            summary_data.append({
                'Place Name': corrected['place'],
                'Town': corrected['town'],
                'Old Coordinates': f"{corrected['old_lat']:.6f}, {corrected['old_lon']:.6f}",
                'New Coordinates': f"{corrected['new_lat']:.6f}, {corrected['new_lon']:.6f}",
                'Old Distance from Trail (km)': corrected['distance_km'],
                'Correction Type': 'Manual Review',
                'English Category': corrected.get('english_category', 'N/A')
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Corrections Summary', index=False)
    
    print(f"✓ Excel file saved: {excel_filename}")
    
    return csv_filename, excel_filename

def create_verification_map(updated_df, trail_geojson_path, corrected_coords_df):
    """Create a verification map showing the corrected stamp positions"""
    print("Creating verification map...")
    
    # Load trail data
    import json
    with open(trail_geojson_path, 'r') as f:
        trail_data = json.load(f)
    
    trail_coords = trail_data['features'][0]['geometry']['coordinates']
    
    # Calculate map center
    trail_lats = [coord[1] for coord in trail_coords]
    trail_lons = [coord[0] for coord in trail_coords]
    center_lat = (min(trail_lats) + max(trail_lats)) / 2
    center_lon = (min(trail_lons) + max(trail_lons)) / 2
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles='OpenStreetMap'
    )
    
    # Add trail
    folium.PolyLine(
        locations=[[coord[1], coord[0]] for coord in trail_coords],
        color='blue',
        weight=4,
        opacity=0.8,
        popup='Camino Frances Trail'
    ).add_to(m)
    
    # Add stamps
    for _, stamp in updated_df.iterrows():
        if pd.isna(stamp['latitude']) or pd.isna(stamp['longitude']):
            continue
        
        # Check if this stamp was corrected
        was_corrected = any(
            (corrected_coords_df['place'] == stamp['place']) & 
            (corrected_coords_df['town'] == stamp['town'])
            for _, corrected_coords_df in corrected_coords_df.iterrows()
        )
        
        # Check if this is a new stamp
        is_new = any(
            (corrected_coords_df['place'] == stamp['place']) & 
            (corrected_coords_df['town'] == stamp['town']) &
            (pd.notna(corrected_coords_df['english_category']) if hasattr(corrected_coords_df, 'english_category') else False)
            for _, corrected_coords_df in corrected_coords_df.iterrows()
        )
        
        # Color code: green for original, orange for corrected, red for new
        if is_new:
            color = 'red'
            status = '🆕 New'
        elif was_corrected:
            color = 'orange'
            status = '🔄 Corrected'
        else:
            color = 'green'
            status = '✅ Original'
        
        popup_text = f"""
        <b>{stamp['place']}</b><br>
        Town: {stamp['town']}<br>
        Coordinates: {stamp['latitude']:.6f}, {stamp['longitude']:.6f}<br>
        Status: {status}
        """
        
        folium.CircleMarker(
            location=[stamp['latitude'], stamp['longitude']],
            radius=4,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 250px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 15px; border-radius: 5px;">
    <h4 style="margin: 0 0 10px 0;">Verification Map Legend</h4>
    <p><span style="color:green;">●</span> Original coordinates</p>
    <p><span style="color:orange;">●</span> Corrected coordinates</p>
    <p><span style="color:red;">●</span> New stamps</p>
    <p><span style="color:blue;">━</span> Camino Frances Trail</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save map
    map_filename = 'clean_output_verification_map.html'
    m.save(map_filename)
    print(f"✓ Verification map saved: {map_filename}")
    
    return map_filename

def main():
    """Main function"""
    print("Clean Output Creator")
    print("=" * 50)
    
    # File paths
    reviewed_file = 'wrongly_geocoded_stamps_5.0km_reviewed_2.xlsx'
    original_csv = 'data/pilgrim_stamps_geocoded.csv'
    trail_geojson = 'camino_frances_main_trail_simple.geojson'
    stamp_images_folder = 'images/stamp_images'
    
    # Step 1: Load and process reviewed data
    reviewed_df = load_reviewed_data(reviewed_file)
    
    # Step 1.5: Copy stamp images
    copy_stamp_images(reviewed_df, stamp_images_folder)
    
    # Get closed stamps before removing them
    closed_stamps_df = pd.read_excel(reviewed_file)
    closed_stamps_df = closed_stamps_df[closed_stamps_df['Google_coords'] == 'CLOSED'].copy()
    
    # Step 2: Process Google coordinates
    corrected_coords_df = process_reviewed_coordinates(reviewed_df)
    
    # Step 3: Update original stamps
    updated_stamps_df = update_original_stamps(original_csv, corrected_coords_df, closed_stamps_df)
    
    # Step 4: Add new stamps
    updated_stamps_df = add_new_stamps(updated_stamps_df, corrected_coords_df)
    
    # Step 5: Create clean output files
    csv_file, excel_file = create_clean_output_files(updated_stamps_df, corrected_coords_df)
    
    # Step 6: Create verification map
    map_file = create_verification_map(updated_stamps_df, trail_geojson, corrected_coords_df)
    
    print("\n" + "=" * 50)
    print("✅ PROCESSING COMPLETE!")
    print(f"📊 Clean CSV: {csv_file}")
    print(f"📊 Clean Excel: {excel_file}")
    print(f"🗺️  Verification Map: {map_file}")
    print(f"🔄 Total stamps corrected: {len(corrected_coords_df)}")
    print(f"❌ Total stamps removed (CLOSED): {len(closed_stamps_df)}")
    print(f"🆕 Total new stamps added: {len(corrected_coords_df[corrected_coords_df['english_category'].notna()])}")
    print(f"📍 Total stamps in output: {len(updated_stamps_df)}")

if __name__ == "__main__":
    main()
