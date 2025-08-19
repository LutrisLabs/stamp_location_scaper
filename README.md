# Pilgrim Stamp Scraper

A Python web scraper for extracting pilgrim stamp locations from the Camino Navarro website.

## Project Overview

This project scrapes the website https://www.lossellosdelcamino.com to extract information about pilgrim stamp locations along the Camino Navarro route. It systematically navigates through town pages and stamp location pages to collect data and download stamp images.

## Features

- Scrapes main page for town category links
- Extracts stamp location links from each town
- Downloads stamp images locally
- Organizes data into structured format
- Exports results to Excel file

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

This project is currently under development with planned subtasks for implementation.
