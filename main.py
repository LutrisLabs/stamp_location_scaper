#!/usr/bin/env python3
"""
Main execution script for the Pilgrim Stamp Scraper.
Scrapes pilgrim stamp locations from the Camino Navarro website.
"""

from scraper import PilgrimStampScraper
import logging
import time

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraping.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main execution function."""
    setup_logging()
    logging.info("Starting Pilgrim Stamp Scraper")
    
    try:
        # Validate category translations before starting
        from utils import validate_category_translations
        logging.info("=" * 60)
        logging.info("Validating category translations...")
        logging.info("=" * 60)
        
        if not validate_category_translations():
            logging.error("Category translation validation failed. Exiting.")
            return
        
        # Initialize scraper
        scraper = PilgrimStampScraper()
        
        # Step 1: Get all town links
        logging.info("=" * 60)
        logging.info("Step 1: Extracting town links from main page")
        logging.info("=" * 60)
        
        town_links = scraper.get_town_links()
        if not town_links:
            logging.error("Failed to extract town links. Exiting.")
            return
        
        logging.info(f"✓ Found {len(town_links)} towns to process")
        
        # Step 2: Get stamp locations for each town
        logging.info("=" * 60)
        logging.info("Step 2: Extracting stamp location links from each town")
        logging.info("=" * 60)
        
        town_stamp_locations = scraper.get_stamp_locations_by_town(town_links)
        if not town_stamp_locations:
            logging.error("Failed to extract stamp locations. Exiting.")
            return
        
        total_stamp_locations = sum(len(locations) for locations in town_stamp_locations.values())
        logging.info(f"✓ Found {total_stamp_locations} total stamp locations across all towns")
        
        # Step 3: Scrape each stamp location and download images
        logging.info("=" * 60)
        logging.info("Step 3: Scraping stamp location data and downloading images")
        logging.info("=" * 60)
        
        scraped_data = []
        processed_count = 0
        failed_count = 0
        total_processed = 0
        missing_category_urls = []
        
        for town_name, stamp_urls in town_stamp_locations.items():
            logging.info(f"Processing stamp locations for town: {town_name} ({len(stamp_urls)} locations)")
            
            for i, stamp_url in enumerate(stamp_urls, 1):
                total_processed += 1
                try:
                    logging.info(f"  [{total_processed}/{total_stamp_locations}] Processing: {stamp_url.split('/')[-1]}")
                    
                    # Add rate limiting delay between requests
                    if i > 1:  # Don't delay for the first request
                        time.sleep(1)
                    
                    # Scrape the stamp location
                    stamp_data = scraper.scrape_stamp_location(stamp_url)
                    if stamp_data:
                        # Track missing categories
                        if not stamp_data.get('categories'):
                            missing_category_urls.append(stamp_url)
                            logging.warning(f"[NO CATEGORIES] {stamp_url}")
                        
                        # Download the image
                        import os
                        from utils import sanitize_filename
                        
                        image_filename = os.path.basename(stamp_data['image_url'])
                        safe_filename = sanitize_filename(image_filename)
                        local_image_path = os.path.join('images', 'stamp_images', safe_filename)
                        
                        if scraper.download_stamp_image(stamp_data['image_url'], local_image_path):
                            # Update the stamp data with local image path and town name
                            stamp_data['local_image_path'] = local_image_path
                            stamp_data['town_name'] = town_name  # Add the town name from the dictionary
                            scraped_data.append(stamp_data)
                            processed_count += 1
                            logging.info(f"    ✓ Successfully processed: {stamp_data['place_name']}")
                        else:
                            logging.warning(f"    ⚠ Failed to download image for: {stamp_data['place_name']}")
                            failed_count += 1
                    else:
                        logging.warning(f"    ⚠ Failed to scrape stamp location: {stamp_url}")
                        failed_count += 1
                        
                except Exception as e:
                    logging.error(f"    ✗ Error processing stamp location {stamp_url}: {e}")
                    failed_count += 1
                    continue
        
        logging.info(f"✓ Successfully processed {processed_count} stamp locations")
        if failed_count > 0:
            logging.warning(f"⚠ Failed to process {failed_count} stamp locations")
        
        # Missing categories summary
        if missing_category_urls:
            logging.warning("=" * 60)
            logging.warning("Pages with NO categories detected:")
            for u in missing_category_urls:
                logging.warning(f" - {u}")
            logging.warning("=" * 60)
        
        # Step 4: Compile data into DataFrame
        logging.info("=" * 60)
        logging.info("Step 4: Compiling data into DataFrame")
        logging.info("=" * 60)
        
        df = scraper.compile_data(scraped_data)
        if df.empty:
            logging.error("Failed to compile data. Exiting.")
            return
        
        logging.info(f"✓ DataFrame created with {len(df)} rows and columns: {list(df.columns)}")
        
        # Step 5: Export to Excel and CSV
        logging.info("=" * 60)
        logging.info("Step 5: Exporting data to Excel and CSV")
        logging.info("=" * 60)
        
        base_filename = "data/pilgrim_stamps"
        if scraper.export_data(df, base_filename):
            logging.info(f"✓ Successfully exported data to:")
            logging.info(f"  - {base_filename}.xlsx")
            logging.info(f"  - {base_filename}.csv")
        else:
            logging.error("Failed to export data to files")
            return
        
        # Final summary
        logging.info("=" * 60)
        logging.info("SCRAPING COMPLETED SUCCESSFULLY!")
        logging.info("=" * 60)
        logging.info(f"Summary:")
        logging.info(f"  - Towns processed: {len(town_links)}")
        logging.info(f"  - Total stamp locations found: {total_stamp_locations}")
        logging.info(f"  - Successfully processed: {processed_count}")
        logging.info(f"  - Failed to process: {failed_count}")
        logging.info(f"  - Success rate: {(processed_count/total_stamp_locations)*100:.1f}%")
        logging.info(f"  - Data exported to: {base_filename}.xlsx and {base_filename}.csv")
        logging.info(f"  - Images saved to: images/stamp_images/")
        
    except KeyboardInterrupt:
        logging.warning("Scraping interrupted by user")
        logging.warning("Pilgrim Stamp Scraper stopped")
    except Exception as e:
        logging.error(f"Unexpected error in main execution: {e}")
        logging.error("Pilgrim Stamp Scraper failed")
        raise

if __name__ == "__main__":
    main()
