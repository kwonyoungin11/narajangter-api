# GitHub 설정 가이드

## 🚀 GitHub에 프로젝트 업로드하기

### 1. GitHub 저장소 생성

1. [GitHub.com](https://github.com)에 로그인
2. 우측 상단 `+` 버튼 → `New repository` 클릭
3. 저장소 설정:
   - Repository name: `narajangter-api`
   - Description: `나라장터 공공입찰 정보 수집 및 분석 시스템`
   - Public/Private 선택
   - **중요**: `Add a README file` 체크 해제 (이미 있음)
   - `Create repository` 클릭

### 2. 로컬 프로젝트를 GitHub에 연결

```bash
cd "/home/ls/nara1/나라장터 api"

# Git 사용자 정보 설정 (최초 1회)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 브랜치 이름을 main으로 변경
git branch -m main

# 파일 추가 및 커밋
git add .
git commit -m "Initial commit: 나라장터 API integration project"

# GitHub 저장소 연결 (YOUR_USERNAME을 실제 GitHub 사용자명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/narajangter-api.git

# 코드 푸시
git push -u origin main
```

### 3. GitHub Secrets 설정 (중요!)

GitHub Actions가 동작하려면 API 키를 GitHub Secrets에 저장해야 합니다:

1. GitHub 저장소 페이지로 이동
2. `Settings` 탭 클릭
3. 좌측 메뉴에서 `Secrets and variables` → `Actions` 클릭
4. `New repository secret` 클릭
5. 다음 시크릿 추가:
   - Name: `NARAJANGTER_API_KEY`
   - Value: 실제 API 키 입력
6. `Add secret` 클릭

## 📱 어디서든 작업하기

### 다른 컴퓨터에서 작업하기

```bash
# 저장소 클론
git clone https://github.com/YOUR_USERNAME/narajangter-api.git
cd narajangter-api

# 의존성 설치
pip3 install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 데이터베이스 초기화
python3 add_indexes.py

# 서버 실행
./start_server.sh
```

### GitHub Codespaces에서 작업하기

1. GitHub 저장소 페이지에서 `Code` 버튼 클릭
2. `Codespaces` 탭 선택
3. `Create codespace on main` 클릭
4. 브라우저에서 VS Code가 열리면 터미널에서:
   ```bash
   pip install -r requirements.txt
   python3 add_indexes.py
   ./start_server.sh
   ```

### 모바일에서 확인하기

GitHub 모바일 앱을 통해 코드 확인, 이슈 관리, PR 리뷰 가능

## 🔄 협업 워크플로우

### 1. 새 기능 개발
```bash
# 최신 코드 받기
git pull origin main

# 새 브랜치 생성
git checkout -b feature/new-feature

# 작업 후 커밋
git add .
git commit -m "feat: 새 기능 추가"

# 푸시
git push origin feature/new-feature
```

### 2. Pull Request 생성
1. GitHub 저장소 페이지에서 `Pull requests` 탭
2. `New pull request` 클릭
3. 브랜치 선택 후 `Create pull request`

### 3. 코드 리뷰 및 머지
- 팀원이 코드 리뷰
- 테스트 통과 확인 (GitHub Actions)
- `Merge pull request` 클릭

## 🔐 보안 주의사항

### 절대 커밋하지 말아야 할 것들
- API 키 (`.env` 파일)
- 데이터베이스 파일 (`*.db`)
- 개인정보가 포함된 파일
- 서비스 키 문서 (`조달청_나라장터*/`)

### 실수로 커밋한 경우
```bash
# 마지막 커밋에서 파일 제거
git rm --cached sensitive_file
git commit --amend

# 이미 푸시한 경우 (주의: force push 필요)
git push --force origin branch_name
```

## 🚨 GitHub Actions 모니터링

### CI/CD 파이프라인 확인
1. GitHub 저장소에서 `Actions` 탭 클릭
2. 워크플로우 실행 상태 확인
3. 실패 시 로그 확인 및 수정

### 일일 동기화 작업 확인
- `Daily Data Sync` 워크플로우가 매일 새벽 2시에 실행
- 수동 실행: Actions → Daily Data Sync → Run workflow

## 📊 프로젝트 상태 배지 추가

README.md 상단에 추가:
```markdown
![CI/CD](https://github.com/YOUR_USERNAME/narajangter-api/workflows/CI%2FCD%20Pipeline/badge.svg)
![Daily Sync](https://github.com/YOUR_USERNAME/narajangter-api/workflows/Daily%20Data%20Sync/badge.svg)
```

## 🆘 문제 해결

### 권한 오류
```bash
# HTTPS 대신 SSH 사용
git remote set-url origin git@github.com:YOUR_USERNAME/narajangter-api.git
```

### 대용량 파일 오류
```bash
# Git LFS 설치 및 사용
git lfs track "*.db"
git add .gitattributes
```

### Actions 실패
- Secrets 설정 확인
- requirements.txt 버전 호환성 확인
- 테스트 코드 오류 확인

## 📝 다음 단계

1. **문서화**: Wiki 페이지 작성
2. **이슈 템플릿**: 버그 리포트, 기능 요청 템플릿 추가
3. **보안 스캔**: Dependabot 활성화
4. **배포 자동화**: AWS/Azure/GCP 연동
5. **모니터링**: Sentry, DataDog 등 연동

---

이제 어디서든 GitHub을 통해 프로젝트에 접근하고 작업할 수 있습니다! 🎉