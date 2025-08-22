#!/usr/bin/env python3
"""
Map visualization script for Camino Francés stages.
Creates an interactive HTML map with numbered markers and connecting lines.
"""

import json
import folium
from typing import Dict, Any, List, Tuple
import re

class CaminoVisualizer:
    """Visualizer for Camino Francés route on an interactive map."""
    
    def __init__(self):
        """Initialize the visualizer."""
        self.map = None
        self.stops_data = []
        self.stage_markers = {}
    
    def load_geocoded_data(self, file_path: str) -> Dict[str, Any]:
        """Load the geocoded Camino Francés data."""
        print(f"Loading geocoded data from: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded data for {len(data['stages'])} stages")
        return data
    
    def extract_stops_in_order(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract stops in sequential order, ignoring B variant routes.
        Returns a list of stops with sequential numbering.
        """
        stops = []
        stop_number = 1
        
        # Sort stages by stage number (1A, 1B, 2, 3, etc.)
        sorted_stages = sorted(data['stages'], key=self._sort_stage_key)
        
        for stage in sorted_stages:
            stage_num = stage['stage_number']
            
            # Skip B variant routes as requested
            if stage_num.endswith('B'):
                print(f"⏭️  Skipping B variant: Stage {stage_num}")
                continue
            
            print(f"Processing Stage {stage_num}: {stage['stage_name']}")
            
            for stop in stage['stops']:
                # Add stop number and stage info
                stop_with_metadata = stop.copy()
                stop_with_metadata['stop_number'] = stop_number
                stop_with_metadata['stage_number'] = stage_num
                stop_with_metadata['stage_name'] = stage['stage_name']
                
                stops.append(stop_with_metadata)
                stop_number += 1
        
        print(f"✅ Extracted {len(stops)} stops in sequential order")
        return stops
    
    def _sort_stage_key(self, stage: Dict[str, Any]) -> Tuple[int, str]:
        """Sort key for stages: numeric part first, then letter."""
        stage_num = stage['stage_number']
        match = re.match(r'(\d+)([A-Z]?)', stage_num)
        if match:
            num = int(match.group(1))
            letter = match.group(2) or ''
            return (num, letter)
        return (999, stage_num)  # Fallback for unexpected formats
    
    def create_map(self, stops: List[Dict[str, Any]]) -> None:
        """Create the interactive map with stops and route lines."""
        if not stops:
            print("❌ No stops to visualize")
            return
        
        # Calculate map center from all coordinates
        lats = [stop['lat'] for stop in stops if stop['lat'] is not None]
        lngs = [stop['long'] for stop in stops if stop['long'] is not None]
        
        if not lats or not lngs:
            print("❌ No valid coordinates found")
            return
        
        center_lat = sum(lats) / len(lats)
        center_lng = sum(lngs) / len(lngs)
        
        # Create map centered on the route
        self.map = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        print(f"🗺️  Created map centered at ({center_lat:.4f}, {center_lng:.4f})")
        
        # Add stops as numbered markers
        self._add_stop_markers(stops)
        
        # Add route lines connecting consecutive stops
        self._add_route_lines(stops)
        
        # Add legend
        self._add_legend()
    
    def _add_stop_markers(self, stops: List[Dict[str, Any]]) -> None:
        """Add numbered markers for each stop."""
        print("📍 Adding stop markers...")
        
        for stop in stops:
            if stop['lat'] is None or stop['long'] is None:
                print(f"⚠️  Skipping {stop['name']} - no coordinates")
                continue
            
            # Create popup content
            popup_content = f"""
            <div style="min-width: 200px;">
                <h4>Stop {stop['stop_number']}</h4>
                <p><strong>{stop['name']}</strong></p>
                <p>Stage: {stop['stage_number']}</p>
                <p>Province: {stop['province']}</p>
                <p>Country: {stop['country']}</p>
                <p>Distance: {stop['distance_from_start']:.1f} km</p>
            </div>
            """
            
            # Create marker with stop number
            marker = folium.Marker(
                location=[stop['lat'], stop['long']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{stop['stop_number']}: {stop['name']}",
                icon=folium.DivIcon(
                    html=f'<div style="background-color: #e74c3c; color: white; border-radius: 50%; width: 25px; height: 25px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">{stop["stop_number"]}</div>',
                    icon_size=(25, 25),
                    icon_anchor=(12, 12)
                )
            )
            
            marker.add_to(self.map)
            
            # Store marker info for route lines
            self.stops_data.append({
                'stop_number': stop['stop_number'],
                'name': stop['name'],
                'lat': stop['lat'],
                'long': stop['long'],
                'stage': stop['stage_number']
            })
        
        print(f"✅ Added {len(self.stops_data)} stop markers")
    
    def _add_route_lines(self, stops: List[Dict[str, Any]]) -> None:
        """Add lines connecting consecutive stops."""
        print("🛤️  Adding route lines...")
        
        # Sort stops by stop number to ensure proper order
        sorted_stops = sorted(self.stops_data, key=lambda x: x['stop_number'])
        
        # Create route line connecting all stops
        route_coords = []
        for stop in sorted_stops:
            route_coords.append([stop['lat'], stop['long']])
        
        # Add the main route line
        folium.PolyLine(
            locations=route_coords,
            color='#3498db',
            weight=3,
            opacity=0.8,
            popup='Camino Francés Main Route'
        ).add_to(self.map)
        
        print(f"✅ Added route line connecting {len(route_coords)} stops")
    
    def _add_legend(self) -> None:
        """Add a legend to the map."""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>Camino Francés Route</h4>
        <p><span style="color: #e74c3c;">🔴</span> Numbered stops (1, 2, 3...)</p>
        <p><span style="color: #3498db;">🔵</span> Route line</p>
        <p><small>Click markers for details</small></p>
        </div>
        '''
        
        self.map.get_root().html.add_child(folium.Element(legend_html))
        print("✅ Added map legend")
    
    def save_map(self, output_file: str) -> None:
        """Save the map to an HTML file."""
        if not self.map:
            print("❌ No map to save")
            return
        
        self.map.save(output_file)
        print(f"✅ Map saved to: {output_file}")
    
    def visualize_camino(self, input_file: str, output_file: str) -> None:
        """Main function to create the Camino Francés visualization."""
        try:
            # Load data
            data = self.load_geocoded_data(input_file)
            
            # Extract stops in order
            stops = self.extract_stops_in_order(data)
            
            # Create map
            self.create_map(stops)
            
            # Save map
            self.save_map(output_file)
            
            print(f"\n🎯 Visualization completed!")
            print(f"   Map saved to: {output_file}")
            print(f"   Total stops visualized: {len(self.stops_data)}")
            print(f"   Open the HTML file in your web browser to view the map")
            
        except Exception as e:
            print(f"❌ Error during visualization: {e}")
            raise

def main():
    """Main function to run the Camino Francés visualization."""
    input_file = "camino_frances_geocoded.json"
    output_file = "camino_frances_map.html"
    
    try:
        visualizer = CaminoVisualizer()
        visualizer.visualize_camino(input_file, output_file)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
