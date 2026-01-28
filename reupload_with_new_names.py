#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파일명을 변경하여 새 버전으로 업로드 (캐시 우회)
"""

import os
import sys
import io
import requests
import shutil
from datetime import datetime

# UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

# 업로드할 페이지들
PAGES = [
    {
        "id": "1191477354",
        "name": "연동 예약 운영 모니터링",
        "old_image": "monitoring_flowchart.png",
        "new_image": "monitoring_flowchart_v2.png"
    },
    {
        "id": "1192394909",
        "name": "국내 연동 신규 상품 등록 (2.0)",
        "old_image": "domestic_product_register.png",
        "new_image": "domestic_product_register_v2.png"
    },
    {
        "id": "1193836635",
        "name": "T&A 입점 상품 검수",
        "old_image": "ta_inspection.png",
        "new_image": "ta_inspection_v2.png"
    },
    {
        "id": "1194033239",
        "name": "한인민박 파트너 검수",
        "old_image": "hanin_partner_inspection.png",
        "new_image": "hanin_partner_inspection_v2.png"
    },
    {
        "id": "1193803904",
        "name": "한인민박 상품 등록",
        "old_image": "hanin_product_register.png",
        "new_image": "hanin_product_register_v2.png"
    }
]

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

def upload_attachment(url, email, api_token, page_id, file_path):
    """첨부파일 업로드 (새 파일로)"""
    endpoint = f"{url}/wiki/rest/api/content/{page_id}/child/attachment"
    
    file_name = os.path.basename(file_path)
    
    # 새 파일로 업로드 (기존 파일명 체크 안함)
    with open(file_path, 'rb') as f:
        files = {'file': (file_name, f, 'image/png')}
        headers = {"X-Atlassian-Token": "no-check"}
        response = requests.post(
            endpoint,
            auth=(email, api_token),
            headers=headers,
            files=files
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

def generate_html(image_filename, page_name):
    """간단한 HTML 생성"""
    html = f"""
<h2>목차</h2>
<ac:structured-macro ac:name="toc" ac:schema-version="1">
  <ac:parameter ac:name="printable">true</ac:parameter>
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
  <ac:parameter ac:name="minLevel">1</ac:parameter>
</ac:structured-macro>

<hr />

<h2>📊 {page_name} 프로세스 플로우차트</h2>

<p>
<ac:image ac:width="1200">
<ri:attachment ri:filename="{image_filename}" />
</ac:image>
</p>
"""
    return html

def main():
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("인증 정보가 없습니다.")
        return
    
    print("=" * 70)
    print("파일명 변경하여 재업로드 (캐시 우회)")
    print("=" * 70)
    
    for page in PAGES:
        print(f"\n[{PAGES.index(page) + 1}/{len(PAGES)}] {page['name']}")
        
        try:
            # 1. 이미지 파일 복사 (v2로)
            old_path = f"mermaid_images/{page['old_image']}"
            new_path = f"mermaid_images/{page['new_image']}"
            shutil.copy2(old_path, new_path)
            print(f"  ✓ 이미지 복사: {page['new_image']}")
            
            # 2. 새 이미지 업로드
            upload_attachment(
                CONFLUENCE_URL,
                CONFLUENCE_EMAIL,
                CONFLUENCE_API_TOKEN,
                page['id'],
                new_path
            )
            print(f"  ✓ 이미지 업로드 완료")
            
            # 3. 페이지 업데이트
            page_data = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, page['id'])
            current_version = page_data["version"]["number"]
            current_title = page_data["title"]
            
            html_content = generate_html(page['new_image'], page['name'])
            
            result = update_page(
                CONFLUENCE_URL,
                CONFLUENCE_EMAIL,
                CONFLUENCE_API_TOKEN,
                page['id'],
                current_title,
                html_content,
                current_version
            )
            
            print(f"  ✓ 페이지 업데이트: v{current_version} → v{result['version']['number']}")
            
        except Exception as e:
            print(f"  ❌ 실패: {e}")
    
    print("\n" + "=" * 70)
    print("✅ 완료! 이제 브라우저에서 강력 새로고침 (Ctrl+Shift+R)하세요!")
    print("=" * 70)

if __name__ == "__main__":
    main()
