#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공급사별 반려 처리 플로우 페이지 - 이미지 크기 통일
"""

import os
import sys
import io
import requests

# UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
TARGET_PAGE_ID = "1177321493"

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

def generate_confluence_html():
    """Confluence HTML 생성 - 모든 이미지 width를 1200으로 통일"""
    
    suppliers = [
        ("트립닷컴", "트립닷컴.png"),
        ("JTR", "JTR.png"),
        ("KLOOK", "KLOOK.png"),
        ("링크티비티", "링크티비티.png"),
        ("레일유럽", "레일유럽.png"),
        ("BMG", "BMG.png"),
        ("GYG", "GYG.png"),
        ("VIATOR", "VIATOR.png"),
        ("TIQETS", "TIQETS.png"),
        ("USH", "USH.png"),
        ("LA디즈니랜드", "LA디즈니랜드.png"),
        ("몽키트레블", "몽키트레블.png"),
        ("KKDAY", "KKDAY.png")
    ]
    
    html = """
<h2>목차</h2>
<ac:structured-macro ac:name="toc" ac:schema-version="1">
  <ac:parameter ac:name="printable">true</ac:parameter>
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
  <ac:parameter ac:name="minLevel">1</ac:parameter>
</ac:structured-macro>

<hr />
<hr />

<h2>반려시트 확인</h2>

<p><strong>반려 알럿 수신 시 가장 먼저 확인해야 할 사항:</strong></p>

<ol>
<li>반려시트 접속</li>
<li>해당 예약 번호 검색</li>
<li>공급사 확인</li>
<li>반려 사유 확인</li>
<li>아래 공급사별 프로세스 플로우차트 참고</li>
</ol>

<hr />

<h2>참고 자료</h2>

<ul>
<li><a href="https://docs.google.com/spreadsheets/d/16c0vj5gC7gkYyi8bU_qfdBwqQxmqfMwe1wiGGCC78zw/edit#gid=0">반려 처리 시트</a></li>
<li><a href="https://docs.google.com/spreadsheets/d/1aRMZdr7tLbCqptVe8f5XRGUViRoUriXoPIgrBbNzlCI/edit?pli=1&amp;gid=802671048#gid=802671048">공급사 어드민 계정 정보</a></li>
<li><a href="https://aicx-kr.slack.com/archives/C02D5KZLM1Q">모니터링 슬랙 채널</a></li>
</ul>

<hr />

<h2>프로세스 플로우차트</h2>

"""
    
    # 각 공급사별 이미지 추가 (width를 1200으로 통일)
    for supplier_name, image_filename in suppliers:
        html += f"""
<h3>{supplier_name}</h3>
<ac:image ac:width="1200">
<ri:attachment ri:filename="{image_filename}" />
</ac:image>

<hr />

"""
    
    return html

def main():
    print("=" * 60)
    print("Confluence Wiki 업데이트 - 공급사별 반려 처리 플로우")
    print("=" * 60)
    
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n인증 정보가 없습니다.")
        return
    
    print(f"\n✓ 인증 정보 확인")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - 대상 페이지: {TARGET_PAGE_ID}")
    
    try:
        print("\n[1/1] 페이지 업데이트 (이미지 크기 통일: 800px → 1200px)...")
        page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, TARGET_PAGE_ID)
        current_version = page["version"]["number"]
        current_title = page["title"]
        
        html_content = generate_confluence_html()
        
        result = update_page(
            CONFLUENCE_URL,
            CONFLUENCE_EMAIL,
            CONFLUENCE_API_TOKEN,
            TARGET_PAGE_ID,
            current_title,
            html_content,
            current_version
        )
        
        print("\n" + "=" * 60)
        print("✅ Confluence Wiki 업데이트 완료!")
        print("=" * 60)
        print(f"📄 페이지: {CONFLUENCE_URL}/wiki/spaces/CD/pages/{TARGET_PAGE_ID}")
        print(f"📊 버전: {current_version} → {result['version']['number']}")
        print(f"🖼️  이미지 개수: 13개 (모두 1200px width로 통일)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
