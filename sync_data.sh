#!/bin/bash
echo "📥 데이터 동기화..."
python3 -c "
import requests
response = requests.post(
    'http://localhost:5000/api/narajangter/sync-bid-notices',
    json={'start_date': '20250101', 'end_date': '20250107'}
)
print(response.json())
"
