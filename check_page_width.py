#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2개 페이지의 현재 설정 확인
"""

import os
import sys
import io
import requests

# UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

PAGE_IDS = {
    "1193803904": "한인민박 상품 등록",
    "1193836635": "T&A 입점 상품 검수"
}

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

def main():
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("인증 정보가 없습니다.")
        return
    
    for page_id, page_name in PAGE_IDS.items():
        print(f"\n{'='*60}")
        print(f"{page_name} (ID: {page_id})")
        print('='*60)
        
        try:
            page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, page_id)
            content = page['body']['storage']['value']
            
            # ac:width 찾기
            import re
            width_matches = re.findall(r'ac:width="(\d+)"', content)
            
            if width_matches:
                print(f"✓ 설정된 width: {width_matches}")
            else:
                print("❌ width 설정 없음!")
            
            # 이미지 파일명 확인
            image_matches = re.findall(r'ri:filename="([^"]+)"', content)
            if image_matches:
                print(f"✓ 이미지 파일: {image_matches}")
                
        except Exception as e:
            print(f"❌ 오류: {e}")

if __name__ == "__main__":
    main()
