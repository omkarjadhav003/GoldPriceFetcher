# GitHub Actions Setup Guide
## Automated Gold Price Scraping Every 30 Minutes

### Overview
This setup enables automatic scraping of Tanishq gold prices for Bangalore and Madhubani every 30 minutes using GitHub Actions.

### Prerequisites
- GitHub repository with your scraper code
- Firebase project with Firestore enabled
- Firebase service account JSON file

### Setup Steps

#### 1. Repository Setup
Ensure your repository contains:
- `main_scraper.py`
- `gold_price_scraper.py` 
- `firebase_config.py`
- `requirements.txt`
- `.github/workflows/gold-price-scraper.yml`

#### 2. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

**Add Repository Secret:**
- **Name:** `FIREBASE_SERVICE_ACCOUNT`
- **Value:** Complete contents of your `firebase_service_account.json` file

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "...",
  "client_x509_cert_url": "..."
}
```

⚠️ **Important:** Never commit the `firebase_service_account.json` file to your repository.

#### 3. Workflow Configuration

The workflow is configured to:
- **Schedule:** Every 30 minutes (`*/30 * * * *`)
- **Manual Trigger:** Available via "Actions" tab
- **Timeout:** 15 minutes per job
- **Cities:** Bangalore, Madhubani
- **Jeweller:** Tanishq
- **Historical Data:** 30 days

#### 4. Testing

**Manual Test:**
1. Go to your repository → Actions tab
2. Click "Gold Price Scraper" workflow
3. Click "Run workflow" button
4. Monitor the execution logs

**Verify Data:**
Check your Firestore `gold_prices` collection for new documents.

### Workflow Features

#### ✅ **Robust Setup**
- Installs Chrome and ChromeDriver automatically
- Handles Python dependencies via requirements.txt
- Secure credential management

#### ✅ **Error Handling**
- Continues if one city fails
- Reports individual job outcomes
- Cleans up credentials after execution

#### ✅ **Monitoring**
- Detailed logs for each step
- Clear success/failure reporting
- Manual triggering capability

### Customization

#### Change Schedule
Edit the cron expression in `.github/workflows/gold-price-scraper.yml`:
```yaml
schedule:
  - cron: '*/15 * * * *'  # Every 15 minutes
  - cron: '0 */2 * * *'   # Every 2 hours
  - cron: '0 9,17 * * *'  # 9 AM and 5 PM daily
```

#### Add More Cities
```yaml
- name: Run scraper for [City]
  run: |
    python3 main_scraper.py \
      --jewellers tanishq \
      --cities [City] \
      --days 30 \
      --firebase-key firebase_service_account.json \
      --collection gold_prices
```

#### Add More Jewellers
```yaml
- name: Run Kalyan scraper
  run: |
    python3 main_scraper.py \
      --jewellers kalyan \
      --cities Bangalore Madhubani \
      --days 30 \
      --firebase-key firebase_service_account.json \
      --collection gold_prices
```

### Cost Considerations

**GitHub Actions Usage:**
- **Public repos:** 2,000 minutes/month free
- **Private repos:** Check your plan limits
- **Estimated usage:** ~5 minutes per run = ~7,200 minutes/month for 30-min intervals

**Recommendations:**
- Monitor usage in Settings → Billing
- Consider running less frequently (hourly) to reduce costs
- Use `workflow_dispatch` for manual testing

### Troubleshooting

#### Common Issues

**1. ChromeDriver Compatibility**
If Chrome/ChromeDriver mismatch occurs, the workflow auto-detects and installs compatible versions.

**2. Firebase Permission Errors**
Ensure your service account has Firestore write permissions:
- Firebase Console → Project Settings → Service Accounts
- Verify the service account has "Firebase Admin SDK" role

**3. Scraping Failures**
- Check if Tanishq website structure changed
- Monitor rate limiting (30-min intervals should be safe)
- Review logs in Actions tab for specific errors

**4. Workflow Not Running**
- Verify cron syntax
- Check if repository has recent activity (GitHub may disable inactive workflows)
- Ensure workflow file is in `main` branch

### Security Best Practices

- ✅ Firebase credentials stored as GitHub Secrets
- ✅ Credentials cleaned up after each run
- ✅ No sensitive data in logs
- ✅ Limited job timeout prevents runaway processes

### Monitoring Success

Check these indicators:
1. **GitHub Actions:** Green checkmarks in Actions tab
2. **Firestore:** New documents in `gold_prices` collection every 30 minutes
3. **Android App:** Fresh data availability

Your automated gold price scraping is now ready! 🚀 