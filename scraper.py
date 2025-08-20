#!/usr/bin/env python3
"""
Core scraping logic for the Pilgrim Stamp Scraper.
Handles web scraping of pilgrim stamp locations from the Camino Navarro website.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import logging
import re
from typing import List, Dict, Optional

class PilgrimStampScraper:
    """Main scraper class for pilgrim stamp locations."""
    
    def __init__(self):
        """Initialize the scraper with base configuration."""
        self.base_url = "https://www.lossellosdelcamino.com"
        self.main_url = f"{self.base_url}/index.php/ruta-desde-roncesvalles/menu-camino-navarro"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_town_links(self) -> List[str]:
        """
        Extract all town category links from the main page.
        
        Returns:
            List of town URLs
        """
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Fetching main page (attempt {attempt + 1}/{max_retries}): {self.main_url}")
                response = self.session.get(self.main_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all links that contain "menu-camino-navarro/category/"
                town_links = set()  # Use set to automatically remove duplicates
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    if "menu-camino-navarro/category/" in href:
                        full_url = urljoin(self.base_url, href)
                        town_links.add(full_url)  # Add to set (duplicates automatically ignored)
                        logging.info(f"Found town link: {full_url}")
                
                # Convert set back to list for return
                unique_town_links = list(town_links)
                logging.info(f"✓ Total unique town links found: {len(unique_town_links)}")
                return unique_town_links
                
            except requests.RequestException as e:
                logging.error(f"Error fetching main page (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logging.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logging.error("Max retries reached. Failed to fetch main page.")
                    return []
            except Exception as e:
                logging.error(f"Unexpected error in get_town_links (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logging.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logging.error("Max retries reached. Failed to fetch main page.")
                    return []
        
        return []
    
    def get_stamp_locations_by_town(self, town_urls: List[str]) -> Dict[str, List[str]]:
        """
        Extract stamp location links for each town.
        
        Args:
            town_urls: List of town URLs to process
            
        Returns:
            Dictionary mapping town names to lists of stamp location URLs
        """
        town_stamp_locations = {}
        
        for i, town_url in enumerate(town_urls, 1):
            try:
                logging.info(f"Processing town {i}/{len(town_urls)}: {town_url}")
                
                # Add rate limiting delay between requests
                if i > 1:  # Don't delay for the first request
                    time.sleep(1)
                
                response = self.session.get(town_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all links that contain "menu-camino-navarro/item/"
                stamp_links = set()  # Use set to avoid duplicates
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    if "menu-camino-navarro/item/" in href:
                        full_url = urljoin(self.base_url, href)
                        stamp_links.add(full_url)
                
                # Convert set to list
                unique_stamp_links = list(stamp_links)
                
                # Extract town name from URL for the dictionary key
                from utils import extract_town_name_from_url
                town_name = extract_town_name_from_url(town_url)
                
                town_stamp_locations[town_name] = unique_stamp_links
                logging.info(f"Found {len(unique_stamp_links)} stamp locations for {town_name}")
                
            except requests.RequestException as e:
                logging.error(f"Error fetching town page {town_url}: {e}")
                # Add empty list for failed towns to maintain structure
                from utils import extract_town_name_from_url
                town_name = extract_town_name_from_url(town_url)
                town_stamp_locations[town_name] = []
            except Exception as e:
                logging.error(f"Unexpected error processing town {town_url}: {e}")
                # Add empty list for failed towns to maintain structure
                from utils import extract_town_name_from_url
                town_name = extract_town_name_from_url(town_url)
                town_stamp_locations[town_name] = []
        
        total_stamp_locations = sum(len(locations) for locations in town_stamp_locations.values())
        logging.info(f"Total stamp locations found across all towns: {total_stamp_locations}")
        
        return town_stamp_locations
    
    def scrape_stamp_location(self, stamp_url: str) -> Optional[Dict]:
        """
        Scrape individual stamp location page for place name, image, and categories.
        
        Args:
            stamp_url: URL of the stamp location page
            
        Returns:
            Dictionary with place name, image URL, categories, and stamp URL, or None if failed
        """
        try:
            logging.info(f"Scraping stamp location: {stamp_url}")
            
            response = self.session.get(stamp_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract place name - try multiple selectors
            place_name = None
            
            # Try to find the main heading (h1, h2, or h3)
            for heading_tag in ['h1', 'h2', 'h3']:
                heading = soup.find(heading_tag)
                if heading and heading.text.strip():
                    place_name = heading.text.strip()
                    break
            
            # If no heading found, try to find title attribute or other text elements
            if not place_name:
                title_tag = soup.find('title')
                if title_tag and title_tag.text.strip():
                    place_name = title_tag.text.strip()
            
            if not place_name:
                logging.warning(f"Could not extract place name from {stamp_url}")
                return None
            
            # Extract image URL - look for img tags with stamp images
            image_url = None
            
            # Look for images that might be stamp images
            img_tags = soup.find_all('img', src=True)
            for img in img_tags:
                src = img['src']
                # Check if this looks like a stamp image (contains media/zoo/images)
                if 'media/zoo/images' in src:
                    image_url = urljoin(self.base_url, src)
                    break
            
            # If no media/zoo/images found, try to find any image
            if not image_url and img_tags:
                # Get the first image that's not a logo or navigation element
                for img in img_tags:
                    src = img['src']
                    # Skip common non-stamp images
                    if any(skip in src.lower() for skip in ['logo', 'nav', 'header', 'footer', 'banner']):
                        continue
                    image_url = urljoin(self.base_url, src)
                    break
            
            if not image_url:
                logging.warning(f"Could not extract image URL from {stamp_url}")
                return None
            
            # Extract categories using robust, multi-strategy approach
            categories_set = set()

            # 1) Primary: containers with element-itemcategory (regardless of extra classes)
            for container in soup.select('div.element-itemcategory, div.element.element-itemcategory'):
                for a in container.select('a[href]'):
                    txt = a.get_text(strip=True)
                    if txt:
                        categories_set.add(txt)

            # 2) Fallback: same category container under .pos-bottom
            if not categories_set:
                for container in soup.select('div.pos-bottom div.element-itemcategory'):
                    for a in container.select('a[href]'):
                        txt = a.get_text(strip=True)
                        if txt:
                            categories_set.add(txt)

            # 3) Fallback: look for a heading that contains "Categor" and grab links within that same block
            if not categories_set:
                heading = soup.find(lambda tag: tag.name in ('h3', 'h4') and re.search(r'categor', tag.get_text(strip=True), re.I))
                if heading:
                    parent = heading.parent
                    for a in parent.find_all('a', href=True):
                        txt = a.get_text(strip=True)
                        if txt:
                            categories_set.add(txt)

            categories = sorted(categories_set)
            if not categories:
                logging.warning(f"No categories found for page: {stamp_url}")
            else:
                logging.info(f"Found {len(categories)} categories: {', '.join(categories)}")
            
            result = {
                'place_name': place_name,
                'image_url': image_url,
                'stamp_url': stamp_url,
                'categories': categories
            }
            
            logging.info(f"Successfully extracted: {place_name} with image: {image_url}")
            if categories:
                logging.info(f"Categories: {', '.join(categories)}")
            
            return result
            
        except requests.RequestException as e:
            logging.error(f"Error fetching stamp location page {stamp_url}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error scraping stamp location {stamp_url}: {e}")
            return None
    
    def download_stamp_image(self, image_url: str, local_path: str) -> bool:
        """
        Download stamp image and save to local path.
        
        Args:
            image_url: URL of the stamp image
            local_path: Local file path to save the image
            
        Returns:
            True if successful, False otherwise
        """
        max_retries = 2
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Downloading image (attempt {attempt + 1}/{max_retries}): {image_url}")
                
                # Ensure the directory exists
                import os
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                # Download the image with streaming for large files
                response = self.session.get(image_url, stream=True, timeout=30)
                response.raise_for_status()
                
                # Check if it's actually an image
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    logging.warning(f"URL does not point to an image: {content_type}")
                    return False
                
                # Check file size (skip if too large, likely not an image)
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
                    logging.warning(f"File too large ({int(content_length)} bytes), likely not an image")
                    return False
                
                # Save the image
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # Filter out keep-alive chunks
                            f.write(chunk)
                
                # Verify the file was created and has content
                if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                    file_size = os.path.getsize(local_path)
                    logging.info(f"✓ Successfully downloaded image to: {local_path} ({file_size} bytes)")
                    return True
                else:
                    logging.error(f"Failed to save image to: {local_path}")
                    if attempt < max_retries - 1:
                        logging.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    return False
                    
            except requests.RequestException as e:
                logging.error(f"Error downloading image (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logging.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                return False
            except Exception as e:
                logging.error(f"Unexpected error downloading image (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logging.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                return False
        
        return False
    
    def compile_data(self, scraped_data: List[Dict]) -> 'pandas.DataFrame':
        """
        Compile scraped data into a pandas DataFrame.
        
        Args:
            scraped_data: List of dictionaries containing scraped data
            
        Returns:
            Pandas DataFrame with columns: route, town, place, categories, english_categories, image_path
        """
        try:
            import pandas as pd
            from utils import translate_categories_to_english, normalize_categories
            
            # Prepare data for DataFrame
            compiled_data = []
            
            for item in scraped_data:
                if item and 'place_name' in item and 'image_url' in item:
                    # Get town name from the stored town_name field
                    town_name = item.get('town_name', 'Unknown Town')
                    
                    # Create local image path
                    import os
                    from utils import sanitize_filename
                    
                    # Extract filename from image URL
                    image_filename = os.path.basename(item['image_url'])
                    # Sanitize the filename
                    safe_filename = sanitize_filename(image_filename)
                    # Create local path in images/stamp_images directory
                    local_image_path = os.path.join('images', 'stamp_images', safe_filename)
                    
                    # Get categories and normalize them
                    categories = normalize_categories(item.get('categories', []))
                    categories_text = '; '.join(categories) if categories else ''
                    
                    # Translate categories to English
                    english_categories = translate_categories_to_english(categories)
                    english_categories_text = '; '.join(english_categories) if english_categories else ''
                    
                    compiled_data.append({
                        'route': 'Camino Navarro',
                        'town': town_name,
                        'place': item['place_name'],
                        'categories': categories_text,
                        'english_categories': english_categories_text,
                        'image_path': local_image_path
                    })
            
            # Create DataFrame
            df = pd.DataFrame(compiled_data)
            
            # Validate DataFrame structure
            expected_columns = ['route', 'town', 'place', 'categories', 'english_categories', 'image_path']
            if not all(col in df.columns for col in expected_columns):
                missing_cols = [col for col in expected_columns if col not in df.columns]
                logging.error(f"Missing columns in DataFrame: {missing_cols}")
                return pd.DataFrame()
            
            logging.info(f"Successfully compiled data into DataFrame with {len(df)} rows")
            logging.info(f"DataFrame columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logging.error(f"Error compiling data: {e}")
            return pd.DataFrame()
    
    def export_data(self, df: 'pandas.DataFrame', base_filename: str) -> bool:
        """
        Export DataFrame to both Excel and CSV formats.
        
        Args:
            df: Pandas DataFrame to export
            base_filename: Base filename without extension (will create .xlsx and .csv)
            
        Returns:
            True if both exports successful, False otherwise
        """
        try:
            import pandas as pd
            import os
            
            # Check if DataFrame is empty
            if df.empty:
                logging.error("Cannot export empty DataFrame")
                return False
            
            # Ensure the data directory exists
            data_dir = os.path.dirname(base_filename)
            if data_dir:
                os.makedirs(data_dir, exist_ok=True)
            
            success_count = 0
            
            # Export to Excel
            excel_filename = f"{base_filename}.xlsx"
            try:
                df.to_excel(excel_filename, index=False, engine='openpyxl')
                
                # Verify the Excel file was created
                if os.path.exists(excel_filename) and os.path.getsize(excel_filename) > 0:
                    logging.info(f"Successfully exported DataFrame to Excel: {excel_filename}")
                    logging.info(f"Excel file size: {os.path.getsize(excel_filename)} bytes")
                    success_count += 1
                else:
                    logging.error(f"Failed to create Excel file: {excel_filename}")
            except Exception as e:
                logging.error(f"Error exporting to Excel: {e}")
            
            # Export to CSV
            csv_filename = f"{base_filename}.csv"
            try:
                df.to_csv(csv_filename, index=False, encoding='utf-8')
                
                # Verify the CSV file was created
                if os.path.exists(csv_filename) and os.path.getsize(csv_filename) > 0:
                    logging.info(f"Successfully exported DataFrame to CSV: {csv_filename}")
                    logging.info(f"CSV file size: {os.path.getsize(csv_filename)} bytes")
                    success_count += 1
                else:
                    logging.error(f"Failed to create CSV file: {csv_filename}")
            except Exception as e:
                logging.error(f"Error exporting to CSV: {e}")
            
            # Log DataFrame information
            logging.info(f"DataFrame shape: {df.shape}")
            logging.info(f"DataFrame columns: {list(df.columns)}")
            
            # Return True if at least one export was successful
            return success_count > 0
                
        except Exception as e:
            logging.error(f"Error in export_data: {e}")
            return False
