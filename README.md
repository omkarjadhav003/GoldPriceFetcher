# Tanishq Gold Price Scraper with Firebase Integration

A Python script that scrapes gold prices (18K, 22K, 24K) from Tanishq's website for the last 30 days and optionally pushes the data to Firebase Firestore.

## Features

- ✅ Scrapes 30 days of historical gold price data
- ✅ Bypasses anti-bot protection using Selenium
- ✅ Firebase Firestore integration
- ✅ Local JSON file backup
- ✅ Comprehensive error handling
- ✅ 5-second delay as requested
- ✅ Proper date formatting (YYYY-MM-DD)

## Installation

1. **Install Python dependencies:**
```bash
pip3 install selenium firebase-admin beautifulsoup4 requests
```

2. **Install ChromeDriver:**
   - ChromeDriver should be automatically managed by Selenium
   - If issues occur, download from: https://chromedriver.chromium.org/

## Firebase Setup

### Option 1: Quick Setup (Recommended)
```bash
python3 setup_firebase.py
```

### Option 2: Manual Setup

1. **Create Firebase Project:**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create new project or select existing one

2. **Enable Firestore:**
   - Go to Firestore Database
   - Create database in test mode

3. **Get Service Account Key:**
   - Go to Project Settings → Service Accounts
   - Click "Generate new private key"
   - Download the JSON file
   - Save as `firebase_service_account.json`

4. **Test Configuration:**
```bash
python3 setup_firebase.py test
```

## Usage

### With Firebase Integration
```bash
# Using service account file
python3 tanishq_selenium_scraper.py --firebase-key firebase_service_account.json

# Using default credentials (if configured)
python3 tanishq_selenium_scraper.py
```

### Without Firebase (Local Only)
```bash
python3 tanishq_selenium_scraper.py --no-firebase
```

### Custom Collection Name
```bash
python3 tanishq_selenium_scraper.py --firebase-key firebase_service_account.json --collection my_gold_rates
```

## Output

### JSON Structure
```json
[
  {
    "carat": "18K",
    "price": 7544.0,
    "date": "2025-07-21"
  },
  {
    "carat": "22K", 
    "price": 9220.0,
    "date": "2025-07-21"
  },
  {
    "carat": "24K",
    "price": 10058.0,
    "date": "2025-07-21"
  }
]
```

### Files Generated
- `tanishq_gold_rates_30days_YYYYMMDD.json` - Complete 30-day dataset
- `tanishq_gold_rates_summary_YYYYMMDD.json` - Summary with latest rates

### Firebase Collections
- `gold_rates` - Individual price entries
- `gold_rates_summary` - Daily summaries

## Firebase Data Structure

### gold_rates Collection
```json
{
  "carat": "18K",
  "price": 7544.0,
  "date": "2025-07-21",
  "timestamp": "2025-07-21T10:30:00Z",
  "source": "tanishq_scraper",
  "updated_at": "2025-07-21T10:30:00.123456"
}
```

### gold_rates_summary Collection
```json
{
  "summary": "Gold rates for last 30 days",
  "total_entries": 90,
  "date_range": {
    "from": "2025-06-22",
    "to": "2025-07-21"
  },
  "latest_rates": [...],
  "timestamp": "2025-07-21T10:30:00Z",
  "source": "tanishq_scraper"
}
```

## Troubleshooting

### Chrome Driver Issues
```bash
# If Chrome driver fails, try updating
pip3 install --upgrade selenium
```

### Firebase Connection Issues
```bash
# Check Firebase configuration
python3 setup_firebase.py check

# Test Firebase connection
python3 setup_firebase.py test
```

### Website Access Issues
- The script uses Selenium to bypass bot detection
- If still blocked, try running at different times
- Check if website structure has changed

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--firebase-key` | Path to Firebase service account JSON | None |
| `--no-firebase` | Disable Firebase integration | False |
| `--collection` | Firebase collection name | `gold_rates` |

## Examples

### Daily Automated Run
```bash
#!/bin/bash
# daily_gold_scraper.sh
cd /path/to/scraper
python3 tanishq_selenium_scraper.py --firebase-key firebase_service_account.json
```

### Cron Job Setup
```bash
# Run daily at 9 AM
0 9 * * * /path/to/daily_gold_scraper.sh
```

## Error Handling

The script includes comprehensive error handling for:
- Network connectivity issues
- Website structure changes
- Firebase connection problems
- Chrome driver failures
- Data parsing errors

## Security Notes

- Keep `firebase_service_account.json` secure and never commit to version control
- Use Firebase security rules to protect your data
- Consider using environment variables for sensitive configuration

## License

This project is for educational and personal use only. Please respect Tanishq's terms of service and robots.txt when using this scraper.