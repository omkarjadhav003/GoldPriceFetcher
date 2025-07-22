#!/usr/bin/env python3
"""
Main Gold Price Scraper
Orchestrates scraping from multiple jewellers and pushes to Firebase
"""

import argparse
import json
from datetime import datetime
from gold_price_scraper import GoldPriceManager
import logging

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Multi-Jeweller Gold Price Scraper')
    parser.add_argument('--firebase-key', type=str, help='Path to Firebase service account JSON file')
    parser.add_argument('--jewellers', nargs='+', choices=['tanishq', 'kalyan', 'joyalukkas'], 
                       default=['tanishq'], help='Jewellers to scrape')
    parser.add_argument('--cities', nargs='+', help='Specific cities to scrape')
    parser.add_argument('--days', type=int, default=30, help='Number of days of historical data')
    parser.add_argument('--collection', type=str, default='gold_prices', help='Firebase collection name')
    parser.add_argument('--no-firebase', action='store_true', help='Skip Firebase upload')
    parser.add_argument('--output-file', type=str, help='Save JSON output to file')
    
    args = parser.parse_args()
    
    # Initialize manager
    firebase_path = None if args.no_firebase else args.firebase_key
    manager = GoldPriceManager(firebase_path)
    
    # Scrape data
    if len(args.jewellers) == 1:
        # Single jeweller
        jeweller = args.jewellers[0]
        logger.info(f"Scraping {jeweller} for {args.days} days")
        data = manager.scrape_jeweller(jeweller, args.cities, args.days)
        all_data = {jeweller: data}
    else:
        # Multiple jewellers
        logger.info(f"Scraping {len(args.jewellers)} jewellers for {args.days} days")
        all_data = {}
        for jeweller in args.jewellers:
            data = manager.scrape_jeweller(jeweller, args.cities, args.days)
            all_data[jeweller] = data
    
    # Flatten data for Firebase
    flat_data = []
    for jeweller_data in all_data.values():
        flat_data.extend(jeweller_data)
    
    # Create summary for display only
    summary = manager.create_summary_data(all_data)
    
    # Output results
    print(f"\n📊 SCRAPING RESULTS:")
    print(f"Total entries: {len(flat_data)}")
    print(f"Jewellers: {summary['jewellers']}")
    print(f"Cities: {summary['cities']}")
    print(f"Date range: {summary['date_range']['from']} to {summary['date_range']['to']}")
    
    # Save to file if requested
    if args.output_file:
        output_data = {
            "data": [item.to_dict() for item in flat_data],
            "summary": summary
        }
        with open(args.output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        logger.info(f"Data saved to {args.output_file}")
    
    # Push to Firebase
    if not args.no_firebase and manager.firebase_manager:
        logger.info("Pushing data to Firebase...")
        
        # Push main data
        success = manager.push_to_firebase(flat_data, args.collection)
        if success:
            logger.info("✅ Successfully pushed gold prices to Firebase")
        else:
            logger.error("❌ Failed to push data to Firebase")
    
    # Print sample data
    if flat_data:
        print(f"\n📋 SAMPLE DATA:")
        sample = flat_data[0].to_dict()
        print(json.dumps(sample, indent=2))
    
    print(f"\n🔥 Firebase Collection Structure:")
    print(f"Collection: {args.collection}")
    print(f"Document ID format: jeweller_city_carat_date")
    print(f"Example: tanishq_mumbai_18k_2025-07-21")

if __name__ == "__main__":
    main()