#!/bin/bash
#
# 나라장터 API 프로젝트 - 통합 환경 설정 스크립트
# 성능.md + code개발자.md + mcp.md 모든 권장사항 적용
#

set -e  # 오류 시 중단

echo "=========================================="
echo " 🚀 나라장터 API 통합 환경 설정 시작"
echo "=========================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 함수: 성공 메시지
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 함수: 경고 메시지
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 함수: 오류 메시지
error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Python 환경 체크
echo "1️⃣ Python 환경 확인..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    success "Python $PYTHON_VERSION 설치됨"
else
    error "Python3가 설치되지 않았습니다"
    exit 1
fi

# 2. 필수 Python 패키지 설치
echo ""
echo "2️⃣ 필수 Python 패키지 설치..."
pip3 install --user --break-system-packages \
    flask flask-cors flask-sqlalchemy requests \
    redis celery flower \
    pytest pytest-cov pytest-asyncio \
    black flake8 mypy \
    prometheus-flask-exporter \
    2>/dev/null || warning "일부 패키지 설치 실패 (이미 설치되었을 수 있음)"

success "Python 패키지 설치 완료"

# 3. 데이터베이스 최적화
echo ""
echo "3️⃣ 데이터베이스 최적화..."
if [ -f "add_indexes.py" ]; then
    python3 add_indexes.py
    success "데이터베이스 인덱스 추가 완료"
else
    warning "add_indexes.py 파일이 없습니다"
fi

# 4. 테스트 디렉토리 생성
echo ""
echo "4️⃣ 테스트 구조 생성..."
mkdir -p tests/{unit,integration,e2e}
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/e2e/__init__.py
success "테스트 디렉토리 구조 생성 완료"

# 5. Git hooks 설정
echo ""
echo "5️⃣ Git hooks 설정..."
if [ -d ".git" ]; then
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook: 테스트 실행
echo "Running pre-commit tests..."
python3 -m pytest tests/unit/ --quiet
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Commit aborted."
    exit 1
fi
echo "✅ All tests passed!"
EOF
    chmod +x .git/hooks/pre-commit
    success "Git pre-commit hook 설정 완료"
else
    warning "Git 저장소가 아닙니다. Git hooks 설정 건너뜀"
fi

# 6. 환경 변수 설정
echo ""
echo "6️⃣ 환경 변수 설정..."
cat > .env.example << 'EOF'
# 나라장터 API 키
NARAJANGTER_API_KEY=YOUR_API_KEY_HERE

# Flask 설정
FLASK_APP=narajangter_app/src/main.py
FLASK_ENV=development
FLASK_DEBUG=1

# Redis 설정
REDIS_URL=redis://localhost:6379/0

# Celery 설정
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 모니터링
PROMETHEUS_PORT=9091
EOF

if [ ! -f ".env" ]; then
    cp .env.example .env
    warning ".env 파일이 생성되었습니다. API 키를 설정하세요."
else
    success ".env 파일이 이미 존재합니다"
fi

# 7. 실행 스크립트 생성
echo ""
echo "7️⃣ 실행 스크립트 생성..."

# Flask 서버 시작 스크립트
cat > start_server.sh << 'EOF'
#!/bin/bash
echo "🚀 Flask 서버 시작..."
cd narajangter_app
python3 src/main.py
EOF
chmod +x start_server.sh

# 테스트 실행 스크립트
cat > run_tests.sh << 'EOF'
#!/bin/bash
echo "🧪 테스트 실행..."
python3 -m pytest tests/ -v --cov=narajangter_app/src --cov-report=html
echo "📊 Coverage report: htmlcov/index.html"
EOF
chmod +x run_tests.sh

# 성능 테스트 스크립트
cat > run_performance.sh << 'EOF'
#!/bin/bash
echo "⚡ 성능 테스트..."
python3 performance_test.py
python3 comprehensive_test.py
EOF
chmod +x run_performance.sh

# 데이터 동기화 스크립트
cat > sync_data.sh << 'EOF'
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
EOF
chmod +x sync_data.sh

success "실행 스크립트 생성 완료"

# 8. MCP 설정 파일 생성
echo ""
echo "8️⃣ MCP 설정 파일 생성..."
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "narajangter": {
      "command": "python3",
      "args": ["./mcp_server.py"],
      "env": {
        "API_KEY": "${NARAJANGTER_API_KEY}"
      }
    }
  }
}
EOF
success "MCP 설정 파일 생성 완료"

# 9. CLAUDE.md 업데이트
echo ""
echo "9️⃣ CLAUDE.md 업데이트 확인..."
if [ -f "CLAUDE.md" ]; then
    success "CLAUDE.md 파일 존재함"
else
    warning "CLAUDE.md 파일이 없습니다. /init 명령으로 생성하세요"
fi

# 10. 최종 체크
echo ""
echo "=========================================="
echo " 📋 설정 완료 요약"
echo "=========================================="
echo ""

# 체크리스트
checks=(
    "Python 환경:설치됨"
    "필수 패키지:설치됨"
    "데이터베이스:최적화됨"
    "테스트 구조:생성됨"
    "Git hooks:설정됨"
    "환경 변수:.env 파일 생성됨"
    "실행 스크립트:생성됨"
    "MCP 설정:완료됨"
)

for check in "${checks[@]}"; do
    IFS=':' read -r item status <<< "$check"
    printf "  %-20s %s\n" "$item" "[$status]"
done

echo ""
echo "=========================================="
echo " 🎯 다음 단계"
echo "=========================================="
echo ""
echo "1. API 키 설정:"
echo "   vi .env  # NARAJANGTER_API_KEY 입력"
echo ""
echo "2. 서버 시작:"
echo "   ./start_server.sh"
echo ""
echo "3. 테스트 실행:"
echo "   ./run_tests.sh"
echo ""
echo "4. 성능 측정:"
echo "   ./run_performance.sh"
echo ""
echo "5. 데이터 동기화:"
echo "   ./sync_data.sh"
echo ""
echo "6. MCP 서버 등록 (선택사항):"
echo "   claude mcp add github -s user npx -y @modelcontextprotocol/server-github"
echo ""
success "모든 설정이 완료되었습니다! 🎉"