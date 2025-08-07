# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a 나라장터 (Korea Public Procurement Service) API integration project that provides a Flask-based web application for searching and analyzing public bidding information, successful bid data, and contract information from the Korean government's procurement system.

## Core Commands

### Running the Application
```bash
# Start the Flask server
cd /home/ls/nara1/나라장터\ api/narajangter_app
python3 src/main.py

# Run in background
nohup python3 src/main.py > /tmp/flask_server.log 2>&1 &

# Stop the server
pkill -f "python3 src/main.py"
```

### Testing API Connections
```bash
# Test final API connections
cd /home/ls/nara1/나라장터\ api
python3 test_final_api.py

# Test specific services
python3 test_api_connection.py  # Bid notices
python3 test_scsbid_api.py      # Successful bids
```

### Package Management
```bash
# Install dependencies (use --break-system-packages flag if needed)
pip3 install --user --break-system-packages -r requirements.txt
```

## Architecture & API Integration

### API Service Structure
The project integrates with three main 나라장터 API services:
1. **공공데이터개방표준서비스** (Public Data Open Standard Service) - Latest version, recommended
   - Base URL: `http://apis.data.go.kr/1230000/ao/PubDataOpnStdService`
   - Operations: `getDataSetOpnStdBidPblancInfo`, `getDataSetOpnStdScsbidInfo`, `getDataSetOpnStdCntrctInfo`

2. **입찰공고정보서비스** (Bid Notice Information Service)
   - Base URL: `http://apis.data.go.kr/1230000/ad/BidPublicInfoService`
   
3. **낙찰정보서비스** (Successful Bid Information Service)
   - Base URL: `http://apis.data.go.kr/1230000/as/ScsbidInfoService`

### Critical API Information
- **Service Key**: Located in `/home/ls/nara1/나라장터 api/조달청_나라장터 입찰공고정보서비스/조달청_나라장터 입찰공고정보서비스.txt`
- **Date Format**: 
  - Bid notices: `YYYYMMDDHHMM` (1-month range limit)
  - Successful bids: `YYYYMMDDHHMM` (1-week range limit)
  - Contracts: `YYYYMMDD` (1-month range limit)
- **Response Format**: JSON or XML (use `type=json` parameter)

### Application Structure
```
narajangter_app/
├── src/
│   ├── main.py              # Flask app entry point (port 5000)
│   ├── database/app.db      # SQLite database
│   ├── models/
│   │   ├── narajangter.py   # BidNotice, SuccessfulBid, ApiConfig models
│   │   └── user.py          # User model
│   ├── routes/
│   │   ├── narajangter.py   # API endpoints (/api/narajangter/*)
│   │   └── user.py          # User endpoints
│   └── static/              # Frontend files (HTML, CSS, JS)
```

### Key Flask Routes
- `/api/narajangter/config` - GET/POST API key configuration
- `/api/narajangter/bid-notices` - GET bid notice list
- `/api/narajangter/successful-bids` - GET successful bid list
- `/api/narajangter/sync-bid-notices` - POST sync data from 나라장터
- `/api/narajangter/analytics/*` - GET analytics data

## Database Models

### BidNotice
Stores bid announcement information with fields like:
- `bid_notice_no`: Unique bid notice number
- `bid_notice_nm`: Bid notice title
- `dminstt_nm`: Demand organization name
- `presmpt_price`: Estimated price
- Date fields: `rgst_dt`, `bid_begin_dt`, `bid_close_dt`, `openg_dt`

### SuccessfulBid
Stores successful bid information with fields like:
- `bid_notice_no`: Related bid notice number
- `scsbid_corp_nm`: Successful bidder company name
- `scsbid_amount`: Successful bid amount
- `scsbid_rate`: Successful bid rate

### ApiConfig
Manages API service keys with:
- `service_key`: Public data portal service key
- `is_active`: Active status flag

## Important API Changes (2025)
The 차세대 나라장터 (Next Generation KONEPS) system launched on January 6, 2025, introducing:
- New API versions and endpoints
- Changed field sizes (e.g., `bidNtceOrd`: 2→3 characters)
- New number format for bid notices: Test flag(1) + Year(2) + Type(2) + Sequence(8)

## Common Tasks

### Updating API Endpoints
When updating API endpoints in `src/routes/narajangter.py`:
1. Use the 공공데이터개방표준서비스 endpoints for better stability
2. Ensure date parameters follow the correct format (YYYYMMDDHHMM or YYYYMMDD)
3. Always include `serviceKey` and `type=json` parameters

### Adding New API Operations
1. Check the API documentation in `/home/ls/nara1/나라장터 api/조달청_나라장터*/` folders
2. Add new endpoint to `src/routes/narajangter.py`
3. Create or update database models in `src/models/narajangter.py`
4. Test with scripts in the root directory

### Debugging API Issues
1. Check response format (XML vs JSON) - API may return XML even with `type=json`
2. Verify date range limits (1 month for bids, 1 week for successful bids)
3. Confirm service key is properly encoded/decoded
4. Check for API service errors (code 12 = service not available)