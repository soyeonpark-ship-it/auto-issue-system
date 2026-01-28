#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Confluence 페이지 복사 스크립트
원본 페이지의 내용과 Mermaid 다이어그램을 대상 페이지로 복사
"""

import os
import sys
import io
import requests
import base64
import re
from pathlib import Path

# UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Confluence 설정
CONFLUENCE_URL = "https://mrtcx.atlassian.net"
SOURCE_PAGE_ID = "780861470"  # 원본 페이지
TARGET_PAGE_ID = "1194000407"  # 대상 페이지

# 환경변수에서 인증 정보 가져오기
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

class ConfluenceClient:
    def __init__(self, url, email, api_token):
        self.url = url
        self.auth = (email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_page(self, page_id):
        """페이지 정보 가져오기"""
        endpoint = f"{self.url}/wiki/rest/api/content/{page_id}?expand=body.storage,version,space"
        response = requests.get(endpoint, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_attachments(self, page_id):
        """페이지의 첨부파일 목록 가져오기"""
        endpoint = f"{self.url}/wiki/rest/api/content/{page_id}/child/attachment?expand=version"
        response = requests.get(endpoint, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        return response.json().get("results", [])
    
    def download_attachment(self, download_url):
        """첨부파일 다운로드"""
        full_url = f"{self.url}{download_url}"
        response = requests.get(full_url, auth=self.auth)
        response.raise_for_status()
        return response.content
    
    def upload_attachment(self, page_id, file_name, file_content):
        """첨부파일 업로드"""
        endpoint = f"{self.url}/wiki/rest/api/content/{page_id}/child/attachment"
        
        # 기존 첨부파일 확인
        response = requests.get(endpoint, auth=self.auth)
        existing_attachments = response.json().get("results", [])
        
        # 기존 첨부파일이 있으면 업데이트, 없으면 새로 업로드
        for attachment in existing_attachments:
            if attachment["title"] == file_name:
                attachment_id = attachment["id"]
                endpoint = f"{self.url}/wiki/rest/api/content/{page_id}/child/attachment/{attachment_id}/data"
                break
        
        # 파일 업로드
        files = {'file': (file_name, file_content, 'image/png')}
        headers = {"X-Atlassian-Token": "no-check"}
        response = requests.post(
            endpoint,
            auth=self.auth,
            headers=headers,
            files=files
        )
        response.raise_for_status()
        return response.json()
    
    def update_page(self, page_id, title, content, version):
        """페이지 업데이트"""
        endpoint = f"{self.url}/wiki/rest/api/content/{page_id}"
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
            auth=self.auth,
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Confluence 페이지 복사 스크립트")
    print("=" * 60)
    
    # 1. 인증 정보 확인
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n❌ 인증 정보가 설정되지 않았습니다.")
        print("\n다음 환경변수를 설정하세요:")
        print("  PowerShell: $env:CONFLUENCE_EMAIL='your-email@example.com'")
        print("             $env:CONFLUENCE_API_TOKEN='your-api-token'")
        print("\nAPI 토큰 생성: https://id.atlassian.com/manage-profile/security/api-tokens")
        return
    
    print(f"\n✓ 인증 정보 확인 완료")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - 원본 페이지 ID: {SOURCE_PAGE_ID}")
    print(f"  - 대상 페이지 ID: {TARGET_PAGE_ID}")
    
    client = ConfluenceClient(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
    
    try:
        # 2. 원본 페이지 가져오기
        print("\n[1/4] 원본 페이지 가져오기...")
        source_page = client.get_page(SOURCE_PAGE_ID)
        source_title = source_page["title"]
        source_content = source_page["body"]["storage"]["value"]
        source_space = source_page["space"]["key"]
        print(f"  ✓ 페이지 제목: {source_title}")
        print(f"  ✓ Space: {source_space}")
        
        # 3. 원본 페이지의 첨부파일 가져오기
        print("\n[2/4] 첨부파일 다운로드 중...")
        source_attachments = client.get_attachments(SOURCE_PAGE_ID)
        print(f"  ✓ 첨부파일 {len(source_attachments)}개 발견")
        
        downloaded_attachments = []
        for attachment in source_attachments:
            file_name = attachment["title"]
            download_url = attachment["_links"]["download"]
            print(f"  - 다운로드 중: {file_name}")
            
            file_content = client.download_attachment(download_url)
            downloaded_attachments.append({
                "name": file_name,
                "content": file_content
            })
        
        # 4. 대상 페이지에 첨부파일 업로드
        print("\n[3/4] 대상 페이지에 첨부파일 업로드 중...")
        for attachment in downloaded_attachments:
            print(f"  - 업로드 중: {attachment['name']}")
            client.upload_attachment(
                TARGET_PAGE_ID,
                attachment['name'],
                attachment['content']
            )
        print(f"  ✓ {len(downloaded_attachments)}개 첨부파일 업로드 완료")
        
        # 5. 대상 페이지 업데이트
        print("\n[4/4] 대상 페이지 업데이트 중...")
        target_page = client.get_page(TARGET_PAGE_ID)
        target_version = target_page["version"]["number"]
        target_title = target_page["title"]
        
        # 원본 내용을 대상 페이지에 복사
        client.update_page(
            TARGET_PAGE_ID,
            target_title,  # 제목은 대상 페이지의 제목 유지
            source_content,  # 내용은 원본 페이지 내용 복사
            target_version
        )
        print(f"  ✓ 페이지 업데이트 완료")
        print(f"  ✓ 버전: {target_version} → {target_version + 1}")
        
        print("\n" + "=" * 60)
        print("✅ 모든 작업이 완료되었습니다!")
        print(f"📄 원본 페이지: {CONFLUENCE_URL}/wiki/spaces/{source_space}/pages/{SOURCE_PAGE_ID}")
        print(f"📄 대상 페이지: {CONFLUENCE_URL}/wiki/spaces/CD/pages/{TARGET_PAGE_ID}")
        print("=" * 60)
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP 오류 발생: {e}")
        if e.response is not None:
            print(f"상태 코드: {e.response.status_code}")
            print(f"응답: {e.response.text}")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
