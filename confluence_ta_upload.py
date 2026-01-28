#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Confluence Wiki 생성 - T&A 입점 상품 검수
"""

import os
import sys
import io
import requests

# UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
TARGET_PAGE_ID = "1193836635"  # CD space

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

def upload_attachment(url, email, api_token, page_id, file_path):
    """첨부파일 업로드"""
    endpoint = f"{url}/wiki/rest/api/content/{page_id}/child/attachment"
    
    # 기존 첨부파일 확인
    response = requests.get(endpoint, auth=(email, api_token))
    existing_attachments = response.json().get("results", [])
    
    file_name = os.path.basename(file_path)
    
    # 기존 첨부파일이 있으면 업데이트
    for attachment in existing_attachments:
        if attachment["title"] == file_name:
            attachment_id = attachment["id"]
            endpoint = f"{url}/wiki/rest/api/content/{page_id}/child/attachment/{attachment_id}/data"
            break
    
    # 파일 업로드
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

def generate_confluence_html(image_filename):
    """Confluence HTML 생성"""
    html = """
<h2>목차</h2>
<ac:structured-macro ac:name="toc" ac:schema-version="1">
  <ac:parameter ac:name="printable">true</ac:parameter>
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
  <ac:parameter ac:name="minLevel">1</ac:parameter>
</ac:structured-macro>

<hr />

<h2>🔗 참고 자료</h2>

<ul>
<li><strong>원본 페이지</strong>: <a href="https://mrtcx.atlassian.net/wiki/spaces/aoh/pages/791707659/T+A">T&amp;A 입점 상품 검수</a></li>
<li><strong>자동화툴 다운로드</strong>:
  <ul>
    <li><a href="https://aicx-partner-app-release.s3.ap-northeast-2.amazonaws.com/AICX+MANAGER-0.3.3-universal.dmg">AICX MANAGER v0.3.3 (macOS)</a></li>
    <li><a href="https://aicx-partner-app-release.s3.ap-northeast-2.amazonaws.com/AICX+MANAGER+Setup+0.3.3.exe">AICX MANAGER v0.3.3 (Windows x64)</a></li>
  </ul>
</li>
<li><strong>매뉴얼 슬라이드</strong>: <a href="https://docs.google.com/presentation/d/1MaIVoXtc2Mrd-HL6kEzoyBTqMdNRrXgnkIFMIHMrzso/edit">구글 프레젠테이션</a></li>
<li><strong>검수 가이드라인 시트</strong>: <a href="https://docs.google.com/spreadsheets/d/1FjqymMxV8VPM5EWvUX9HkQZuFVkt-Ecz66vT9YJfxec/edit">구글 시트</a></li>
<li><strong>동의서 응답시트</strong>: <a href="https://docs.google.com/spreadsheets/d/1Aq1Wiotw7PFHgIkE6QBwWU4EnyzHuXbaFTwORZ7Syz8/edit">구글 시트</a></li>
</ul>

<hr />

<h2>📊 T&amp;A 입점 상품 검수 프로세스 플로우차트</h2>

<p>
<ac:image ac:width="1200">
<ri:attachment ri:filename="{}" />
</ac:image>
</p>
""".format(image_filename)
    
    return html

def main():
    print("=" * 60)
    print("Confluence Wiki 생성 - T&A 입점 상품 검수")
    print("=" * 60)
    
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n인증 정보가 없습니다.")
        return
    
    print(f"\n✓ 인증 정보 확인")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - 대상 페이지: {TARGET_PAGE_ID}")
    
    try:
        image_path = "mermaid_images/ta_inspection.png"
        
        # 1. 이미지 업로드
        print("\n[1/2] Mermaid 플로우차트 이미지 업로드...")
        upload_attachment(
            CONFLUENCE_URL,
            CONFLUENCE_EMAIL,
            CONFLUENCE_API_TOKEN,
            TARGET_PAGE_ID,
            image_path
        )
        print(f"  ✓ 이미지 업로드 완료: {os.path.basename(image_path)}")
        
        # 2. 페이지 업데이트
        print("\n[2/2] 페이지 업데이트...")
        page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, TARGET_PAGE_ID)
        current_version = page["version"]["number"]
        current_title = page["title"]
        
        html_content = generate_confluence_html(os.path.basename(image_path))
        
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
        print("✅ Confluence Wiki 생성 완료!")
        print("=" * 60)
        print(f"📄 페이지: {CONFLUENCE_URL}/wiki/spaces/CD/pages/{TARGET_PAGE_ID}")
        print(f"📊 버전: {current_version} → {result['version']['number']}")
        print(f"🖼️  플로우차트: {os.path.basename(image_path)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
