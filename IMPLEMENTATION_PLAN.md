# 나라장터 API 프로젝트 통합 구현 계획

## 📋 개요
성능.md, code개발자.md, mcp.md 문서의 모든 권장사항을 통합하여 고성능, 자동화된 개발 환경을 구축합니다.

## 🎯 구현 목표
- **성능**: API 응답 < 1초, 동시 사용자 50명, 100 TPS
- **자동화**: 반복 작업 80% 자동화
- **품질**: 테스트 커버리지 80%, 버그율 50% 감소

## 📅 구현 로드맵

### Phase 1: 기초 인프라 (완료 ✅)
```bash
# 이미 완료된 작업들
- [x] 데이터베이스 인덱스 13개 추가
- [x] API 타임아웃 30초 설정
- [x] URL 인코딩 문제 해결
- [x] 배치 처리 최적화 (BatchProcessor)
- [x] API Helper 유틸리티
- [x] 성능 테스트 스크립트
```

### Phase 2: MCP 서버 통합 (1주차)

#### 2.1 MCP 서버 설정
```bash
# 1. 전역 MCP 서버 등록
claude mcp add github -s user npx -y @modelcontextprotocol/server-github
claude mcp add brave-search -s user npx -y @modelcontextprotocol/server-brave-search
claude mcp add gemini-cli -s user npx -y @google/gemini-cli

# 2. 프로젝트 전용 MCP 설정
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

# 3. 환경변수 프리셋
export CLAUDE_ALLOWED_TOOLS="mcp__github__*,mcp__gemini-cli__*"
```

#### 2.2 MCP 서버 구현
```python
# mcp_server.py - 나라장터 전용 MCP 서버
"""
나라장터 API MCP 서버
자동 동기화, 분석, 알림 기능
"""
import asyncio
from mcp import Server, Tool

class NarajangterMCPServer(Server):
    async def sync_daily_data(self):
        """매일 자동 데이터 동기화"""
        # BatchProcessor 활용
        pass
    
    async def analyze_trends(self):
        """입찰 트렌드 분석"""
        pass
    
    async def alert_opportunities(self):
        """관심 입찰 알림"""
        pass
```

### Phase 3: 자동화 & TDD (2주차)

#### 3.1 테스트 자동화
```bash
# tests/ 디렉토리 구조
tests/
├── unit/
│   ├── test_api_helper.py
│   ├── test_batch_processor.py
│   └── test_models.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_database.py
└── e2e/
    └── test_full_workflow.py

# 테스트 실행 스크립트
cat > run_tests.sh << 'EOF'
#!/bin/bash
echo "🧪 Running tests..."

# Unit tests
pytest tests/unit/ -v --cov=src --cov-report=html

# Integration tests
pytest tests/integration/ -v

# E2E tests (if server running)
if curl -s http://localhost:5000 > /dev/null; then
    pytest tests/e2e/ -v
fi

echo "📊 Coverage report: htmlcov/index.html"
EOF
```

#### 3.2 Git Hooks 설정
```bash
# .claude/settings.json
{
  "hooks": {
    "onFileSave": [
      {
        "pattern": "*.py",
        "command": "black ${file} && flake8 ${file}"
      },
      {
        "pattern": "*.js",
        "command": "prettier --write ${file}"
      }
    ],
    "preCommit": "pytest tests/unit/ --quiet"
  }
}
```

### Phase 4: 성능 최적화 고급 (3주차)

#### 4.1 Redis 캐싱
```python
# cache_manager.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 캐시 확인
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 실행 및 캐싱
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# 사용 예
@cache_result(ttl=1800)
def get_analytics_data(start_date, end_date):
    # 무거운 분석 작업
    pass
```

#### 4.2 Celery 비동기 처리
```python
# celery_tasks.py
from celery import Celery
from src.utils.batch_processor import BatchProcessor

celery_app = Celery('narajangter', broker='redis://localhost:6379')

@celery_app.task
def sync_data_async(start_date, end_date):
    """비동기 데이터 동기화"""
    processor = BatchProcessor(db, SERVICE_KEY)
    return processor.sync_bid_notices_optimized(start_date, end_date)

@celery_app.task
def generate_report_async(report_type):
    """비동기 보고서 생성"""
    # 대용량 보고서 생성
    pass

# 스케줄러 설정
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'daily-sync': {
        'task': 'sync_data_async',
        'schedule': crontab(hour=2, minute=0),  # 매일 새벽 2시
    },
}
```

### Phase 5: 멀티 에이전트 & 병렬 처리 (4주차)

#### 5.1 Agent Pool 설정
```bash
# agent_pool.sh
#!/bin/bash
# 멀티 에이전트 풀 시작

claude-code agent-pool start --max 5 \
  --agent frontend --context "./src/static" \
  --agent backend --context "./src" \
  --agent database --context "./src/models" \
  --agent api --context "./src/routes" \
  --agent test --context "./tests"
```

#### 5.2 병렬 워크플로우
```json
// workflows/parallel_sync.json
{
  "name": "병렬 데이터 동기화",
  "agents": [
    {
      "id": "bid_sync",
      "agent": "api",
      "task": "입찰공고 동기화",
      "params": {"date_range": "1_month"}
    },
    {
      "id": "success_sync",
      "agent": "api",
      "task": "낙찰정보 동기화",
      "params": {"date_range": "1_week"}
    },
    {
      "id": "analytics",
      "agent": "backend",
      "task": "분석 데이터 생성",
      "depends_on": ["bid_sync", "success_sync"]
    }
  ]
}
```

## 🛠️ 구현 스크립트

### 통합 설치 스크립트
```bash
#!/bin/bash
# install_all.sh

echo "🚀 나라장터 API 통합 환경 설치"

# 1. Python 패키지
pip3 install --user --break-system-packages \
  redis celery flower pytest pytest-cov black flake8

# 2. Node.js 도구
npm install -g prettier eslint

# 3. MCP 서버
claude mcp add github -s user npx -y @modelcontextprotocol/server-github
claude mcp add gemini-cli -s user npx -y @google/gemini-cli

# 4. Redis 시작 (Docker)
docker run -d --name redis -p 6379:6379 redis:alpine

# 5. 데이터베이스 최적화
python3 add_indexes.py

# 6. 초기 데이터 동기화
python3 -c "
from src.utils.batch_processor import BatchProcessor
# 최근 1주일 데이터 동기화
processor = BatchProcessor(db, SERVICE_KEY)
processor.sync_bid_notices_optimized('20250101', '20250107')
"

echo "✅ 설치 완료!"
```

### 개발 워크플로우 자동화
```bash
#!/bin/bash
# dev_workflow.sh

# 1. Plan Mode로 설계
echo "📝 설계 모드 시작..."
claude --plan-mode "나라장터 신규 기능 설계"

# 2. TDD로 테스트 먼저
echo "🧪 테스트 작성..."
claude "tests/test_new_feature.py 작성. mock 없이 실제 테스트"

# 3. 구현
echo "💻 구현..."
claude "테스트 통과하도록 구현"

# 4. 성능 테스트
echo "⚡ 성능 측정..."
python3 performance_test.py

# 5. 커밋 & PR
echo "📦 커밋 준비..."
git add .
git commit -m "feat: 신규 기능 구현"
```

## 📊 모니터링 대시보드

### Grafana + Prometheus 설정
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
  
  flask-exporter:
    image: pryorda/flask_exporter
    environment:
      - FLASK_APP_URL=http://host.docker.internal:5000
    ports:
      - "9091:9091"
```

## 🎯 성공 지표

### 주간 체크리스트
- [ ] API 응답 시간 < 500ms (95 percentile)
- [ ] 테스트 커버리지 > 80%
- [ ] 일일 동기화 성공률 100%
- [ ] 캐시 적중률 > 40%
- [ ] 코드 리뷰 자동화율 > 60%

### 월간 목표
- [ ] 동시 사용자 100명 처리
- [ ] 일일 100만 건 데이터 처리
- [ ] 다운타임 < 0.1%
- [ ] 배포 자동화 100%

## 💡 팁 & 트릭

1. **5분 피드백 루프**: 작은 단위로 자주 테스트
2. **캐시 우선**: 모든 읽기 작업에 캐시 적용
3. **병렬 처리**: CPU 코어 수만큼 워커 실행
4. **프로파일링**: 월 1회 성능 프로파일링
5. **문서화**: 코드 변경 시 CLAUDE.md 자동 업데이트

## 🚦 다음 단계

1. **즉시 실행**: Phase 2 MCP 서버 설정
2. **이번 주**: TDD 환경 구축
3. **다음 주**: Redis + Celery 통합
4. **월말**: 전체 시스템 부하 테스트

---
*이 계획은 지속적으로 업데이트됩니다. 피드백은 Issues에 남겨주세요.*