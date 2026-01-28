#!/usr/bin/env python3
"""
Confluence 페이지 목차 중복 제거
"""

import os
import requests
import re

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
    print("Remove duplicate TOC")
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
        
        # TOC 매크로 패턴
        toc_pattern = r'<h2>목차</h2>\s*<ac:structured-macro ac:name="toc"[^>]*>.*?</ac:structured-macro>'
        
        # 모든 TOC 찾기
        toc_matches = list(re.finditer(toc_pattern, current_body, re.DOTALL))
        print(f"  [OK] Found {len(toc_matches)} TOC sections")
        
        if len(toc_matches) > 1:
            # 첫 번째 TOC만 남기고 나머지 제거
            new_body = current_body
            for match in reversed(toc_matches[1:]):  # 뒤에서부터 제거
                new_body = new_body[:match.start()] + new_body[match.end():]
            
            print(f"  [OK] Removed {len(toc_matches) - 1} duplicate TOC(s)")
        else:
            print("  [OK] No duplicate TOC found")
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
