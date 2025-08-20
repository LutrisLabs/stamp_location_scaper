#!/usr/bin/env python3
"""
Geocoding script for pilgrim stamps data.
Converts town and place names to coordinates using free geocoding services.
"""

import pandas as pd
import time
import requests
from typing import Tuple, Optional, Dict, Any
import folium
from folium import Popup, Marker
import logging
from pathlib import Path
import json
import googlemaps
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PilgrimStampGeocoder:
    """Geocoder for pilgrim stamp locations using free services."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PilgrimStampGeocoder/1.0 (https://github.com/yourusername)'
        })
        self.rate_limit_delay = 1.0  # seconds between requests
        
        # Initialize Google Maps client (optional)
        self.google_client = None
        google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if google_api_key:
            try:
                self.google_client = googlemaps.Client(key=google_api_key)
                logger.info("✅ Google Maps API client initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize Google Maps API: {e}")
                self.google_client = None
        else:
            logger.warning("⚠️  GOOGLE_MAPS_API_KEY environment variable not set - Google geocoding disabled")
        
        logger.info("PilgrimStampGeocoder initialized successfully")
        logger.info(f"Rate limiting set to {self.rate_limit_delay} seconds between requests")
        if self.google_client:
            logger.info("🌍 Dual geocoding enabled: Nominatim + Google Maps")
        else:
            logger.info("🌍 Single geocoding: Nominatim only")
    
    def geocode_nominatim(self, query: str) -> Optional[Tuple[float, float]]:
        """
        Geocode using OpenStreetMap Nominatim service (free).
        
        Args:
            query: Search query string
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'es'  # Restrict to Spain
            }
            
            logger.debug(f"Querying Nominatim with: {query}")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                lat = float(result['lat'])
                lon = float(result['lon'])
                logger.info(f"Found coordinates for '{query}': ({lat}, {lon})")
                return (lat, lon)
            else:
                logger.warning(f"No results found for '{query}'")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for '{query}': {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"Data parsing error for '{query}': {e}")
            return None
    
    def geocode_google(self, query: str) -> Optional[Tuple[float, float]]:
        """
        Geocode using Google Maps Geocoding API.
        
        Args:
            query: Search query string
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        if not self.google_client:
            logger.debug("Google Maps API not available")
            return None
            
        try:
            logger.debug(f"Querying Google Maps with: {query}")
            
            # Google Maps geocoding with region bias for Spain
            result = self.google_client.geocode(
                query,
                region='es',  # Bias towards Spain
                language='en'
            )
            
            if result and len(result) > 0:
                location = result[0]['geometry']['location']
                lat = location['lat']
                lng = location['lng']
                
                # Check if the result is in Spain (basic validation)
                if 'address_components' in result[0]:
                    country_found = False
                    for component in result[0]['address_components']:
                        if 'country' in component['types'] and component['short_name'] == 'ES':
                            country_found = True
                            break
                    
                    if not country_found:
                        logger.warning(f"Google result for '{query}' may not be in Spain")
                
                logger.info(f"Found Google coordinates for '{query}': ({lat}, {lng})")
                return (lat, lng)
            else:
                logger.debug(f"No Google results found for '{query}'")
                return None
                
        except Exception as e:
            logger.error(f"Google geocoding error for '{query}': {e}")
            return None
    
    def geocode_location(self, place: str, town: str) -> Dict[str, Any]:
        """
        Geocode a location using both Nominatim and Google Maps APIs.
        Returns results from both services for comparison.
        
        Args:
            place: Specific place name
            town: Town name
            
        Returns:
            Dictionary with results from both services and final coordinates
        """
        logger.info(f"Starting dual geocoding for place='{place}', town='{town}'")
        
        # Initialize result structure
        result = {
            'nominatim_coords': None,
            'google_coords': None,
            'final_coords': None,
            'nominatim_query': '',
            'google_query': '',
            'geocoding_source': 'none',
            'confidence': 'low'
        }
        
        # Only Strategy 1: Place + Town + Spain (building-level precision required)
        if not place or not place.strip():
            logger.warning(f"❌ Empty place name - cannot geocode with required precision for town '{town}'")
            return result
            
        query = f"{place}, {town}, Spain"
        result['nominatim_query'] = query
        result['google_query'] = query
        
        # Try Nominatim first
        logger.info(f"🌐 Nominatim: Trying '{query}'")
        nominatim_coords = self.geocode_nominatim(query)
        result['nominatim_coords'] = nominatim_coords
        
        if nominatim_coords:
            logger.info(f"✅ Nominatim successful: {nominatim_coords}")
        else:
            logger.warning(f"❌ Nominatim failed")
        
        # Try Google Maps (if available)
        if self.google_client:
            logger.info(f"🗺️  Google Maps: Trying '{query}'")
            google_coords = self.geocode_google(query)
            result['google_coords'] = google_coords
            
            if google_coords:
                logger.info(f"✅ Google Maps successful: {google_coords}")
            else:
                logger.warning(f"❌ Google Maps failed")
        else:
            logger.info("🗺️  Google Maps: Not available")
        
        # Determine final coordinates and confidence
        if nominatim_coords and self.google_client and google_coords:
            # Both services succeeded - check if they're close
            lat_diff = abs(nominatim_coords[0] - google_coords[0])
            lon_diff = abs(nominatim_coords[1] - google_coords[1])
            
            if lat_diff < 0.001 and lon_diff < 0.001:  # Very close coordinates
                result['final_coords'] = nominatim_coords  # Prefer Nominatim (free)
                result['geocoding_source'] = 'nominatim'
                result['confidence'] = 'very_high'
                logger.info(f"🎯 High confidence: Both services agree → {result['final_coords']}")
            else:
                # Different coordinates - prefer the one closer to town center
                # For now, prefer Nominatim as it's free and usually accurate
                result['final_coords'] = nominatim_coords
                result['geocoding_source'] = 'nominatim'
                result['confidence'] = 'high'
                logger.info(f"⚠️  Different coordinates - using Nominatim → {result['final_coords']}")
                
        elif nominatim_coords:
            result['final_coords'] = nominatim_coords
            result['geocoding_source'] = 'nominatim'
            result['confidence'] = 'medium'
            logger.info(f"✅ Nominatim only → {result['final_coords']}")
            
        elif self.google_client and google_coords:
            result['final_coords'] = google_coords
            result['geocoding_source'] = 'google'
            result['confidence'] = 'medium'
            logger.info(f"✅ Google Maps only → {result['final_coords']}")
            
        else:
            logger.warning(f"❌ Both services failed for '{place}' in '{town}'")
        
        return result
    
    def geocode_dataset(self, csv_path: str) -> pd.DataFrame:
        """
        Geocode the entire pilgrim stamps dataset.
        
        Args:
            csv_path: Path to the input CSV file
            
        Returns:
            DataFrame with added latitude and longitude columns
        """
        logger.info(f"Loading dataset from {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Add coordinate columns for dual geocoding
        df['latitude'] = None
        df['longitude'] = None
        df['geocoding_status'] = 'pending'
        df['geocoding_source'] = 'none'
        df['confidence'] = 'low'
        
        # Nominatim results
        df['nominatim_latitude'] = None
        df['nominatim_longitude'] = None
        df['nominatim_query'] = ''
        df['nominatim_success'] = False
        
        # Google Maps results
        df['google_latitude'] = None
        df['google_longitude'] = None
        df['google_query'] = ''
        df['google_success'] = False
        
        total_rows = len(df)
        successful_geocodes = 0
        
        logger.info(f"Starting geocoding of {total_rows} locations...")
        logger.info("Note: Only building-level precision accepted - town-level coordinates will be rejected")
        
        for index, row in df.iterrows():
            place = str(row['place']).strip()
            town = str(row['town']).strip()
            
            logger.info(f"\n--- Processing {index + 1}/{total_rows}: {place} in {town} ---")
            
            geocoding_result = self.geocode_location(place, town)
            
            # Store Nominatim results
            if geocoding_result['nominatim_coords']:
                df.at[index, 'nominatim_latitude'] = geocoding_result['nominatim_coords'][0]
                df.at[index, 'nominatim_longitude'] = geocoding_result['nominatim_coords'][1]
                df.at[index, 'nominatim_success'] = True
                df.at[index, 'nominatim_query'] = geocoding_result['nominatim_query']
            
            # Store Google Maps results
            if geocoding_result['google_coords']:
                df.at[index, 'google_latitude'] = geocoding_result['google_coords'][0]
                df.at[index, 'google_longitude'] = geocoding_result['google_coords'][1]
                df.at[index, 'google_success'] = False  # Will be set to True below
                df.at[index, 'google_query'] = geocoding_result['google_query']
            
            # Store final results
            if geocoding_result['final_coords']:
                df.at[index, 'latitude'] = geocoding_result['final_coords'][0]
                df.at[index, 'longitude'] = geocoding_result['final_coords'][1]
                df.at[index, 'geocoding_status'] = 'success'
                df.at[index, 'geocoding_source'] = geocoding_result['geocoding_source']
                df.at[index, 'confidence'] = geocoding_result['confidence']
                
                # Mark Google as successful if it was used
                if geocoding_result['geocoding_source'] == 'google':
                    df.at[index, 'google_success'] = True
                
                successful_geocodes += 1
                logger.info(f"✅ Row {index + 1} geocoded successfully via {geocoding_result['geocoding_source']}: {geocoding_result['final_coords']} (confidence: {geocoding_result['confidence']})")
            else:
                df.at[index, 'geocoding_status'] = 'failed'
                df.at[index, 'geocoding_source'] = 'none'
                df.at[index, 'confidence'] = 'low'
                logger.warning(f"❌ Row {index + 1} geocoding failed on both services")
            
            # Rate limiting between requests
            time.sleep(self.rate_limit_delay)
            
            # Progress update every 5 rows
            if (index + 1) % 5 == 0:
                current_success_rate = (successful_geocodes / (index + 1)) * 100
                
                # Count Nominatim and Google successes
                nominatim_successes = df.head(index + 1)['nominatim_success'].sum()
                google_successes = df.head(index + 1)['google_success'].sum()
                
                logger.info(f"📊 Progress: {index + 1}/{total_rows} ({((index + 1)/total_rows)*100:.1f}%)")
                logger.info(f"   • Overall success rate: {current_success_rate:.1f}%")
                logger.info(f"   • Nominatim successes: {nominatim_successes}")
                logger.info(f"   • Google Maps successes: {google_successes}")
        
        # Final summary with dual geocoding statistics
        final_success_rate = (successful_geocodes / total_rows) * 100
        nominatim_total_successes = df['nominatim_success'].sum()
        google_total_successes = df['google_success'].sum()
        
        logger.info(f"\n🎯 DUAL GECODING COMPLETE!")
        logger.info(f"Total locations processed: {total_rows}")
        logger.info(f"Overall successfully geocoded: {successful_geocodes}")
        logger.info(f"Failed geocoding: {total_rows - successful_geocodes}")
        logger.info(f"Final success rate: {final_success_rate:.1f}%")
        
        logger.info(f"\n📊 Service Performance:")
        logger.info(f"   • Nominatim: {nominatim_total_successes}/{total_rows} ({nominatim_total_successes/total_rows*100:.1f}%)")
        logger.info(f"   • Google Maps: {google_total_successes}/{total_rows} ({google_total_successes/total_rows*100:.1f}%)")
        
        if final_success_rate < 50:
            logger.warning("⚠️  Low success rate - consider reviewing place names or geocoding strategy")
        elif final_success_rate < 80:
            logger.info("📈 Moderate success rate - some locations may need manual review")
        else:
            logger.info("🎉 High success rate - excellent results!")
        
        return df
    
    def create_folium_map(self, df: pd.DataFrame, output_path: str = "pilgrim_stamps_map.html"):
        """
        Create an interactive Folium map of all geocoded locations.
        
        Args:
            df: DataFrame with latitude, longitude columns
            output_path: Path to save the HTML map
        """
        # Filter successful geocodes
        geocoded_df = df[df['geocoding_status'] == 'success'].copy()
        
        if len(geocoded_df) == 0:
            logger.error("❌ No successful geocodes to map!")
            return
        
        logger.info(f"Creating interactive map with {len(geocoded_df)} successfully geocoded locations")
        
        # Calculate center of the map (average of all coordinates)
        center_lat = geocoded_df['latitude'].mean()
        center_lon = geocoded_df['longitude'].mean()
        
        logger.info(f"Map center calculated: ({center_lat:.6f}, {center_lon:.6f})")
        
        # Create the map with appropriate zoom level for Camino de Santiago region
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Add markers for each successfully geocoded location
        marker_count = 0
        for _, row in geocoded_df.iterrows():
            # Prepare popup content with all relevant information
            place = str(row['place'])
            town = str(row['town'])
            route = str(row['route'])
            categories_en = str(row['english_categories']) if pd.notna(row['english_categories']) and row['english_categories'] else 'N/A'
            categories_es = str(row['categories']) if pd.notna(row['categories']) and row['categories'] else 'N/A'
            lat = row['latitude']
            lon = row['longitude']
            
            # Create detailed popup content with dual geocoding info
            confidence = row.get('confidence', 'low')
            source = row.get('geocoding_source', 'unknown')
            
            # Get Nominatim and Google results if available
            nominatim_lat = row.get('nominatim_latitude')
            nominatim_lon = row.get('nominatim_longitude')
            google_lat = row.get('google_latitude')
            google_lon = row.get('google_longitude')
            
            # Get image path and check if it exists
            image_path = row.get('image_path', '')
            image_html = ""
            if pd.notna(image_path) and image_path and Path(image_path).exists():
                image_html = f"""
                <div style="text-align: center; margin: 10px 0;">
                    <img src="{image_path}" alt="Pilgrim Stamp" style="max-width: 280px; max-height: 200px; border: 2px solid #ddd; border-radius: 5px;">
                </div>
                <hr style="margin: 8px 0;">
                """
            
            popup_content = f"""
            <div style="width: 320px; font-family: Arial, sans-serif;">
                <h3 style="color: #2E8B57; margin-bottom: 10px; font-size: 16px;">{place}</h3>
                <hr style="margin: 8px 0;">
                <p style="margin: 5px 0;"><strong>🏘️ Town:</strong> {town}</p>
                <p style="margin: 5px 0;"><strong>🚶‍♂️ Route:</strong> {route}</p>
                <p style="margin: 5px 0;"><strong>📍 Final Coordinates:</strong> {lat:.6f}, {lon:.6f}</p>
                <p style="margin: 5px 0;"><strong>🎯 Source:</strong> {source} ({confidence} confidence)</p>
                <hr style="margin: 8px 0;">
                <p style="margin: 5px 0; font-size: 11px;"><strong>Nominatim:</strong> {f'{nominatim_lat:.6f}, {nominatim_lon:.6f}' if pd.notna(nominatim_lat) else 'Failed'}</p>
                <p style="margin: 5px 0; font-size: 11px;"><strong>Google Maps:</strong> {f'{google_lat:.6f}, {google_lon:.6f}' if pd.notna(google_lat) else 'Failed'}</p>
                <hr style="margin: 8px 0;">
                {image_html}
                <p style="margin: 5px 0; font-size: 12px;"><strong>Categories (EN):</strong><br>{categories_en if pd.notna(categories_en) and categories_en else 'N/A'}</p>
                <p style="margin: 5px 0; font-size: 12px;"><strong>Categorías (ES):</strong><br>{categories_es if pd.notna(categories_es) and categories_es else 'N/A'}</p>
            </div>
            """
            
            # Create tooltip (short preview on hover)
            tooltip_text = f"{place} - {town}"
            if len(tooltip_text) > 40:
                tooltip_text = tooltip_text[:37] + "..."
            
            # Add marker with different colors based on category and confidence
            marker_color = 'blue'  # default
            
            # Check both place name and categories for better color determination
            place_lower = place.lower()
            categories_en_lower = str(categories_en).lower() if pd.notna(categories_en) and categories_en else ""
            categories_es_lower = str(categories_es).lower() if pd.notna(categories_es) and categories_es else ""
            
            if ('albergue' in place_lower or 'hostel' in place_lower or 
                'hostel' in categories_en_lower or 'albergue' in categories_es_lower):
                marker_color = 'green'  # Hostels/Albergues
            elif ('hotel' in place_lower or 'hotel' in categories_en_lower or 
                  'hotel' in categories_es_lower):
                marker_color = 'purple'  # Hotels
            elif ('bar' in place_lower or 'restaurant' in place_lower or 'café' in place_lower or
                  'bar' in categories_en_lower or 'restaurant' in categories_en_lower or
                  'bar' in categories_es_lower or 'restaurante' in categories_es_lower):
                marker_color = 'orange'  # Food & Drink
            elif ('iglesia' in place_lower or 'catedral' in place_lower or 'church' in place_lower or
                  'church' in categories_en_lower or 'iglesia' in categories_es_lower or 
                  'catedral' in categories_es_lower):
                marker_color = 'red'  # Religious sites
            
            # Add confidence indicator to tooltip
            confidence = row.get('confidence', 'low')
            source = row.get('geocoding_source', 'unknown')
            tooltip_text = f"{place} - {town} ({confidence} confidence, {source})"
            if len(tooltip_text) > 50:
                tooltip_text = tooltip_text[:47] + "..."
            
            # Add marker to map
            Marker(
                location=[lat, lon],
                popup=Popup(popup_content, max_width=300),
                tooltip=tooltip_text,
                icon=folium.Icon(color=marker_color, icon='info-sign')
            ).add_to(m)
            
            marker_count += 1
        
        # Add a legend to explain marker colors and confidence
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 250px; height: 200px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>Legend</h4>
        <i class="fa fa-map-marker fa-2x" style="color:green"></i> Albergues/Hostels<br>
        <i class="fa fa-map-marker fa-2x" style="color:purple"></i> Hotels<br>
        <i class="fa fa-map-marker fa-2x" style="color:orange"></i> Bars/Restaurants<br>
        <i class="fa fa-map-marker fa-2x" style="color:red"></i> Religious Sites<br>
        <i class="fa fa-map-marker fa-2x" style="color:blue"></i> Other Locations<br>
        <hr style="margin: 8px 0;">
        <strong>Confidence Levels:</strong><br>
        🎯 Very High: Both services agree<br>
        ✅ High: Both services tried<br>
        📍 Medium: One service succeeded<br>
        ⚠️ Low: Both services failed
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save the map
        m.save(output_path)
        logger.info(f"✅ Interactive map saved to {output_path}")
        logger.info(f"📍 Added {marker_count} markers to the map")
        
        # Create a summary text file
        summary_path = output_path.replace('.html', '_summary.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"Pilgrim Stamps Interactive Map Summary\n")
            f.write(f"=====================================\n\n")
            f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total locations in dataset: {len(df)}\n")
            f.write(f"Successfully geocoded: {len(geocoded_df)}\n")
            f.write(f"Failed geocoding: {len(df) - len(geocoded_df)}\n")
            f.write(f"Success rate: {(len(geocoded_df)/len(df))*100:.1f}%\n\n")
            
            # Dual geocoding statistics
            nominatim_successes = df['nominatim_success'].sum()
            google_successes = df['google_success'].sum()
            f.write(f"Dual Geocoding Performance:\n")
            f.write(f"- Nominatim: {nominatim_successes}/{len(df)} ({nominatim_successes/len(df)*100:.1f}%)\n")
            f.write(f"- Google Maps: {google_successes}/{len(df)} ({google_successes/len(df)*100:.1f}%)\n\n")
            
            f.write(f"Map Details:\n")
            f.write(f"- Center coordinates: {center_lat:.6f}, {center_lon:.6f}\n")
            f.write(f"- Markers added: {marker_count}\n")
            f.write(f"- Map file: {output_path}\n\n")
            
            f.write(f"Marker Color Legend:\n")
            f.write(f"- Green: Albergues/Hostels\n")
            f.write(f"- Purple: Hotels\n")
            f.write(f"- Orange: Bars/Restaurants\n")
            f.write(f"- Red: Religious Sites\n")
            f.write(f"- Blue: Other Locations\n\n")
            
            if len(geocoded_df) > 0:
                f.write(f"Successfully Geocoded Locations:\n")
                f.write(f"--------------------------------\n")
                for idx, row in geocoded_df.iterrows():
                    f.write(f"{idx+1}. {row['place']} in {row['town']} → ({row['latitude']:.6f}, {row['longitude']:.6f})\n")
            
            if len(df) - len(geocoded_df) > 0:
                failed_df = df[df['geocoding_status'] == 'failed']
                f.write(f"\nFailed Geocoding Locations:\n")
                f.write(f"---------------------------\n")
                for idx, row in failed_df.iterrows():
                    f.write(f"{idx+1}. {row['place']} in {row['town']}\n")
        
        logger.info(f"📄 Summary report saved to {summary_path}")
        logger.info(f"🌐 Open {output_path} in your browser to view the interactive map!")

def main():
    """Main function to run the complete pilgrim stamps geocoding process."""
    logger.info("🚀 Starting Pilgrim Stamps Geocoding Script")
    logger.info("=" * 60)
    
    # File paths
    input_csv = "data/pilgrim_stamps.csv"
    output_csv = "data/pilgrim_stamps_geocoded.csv"
    output_excel = "data/pilgrim_stamps_geocoded.xlsx"
    map_output = "pilgrim_stamps_map.html"
    
    # Check if input file exists
    if not Path(input_csv).exists():
        logger.error(f"❌ Input file not found: {input_csv}")
        logger.error("Please ensure the pilgrim_stamps.csv file exists in the data/ directory")
        return
    
    # Initialize geocoder
    try:
        logger.info("🔧 Initializing geocoder...")
        geocoder = PilgrimStampGeocoder()
        logger.info("✅ Geocoder initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize geocoder: {e}")
        return
    
    try:
        # Step 1: Geocode the entire dataset
        logger.info("\n" + "="*60)
        logger.info("STEP 1: GECODING ENTIRE DATASET")
        logger.info("="*60)
        
        logger.info(f"📁 Processing dataset: {input_csv}")
        logger.info("⚠️  Note: Only building-level precision accepted - this may take several minutes")
        
        start_time = time.time()
        geocoded_df = geocoder.geocode_dataset(input_csv)
        end_time = time.time()
        
        processing_time = end_time - start_time
        logger.info(f"⏱️  Dataset processing completed in {processing_time:.1f} seconds")
        
        # Step 2: Save geocoded data to CSV
        logger.info("\n" + "="*60)
        logger.info("STEP 2: SAVING GECODED DATA")
        logger.info("="*60)
        
        try:
            # Save to CSV
            geocoded_df.to_csv(output_csv, index=False)
            csv_size = Path(output_csv).stat().st_size
            logger.info(f"✅ Geocoded data saved to CSV: {output_csv} ({csv_size} bytes)")
            
            # Save to Excel
            try:
                geocoded_df.to_excel(output_excel, index=False)
                excel_size = Path(output_excel).stat().st_size
                logger.info(f"✅ Geocoded data saved to Excel: {output_excel} ({excel_size} bytes)")
            except Exception as e:
                logger.warning(f"⚠️  Could not save to Excel: {e}")
                logger.info("📊 CSV file is still available for data analysis")
            
        except Exception as e:
            logger.error(f"❌ Failed to save geocoded data: {e}")
            return
        
        # Step 3: Create interactive map
        logger.info("\n" + "="*60)
        logger.info("STEP 3: CREATING INTERACTIVE MAP")
        logger.info("="*60)
        
        successful_geocodes = len(geocoded_df[geocoded_df['geocoding_status'] == 'success'])
        
        if successful_geocodes > 0:
            logger.info(f"🗺️  Creating map with {successful_geocodes} successfully geocoded locations...")
            geocoder.create_folium_map(geocoded_df, map_output)
            
            # Verify map creation
            if Path(map_output).exists():
                map_size = Path(map_output).stat().st_size
                logger.info(f"✅ Interactive map created: {map_output} ({map_size} bytes)")
            else:
                logger.error(f"❌ Map file not created: {map_output}")
        else:
            logger.warning("⚠️  No successful geocodes - cannot create map")
        
        # Final summary and recommendations
        logger.info("\n" + "="*60)
        logger.info("🎯 FINAL SUMMARY & RECOMMENDATIONS")
        logger.info("="*60)
        
        total_locations = len(geocoded_df)
        failed_geocodes = total_locations - successful_geocodes
        success_rate = (successful_geocodes / total_locations) * 100
        
        logger.info(f"📊 Total locations processed: {total_locations}")
        logger.info(f"✅ Successfully geocoded: {successful_geocodes}")
        logger.info(f"❌ Failed geocoding: {failed_geocodes}")
        logger.info(f"📈 Success rate: {success_rate:.1f}%")
        logger.info(f"⏱️  Total processing time: {processing_time:.1f} seconds")
        
        # Success rate analysis and recommendations
        if success_rate >= 80:
            logger.info("🎉 Excellent results! High success rate achieved")
        elif success_rate >= 60:
            logger.info("📈 Good results! Moderate success rate - some locations may need review")
        elif success_rate >= 40:
            logger.info("⚠️  Moderate results - consider reviewing place names for failed locations")
        else:
            logger.warning("🔴 Low success rate - consider reviewing geocoding strategy or place names")
        
        # File locations
        logger.info(f"\n📁 Output files created:")
        logger.info(f"   • Geocoded CSV: {output_csv}")
        if Path(output_excel).exists():
            logger.info(f"   • Geocoded Excel: {output_excel}")
        if successful_geocodes > 0:
            logger.info(f"   • Interactive map: {map_output}")
            logger.info(f"   • Summary report: {map_output.replace('.html', '_summary.txt')}")
        
        logger.info(f"\n🌐 Next steps:")
        logger.info(f"   1. Review the geocoded CSV/Excel files for data quality")
        logger.info(f"   2. Open the HTML map in your browser to visualize locations")
        logger.info(f"   3. Use coordinates for further spatial analysis if needed")
        
        logger.info("\n🎉 Pilgrim stamps geocoding process completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ An error occurred during processing: {e}")
        logger.error("Please check the error details above and try again")
        raise

if __name__ == "__main__":
    main()
