#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T&A 페이지 설정 확인 및 다른 페이지들과 비교
"""

import os
import sys
import io
import requests
import re

# UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

# T&A 페이지 (기준)
REFERENCE_PAGE_ID = "1193836635"

# 비교할 페이지들
COMPARISON_PAGES = {
    "1191477354": "연동 예약 운영 모니터링",
    "1192394909": "국내 연동 신규 상품 등록 (2.0)",
    "1193803904": "한인민박 상품 등록",
    "1194033239": "한인민박 파트너 검수",
    "1194000407": "해외 연동 신규 상품 등록 (3.0)",
    "1176109101": "해외 연동 신규 상품 등록 (2.0)"
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

def analyze_page(content):
    """페이지 HTML 분석"""
    # ac:width 찾기
    width_match = re.search(r'ac:width="(\d+)"', content)
    width = width_match.group(1) if width_match else "없음"
    
    # 이미지 파일명
    image_match = re.search(r'ri:filename="([^"]+)"', content)
    image = image_match.group(1) if image_match else "없음"
    
    # ac:image 태그 전체
    image_tag = re.search(r'<ac:image[^>]*>', content)
    tag = image_tag.group(0) if image_tag else "없음"
    
    return width, image, tag

def main():
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("인증 정보가 없습니다.")
        return
    
    print("=" * 80)
    print("T&A 페이지 설정 확인 (기준)")
    print("=" * 80)
    
    # T&A 페이지 분석
    ref_page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, REFERENCE_PAGE_ID)
    ref_content = ref_page['body']['storage']['value']
    ref_width, ref_image, ref_tag = analyze_page(ref_content)
    
    print(f"✓ Width: {ref_width}px")
    print(f"✓ 이미지: {ref_image}")
    print(f"✓ 태그:\n{ref_tag}")
    
    print("\n" + "=" * 80)
    print("다른 페이지들과 비교")
    print("=" * 80)
    
    for page_id, page_name in COMPARISON_PAGES.items():
        try:
            page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, page_id)
            content = page['body']['storage']['value']
            width, image, tag = analyze_page(content)
            
            match = "✅" if width == ref_width else "❌"
            print(f"\n{match} {page_name} (ID: {page_id})")
            print(f"   Width: {width}px")
            print(f"   이미지: {image}")
            
        except Exception as e:
            print(f"\n❌ {page_name}: 오류 - {e}")

if __name__ == "__main__":
    main()
