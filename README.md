# YouTube Channel Crawler v1.0

![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)
![YouTube API](https://img.shields.io/badge/YouTube%20API-v3-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Overview
A interface application for bulk collection and analysis of YouTube channels data. Built with Python and Tkinter, it uses Youtube APi to crawl channels info with quota management and a caching systems.

---

## ✨ Features

### 🔍 Search & Crawling
- **Multi-keyword Search:** Process multiple search terms simultaneously  
- **Country-Filtered Results:** Target specific geographic regions  
- **Shorts Detection:** Identify Shorts-focused channels using 4 detection methods  
- **Smart Filtering:** Exclude previously processed channels automatically  

### 💾 Intelligent Data Management
- **Dual-Layer Cache System:**
  - Session history tracking (`crawl_history.json`)
  - Channel ID master cache (`master_cache.csv`)
  - Complete data reuse from exports
- **Auto-Cleanup:** Configurable expiration for old sessions  
- **Multiple Export Formats:** Excel (.xlsx) and CSV (.csv)

### ⚡ Performance Optimization
- **Quota-Aware Processing:** Max 80 search calls per session  
- **Batch API Calls:** Process 50 channels per API call  
- **Real-time Progress Tracking:** Live quota usage and progress bars  
- **Threaded Execution:** Non-blocking UI during crawls  

---

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher  
- YouTube Data API v3 key  
- 100MB free disk space  

### Step-by-Step Setup

#### Clone the Application
```bash
git clone github.com/Retolc/YouTube-Channel-Crawler-v1.0.git
cd YouTube-Channel-Crawler-v1.0
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

**Required Packages**
```text
google-api-python-client>=2.80.0
pandas>=1.5.0
openpyxl>=3.0.0
Pillow>=9.0.0
python-dateutil>=2.8.0
requests>=2.28.0
```

#### Configure API Key
```text
Go to Google Cloud Console
Create a new project or select existing
Enable YouTube Data API v3
Create credentials (API Key)
Copy your API key
```

#### Run the Application
```bash
python main.py
```

---

## 🎯 Quick Start Guide

### First-Time Setup
- Launch `main.py`
- Enter your YouTube API key in the top field
- Click **💾 Save** to validate and store the key
- You're ready to crawl

### Basic Crawl Session

**Enter Search Terms (one per line)**
```text
cooking tutorials
recipe channels
baking lessons
```

**Select Countries (optional)**
- Click **🌍 Popular** for common countries
- Or manually select from the checkbox list
- Leave empty for global search

**Adjust Settings**
- Videos per term: 10–50 (recommended: 30)
- Export format: Excel or CSV
- Filename: Auto-generated or custom

**Start Crawling**
- Click **▶ START CRAWLING**
- Monitor progress in real time
- Export location: `exports/` folder

---

## 📊 How It Works

### The Crawling Pipeline
```text
Search Terms → YouTube API Search → Channel IDs → Filter Cache →
API Details → Detect Shorts → Calculate Metrics → Export Data
```

### Shorts Detection Methods

**URL Pattern Analysis (Most Reliable)**
- Checks `youtube.com/shorts/{video_id}` URL existence  
- Zero quota cost, ~90% accuracy  

**Thumbnail Dimension Analysis**
- Detects vertical thumbnails (9:16 aspect ratio)  
- Zero quota cost, ~80% accuracy  

**Keyword Detection**
- Searches for "shorts", "#shorts", "tiktok", "reels"  
- Zero quota cost, ~70% accuracy  

**Duration Analysis (Optional)**
- Detects videos under 60 seconds  
- 1 quota unit, ~95% accuracy  

### Quota Management Strategy
```text
Search Calls: 100 units each (max 80 calls/session = 8,000 units)
Channel Details: ~3 units per new channel

Cache Benefits:
- Cached channels: 0 units (data reuse)
- Historical channels: ~2 units (skip last video check)
- New channels: ~3 units (full processing)
```

Example: Processing 1,000 channels with 50% cache hit ≈ 1,500 units.

---

## 📁 File Structure
```text
youtube-crawler-pro/
├── main.py                 # Main application (GUI)
├── youtube_api.py          # YouTube API wrapper
├── data_handler.py         # Data processing & export
├── requirements.txt        # Python dependencies
├── config/
│   ├── api_key.txt
│   ├── crawl_history.json
│   ├── theme.json
│   └── cleanup_settings.json
├── exports/
│   ├── Youtube_Crawl_20240101_120000.xlsx
│   ├── MASTER
│     └── master.csv
└── README.md
```

---

## 📈 Data Output Format

The export includes 40+ data points per channel.

### Basic Information
```text
channel_id, channel_title, custom_url, channel_url,
description, email, has_email,
country, country_name, published_at, created_date
```

### Statistics
```text
subscriber_count, view_count, video_count, hidden_subscriber_count
```

### Shorts Detection
```text
search_video_is_shorts_url, last_video_is_shorts_url,
search_video_is_shorts_thumb, last_video_is_shorts_thumb,
shorts_in_title, shorts_in_description,
shorts_mentions_count, search_video_is_shorts_keyword,
last_video_duration_seconds, last_video_is_short_by_duration,
search_video_shorts_score, shorts_confidence_score
```

### Activity Metrics
```text
last_video_title, last_video_published,
days_since_last_video, activity_score, activity_status,
channel_size
```

### Playlist Data
```text
playlist_count, playlist_names, playlist_video_counts
```

### Social & Links
```text
social_links, websites, total_links_found,
keywords, profile_image, collected_at
```

---

## ⚙️ Advanced Configuration

### Customizing Search Parameters
```python
MAX_SEARCH_CALLS = 80
RESULTS_PER_CALL = 50
CACHE_EXPIRY_DAYS = 30

SHORTS_CONFIDENCE_THRESHOLD = 60
SHORTS_DURATION_THRESHOLD = 60
```

### Theme Customization
- Toggle between dark/light mode using **🌙 Dark Mode** / **☀️ Light Mode**
- Preferences saved in `config/theme.json`

### Auto-Cleanup Settings
```json
{
  "auto_cleanup_enabled": true,
  "cleanup_days": 30,
  "preserve_master_cache": true
}
```

---

## 🔧 Troubleshooting

### API Key Errors
```text
Invalid API key or not found
```
- Verify key in `config/api_key.txt`
- Ensure YouTube Data API v3 is enabled
- Check quota limits in Google Cloud Console

### Quota Exhaustion
```text
Quota exceeded for quota metric
```
- Wait for daily reset
- Reduce search terms or videos per term
- Enable aggressive caching

### Export File Issues
```text
Permission denied writing to exports/
```
- Run as administrator (Windows)
- Check folder permissions

### Memory Issues
```text
MemoryError during export
```
- Reduce videos per term (≤20)
- Split search into multiple sessions
- Use CSV instead of Excel

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 Performance Tips

### Optimal Settings
- Discovery: 35 videos per term, Global

### Quota Optimization
- Dont Use country filtering
- maintain all caches

### Data Quality
- Email extraction works best when channels list contact info
- Shorts detection most accurate with all methods deduction

---

## 🔒 Privacy & Compliance

### Data Collection
- Only publicly available YouTube data
- No private user information collected
- All data sourced from YouTube Data API

### GDPR / CCPA
- Users control all collected data
- Full export/delete via UI
- No data sent to external servers

### API Compliance
- Respects YouTube API Terms of Service
- Implements quota limits and retry logic
- Proper attribution included

---

## 🤝 Contributing
- Fork the repository
- Create a feature branch
- Make your changes
- Test thoroughly
- Submit a pull request

### Development Setup
```bash
git clone -b develop https://github.com/Retolc/YouTube-Channel-Crawler-v1.0.git
cd YouTube-Channel-Crawler-v1.0

pip install -r requirements-dev.txt
python -m pytest tests/
black main.py youtube_api.py data_handler.py
```

---

## 📄 License
MIT License — see LICENSE file for details.

---

**Version:** 1.0.0
