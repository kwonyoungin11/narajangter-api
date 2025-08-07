# 나라장터 API Integration Project

한국 조달청 나라장터(KONEPS) 공공입찰 정보를 수집하고 분석하는 Flask 기반 웹 애플리케이션입니다.

## 🚀 주요 기능

- **입찰공고 정보**: 실시간 입찰공고 조회 및 동기화
- **낙찰정보 분석**: 낙찰률, 낙찰금액 통계 분석
- **계약정보 관리**: 계약 체결 정보 추적
- **자동 데이터 동기화**: 배치 처리를 통한 대량 데이터 수집
- **성능 최적화**: 13개 데이터베이스 인덱스, 병렬 처리, 캐싱

## 📋 필수 요구사항

- Python 3.8+
- SQLite3
- Redis (선택사항, 캐싱용)
- 나라장터 오픈API 서비스 키 ([data.go.kr](https://www.data.go.kr)에서 발급)

## 🛠️ 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/YOUR_USERNAME/narajangter-api.git
cd narajangter-api
```

### 2. 의존성 설치
```bash
pip3 install --user -r requirements.txt
# 또는 가상환경 사용
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일 편집하여 API 키 입력
vi .env
```

`.env` 파일 내용:
```
NARAJANGTER_API_KEY=YOUR_API_KEY_HERE
FLASK_ENV=development
FLASK_DEBUG=1
```

### 4. 데이터베이스 초기화
```bash
python3 add_indexes.py
```

### 5. 서버 실행
```bash
./start_server.sh
# 또는
cd narajangter_app
python3 src/main.py
```

서버는 `http://localhost:5000`에서 실행됩니다.

## 📁 프로젝트 구조

```
.
├── narajangter_app/
│   └── src/
│       ├── main.py              # Flask 앱 진입점
│       ├── database/            # SQLite 데이터베이스
│       ├── models/              # 데이터베이스 모델
│       ├── routes/              # API 엔드포인트
│       ├── utils/               # 유틸리티 (API helper, 배치 처리)
│       └── static/              # 프론트엔드 파일
├── tests/                       # 테스트 코드
├── scripts/                     # 실행 스크립트
├── add_indexes.py              # DB 인덱스 생성
├── performance_test.py         # 성능 테스트
├── comprehensive_test.py       # 통합 테스트
└── requirements.txt            # Python 의존성
```

## 🔌 API 엔드포인트

### 입찰공고
- `GET /api/narajangter/bid-notices` - 입찰공고 목록 조회
- `POST /api/narajangter/sync-bid-notices` - 입찰공고 동기화

### 낙찰정보
- `GET /api/narajangter/successful-bids` - 낙찰정보 목록 조회
- `POST /api/narajangter/sync-successful-bids` - 낙찰정보 동기화

### 분석
- `GET /api/narajangter/analytics/bid-amount` - 입찰금액 분석
- `GET /api/narajangter/analytics/successful-bid-rate` - 낙찰률 분석

### 설정
- `GET /api/narajangter/config` - API 설정 조회
- `POST /api/narajangter/config` - API 설정 저장

## 🧪 테스트

### 단위 테스트
```bash
pytest tests/unit/ -v
```

### 통합 테스트
```bash
pytest tests/integration/ -v
```

### 성능 테스트
```bash
python3 performance_test.py
```

### 전체 테스트 with 커버리지
```bash
./run_tests.sh
```

## ⚡ 성능 최적화

프로젝트는 다음과 같은 최적화를 포함합니다:

1. **데이터베이스 인덱싱**: 13개 전략적 인덱스
2. **배치 처리**: ThreadPoolExecutor를 통한 병렬 페이지 처리
3. **API 타임아웃**: 30초 타임아웃, 3회 재시도
4. **벌크 삽입**: SQLAlchemy bulk_insert_mappings
5. **연결 풀링**: 데이터베이스 연결 재사용

## 🚀 배포

### Docker 배포
```bash
docker build -t narajangter-api .
docker run -p 5000:5000 --env-file .env narajangter-api
```

### GitHub Actions CI/CD
`.github/workflows/` 디렉토리의 워크플로우 파일 참조

## 📊 모니터링

### 로그 확인
```bash
tail -f /tmp/flask_server.log
```

### 성능 메트릭
```bash
python3 performance_test.py
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🔗 관련 링크

- [나라장터 공식 사이트](https://www.g2b.go.kr)
- [공공데이터포털](https://www.data.go.kr)
- [나라장터 API 문서](https://www.data.go.kr/data/15000705/openapi.do)

## ⚠️ 주의사항

- API 서비스 키는 절대 GitHub에 커밋하지 마세요
- 날짜 범위 제한: 입찰공고 1개월, 낙찰정보 1주일
- 2025년 1월 6일부터 차세대 나라장터 시스템 적용

## 📞 문의

프로젝트 관련 문의사항은 Issues 탭을 이용해주세요.