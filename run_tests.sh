#!/bin/bash
echo "🧪 테스트 실행..."
python3 -m pytest tests/ -v --cov=narajangter_app/src --cov-report=html
echo "📊 Coverage report: htmlcov/index.html"
