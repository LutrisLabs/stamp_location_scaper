# Pilgrim Stamp Scraper

A Python web scraper for extracting pilgrim stamp locations from multiple Camino routes including Camino Navarro and Camino Francés.

## Project Overview

This project scrapes the website https://www.lossellosdelcamino.com to extract information about pilgrim stamp locations along multiple Camino routes. It systematically navigates through town pages and stamp location pages to collect data and download stamp images for both the Navarrese Way and the full French Way.

## Features

- Scrapes multiple Camino routes (Navarrese and French Ways)
- Scrapes main page for town category links per route
- Extracts stamp location links from each town per route
- Downloads stamp images locally
- Organizes data into structured format with route identification
- Exports results to Excel file with comprehensive multi-route data

## Project Structure

```
stamp_location_scaper/
├── requirements.txt      # Python dependencies
├── main.py              # Main execution script
├── scraper.py           # Core scraping logic
├── utils.py             # Utility functions
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
- Excel file with columns: route, town, place, image_path
- Local directory structure with downloaded stamp images
- Structured data ready for geocoding analysis

## Dependencies

- requests: HTTP requests
- beautifulsoup4: HTML parsing
- pandas: Data manipulation
- openpyxl: Excel file export
- lxml: XML/HTML parser

## Status

This project now supports multi-route scraping for both Camino Navarro and Camino Francés routes. The scraper automatically processes both routes sequentially and provides comprehensive statistics for each route.
