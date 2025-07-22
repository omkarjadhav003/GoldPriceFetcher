#!/usr/bin/env python3
"""
Modular Gold Price Scraper
Supports multiple jewellers, cities, and provides structured data for Android app
"""

import json
import time
import argparse
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoldPriceData:
    """Data structure for gold price information"""
    
    def __init__(self, jeweller: str, city: str, carat: str, price: float, date: str, 
                 source_url: str = None, additional_info: Dict = None):
        self.jeweller = jeweller
        self.city = city
        self.carat = carat
        self.price = price
        self.date = date
        self.source_url = source_url
        self.additional_info = additional_info or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "jeweller": self.jeweller,
            "city": self.city,
            "carat": self.carat,
            "price": self.price,
            "date": self.date,
            "source_url": self.source_url,
            "timestamp": self.timestamp,
            "additional_info": self.additional_info
        }
    
    def get_document_id(self) -> str:
        """Generate unique document ID for Firebase"""
        return f"{self.jeweller}_{self.city}_{self.carat}_{self.date}".lower().replace(" ", "_")

class BaseJewellerScraper(ABC):
    """Abstract base class for jeweller scrapers"""
    
    def __init__(self, jeweller_name: str, supported_cities: List[str]):
        self.jeweller_name = jeweller_name
        self.supported_cities = supported_cities
        self.carats = ["18K", "22K", "24K"]
    
    @abstractmethod
    def scrape_city_prices(self, city: str, days: int = 30) -> List[GoldPriceData]:
        """Scrape gold prices for a specific city"""
        pass
    
    @abstractmethod
    def get_source_url(self, city: str = None) -> str:
        """Get the source URL for scraping"""
        pass
    
    def scrape_all_cities(self, days: int = 30) -> List[GoldPriceData]:
        """Scrape prices for all supported cities"""
        all_data = []
        for city in self.supported_cities:
            try:
                logger.info(f"Scraping {self.jeweller_name} prices for {city}")
                city_data = self.scrape_city_prices(city, days)
                all_data.extend(city_data)
                time.sleep(2)  # Respectful delay between cities
            except Exception as e:
                logger.error(f"Failed to scrape {city} for {self.jeweller_name}: {e}")
        return all_data
    
    def validate_data(self, data: List[GoldPriceData]) -> List[GoldPriceData]:
        """Validate and filter data"""
        valid_data = []
        for item in data:
            if (item.price > 1000 and item.price < 20000 and  # Reasonable price range
                item.carat in self.carats and
                item.city in self.supported_cities):
                valid_data.append(item)
            else:
                logger.warning(f"Invalid data filtered: {item.to_dict()}")
        return valid_data

class TanishqScraper(BaseJewellerScraper):
    """Optimized Tanishq jeweller scraper implementation using hidden inputs"""
    
    def __init__(self):
        # Tanishq has presence in major cities - you can expand this list
        supported_cities = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", 
            "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
        ]
        super().__init__("Tanishq", supported_cities)
        self.base_url = "https://www.tanishq.co.in/gold-rate.html"
    
    def get_source_url(self, city: str = None) -> str:
        """Get source URL - Tanishq shows national rates"""
        return f"{self.base_url}?lang=en_IN"
    
    def scrape_city_prices(self, city: str, days: int = 30) -> List[GoldPriceData]:
        """Optimized Tanishq scraper using hidden input fields"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        import time
        import re
        
        logger.info(f"🚀 Starting optimized Tanishq scraping for {city} ({days} days)")
        
        # Setup Chrome options for optimal performance
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        structured_data = []
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            wait = WebDriverWait(driver, 30)
            logger.info("✅ Chrome driver setup successful")
            
            # Navigate to Tanishq gold rates page
            url = self.get_source_url(city)
            logger.info(f"🌐 Navigating to: {url}")
            driver.get(url)
            
            # Wait for page to load
            logger.info("⏳ Waiting for page to load...")
            time.sleep(15)
            
            # Close any popups
            self._close_popups(driver)
            
            # Wait for gold rate data elements
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".goldpurity-rate")))
                logger.info("✅ Gold rate data elements found")
            except TimeoutException:
                logger.warning("⚠️ Gold rate data elements not found, continuing...")
            
            # Extract data using optimized method
            all_price_data = self._extract_from_hidden_inputs(driver, days)
            
            # Convert to GoldPriceData format for compatibility
            for carat, prices in all_price_data.items():
                for price_item in prices:
                    gold_data = GoldPriceData(
                        jeweller="Tanishq",
                        city=city,
                        carat=carat,
                        price=price_item['price'],
                        date=price_item['date'],
                        source_url=url,
                        additional_info={
                            "extraction_method": "optimized_hidden_inputs",
                            "currency": "INR",
                            "unit": "per_gram"
                        }
                    )
                    structured_data.append(gold_data)
            
            logger.info(f"✅ Successfully extracted {len(structured_data)} gold rate entries")
            
            driver.quit()
            return structured_data
            
        except Exception as e:
            logger.error(f"❌ Failed to scrape Tanishq data: {e}")
            if 'driver' in locals():
                driver.quit()
            return []
    
    def _close_popups(self, driver):
        """Close any popups that might interfere with scraping"""
        from selenium.webdriver.common.by import By
        
        popup_selectors = [
            ".gdex-popup-overlay",
            ".popup-close", 
            ".close",
            "[aria-label='Close']",
            ".modal-close",
            ".overlay-close"
        ]
        
        for selector in popup_selectors:
            try:
                popup_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for popup in popup_elements:
                    if popup.is_displayed():
                        popup.click()
                        time.sleep(1)
                        logger.info(f"🚫 Closed popup: {selector}")
            except:
                continue
    
    def _extract_from_hidden_inputs(self, driver, days: int = 30) -> dict:
        """Extract all gold prices from hidden input fields - most efficient method"""
        from selenium.webdriver.common.by import By
        
        logger.info("🎯 Extracting from hidden input fields...")
        
        all_data = {}
        
        try:
            # Extract data from hidden input fields
            input_ids = {
                '18K': 'goldRate18KT',
                '22K': 'goldRate22KT', 
                '24K': 'goldRate24KT'
            }
            
            # Get dates array
            dates_input = driver.find_element(By.ID, "goldRateDates")
            dates_value = dates_input.get_attribute("value")
            logger.info(f"📅 Found dates input with {len(dates_value)} characters")
            
            # Parse dates - format: [23-06-2025, 24-06-2025, ...]
            dates_str = dates_value.strip('[]')
            dates_list = [date.strip() for date in dates_str.split(',')]
            logger.info(f"📅 Parsed {len(dates_list)} dates")
            
            # Extract prices for each carat
            for carat, input_id in input_ids.items():
                try:
                    price_input = driver.find_element(By.ID, input_id)
                    prices_value = price_input.get_attribute("value")
                    logger.info(f"💰 Found {carat} prices array")
                    
                    # Parse prices - format: [7585, 7523, 7454, ...]
                    prices_str = prices_value.strip('[]')
                    prices_list = [float(price.strip()) for price in prices_str.split(',')]
                    logger.info(f"💰 Parsed {len(prices_list)} {carat} prices")
                    
                    # Combine dates and prices
                    carat_data = []
                    for i, (date_str, price) in enumerate(zip(dates_list, prices_list)):
                        if i >= days:  # Limit to requested days
                            break
                            
                        # Convert date format from DD-MM-YYYY to YYYY-MM-DD
                        formatted_date = self._parse_date(date_str)
                        if formatted_date:
                            carat_data.append({
                                'price': price,
                                'date': formatted_date
                            })
                    
                    # Reverse to get latest first (data seems to be oldest first)
                    carat_data.reverse()
                    all_data[carat] = carat_data
                    logger.info(f"✅ Extracted {len(carat_data)} days of {carat} data from hidden inputs")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to extract {carat} from hidden inputs: {e}")
                    continue
            
            return all_data
            
        except Exception as e:
            logger.error(f"❌ Failed to extract from hidden inputs: {e}")
            return {}
    
    def _parse_date(self, date_text: str) -> str:
        """Parse date from DD-MM-YYYY to YYYY-MM-DD format"""
        try:
            # Handle DD-MM-YYYY format
            if re.match(r'\d{2}-\d{2}-\d{4}', date_text):
                day, month, year = date_text.split('-')
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Handle DD/MM/YYYY format  
            if re.match(r'\d{2}/\d{2}/\d{4}', date_text):
                day, month, year = date_text.split('/')
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            return date_text
        except Exception as e:
            logger.debug(f"Error parsing date '{date_text}': {e}")
            return date_text
    


class KalyanJewellersScraper(BaseJewellerScraper):
    """Kalyan Jewellers scraper implementation (placeholder)"""
    
    def __init__(self):
        supported_cities = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
            "Hyderabad", "Pune", "Kochi", "Thrissur", "Coimbatore"
        ]
        super().__init__("Kalyan Jewellers", supported_cities)
        self.base_url = "https://www.kalyanjewellers.net"
    
    def get_source_url(self, city: str = None) -> str:
        return f"{self.base_url}/gold-rate"
    
    def scrape_city_prices(self, city: str, days: int = 30) -> List[GoldPriceData]:
        """Placeholder for Kalyan Jewellers scraper"""
        logger.info(f"Kalyan Jewellers scraper not implemented yet for {city}")
        # TODO: Implement Kalyan Jewellers scraping logic
        return []

class JoyalukkasJewellersScraper(BaseJewellerScraper):
    """Joyalukkas Jewellers scraper implementation (placeholder)"""
    
    def __init__(self):
        supported_cities = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
            "Hyderabad", "Dubai", "Kuwait", "Qatar"  # International presence
        ]
        super().__init__("Joyalukkas", supported_cities)
        self.base_url = "https://www.joyalukkas.com"
    
    def get_source_url(self, city: str = None) -> str:
        return f"{self.base_url}/gold-rate"
    
    def scrape_city_prices(self, city: str, days: int = 30) -> List[GoldPriceData]:
        """Placeholder for Joyalukkas scraper"""
        logger.info(f"Joyalukkas scraper not implemented yet for {city}")
        # TODO: Implement Joyalukkas scraping logic
        return []

class GoldPriceManager:
    """Main manager class for coordinating multiple jeweller scrapers"""
    
    def __init__(self, firebase_service_account_path: str = None):
        self.scrapers = {
            "tanishq": TanishqScraper(),
            "kalyan": KalyanJewellersScraper(),
            "joyalukkas": JoyalukkasJewellersScraper()
        }
        
        # Initialize Firebase if credentials provided
        self.firebase_manager = None
        if firebase_service_account_path:
            from firebase_config import FirebaseManager
            self.firebase_manager = FirebaseManager(firebase_service_account_path)
            if not self.firebase_manager.initialize_firebase():
                logger.warning("Firebase initialization failed")
                self.firebase_manager = None
    
    def scrape_jeweller(self, jeweller_name: str, cities: List[str] = None, days: int = 30) -> List[GoldPriceData]:
        """Scrape data for a specific jeweller"""
        if jeweller_name not in self.scrapers:
            raise ValueError(f"Unsupported jeweller: {jeweller_name}")
        
        scraper = self.scrapers[jeweller_name]
        
        if cities:
            # Scrape specific cities
            all_data = []
            for city in cities:
                if city in scraper.supported_cities:
                    city_data = scraper.scrape_city_prices(city, days)
                    all_data.extend(city_data)
                else:
                    logger.warning(f"{city} not supported by {jeweller_name}")
            return all_data
        else:
            # Scrape all supported cities
            return scraper.scrape_all_cities(days)
    
    def scrape_all_jewellers(self, cities: List[str] = None, days: int = 30) -> Dict[str, List[GoldPriceData]]:
        """Scrape data from all jewellers"""
        all_data = {}
        for jeweller_name in self.scrapers.keys():
            try:
                logger.info(f"Scraping {jeweller_name}")
                jeweller_data = self.scrape_jeweller(jeweller_name, cities, days)
                all_data[jeweller_name] = jeweller_data
                time.sleep(5)  # Respectful delay between jewellers
            except Exception as e:
                logger.error(f"Failed to scrape {jeweller_name}: {e}")
                all_data[jeweller_name] = []
        return all_data
    
    def push_to_firebase(self, data: List[GoldPriceData], collection_name: str = "gold_prices") -> bool:
        """Push structured data to Firebase"""
        if not self.firebase_manager:
            logger.error("Firebase not initialized")
            return False
        
        try:
            batch = self.firebase_manager.db.batch()
            batch_count = 0
            
            for item in data:
                doc_id = item.get_document_id()
                doc_ref = self.firebase_manager.db.collection(collection_name).document(doc_id)
                
                # Add Firebase metadata
                firebase_data = item.to_dict()
                from firebase_admin import firestore
                firebase_data['firebase_timestamp'] = firestore.SERVER_TIMESTAMP
                
                batch.set(doc_ref, firebase_data, merge=True)
                batch_count += 1
                
                # Commit in batches of 500
                if batch_count >= 500:
                    batch.commit()
                    logger.info(f"Committed batch of {batch_count} documents")
                    batch = self.firebase_manager.db.batch()
                    batch_count = 0
            
            # Commit remaining documents
            if batch_count > 0:
                batch.commit()
                logger.info(f"Committed final batch of {batch_count} documents")
            
            logger.info(f"Successfully pushed {len(data)} gold price entries to Firebase")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push to Firebase: {e}")
            return False
    
    def create_summary_data(self, all_data: Dict[str, List[GoldPriceData]]) -> Dict[str, Any]:
        """Create summary data for Firebase"""
        total_entries = sum(len(data) for data in all_data.values())
        
        # Get unique dates, cities, jewellers
        all_dates = set()
        all_cities = set()
        all_jewellers = set()
        
        for jeweller, data_list in all_data.items():
            all_jewellers.add(jeweller)
            for item in data_list:
                all_dates.add(item.date)
                all_cities.add(item.city)
        
        # Get latest rates for each jeweller/city/carat combination
        latest_rates = {}
        latest_date = max(all_dates) if all_dates else None
        
        if latest_date:
            for jeweller, data_list in all_data.items():
                for item in data_list:
                    if item.date == latest_date:
                        key = f"{item.jeweller}_{item.city}_{item.carat}"
                        latest_rates[key] = item.to_dict()
        
        return {
            "summary": f"Gold prices from {len(all_jewellers)} jewellers across {len(all_cities)} cities",
            "total_entries": total_entries,
            "jewellers": list(all_jewellers),
            "cities": list(all_cities),
            "date_range": {
                "from": min(all_dates) if all_dates else None,
                "to": max(all_dates) if all_dates else None
            },
            "latest_rates": latest_rates,
            "scrape_timestamp": datetime.now().isoformat(),
            "data_structure": {
                "jeweller": "string",
                "city": "string", 
                "carat": "string (18K, 22K, 24K)",
                "price": "float (INR per gram)",
                "date": "string (YYYY-MM-DD)"
            }
        }
    
    def push_summary_to_firebase(self, summary_data: Dict[str, Any], collection_name: str = "gold_prices_summary") -> bool:
        """Push summary data to Firebase"""
        if not self.firebase_manager:
            logger.error("Firebase not initialized")
            return False
        
        try:
            doc_id = datetime.now().strftime("%Y-%m-%d")
            doc_ref = self.firebase_manager.db.collection(collection_name).document(doc_id)
            
            from firebase_admin import firestore
            summary_data['firebase_timestamp'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(summary_data, merge=True)
            
            logger.info(f"Successfully pushed summary data to Firebase")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push summary to Firebase: {e}")
            return False