#!/usr/bin/env python3
"""
Test script for the enhanced Pilgrim Stamp Scraper.
Tests the system with only 2 towns to verify functionality.
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
            logging.FileHandler('test_scraping.log'),
            logging.StreamHandler()
        ]
    )

def test_small_sample():
    """Test the scraper with only 2 towns."""
    setup_logging()
    logging.info("Starting Small Sample Test for Pilgrim Stamp Scraper")
    
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
        
        # Step 1: Get first 2 town links only
        logging.info("=" * 60)
        logging.info("Step 1: Extracting first 2 town links from main page")
        logging.info("=" * 60)
        
        all_town_links = scraper.get_town_links()
        if not all_town_links:
            logging.error("Failed to extract town links. Exiting.")
            return
        
        # Take only first 2 towns for testing
        town_links = all_town_links[:2]
        logging.info(f"✓ Testing with first 2 towns out of {len(all_town_links)} total")
        
        # Step 2: Get stamp locations for these 2 towns
        logging.info("=" * 60)
        logging.info("Step 2: Extracting stamp location links from 2 towns")
        logging.info("=" * 60)
        
        town_stamp_locations = scraper.get_stamp_locations_by_town(town_links)
        if not town_stamp_locations:
            logging.error("Failed to extract stamp locations. Exiting.")
            return
        
        total_stamp_locations = sum(len(locations) for locations in town_stamp_locations.values())
        logging.info(f"✓ Found {total_stamp_locations} total stamp locations across 2 towns")
        
        # Step 3: Scrape each stamp location and download images
        logging.info("=" * 60)
        logging.info("Step 3: Scraping stamp location data and downloading images")
        logging.info("=" * 60)
        
        scraped_data = []
        processed_count = 0
        failed_count = 0
        total_processed = 0
        
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
        
        base_filename = "data/test_pilgrim_stamps_2towns"
        if scraper.export_data(df, base_filename):
            logging.info(f"✓ Successfully exported data to:")
            logging.info(f"  - {base_filename}.xlsx")
            logging.info(f"  - {base_filename}.csv")
        else:
            logging.error("Failed to export data to files")
            return
        
        # Final summary
        logging.info("=" * 60)
        logging.info("SMALL SAMPLE TEST COMPLETED SUCCESSFULLY!")
        logging.info("=" * 60)
        logging.info(f"Summary:")
        logging.info(f"  - Towns processed: {len(town_links)} (out of {len(all_town_links)} total)")
        logging.info(f"  - Total stamp locations found: {total_stamp_locations}")
        logging.info(f"  - Successfully processed: {processed_count}")
        logging.info(f"  - Failed to process: {failed_count}")
        logging.info(f"  - Success rate: {(processed_count/total_stamp_locations)*100:.1f}%")
        logging.info(f"  - Data exported to: {base_filename}.xlsx and {base_filename}.csv")
        logging.info(f"  - Images saved to: images/stamp_images/")
        
    except KeyboardInterrupt:
        logging.warning("Test interrupted by user")
        logging.warning("Small sample test stopped")
    except Exception as e:
        logging.error(f"Unexpected error in test execution: {e}")
        logging.error("Small sample test failed")
        raise

if __name__ == "__main__":
    test_small_sample()
