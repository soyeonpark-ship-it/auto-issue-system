#!/usr/bin/env python3
"""
Confluence 페이지에 반려시트 확인 단계 추가
"""

import os
import requests

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
PAGE_ID = "1177321493"
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

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
    print("Add 'Check Rejection Sheet' step")
    print("=" * 60)
    
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n[ERROR] Authentication info missing")
        return
    
    print(f"\n[OK] Authentication confirmed")
    print(f"  - Page ID: {PAGE_ID}")
    
    try:
        print("\n[1/2] Getting current page...")
        page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, PAGE_ID)
        current_version = page["version"]["number"]
        current_title = page["title"]
        current_body = page["body"]["storage"]["value"]
        
        print(f"  [OK] Current version: {current_version}")
        print(f"  [OK] Title: {current_title}")
        
        # 반려시트 확인 섹션 추가
        sheet_section = """
<hr />

<h2 id="rejection-sheet-check">📋 반려시트 확인</h2>

<p><strong>반려 알럿 수신 시 가장 먼저 확인해야 할 사항:</strong></p>

<ol>
<li><a href="https://docs.google.com/spreadsheets/d/16c0vj5gC7gkYyi7bU_qfdBwqQxmqfMwe1wiGGCC78zw/edit#gid=0">반려 처리 시트</a> 접속</li>
<li>해당 예약 번호 검색</li>
<li>공급사 확인</li>
<li>반려 사유 확인</li>
<li>아래 공급사별 프로세스 플로우차트 참고</li>
</ol>

"""
        
        # 목차 다음에 반려시트 확인 섹션 삽입
        if "<h2>목차</h2>" in current_body:
            # 목차와 참고자료 사이에 삽입
            parts = current_body.split('<h2>🔗 참고 자료</h2>')
            if len(parts) == 2:
                new_body = parts[0] + sheet_section + '<h2>🔗 참고 자료</h2>' + parts[1]
            else:
                new_body = current_body
        else:
            new_body = current_body
        
        print("\n[2/2] Updating page...")
        result = update_page(
            CONFLUENCE_URL,
            CONFLUENCE_EMAIL,
            CONFLUENCE_API_TOKEN,
            PAGE_ID,
            current_title,
            new_body,
            current_version
        )
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Page updated!")
        print(f"Page: {CONFLUENCE_URL}/wiki/spaces/CD/pages/{PAGE_ID}")
        print(f"Version: {current_version} -> {result['version']['number']}")
        print("=" * 60)
        
    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] HTTP error: {e}")
        if e.response:
            print(f"Response: {e.response.text[:500]}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
