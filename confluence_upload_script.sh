#!/bin/bash

# Confluence 자동 업로드 스크립트 (Bash 버전)
# 더 간단한 방법으로 Mermaid를 Confluence에 업로드

set -e

# 설정
CONFLUENCE_URL="https://mrtcx.atlassian.net"
PAGE_ID="1177321493"
INPUT_DIR="공급사별_반려_처리"
OUTPUT_DIR="mermaid_images"

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "Confluence 자동 업로드 스크립트"
echo "============================================================"

# 1. 인증 정보 확인
if [ -z "$CONFLUENCE_EMAIL" ] || [ -z "$CONFLUENCE_API_TOKEN" ]; then
    echo -e "${RED}❌ 인증 정보가 설정되지 않았습니다.${NC}"
    echo ""
    echo "다음 환경변수를 설정하세요:"
    echo "  export CONFLUENCE_EMAIL='your-email@example.com'"
    echo "  export CONFLUENCE_API_TOKEN='your-api-token'"
    echo ""
    echo "API 토큰 생성: https://id.atlassian.com/manage-profile/security/api-tokens"
    exit 1
fi

echo -e "${GREEN}✓ 인증 정보 확인 완료${NC}"
echo "  - Email: $CONFLUENCE_EMAIL"
echo "  - Page ID: $PAGE_ID"

# 2. 출력 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# 3. Mermaid 이미지 생성
echo ""
echo "[1/3] Mermaid 다이어그램을 이미지로 변환 중..."

count=0
for md_file in "$INPUT_DIR"/*.md; do
    filename=$(basename "$md_file")
    
    # README.md 건너뛰기
    if [ "$filename" = "README.md" ]; then
        continue
    fi
    
    base_name="${filename%.md}"
    echo "  처리 중: $filename"
    
    # Mermaid 코드 추출 (awk 사용)
    awk '/```mermaid/,/```/' "$md_file" | sed '1d;$d' > "$OUTPUT_DIR/${base_name}.mmd"
    
    # Mermaid CLI로 이미지 생성
    if npx -y @mermaid-js/mermaid-cli@latest \
        -i "$OUTPUT_DIR/${base_name}.mmd" \
        -o "$OUTPUT_DIR/${base_name}.png" \
        -b transparent > /dev/null 2>&1; then
        echo -e "    ${GREEN}✓ 이미지 생성: ${base_name}.png${NC}"
        ((count++))
    else
        echo -e "    ${RED}✗ 이미지 생성 실패${NC}"
    fi
done

echo -e "${GREEN}  ✓ ${count}개 이미지 생성 완료${NC}"

# 4. Confluence API 호출 함수
confluence_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -n "$data" ]; then
        curl -s -X "$method" \
            -u "${CONFLUENCE_EMAIL}:${CONFLUENCE_API_TOKEN}" \
            -H "Content-Type: application/json" \
            "${CONFLUENCE_URL}/wiki/rest/api/${endpoint}" \
            -d "$data"
    else
        curl -s -X "$method" \
            -u "${CONFLUENCE_EMAIL}:${CONFLUENCE_API_TOKEN}" \
            -H "Content-Type: application/json" \
            "${CONFLUENCE_URL}/wiki/rest/api/${endpoint}"
    fi
}

# 5. 페이지 정보 가져오기
echo ""
echo "[2/3] Confluence 페이지 정보 가져오기..."

page_info=$(confluence_api "GET" "content/${PAGE_ID}?expand=body.storage,version")
current_version=$(echo "$page_info" | jq -r '.version.number')
page_title=$(echo "$page_info" | jq -r '.title')

if [ -z "$current_version" ] || [ "$current_version" = "null" ]; then
    echo -e "${RED}❌ 페이지 정보를 가져올 수 없습니다.${NC}"
    echo "응답: $page_info"
    exit 1
fi

echo -e "${GREEN}  ✓ 페이지 정보 가져오기 완료${NC}"
echo "  - 제목: $page_title"
echo "  - 버전: $current_version"

# 6. 이미지 업로드
echo ""
echo "[3/3] 이미지 업로드 중..."

upload_count=0
for png_file in "$OUTPUT_DIR"/*.png; do
    filename=$(basename "$png_file")
    echo "  업로드 중: $filename"
    
    # 첨부파일 업로드
    curl -s -X POST \
        -u "${CONFLUENCE_EMAIL}:${CONFLUENCE_API_TOKEN}" \
        -H "X-Atlassian-Token: no-check" \
        -F "file=@${png_file}" \
        "${CONFLUENCE_URL}/wiki/rest/api/content/${PAGE_ID}/child/attachment" \
        > /dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "    ${GREEN}✓ 업로드 완료${NC}"
        ((upload_count++))
    else
        echo -e "    ${RED}✗ 업로드 실패${NC}"
    fi
done

echo -e "${GREEN}  ✓ ${upload_count}개 이미지 업로드 완료${NC}"

# 7. 페이지 컨텐츠 생성
echo ""
echo "페이지 컨텐츠 생성 중..."

content="<h1>공급사별 반려 처리 프로세스맵</h1>
<ac:structured-macro ac:name=\"info\">
<ac:rich-text-body>
<p>이 페이지는 자동으로 생성되었습니다.</p>
</ac:rich-text-body>
</ac:structured-macro>
<h2>목차</h2>
<p><ac:structured-macro ac:name=\"toc\" /></p>
"

for png_file in "$OUTPUT_DIR"/*.png; do
    filename=$(basename "$png_file")
    title="${filename%.png}"
    title="${title//_반려처리/}"
    
    content+="<h2>${title}</h2>
<ac:image>
<ri:attachment ri:filename=\"${filename}\" />
</ac:image>
<hr />
"
done

# 8. 페이지 업데이트
echo "페이지 업데이트 중..."

new_version=$((current_version + 1))

update_data=$(cat <<EOF
{
  "version": {
    "number": ${new_version}
  },
  "title": "${page_title}",
  "type": "page",
  "body": {
    "storage": {
      "value": $(echo "$content" | jq -Rs .),
      "representation": "storage"
    }
  }
}
EOF
)

response=$(confluence_api "PUT" "content/${PAGE_ID}" "$update_data")

if echo "$response" | jq -e '.version.number' > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ 페이지 업데이트 완료${NC}"
else
    echo -e "${RED}  ✗ 페이지 업데이트 실패${NC}"
    echo "응답: $response"
    exit 1
fi

# 9. 완료
echo ""
echo "============================================================"
echo -e "${GREEN}✅ 모든 작업이 완료되었습니다!${NC}"
echo "📄 페이지 확인: ${CONFLUENCE_URL}/wiki/spaces/aoh/pages/${PAGE_ID}"
echo "============================================================"
