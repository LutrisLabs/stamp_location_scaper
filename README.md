# Pilgrim Stamp Scraper

A Python web scraper for extracting pilgrim stamp locations from multiple Camino routes including Camino Navarro and Camino Francés.

## Project Overview

This project scrapes the website https://www.lossellosdelcamino.com to extract information about pilgrim stamp locations along multiple Camino routes. It systematically navigates through town pages and stamp location pages to collect data and download stamp images for both the Navarrese Way and the full French Way.

## Features

- Scrapes multiple Camino routes (Navarrese and French Ways)
- Extracts stamp location links from each town per route
- Downloads stamp images locally with robust retry mechanisms
- Extracts comprehensive category information for each location
- Organizes data into structured format with route identification
- Exports results to Excel and CSV formats
- Includes Google Maps geocoding for precise coordinates
- Creates interactive maps with all locations
- Category analysis and standardization for clean data organization
- CSV-to-GeoJSON conversion with simplified property structure

## Project Structure

```
stamp_location_scaper/
├── requirements.txt      # Python dependencies
├── main.py              # Main execution script
├── scraper.py           # Core scraping logic
├── utils.py             # Utility functions
├── analyze_categories.py # Category analysis and standardization
├── csv_to_geojson.py    # CSV to GeoJSON converter
├── data/                # Output data directory
├── images/              # Downloaded images directory
│   └── stamp_images/    # Stamp images organized by location
└── README.md            # This file
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main script:
```bash
python main.py
```

## Output

The scraper produces:
- Excel and CSV files with columns: route, town, place, categories, english_categories, image_path
- Local directory structure with downloaded stamp images
- Structured data with complete category information
- Geocoded coordinates for all locations
- Interactive HTML map with all pilgrim stamp locations
- Clean GeoJSON files with standardized categories for mapping applications

## Dependencies

- requests: HTTP requests
- beautifulsoup4: HTML parsing
- pandas: Data manipulation
- openpyxl: Excel file export
- lxml: XML/HTML parser
- googlemaps: Google Maps API integration
- folium: Interactive map generation
- shapely: Geometric operations
- numpy: Numerical computing

## Status

This project now supports multi-route scraping for both Camino Navarro and Camino Francés routes with robust error handling and retry mechanisms. The scraper automatically processes both routes sequentially, extracts comprehensive category information, and provides precise geocoding via Google Maps API. All 976 locations now have complete category coverage and coordinates. Recent improvements include category standardization and streamlined GeoJSON export for better mapping integration.
