# Confluence 자동 업로드 가이드

## 📋 개요

Mermaid 다이어그램을 자동으로 이미지로 변환하고 Confluence 페이지에 업로드하는 스크립트입니다.

## 🚀 빠른 시작

### 1. 환경 설정

#### 필수 도구 설치

```bash
# Node.js 설치 (Mermaid CLI 사용)
# Windows: https://nodejs.org 에서 다운로드
# Mac: brew install node
# Linux: sudo apt install nodejs npm

# jq 설치 (JSON 파싱용, Bash 스크립트만 해당)
# Windows: choco install jq
# Mac: brew install jq
# Linux: sudo apt install jq
```

#### Confluence API 토큰 생성

1. https://id.atlassian.com/manage-profile/security/api-tokens 접속
2. "Create API token" 클릭
3. 토큰 이름 입력 (예: "Confluence Upload Script")
4. 생성된 토큰 복사 (⚠️ 한 번만 표시됨)

### 2. 환경변수 설정

#### Windows (PowerShell)
```powershell
$env:CONFLUENCE_EMAIL = "your-email@example.com"
$env:CONFLUENCE_API_TOKEN = "your-api-token-here"
```

#### Mac/Linux (Bash)
```bash
export CONFLUENCE_EMAIL="your-email@example.com"
export CONFLUENCE_API_TOKEN="your-api-token-here"
```

**영구 설정 (선택사항):**
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
echo 'export CONFLUENCE_EMAIL="your-email@example.com"' >> ~/.bashrc
echo 'export CONFLUENCE_API_TOKEN="your-api-token-here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. 스크립트 실행

#### Python 버전 (추천)
```bash
# 필수 패키지 설치
pip install requests

# 스크립트 실행
python confluence_upload_script.py
```

#### Bash 버전 (Mac/Linux)
```bash
# 실행 권한 부여
chmod +x confluence_upload_script.sh

# 스크립트 실행
./confluence_upload_script.sh
```

## 📁 파일 구조

```
프로젝트_루트/
├── 공급사별_반려_처리/          # Mermaid 코드가 포함된 .md 파일들
│   ├── README.md
│   ├── 트립닷컴_반려처리.md
│   ├── JTR_반려처리.md
│   └── ...
├── mermaid_images/              # 생성된 이미지 (자동 생성)
│   ├── 트립닷컴_반려처리.png
│   ├── 트립닷컴_반려처리.mmd
│   └── ...
├── confluence_upload_script.py  # Python 스크립트
├── confluence_upload_script.sh  # Bash 스크립트
└── README_자동업로드.md          # 이 파일
```

## 🔧 동작 원리

### Python 스크립트

```
1. .md 파일에서 Mermaid 코드 추출
   ↓
2. Mermaid CLI로 PNG 이미지 생성
   ↓
3. Confluence API로 이미지 업로드
   ↓
4. Confluence 페이지 HTML 생성
   ↓
5. 페이지 업데이트
```

### Bash 스크립트

```
1. awk로 Mermaid 코드 추출
   ↓
2. npx로 PNG 이미지 생성
   ↓
3. curl로 이미지 업로드
   ↓
4. jq로 JSON 생성
   ↓
5. curl로 페이지 업데이트
```

## ⚙️ 설정 수정

### 페이지 ID 변경

스크립트 상단의 `PAGE_ID` 수정:

**Python:**
```python
PAGE_ID = "1177321493"  # 여기를 변경
```

**Bash:**
```bash
PAGE_ID="1177321493"  # 여기를 변경
```

### Confluence URL 변경

```python
CONFLUENCE_URL = "https://mrtcx.atlassian.net"  # 여기를 변경
```

### 입력/출력 디렉토리 변경

```python
INPUT_DIR = "공급사별_반려_처리"  # 입력 디렉토리
OUTPUT_DIR = "mermaid_images"    # 출력 디렉토리
```

## 🐛 트러블슈팅

### 1. 인증 오류 (401 Unauthorized)

**문제:**
```
❌ 오류 발생: 401 Client Error: Unauthorized
```

**해결:**
- 이메일과 API 토큰이 정확한지 확인
- API 토큰을 새로 생성해서 재시도
- Confluence 권한 확인 (페이지 편집 권한 필요)

### 2. Mermaid CLI 오류

**문제:**
```
npx: command not found
```

**해결:**
```bash
# Node.js 설치 확인
node --version
npm --version

# Node.js 재설치
```

### 3. jq 명령어 오류 (Bash만)

**문제:**
```
jq: command not found
```

**해결:**
```bash
# Mac
brew install jq

# Linux
sudo apt install jq

# Windows
choco install jq
```

### 4. Python 패키지 오류

**문제:**
```
ModuleNotFoundError: No module named 'requests'
```

**해결:**
```bash
pip install requests
```

### 5. 한글 파일명 오류

**문제:**
```
UnicodeDecodeError: 'cp949' codec can't decode
```

**해결:**
- 스크립트에서 `encoding='utf-8'` 확인
- Windows에서는 PowerShell 사용 권장

### 6. 이미지 생성 실패

**문제:**
```
✗ 이미지 생성 실패
```

**해결:**
1. Mermaid 문법 확인
2. `.mmd` 파일 내용 수동 확인
3. Mermaid Live Editor에서 테스트: https://mermaid.live/

## 📊 성능

- **처리 속도**: 공급사 1개당 약 2-3초
- **13개 공급사**: 약 30-40초 소요
- **병렬 처리**: 추가 최적화 가능

## 🔐 보안

### API 토큰 관리

⚠️ **주의사항:**
- API 토큰을 Git에 커밋하지 마세요
- `.env` 파일 사용 시 `.gitignore`에 추가

**`.gitignore` 예시:**
```
.env
confluence_upload_script.py
mermaid_images/
*.pyc
__pycache__/
```

### 권한 최소화

- API 토큰은 필요한 권한만 부여
- Confluence 페이지 편집 권한만 필요
- 관리자 권한은 불필요

## 🚀 고급 사용법

### 1. 특정 파일만 업로드

```python
# confluence_upload_script.py 수정
def generate_mermaid_images(input_dir="공급사별_반려_처리", output_dir="mermaid_images", filter_list=None):
    for md_file in Path(input_dir).glob("*.md"):
        if filter_list and md_file.stem not in filter_list:
            continue
        # ...

# 실행 시
mermaid_files = generate_mermaid_images(filter_list=["트립닷컴_반려처리", "JTR_반려처리"])
```

### 2. 자동화 (cron/Task Scheduler)

**Linux/Mac (cron):**
```bash
# crontab -e
# 매일 오전 9시 실행
0 9 * * * cd /path/to/project && /usr/bin/python3 confluence_upload_script.py
```

**Windows (Task Scheduler):**
1. "작업 스케줄러" 실행
2. "작업 만들기" 클릭
3. 트리거: 매일 오전 9시
4. 동작: `python confluence_upload_script.py` 실행

### 3. 여러 페이지 동시 업로드

```python
PAGES = [
    {"id": "1177321493", "title": "공급사별 반려 처리"},
    {"id": "1177321494", "title": "기타 프로세스"},
]

for page in PAGES:
    print(f"업로드 중: {page['title']}")
    # ... 업로드 로직
```

## 📞 지원

문제가 발생하면:
1. 에러 메시지 전체 복사
2. 사용한 명령어 기록
3. 환경 정보 (OS, Python/Node 버전)
4. 팀에 문의

## 📝 변경 이력

- **v1.0** (2025-01-21)
  - 초기 버전
  - Python 및 Bash 스크립트 제공
  - 13개 공급사 프로세스맵 자동 업로드
