#!/usr/bin/env python3
"""
Camino Francés Route Analysis
Analyzes the stages, distances, difficulties, and provides insights from the route data.
"""

import json
import statistics
from collections import Counter, defaultdict
from typing import Dict, List, Any

def load_camino_data(file_path: str) -> Dict[str, Any]:
    """Load and validate the Camino data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return None

def analyze_route_overview(data: Dict[str, Any]) -> None:
    """Display basic route overview."""
    print("=" * 60)
    print("CAMINO FRANCÉS ROUTE OVERVIEW")
    print("=" * 60)
    print(f"Route: {data['route']}")
    print(f"Start: {data['start']}")
    print(f"End: {data['end']}")
    print(f"Total Stages: {len(data['stages'])}")
    print()

def analyze_stages(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze stage information and return statistics."""
    stages = data['stages']
    
    # Basic statistics
    total_distance = sum(stage['distance_km'] for stage in stages)
    avg_stage_distance = total_distance / len(stages)
    
    # Difficulty analysis
    difficulties = [stage['difficulty'] for stage in stages]
    difficulty_counts = Counter(difficulties)
    
    # Time analysis
    time_ranges = []
    for stage in stages:
        time_str = stage['average_time_hours']
        if '-' in time_str:
            try:
                min_time, max_time = map(float, time_str.split('-'))
                time_ranges.append((min_time, max_time))
            except ValueError:
                continue
    
    avg_min_time = statistics.mean([t[0] for t in time_ranges]) if time_ranges else 0
    avg_max_time = statistics.mean([t[1] for t in time_ranges]) if time_ranges else 0
    
    # Country and province analysis
    countries = set()
    provinces = set()
    for stage in stages:
        for stop in stage['stops']:
            countries.add(stop['country'])
            provinces.add(stop['province'])
    
    return {
        'total_distance': total_distance,
        'avg_stage_distance': avg_stage_distance,
        'difficulty_counts': difficulty_counts,
        'avg_min_time': avg_min_time,
        'avg_max_time': avg_max_time,
        'countries': countries,
        'provinces': provinces,
        'stages': stages
    }

def analyze_stops(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze stop information across all stages."""
    all_stops = []
    for stage in data['stages']:
        for stop in stage['stops']:
            all_stops.append(stop)
    
    # Country distribution
    country_counts = Counter(stop['country'] for stop in all_stops)
    
    # Province distribution
    province_counts = Counter(stop['province'] for stop in all_stops)
    
    # Distance analysis
    distances = [stop['distance_from_start'] for stop in all_stops if 'distance_from_start' in stop]
    
    return {
        'total_stops': len(all_stops),
        'country_counts': country_counts,
        'province_counts': province_counts,
        'distances': distances
    }

def display_stage_analysis(stats: Dict[str, Any]) -> None:
    """Display stage analysis results."""
    print("STAGE ANALYSIS")
    print("-" * 40)
    print(f"Total Route Distance: {stats['total_distance']:.1f} km")
    print(f"Average Stage Distance: {stats['avg_stage_distance']:.1f} km")
    print(f"Average Stage Time: {stats['avg_min_time']:.1f}-{stats['avg_max_time']:.1f} hours")
    print()
    
    print("Difficulty Distribution:")
    for difficulty, count in stats['difficulty_counts'].items():
        print(f"  {difficulty}: {count} stages")
    print()
    
    print("Countries Visited:")
    for country in sorted(stats['countries']):
        print(f"  {country}")
    print()
    
    print("Provinces/Regions Visited:")
    for province in sorted(stats['provinces']):
        print(f"  {province}")
    print()

def display_stop_analysis(stop_stats: Dict[str, Any]) -> None:
    """Display stop analysis results."""
    print("STOP ANALYSIS")
    print("-" * 40)
    print(f"Total Stops: {stop_stats['total_stops']}")
    print()
    
    print("Country Distribution:")
    for country, count in stop_stats['country_counts'].most_common():
        print(f"  {country}: {count} stops")
    print()
    
    print("Province/Region Distribution (Top 10):")
    for province, count in stop_stats['province_counts'].most_common(10):
        print(f"  {province}: {count} stops")
    print()

def analyze_stage_variations(data: Dict[str, Any]) -> None:
    """Analyze variations in stage planning."""
    print("STAGE VARIATIONS ANALYSIS")
    print("-" * 40)
    
    # Find stages with alternatives
    stage_numbers = [stage['stage_number'] for stage in data['stages']]
    stage_counts = Counter(stage_numbers)
    
    alternative_stages = {num: count for num, count in stage_counts.items() if count > 1}
    
    if alternative_stages:
        print("Stages with Alternative Routes:")
        for stage_num, count in alternative_stages.items():
            print(f"  Stage {stage_num}: {count} alternatives")
            
            # Show the alternatives
            alternatives = [s for s in data['stages'] if s['stage_number'] == stage_num]
            for alt in alternatives:
                print(f"    - {alt['stage_name']} ({alt['distance_km']} km)")
        print()
    else:
        print("No alternative stage routes found.")
        print()

def analyze_distance_progression(data: Dict[str, Any]) -> None:
    """Analyze how distances progress throughout the route."""
    print("DISTANCE PROGRESSION ANALYSIS")
    print("-" * 40)
    
    # Sort stages by stage number for proper progression
    sorted_stages = sorted(data['stages'], key=lambda x: x['stage_number'])
    
    print("Stage-by-Stage Distance Progression:")
    cumulative_distance = 0
    for stage in sorted_stages:
        cumulative_distance += stage['distance_km']
        print(f"  Stage {stage['stage_number']}: {stage['distance_km']:.1f} km "
              f"(Total: {cumulative_distance:.1f} km)")
    
    print()
    
    # Find longest and shortest stages
    longest_stage = max(data['stages'], key=lambda x: x['distance_km'])
    shortest_stage = min(data['stages'], key=lambda x: x['distance_km'])
    
    print(f"Longest Stage: {longest_stage['stage_name']} ({longest_stage['distance_km']} km)")
    print(f"Shortest Stage: {shortest_stage['stage_name']} ({shortest_stage['distance_km']} km)")
    print()

def main():
    """Main analysis function."""
    # Load data
    data = load_camino_data('camino_frances_stages.json')
    if not data:
        return
    
    # Perform analysis
    stage_stats = analyze_stages(data)
    stop_stats = analyze_stops(data)
    
    # Display results
    analyze_route_overview(data)
    display_stage_analysis(stage_stats)
    display_stop_analysis(stop_stats)
    analyze_stage_variations(data)
    analyze_distance_progression(data)
    
    # Additional insights
    print("ADDITIONAL INSIGHTS")
    print("-" * 40)
    print(f"• The route crosses {len(stage_stats['countries'])} countries")
    print(f"• Pilgrims visit {len(stage_stats['provinces'])} different provinces/regions")
    print(f"• Average daily walking distance: {stage_stats['avg_stage_distance']:.1f} km")
    print(f"• Total estimated walking time: {stage_stats['avg_max_time'] * len(data['stages']):.0f} hours")
    print(f"• The route offers {len([s for s in data['stages'] if 'A' in s['stage_number'] or 'B' in s['stage_number']])} alternative route options")

if __name__ == "__main__":
    main()
