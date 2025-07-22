#!/usr/bin/env python3
"""
Firebase Configuration and Helper Functions
Handles Firebase initialization and data operations for gold price data
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class FirebaseManager:
    def __init__(self, service_account_path: Optional[str] = None):
        """
        Initialize Firebase connection
        
        Args:
            service_account_path: Path to Firebase service account JSON file
                                If None, will try to use default credentials or environment
        """
        self.db = None
        self.app = None
        self.service_account_path = service_account_path
        
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                if self.service_account_path:
                    # Use service account file
                    cred = credentials.Certificate(self.service_account_path)
                    self.app = firebase_admin.initialize_app(cred)
                    logger.info(f"Firebase initialized with service account: {self.service_account_path}")
                else:
                    # Try to use default credentials (for local development)
                    try:
                        self.app = firebase_admin.initialize_app()
                        logger.info("Firebase initialized with default credentials")
                    except Exception as e:
                        logger.error(f"Failed to initialize with default credentials: {e}")
                        logger.info("Please provide service account path or set up default credentials")
                        return False
            else:
                self.app = firebase_admin.get_app()
                logger.info("Using existing Firebase app")
            
            self.db = firestore.client()
            logger.info("Firestore client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            return False
    
    def push_gold_rates(self, gold_rates: List[Dict[str, Any]], collection_name: str = "gold_rates") -> bool:
        """
        Push gold rates data to Firestore
        
        Args:
            gold_rates: List of gold rate dictionaries with keys: carat, price, date
            collection_name: Firestore collection name
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db:
            logger.error("Firestore client not initialized")
            return False
        
        try:
            batch = self.db.batch()
            batch_count = 0
            total_pushed = 0
            
            for rate in gold_rates:
                # Create document ID using date and carat for uniqueness
                doc_id = f"{rate['date']}_{rate['carat']}"
                doc_ref = self.db.collection(collection_name).document(doc_id)
                
                # Add metadata
                rate_data = {
                    **rate,
                    'timestamp': firestore.SERVER_TIMESTAMP,
                    'source': 'tanishq_scraper',
                    'updated_at': datetime.now().isoformat()
                }
                
                batch.set(doc_ref, rate_data, merge=True)
                batch_count += 1
                total_pushed += 1
                
                # Firestore batch limit is 500 operations
                if batch_count >= 500:
                    batch.commit()
                    logger.info(f"Committed batch of {batch_count} documents")
                    batch = self.db.batch()
                    batch_count = 0
            
            # Commit remaining documents
            if batch_count > 0:
                batch.commit()
                logger.info(f"Committed final batch of {batch_count} documents")
            
            logger.info(f"Successfully pushed {total_pushed} gold rate entries to Firestore")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push gold rates to Firestore: {e}")
            return False
    
    def push_summary_data(self, summary_data: Dict[str, Any], collection_name: str = "gold_rates_summary") -> bool:
        """
        Push summary data to Firestore
        
        Args:
            summary_data: Summary dictionary with metadata
            collection_name: Firestore collection name for summary
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db:
            logger.error("Firestore client not initialized")
            return False
        
        try:
            # Use current date as document ID for summary
            doc_id = datetime.now().strftime("%Y-%m-%d")
            doc_ref = self.db.collection(collection_name).document(doc_id)
            
            # Add metadata
            summary_with_metadata = {
                **summary_data,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'source': 'tanishq_scraper',
                'created_at': datetime.now().isoformat()
            }
            
            doc_ref.set(summary_with_metadata, merge=True)
            logger.info(f"Successfully pushed summary data to Firestore document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push summary data to Firestore: {e}")
            return False
    
    def get_latest_rates(self, collection_name: str = "gold_rates", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get latest gold rates from Firestore
        
        Args:
            collection_name: Firestore collection name
            limit: Number of latest records to fetch
            
        Returns:
            List of gold rate dictionaries
        """
        if not self.db:
            logger.error("Firestore client not initialized")
            return []
        
        try:
            docs = (self.db.collection(collection_name)
                   .order_by('date', direction=firestore.Query.DESCENDING)
                   .limit(limit)
                   .stream())
            
            rates = []
            for doc in docs:
                rate_data = doc.to_dict()
                rates.append(rate_data)
            
            logger.info(f"Retrieved {len(rates)} latest gold rates from Firestore")
            return rates
            
        except Exception as e:
            logger.error(f"Failed to get latest rates from Firestore: {e}")
            return []
    
    def check_existing_data(self, date: str, collection_name: str = "gold_rates") -> bool:
        """
        Check if data for a specific date already exists
        
        Args:
            date: Date string in YYYY-MM-DD format
            collection_name: Firestore collection name
            
        Returns:
            bool: True if data exists, False otherwise
        """
        if not self.db:
            logger.error("Firestore client not initialized")
            return False
        
        try:
            docs = (self.db.collection(collection_name)
                   .where('date', '==', date)
                   .limit(1)
                   .stream())
            
            return len(list(docs)) > 0
            
        except Exception as e:
            logger.error(f"Failed to check existing data: {e}")
            return False

def create_firebase_config_template():
    """Create a template for Firebase service account configuration"""
    template = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
    }
    
    with open('firebase_service_account_template.json', 'w') as f:
        json.dump(template, f, indent=2)
    
    print("Created firebase_service_account_template.json")
    print("Please:")
    print("1. Go to Firebase Console > Project Settings > Service Accounts")
    print("2. Generate a new private key")
    print("3. Replace the template with your actual service account JSON")
    print("4. Rename the file to 'firebase_service_account.json'")

if __name__ == "__main__":
    # Create template if run directly
    create_firebase_config_template()