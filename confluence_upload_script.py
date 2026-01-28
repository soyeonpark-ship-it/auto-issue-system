#!/usr/bin/env python3
"""
Confluence 자동 업로드 스크립트
- Mermaid 다이어그램을 이미지로 변환
- Confluence 페이지에 자동 업로드
"""

import os
import requests
import base64
from pathlib import Path
import subprocess
import json

# Confluence 설정
CONFLUENCE_URL = "https://mrtcx.atlassian.net"
PAGE_ID = "1177321493"

# 환경변수에서 인증 정보 가져오기
# 사용법: export CONFLUENCE_EMAIL="your-email@example.com"
#        export CONFLUENCE_API_TOKEN="your-api-token"
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

class ConfluenceUploader:
    def __init__(self, url, email, api_token):
        self.url = url
        self.auth = (email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_page(self, page_id):
        """페이지 정보 가져오기"""
        endpoint = f"{self.url}/wiki/rest/api/content/{page_id}?expand=body.storage,version"
        response = requests.get(endpoint, auth=self.auth, headers=self.headers)
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
    
    def upload_attachment(self, page_id, file_path):
        """이미지 첨부 파일 업로드"""
        endpoint = f"{self.url}/wiki/rest/api/content/{page_id}/child/attachment"
        
        # 기존 첨부파일 확인
        response = requests.get(endpoint, auth=self.auth)
        existing_attachments = response.json().get("results", [])
        
        file_name = os.path.basename(file_path)
        
        # 기존 첨부파일이 있으면 업데이트, 없으면 새로 업로드
        for attachment in existing_attachments:
            if attachment["title"] == file_name:
                # 업데이트
                attachment_id = attachment["id"]
                endpoint = f"{self.url}/wiki/rest/api/content/{page_id}/child/attachment/{attachment_id}/data"
                break
        
        # 파일 업로드
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f, 'image/png')}
            headers = {"X-Atlassian-Token": "no-check"}
            response = requests.post(
                endpoint,
                auth=self.auth,
                headers=headers,
                files=files
            )
            response.raise_for_status()
            return response.json()


def generate_mermaid_images(input_dir="공급사별_반려_처리", output_dir="mermaid_images"):
    """Mermaid 파일을 이미지로 변환"""
    os.makedirs(output_dir, exist_ok=True)
    
    mermaid_files = []
    
    # .md 파일에서 Mermaid 코드 추출
    for md_file in Path(input_dir).glob("*.md"):
        if md_file.name == "README.md":
            continue
        
        print(f"처리 중: {md_file.name}")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Mermaid 코드 추출
        if "```mermaid" in content:
            start = content.find("```mermaid") + len("```mermaid")
            end = content.find("```", start)
            mermaid_code = content[start:end].strip()
            
            # .mmd 파일로 저장
            base_name = md_file.stem
            mmd_file = Path(output_dir) / f"{base_name}.mmd"
            png_file = Path(output_dir) / f"{base_name}.png"
            
            with open(mmd_file, 'w', encoding='utf-8') as f:
                f.write(mermaid_code)
            
            # Mermaid CLI로 이미지 생성
            try:
                subprocess.run([
                    "npx", "@mermaid-js/mermaid-cli@latest",
                    "-i", str(mmd_file),
                    "-o", str(png_file),
                    "-b", "transparent"
                ], check=True)
                
                mermaid_files.append({
                    "title": base_name,
                    "mmd_file": str(mmd_file),
                    "png_file": str(png_file)
                })
                print(f"  ✓ 이미지 생성: {png_file}")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ 이미지 생성 실패: {e}")
    
    return mermaid_files


def generate_confluence_content(mermaid_files):
    """Confluence HTML 컨텐츠 생성"""
    html = """
<h1>공급사별 반려 처리 프로세스맵</h1>

<ac:structured-macro ac:name="info">
<ac:rich-text-body>
<p>이 페이지는 자동으로 생성되었습니다. 각 공급사별 상세 처리 방법은 개별 파일을 참조하세요.</p>
</ac:rich-text-body>
</ac:structured-macro>

<h2>목차</h2>
<p><ac:structured-macro ac:name="toc" /></p>

"""
    
    # 공급사별 섹션 추가
    for item in mermaid_files:
        title = item["title"].replace("_반려처리", "")
        html += f"""
<h2>{title}</h2>
<ac:image>
<ri:attachment ri:filename="{os.path.basename(item['png_file'])}" />
</ac:image>

<p><a href="공급사별_반려_처리/{item['title']}.md">📄 상세 처리 방법 보기</a></p>
<hr />

"""
    
    return html


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Confluence 자동 업로드 스크립트")
    print("=" * 60)
    
    # 1. 인증 정보 확인
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n❌ 인증 정보가 설정되지 않았습니다.")
        print("\n다음 환경변수를 설정하세요:")
        print("  export CONFLUENCE_EMAIL='your-email@example.com'")
        print("  export CONFLUENCE_API_TOKEN='your-api-token'")
        print("\nAPI 토큰 생성: https://id.atlassian.com/manage-profile/security/api-tokens")
        return
    
    print(f"\n✓ 인증 정보 확인 완료")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - Page ID: {PAGE_ID}")
    
    # 2. Mermaid 이미지 생성
    print("\n[1/3] Mermaid 다이어그램을 이미지로 변환 중...")
    mermaid_files = generate_mermaid_images()
    print(f"  ✓ {len(mermaid_files)}개 이미지 생성 완료")
    
    # 3. Confluence 업로드
    print("\n[2/3] Confluence에 업로드 중...")
    uploader = ConfluenceUploader(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
    
    try:
        # 페이지 정보 가져오기
        page = uploader.get_page(PAGE_ID)
        current_version = page["version"]["number"]
        title = page["title"]
        print(f"  ✓ 페이지 정보 가져오기 완료 (버전: {current_version})")
        
        # 이미지 업로드
        for item in mermaid_files:
            png_file = item["png_file"]
            print(f"  - 업로드 중: {os.path.basename(png_file)}")
            uploader.upload_attachment(PAGE_ID, png_file)
        print(f"  ✓ {len(mermaid_files)}개 이미지 업로드 완료")
        
        # 3. 페이지 업데이트
        print("\n[3/3] 페이지 업데이트 중...")
        new_content = generate_confluence_content(mermaid_files)
        uploader.update_page(PAGE_ID, title, new_content, current_version)
        print(f"  ✓ 페이지 업데이트 완료")
        
        print("\n" + "=" * 60)
        print("✅ 모든 작업이 완료되었습니다!")
        print(f"📄 페이지 확인: {CONFLUENCE_URL}/wiki/spaces/aoh/pages/{PAGE_ID}")
        print("=" * 60)
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ 오류 발생: {e}")
        print(f"응답: {e.response.text}")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()
