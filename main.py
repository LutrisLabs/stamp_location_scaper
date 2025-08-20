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
        
        # Define routes to scrape
        routes = ["navarro", "frances"]
        all_scraped_data = []
        
        for route in routes:
            logging.info("=" * 60)
            logging.info(f"Processing route: {route.upper()}")
            logging.info("=" * 60)
            
            # Initialize scraper for this route
            scraper = PilgrimStampScraper(route)
            
            # Step 1: Get all town links for this route
            logging.info(f"Step 1: Extracting town links from {scraper.route_name} main page")
            logging.info("=" * 60)
            
            town_links = scraper.get_town_links()
            if not town_links:
                logging.warning(f"No town links found for {scraper.route_name}. Continuing to next route.")
                continue
            
            logging.info(f"✓ Found {len(town_links)} towns to process for {scraper.route_name}")
            
            # Step 2: Get stamp locations for each town in this route
            logging.info(f"Step 2: Extracting stamp location links from each town in {scraper.route_name}")
            logging.info("=" * 60)
            
            town_stamp_locations = scraper.get_stamp_locations_by_town(town_links)
            if not town_stamp_locations:
                logging.warning(f"No stamp locations found for {scraper.route_name}. Continuing to next route.")
                continue
            
            total_stamp_locations = sum(len(locations) for locations in town_stamp_locations.values())
            logging.info(f"✓ Found {total_stamp_locations} total stamp locations across all towns in {scraper.route_name}")
            
            # Step 3: Scrape each stamp location and download images for this route
            logging.info(f"Step 3: Scraping stamp location data and downloading images for {scraper.route_name}")
            logging.info("=" * 60)
            
            route_scraped_data = []
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
                                route_scraped_data.append(stamp_data)
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
                
                # Add 5-second delay after completing each town
                logging.info(f"Completed town: {town_name}. Waiting 5 seconds before next town...")
                time.sleep(5)
            
            logging.info(f"✓ Successfully processed {processed_count} stamp locations for {scraper.route_name}")
            if failed_count > 0:
                logging.warning(f"⚠ Failed to process {failed_count} stamp locations for {scraper.route_name}")
            
            # Add route data to overall collection
            all_scraped_data.extend(route_scraped_data)
            
            # Add delay between routes to be respectful
            if route != routes[-1]:  # Not the last route
                logging.info("Waiting 5 seconds before processing next route...")
                time.sleep(5)
        
        # Step 4: Compile all data into DataFrame
        logging.info("=" * 60)
        logging.info("Step 4: Compiling all route data into DataFrame")
        logging.info("=" * 60)
        
        # Use the last scraper instance to compile data (they all have the same method)
        df = scraper.compile_data(all_scraped_data)
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
        
        # Calculate totals across all routes
        total_processed = len(all_scraped_data)
        total_towns = len(set(item['town_name'] for item in all_scraped_data if 'town_name' in item))
        
        # Calculate route-specific statistics
        route_stats = {}
        for route in routes:
            route_scraper = PilgrimStampScraper(route)
            route_name = route_scraper.route_name
            route_data = [item for item in all_scraped_data if 'route' in item and item['route'] == route_name]
            route_stats[route] = {
                'name': route_name,
                'count': len(route_data),
                'towns': len(set(item['town_name'] for item in route_data if 'town_name' in item))
            }
        
        logging.info(f"Summary:")
        logging.info(f"  - Routes processed: {len(routes)} ({', '.join(routes)})")
        logging.info(f"  - Total towns processed: {total_towns}")
        logging.info(f"  - Total stamp locations successfully processed: {total_processed}")
        
        # Show breakdown by route
        logging.info(f"\nRoute Breakdown:")
        for route, stats in route_stats.items():
            logging.info(f"  - {stats['name']}: {stats['count']} stamp locations from {stats['towns']} towns")
        
        logging.info(f"\nOutput Files:")
        logging.info(f"  - Data exported to: {base_filename}.xlsx and {base_filename}.csv")
        logging.info(f"  - Images saved to: images/stamp_images/")
        
        # Success rate analysis
        if total_processed > 0:
            logging.info(f"\nSuccess Analysis:")
            if total_processed >= 100:
                logging.info(f"  🎉 Excellent results! High volume of data collected")
            elif total_processed >= 50:
                logging.info(f"  📈 Good results! Substantial data collected")
            elif total_processed >= 20:
                logging.info(f"  ✅ Moderate results! Adequate data collected")
            else:
                logging.info(f"  ⚠️  Limited results! Consider reviewing scraping strategy")
        
    except KeyboardInterrupt:
        logging.warning("Scraping interrupted by user")
        logging.warning("Pilgrim Stamp Scraper stopped")
    except Exception as e:
        logging.error(f"Unexpected error in main execution: {e}")
        logging.error("Pilgrim Stamp Scraper failed")
        raise

if __name__ == "__main__":
    main()
