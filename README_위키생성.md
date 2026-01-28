# Confluence Wiki 자동 생성 가이드

## 🎯 한 줄 요약

Confluence 페이지를 Mermaid 플로우차트로 시각화하여 새 페이지에 자동 업로드합니다.

## 📝 사용 방법

### 기본 프롬프트

```
@.cursor/rules/confluence-wiki-generator.mdc 
[원본 페이지 URL] 을 [대상 페이지 URL] 위키 생성해줘
```

### 실제 예시

```
@.cursor/rules/confluence-wiki-generator.mdc 
https://mrtcx.atlassian.net/wiki/spaces/aoh/pages/882901069 
을 
https://mrtcx.atlassian.net/wiki/spaces/aoh/pages/1176109101 
위키 생성해줘
```

## 🚀 빠른 시작

### 1단계: 환경 설정 (최초 1회)

```powershell
$env:CONFLUENCE_EMAIL = "your.email@aicx.kr"
$env:CONFLUENCE_API_TOKEN = "your_api_token"
```

### 2단계: 프롬프트 입력

```
@.cursor/rules/confluence-wiki-generator.mdc 
[원본ID] 을 [대상ID] 위키 생성해줘
```

### 3단계: 자동 완료!

AI가 자동으로:
- ✅ 원본 페이지 분석
- ✅ Mermaid 플로우차트 생성
- ✅ PNG 이미지 변환
- ✅ Confluence 업로드

## 📊 생성되는 페이지 구조

```
┌─────────────────────────────────┐
│ 목차 (자동 생성)                │
├─────────────────────────────────┤
│ 🔗 참고 자료                    │
│  - 링크 1                       │
│  - 링크 2                       │
├─────────────────────────────────┤
│ 📊 프로세스 플로우차트          │
│  [이미지]                       │
└─────────────────────────────────┘
```

## 🎨 다양한 프롬프트 형식

### 짧은 버전 (페이지 ID만)
```
@.cursor/rules/confluence-wiki-generator.mdc 
882901069 을 1176109101 위키 생성해줘
```

### 설명 포함
```
@.cursor/rules/confluence-wiki-generator.mdc 
상품 등록 가이드(882901069)를 플로우차트(1176109101)로 위키 생성해줘
```

### 여러 줄
```
@.cursor/rules/confluence-wiki-generator.mdc 
https://mrtcx.atlassian.net/wiki/spaces/aoh/pages/882901069/2.0 
을 
https://mrtcx.atlassian.net/wiki/spaces/aoh/pages/1176109101/2.0 
위키 생성해줘
```

## 🔑 핵심 키워드

1. `@.cursor/rules/confluence-wiki-generator.mdc` - 규칙 파일
2. `[원본 URL 또는 ID]` - 복제할 페이지
3. `을` - 구분자
4. `[대상 URL 또는 ID]` - 생성할 페이지
5. `위키 생성해줘` - 트리거

## ✅ 실행 결과 예시

```
============================================================
[SUCCESS] Confluence Wiki 생성 완료!
============================================================

📄 페이지: https://mrtcx.atlassian.net/wiki/spaces/aoh/pages/1176109101
📊 버전: 5 -> 6
🖼️  이미지: 1개

생성된 파일:
  - 해외_연동_신규_상품_등록/해외_연동_신규_상품_등록_2.0_플로우.md
  - mermaid_images/해외_연동_신규_상품_등록_2.0_플로우.md.png

============================================================
```

## 📁 프로젝트 구조

```
ojm/
├── .cursor/rules/
│   ├── confluence-wiki-generator.mdc        # 핵심 규칙
│   └── confluence-wiki-prompt-guide.mdc     # 상세 가이드
├── confluence_upload_mermaid_images.py      # 업로드 스크립트
├── mermaid_images/                          # 생성된 이미지
├── [프로세스명]/                            # 프로세스별 폴더
│   └── [프로세스명].md                      # Mermaid 소스
└── README_위키생성.md                       # 이 파일
```

## 🛠️ 기술 스택

- **Confluence REST API**: 페이지 읽기/쓰기
- **Mermaid**: 플로우차트 작성
- **Mermaid.ink**: 이미지 변환
- **Python**: 자동화 스크립트
- **Cursor Rules**: AI 동작 정의

## 📚 관련 문서

- **confluence-wiki-generator.mdc**: AI 동작 규칙 정의
- **confluence-wiki-prompt-guide.mdc**: 상세 프롬프트 가이드
- **README_자동업로드.md**: 수동 실행 가이드

## 💡 활용 예시

### 예시 1: 프로세스 문서화
```
복잡한 업무 프로세스 → 명확한 플로우차트
```

### 예시 2: 팀 온보딩
```
텍스트 가이드 → 시각적 프로세스 맵
```

### 예시 3: 표준화
```
여러 페이지 → 일관된 포맷
```

## ⚠️ 주의사항

1. **환경 변수 설정 필수**
   - `CONFLUENCE_EMAIL`
   - `CONFLUENCE_API_TOKEN`

2. **페이지 권한 확인**
   - 원본: 읽기 권한
   - 대상: 쓰기 권한

3. **네트워크 연결**
   - Confluence 접근 가능
   - mermaid.ink 접근 가능

## 🔧 문제 해결

### 인증 실패
```
[ERROR] Authentication failed
→ API 토큰 재확인
```

### 페이지 없음
```
[ERROR] Page not found
→ 페이지 ID 확인
```

### 이미지 변환 실패
```
[ERROR] Mermaid conversion failed
→ Mermaid 문법 확인
```

## 🎓 추가 학습

- [Confluence API 문서](https://developer.atlassian.com/cloud/confluence/rest/)
- [Mermaid 문법](https://mermaid.js.org/syntax/flowchart.html)
- [프로세스 맵 작성 규칙](.cursor/rules/mermaid-flowchart-adaptive.mdc)

## 📞 도움말

문제가 있나요?

1. 프롬프트 포맷 확인
2. 환경 변수 확인
3. 페이지 권한 확인
4. confluence-wiki-prompt-guide.mdc 참조

## 🚀 다음 단계

1. **첫 번째 위키 생성하기**
2. **팀과 공유하기**
3. **표준 프로세스 문서화하기**
4. **지속적으로 개선하기**

---

**Happy Wiki Creating! 🎉**
