# Firestore Android Integration Guide
## Gold Price Data Integration

### Data Availability
- **Jewellers:** Tanishq, Kalyan
- **Cities:** Bangalore, Madhubani
- **Gold Types:** 18K, 22K, 24K
- **Historical Data:** 30 days per scraping session

### Firestore Configuration

**Project ID:** `your-project-id`
**Database:** `(default)`
**Collection:** `gold_prices`

### Authentication
Use Firebase service account or configure Firebase Authentication for your Android app. The data is read-accessible with proper Firebase project permissions.

### Data Structure

#### Collection: `gold_prices`
```json
{
  "jeweller": "Tanishq | Kalyan",
  "city": "Bangalore | Madhubani", 
  "carat": "18K | 22K | 24K",
  "price": 7630.0,
  "date": "22-07-2025",
  "source_url": "https://www.tanishq.co.in/gold-rate.html?lang=en_IN",
  "timestamp": "2025-07-22T23:24:37.870383",
  "additional_info": {
    "extraction_method": "optimized_hidden_inputs",
    "currency": "INR",
    "unit": "per_gram"
  }
}
```

#### Document ID Format
`{jeweller}_{city}_{carat}_{date}`

**Examples:**
- `tanishq_bangalore_18k_2025-07-22`
- `kalyan_madhubani_22k_2025-07-21`

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `jeweller` | String | "Tanishq" or "Kalyan" |
| `city` | String | "Bangalore" or "Madhubani" |
| `carat` | String | "18K", "22K", or "24K" |
| `price` | Number | Price per gram in INR |
| `date` | String | Date in DD-MM-YYYY format |
| `timestamp` | String | ISO timestamp of data extraction |
| `additional_info.currency` | String | Always "INR" |
| `additional_info.unit` | String | Always "per_gram" |

### Query Patterns

#### Latest Prices by Jeweller & City
```kotlin
// Query latest gold rates for Tanishq in Bangalore
db.collection("gold_prices")
  .whereEqualTo("jeweller", "Tanishq")
  .whereEqualTo("city", "Bangalore")
  .orderBy("timestamp", Query.Direction.DESCENDING)
  .limit(3) // 18K, 22K, 24K latest rates
```

#### Historical Data for Specific Carat
```kotlin
// Get 30-day price history for 22K gold
db.collection("gold_prices")
  .whereEqualTo("jeweller", "Tanishq")
  .whereEqualTo("city", "Bangalore")
  .whereEqualTo("carat", "22K")
  .orderBy("timestamp", Query.Direction.DESCENDING)
  .limit(30)
```

#### Compare Jewellers
```kotlin
// Get latest 22K prices from both jewellers in Bangalore
db.collection("gold_prices")
  .whereEqualTo("city", "Bangalore")
  .whereEqualTo("carat", "22K")
  .orderBy("timestamp", Query.Direction.DESCENDING)
  .limit(10)
```

### Data Update Frequency
- **Tanishq:** Real-time scraping capability, typically updated daily
- **Kalyan:** Will be implemented as needed
- **Timestamp field** indicates exact scraping time

### Notes
- Prices are in INR per gram
- Date field uses DD-MM-YYYY format for display
- Use timestamp field for sorting/filtering
- Document IDs are predictable for direct access if needed
- All price data is validated for reasonable ranges (₹5,000-₹15,000) 