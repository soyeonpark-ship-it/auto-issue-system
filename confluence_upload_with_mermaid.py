#!/usr/bin/env python3
"""
Confluence 업로드 - Mermaid 다이어그램 포함
"""

import os
import requests
import re
from pathlib import Path

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
PAGE_ID = "1177321493"
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

def extract_mermaid(md_file):
    """마크다운 파일에서 Mermaid 코드 추출"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def get_all_mermaid_diagrams(input_dir="공급사별_반려_처리"):
    """모든 Mermaid 다이어그램 추출"""
    diagrams = []
    
    files = [
        "트립닷컴_반려처리.md",
        "JTR_반려처리.md",
        "KLOOK_반려처리.md",
        "링크티비티_반려처리.md",
        "레일유럽_반려처리.md",
        "BMG_반려처리.md",
        "GYG_반려처리.md",
        "VIATOR_반려처리.md",
        "TIQETS_반려처리.md",
        "USH_반려처리.md",
        "LA디즈니랜드_반려처리.md",
        "몽키트레블_반려처리.md",
        "KKDAY_반려처리.md"
    ]
    
    for filename in files:
        filepath = Path(input_dir) / filename
        if filepath.exists():
            mermaid_code = extract_mermaid(filepath)
            if mermaid_code:
                title = filename.replace("_반려처리.md", "")
                diagrams.append({
                    "title": title,
                    "code": mermaid_code
                })
                print(f"  ✓ {title}")
    
    return diagrams

def generate_confluence_html(diagrams):
    """Confluence HTML 생성 (Mermaid 포함)"""
    html = """
<h1>공급사별 반려 처리 가이드</h1>

<ac:structured-macro ac:name="info">
<ac:rich-text-body>
<p>이 페이지는 자동으로 생성되었습니다. 각 공급사별 Mermaid 다이어그램과 상세 처리 방법을 확인하세요.</p>
</ac:rich-text-body>
</ac:structured-macro>

<h2>목차</h2>
<ac:structured-macro ac:name="toc" ac:schema-version="1">
  <ac:parameter ac:name="printable">true</ac:parameter>
  <ac:parameter ac:name="style">disc</ac:parameter>
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
  <ac:parameter ac:name="minLevel">1</ac:parameter>
</ac:structured-macro>

<hr />

<h2>🔗 참고 자료</h2>
<ul>
<li><a href="https://docs.google.com/spreadsheets/d/16c0vj5gC7gkYyi8bU_qfdBwqQxmqfMwe1wiGGCC78zw/edit#gid=0">반려 처리 시트</a></li>
<li><a href="https://docs.google.com/spreadsheets/d/1aRMZdr7tLbCqptVe8f5XRGUViRoUriXoPIgrBbNzlCI/edit?pli=1&gid=802671048#gid=802671048">공급사 어드민 및 이메일 계정 정보</a></li>
<li><a href="https://aicx-kr.slack.com/archives/C02D5KZLM1Q">모니터링 슬랙 채널</a></li>
</ul>

<hr />
"""
    
    # 각 공급사별 다이어그램 추가
    for diagram in diagrams:
        html += f"""
<h2>{diagram['title']}</h2>

<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">mermaid</ac:parameter>
<ac:parameter ac:name="theme">confluence</ac:parameter>
<ac:plain-text-body><![CDATA[{diagram['code']}]]></ac:plain-text-body>
</ac:structured-macro>

<hr />

"""
    
    return html

def get_page(url, email, api_token, page_id):
    """페이지 정보 가져오기"""
    endpoint = f"{url}/wiki/rest/api/content/{page_id}?expand=body.storage,version"
    response = requests.get(
        endpoint,
        auth=(email, api_token),
        headers={"Accept": "application/json"}
    )
    response.raise_for_status()
    return response.json()

def update_page(url, email, api_token, page_id, title, content, version):
    """페이지 업데이트"""
    endpoint = f"{url}/wiki/rest/api/content/{page_id}"
    data = {
        "version": {"number": version + 1},
        "title": title,
        "type": "page",
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }
    response = requests.put(
        endpoint,
        auth=(email, api_token),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        json=data
    )
    response.raise_for_status()
    return response.json()

def main():
    print("=" * 60)
    print("Confluence 업로드 - Mermaid 다이어그램 포함")
    print("=" * 60)
    
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n인증 정보가 없습니다.")
        return
    
    print(f"\n✓ 인증 정보 확인")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - Page ID: {PAGE_ID}")
    
    try:
        # Mermaid 다이어그램 추출
        print("\n[1/3] Mermaid 다이어그램 추출 중...")
        diagrams = get_all_mermaid_diagrams()
        print(f"  ✓ {len(diagrams)}개 다이어그램 추출 완료")
        
        # HTML 생성
        print("\n[2/3] Confluence HTML 생성 중...")
        html_content = generate_confluence_html(diagrams)
        print(f"  ✓ HTML 생성 완료")
        
        # 페이지 정보 가져오기
        print("\n[3/3] 페이지 업데이트 중...")
        page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, PAGE_ID)
        current_version = page["version"]["number"]
        current_title = page["title"]
        
        # 페이지 업데이트
        result = update_page(
            CONFLUENCE_URL,
            CONFLUENCE_EMAIL,
            CONFLUENCE_API_TOKEN,
            PAGE_ID,
            current_title,
            html_content,
            current_version
        )
        
        print("\n" + "=" * 60)
        print("✅ 업로드 완료!")
        print(f"📄 페이지: {CONFLUENCE_URL}/wiki/spaces/aoh/pages/{PAGE_ID}")
        print(f"📊 버전: {current_version} → {result['version']['number']}")
        print(f"📈 다이어그램: {len(diagrams)}개")
        print("=" * 60)
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP 오류: {e}")
        if e.response:
            print(f"응답: {e.response.text[:500]}")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
