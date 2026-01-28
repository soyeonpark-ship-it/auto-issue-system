#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
원본 Confluence 페이지 내용 가져오기
"""

import os
import sys
import io
import requests
import json

# UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
SOURCE_PAGE_ID = "780861470"

CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

def get_page(url, email, api_token, page_id):
    """페이지 정보 가져오기"""
    endpoint = f"{url}/wiki/rest/api/content/{page_id}?expand=body.storage,version,space"
    response = requests.get(
        endpoint,
        auth=(email, api_token),
        headers={"Accept": "application/json"}
    )
    response.raise_for_status()
    return response.json()

def main():
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("인증 정보가 없습니다.")
        return
    
    print(f"원본 페이지 가져오는 중... (ID: {SOURCE_PAGE_ID})")
    
    try:
        page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, SOURCE_PAGE_ID)
        
        print(f"\n제목: {page['title']}")
        print(f"Space: {page['space']['key']}")
        print(f"\n페이지 내용을 content.json에 저장합니다...")
        
        # 내용을 JSON 파일로 저장
        with open('confluence_content.json', 'w', encoding='utf-8') as f:
            json.dump(page, f, ensure_ascii=False, indent=2)
        
        # HTML 내용을 별도 파일로 저장
        with open('confluence_content.html', 'w', encoding='utf-8') as f:
            f.write(page['body']['storage']['value'])
        
        print("✓ confluence_content.json 저장 완료")
        print("✓ confluence_content.html 저장 완료")
        
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
