#!/usr/bin/env python3
"""
Confluence Wiki 업로드 스크립트 - 해외 호텔 예약 확정 프로세스
"""

import os
import sys
import requests
from pathlib import Path

# UTF-8 출력 강제
sys.stdout.reconfigure(encoding='utf-8')

# Confluence API 설정
CONFLUENCE_BASE_URL = "https://mrtcx.atlassian.net/wiki"
PAGE_ID = "1194459151"

# 환경 변수에서 인증 정보 가져오기
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL", "soyeon.park@aicx.kr")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

# 이미지 파일 경로
IMAGE_PATH = Path("mermaid_images/overseas_hotel_booking.png")

def upload_attachment(page_id: str, file_path: Path, auth: tuple) -> dict:
    """Confluence 페이지에 첨부파일 업로드"""
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}/child/attachment"
    
    headers = {
        "X-Atlassian-Token": "no-check"
    }
    
    with open(file_path, 'rb') as f:
        files = {
            'file': (file_path.name, f, 'image/png')
        }
        response = requests.post(url, auth=auth, headers=headers, files=files)
    
    if response.status_code == 200:
        return response.json()['results'][0]
    else:
        response.raise_for_status()

def get_page(page_id: str, auth: tuple) -> dict:
    """현재 페이지 정보 가져오기"""
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}"
    params = {"expand": "version,body.storage"}
    response = requests.get(url, auth=auth, params=params)
    response.raise_for_status()
    return response.json()

def update_page(page_id: str, title: str, content: str, version: int, auth: tuple):
    """페이지 업데이트"""
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}"
    
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
    
    response = requests.put(url, json=data, auth=auth)
    response.raise_for_status()
    return response.json()

def main():
    print("=" * 60)
    print("Confluence Wiki 생성 - 해외 호텔 예약 확정")
    print("=" * 60)
    print()
    
    auth = (CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
    
    print("인증 정보 확인")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - 대상 페이지: {PAGE_ID}")
    print()
    
    # 1. 이미지 업로드
    print("[1/2] Mermaid 플로우차트 이미지 업로드...")
    attachment = upload_attachment(PAGE_ID, IMAGE_PATH, auth)
    print(f"  이미지 업로드 완료: {IMAGE_PATH.name}")
    print()
    
    # 2. 페이지 업데이트
    print("[2/2] 페이지 업데이트...")
    
    page = get_page(PAGE_ID, auth)
    current_version = page['version']['number']
    current_title = page['title']
    
    # Confluence HTML 생성 (제목 수정하지 않음)
    confluence_html = f'''<ac:structured-macro ac:name="toc" ac:schema-version="1">
  <ac:parameter ac:name="printable">true</ac:parameter>
  <ac:parameter ac:name="style">disc</ac:parameter>
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
  <ac:parameter ac:name="minLevel">1</ac:parameter>
  <ac:parameter ac:name="class">bigpink</ac:parameter>
  <ac:parameter ac:name="exclude"></ac:parameter>
  <ac:parameter ac:name="type">list</ac:parameter>
  <ac:parameter ac:name="outline">clear</ac:parameter>
  <ac:parameter ac:name="include"></ac:parameter>
</ac:structured-macro>

<hr/>

<h2>프로세스 플로우차트</h2>
<p><ac:image ac:align="center" ac:layout="center" ac:width="1200">
  <ri:attachment ri:filename="{IMAGE_PATH.name}"/>
</ac:image></p>

<hr/>

<h2>참고 자료</h2>
<ul>
  <li><strong>MRT 사이트</strong>: 여행자 예약</li>
  <li><strong>대시보드</strong>: 예약현황 확인 (확정대기 상태)</li>
  <li><strong>파트너 페이지</strong>: 예약 관리 및 확정 처리</li>
  <li><strong>센드버드</strong>: 여행자와의 채팅</li>
  <li><strong>관리시트</strong>: 예약 정보 기록 및 Stay실 공유</li>
  <li><strong>메일</strong>: global.ops@myrealtrip.com, global.hotels@myrealtrip.com, Myrealtrip.global@gmail.com</li>
  <li><strong>네이트온</strong>: 랜드사 관리 호텔 핫라인</li>
</ul>
'''
    
    result = update_page(PAGE_ID, current_title, confluence_html, current_version, auth)
    print()
    
    print("=" * 60)
    print("Confluence Wiki 생성 완료!")
    print("=" * 60)
    print(f"페이지: {CONFLUENCE_BASE_URL}/spaces/CD/pages/{PAGE_ID}")
    print(f"제목: {current_title}")
    print(f"버전: {current_version} → {result['version']['number']}")
    print(f"플로우차트: {IMAGE_PATH.name}")
    print("=" * 60)

if __name__ == "__main__":
    main()
