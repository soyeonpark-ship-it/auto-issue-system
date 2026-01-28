#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Confluence 페이지 복사 스크립트
원본 페이지 → 대상 페이지로 내용 및 첨부파일 복사
"""

import os
import sys
import io
import requests
from pathlib import Path

# UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
SOURCE_PAGE_ID = "780861470"  # aoh space
TARGET_PAGE_ID = "1194000407"  # CD space

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

def get_attachments(url, email, api_token, page_id):
    """페이지의 첨부파일 목록 가져오기"""
    endpoint = f"{url}/wiki/rest/api/content/{page_id}/child/attachment?expand=version"
    response = requests.get(
        endpoint,
        auth=(email, api_token),
        headers={"Accept": "application/json"}
    )
    response.raise_for_status()
    return response.json().get("results", [])

def download_attachment(url, email, api_token, download_link):
    """첨부파일 다운로드"""
    full_url = f"{url}{download_link}"
    response = requests.get(
        full_url, 
        auth=(email, api_token),
        headers={"Accept": "application/octet-stream"}
    )
    response.raise_for_status()
    return response.content

def upload_attachment(url, email, api_token, page_id, file_name, file_content):
    """첨부파일 업로드"""
    endpoint = f"{url}/wiki/rest/api/content/{page_id}/child/attachment"
    
    # 기존 첨부파일 확인
    response = requests.get(endpoint, auth=(email, api_token))
    existing_attachments = response.json().get("results", [])
    
    # 기존 첨부파일이 있으면 업데이트
    for attachment in existing_attachments:
        if attachment["title"] == file_name:
            attachment_id = attachment["id"]
            endpoint = f"{url}/wiki/rest/api/content/{page_id}/child/attachment/{attachment_id}/data"
            break
    
    # 파일 업로드
    files = {'file': (file_name, file_content, 'image/png')}
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

def main():
    print("=" * 60)
    print("Confluence 페이지 복사")
    print("=" * 60)
    
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n인증 정보가 없습니다.")
        print("환경 변수를 설정하세요:")
        print("  $env:CONFLUENCE_EMAIL='your-email'")
        print("  $env:CONFLUENCE_API_TOKEN='your-token'")
        return
    
    print(f"\n✓ 인증 정보 확인")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - 원본: {SOURCE_PAGE_ID}")
    print(f"  - 대상: {TARGET_PAGE_ID}")
    
    try:
        # 1. 원본 페이지 가져오기
        print("\n[1/4] 원본 페이지 가져오기...")
        source_page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, SOURCE_PAGE_ID)
        source_title = source_page["title"]
        source_content = source_page["body"]["storage"]["value"]
        source_space = source_page["space"]["key"]
        print(f"  ✓ 제목: {source_title}")
        print(f"  ✓ Space: {source_space}")
        
        # 2. 첨부파일 다운로드 (선택적)
        print("\n[2/4] 첨부파일 확인...")
        try:
            attachments = get_attachments(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, SOURCE_PAGE_ID)
            print(f"  ✓ 첨부파일: {len(attachments)}개")
            
            downloaded = []
            for att in attachments:
                file_name = att["title"]
                download_link = att["_links"]["download"]
                print(f"  - 다운로드 시도: {file_name}")
                
                try:
                    file_content = download_attachment(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, download_link)
                    downloaded.append({
                        "name": file_name,
                        "content": file_content
                    })
                    print(f"    ✓ 성공")
                except Exception as e:
                    print(f"    ⚠ 건너뜀: {str(e)[:50]}")
                    continue
        except Exception as e:
            print(f"  ⚠ 첨부파일 다운로드 실패, 계속 진행: {e}")
            downloaded = []
        
        # 3. 대상 페이지에 첨부파일 업로드 (있는 경우만)
        if downloaded:
            print("\n[3/4] 첨부파일 업로드...")
            for item in downloaded:
                print(f"  - 업로드: {item['name']}")
                try:
                    upload_attachment(
                        CONFLUENCE_URL,
                        CONFLUENCE_EMAIL,
                        CONFLUENCE_API_TOKEN,
                        TARGET_PAGE_ID,
                        item['name'],
                        item['content']
                    )
                    print(f"    ✓ 성공")
                except Exception as e:
                    print(f"    ⚠ 실패: {str(e)[:50]}")
            print(f"  ✓ {len(downloaded)}개 업로드 완료")
        else:
            print("\n[3/4] 첨부파일 없음, 건너뜀")
        
        # 4. 대상 페이지 업데이트
        print("\n[4/4] 페이지 업데이트...")
        target_page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, TARGET_PAGE_ID)
        target_version = target_page["version"]["number"]
        target_title = target_page["title"]
        target_space = target_page["space"]["key"]
        
        result = update_page(
            CONFLUENCE_URL,
            CONFLUENCE_EMAIL,
            CONFLUENCE_API_TOKEN,
            TARGET_PAGE_ID,
            target_title,  # 제목은 대상 페이지 제목 유지
            source_content,  # 내용은 원본 복사
            target_version
        )
        
        print("\n" + "=" * 60)
        print("✅ 복사 완료!")
        print(f"📄 원본: {CONFLUENCE_URL}/wiki/spaces/{source_space}/pages/{SOURCE_PAGE_ID}")
        print(f"📄 대상: {CONFLUENCE_URL}/wiki/spaces/{target_space}/pages/{TARGET_PAGE_ID}")
        print(f"📊 버전: {target_version} → {result['version']['number']}")
        print(f"🖼️  첨부파일: {len(downloaded)}개")
        print("=" * 60)
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP 오류: {e}")
        if e.response:
            print(f"응답: {e.response.text[:500]}")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
