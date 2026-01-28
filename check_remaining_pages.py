#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
나머지 2개 페이지 확인
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
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

PAGE_IDS = ["1177321493", "1176109101"]

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
    
    for page_id in PAGE_IDS:
        print(f"\n{'='*60}")
        print(f"페이지 ID: {page_id}")
        print('='*60)
        
        try:
            page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, page_id)
            print(f"제목: {page['title']}")
            print(f"Space: {page['space']['key']}")
            print(f"URL: {CONFLUENCE_URL}/wiki/spaces/{page['space']['key']}/pages/{page_id}")
            
            # 내용 미리보기
            content = page['body']['storage']['value']
            print(f"\n내용 길이: {len(content)} 문자")
            
            # 첨부된 이미지 확인
            if 'ri:attachment' in content:
                print("✓ 플로우차트 이미지 포함됨")
            
        except Exception as e:
            print(f"❌ 오류: {e}")

if __name__ == "__main__":
    main()
