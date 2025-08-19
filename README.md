# Pilgrim Stamp Location Scraper

A Python web scraper designed to extract pilgrim stamp locations from the Camino Navarro route website and organize them into a structured dataset for geocoding analysis.

## Project Overview

This project scrapes the website [Los Sellos del Camino](https://www.lossellosdelcamino.com/index.php/ruta-desde-roncesvalles/menu-camino-navarro) to collect information about pilgrim stamp locations along the Camino Navarro route. The scraper navigates through a three-level hierarchy:

1. **Main Page** → Lists all towns along the route
2. **Town Pages** → Lists all stamp locations within each town
3. **Stamp Location Pages** → Contains place names and stamp images

## Features

- Systematic extraction of all town names and stamp locations
- Automatic download of stamp images with organized local storage
- Data compilation into structured format with columns: `route`, `town`, `place`, `image_path`
- Excel export for further analysis and geocoding
- Rate limiting and error handling for robust scraping
- Progress tracking and logging

## Project Structure

```
stamp_location_scaper/
├── requirements.txt          # Python dependencies
├── main.py                  # Main execution script
├── scraper.py               # Core scraping logic
├── utils.py                 # Utility functions
├── data/                    # Output data directory
├── images/                  # Downloaded stamp images
│   └── stamp_images/        # Organized by town/location
└── README.md                # This file
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd stamp_location_scaper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main scraper:
```bash
python main.py
```

The scraper will:
- Extract all town and stamp location data
- Download stamp images to the `images/stamp_images/` directory
- Generate an Excel file in the `data/` directory with columns:
  - `route`: Route name (Camino Navarro)
  - `town`: Town name
  - `place`: Specific stamp location name
  - `image_path`: Local path to downloaded image

## Output

- **Excel File**: `data/pilgrim_stamps.xlsx` containing all scraped data
- **Images**: Downloaded stamp images organized in local directory structure
- **Logs**: Progress tracking and error reporting during execution

## Data Structure

The final dataset will contain entries like:
- Route: Camino Navarro
- Town: Roncesvalles / Orreaga
- Place: Apartamentos Casa de los Beneficiados
- Image Path: images/stamp_images/roncesvalles12_23a33a5cf90998a466ef4977db95e958.jpg

## Requirements

- Python 3.8+
- Internet connection for web scraping
- Sufficient disk space for image downloads

## License

This project is for educational and research purposes. Please respect the website's terms of service and implement appropriate rate limiting when scraping.
