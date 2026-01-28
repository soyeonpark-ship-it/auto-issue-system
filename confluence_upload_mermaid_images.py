#!/usr/bin/env python3
"""
Confluence 업로드 - Mermaid를 온라인 서비스로 이미지 변환 후 업로드
"""

import os
import requests
import re
import base64
from pathlib import Path
import time

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
PAGE_ID = "1177321493"  # 공급사별 반려 처리 페이지 ID
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

# Mermaid 온라인 렌더링 서비스
MERMAID_INK_URL = "https://mermaid.ink/img/"

def extract_mermaid(md_file):
    """마크다운 파일에서 Mermaid 코드 추출"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def mermaid_to_image_url(mermaid_code):
    """Mermaid 코드를 mermaid.ink 이미지 URL로 변환"""
    # Base64 인코딩
    encoded = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
    return f"{MERMAID_INK_URL}{encoded}"

def download_image(url, filename):
    """이미지 다운로드"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        os.makedirs("mermaid_images", exist_ok=True)
        filepath = f"mermaid_images/{filename}.png"
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filepath
    except Exception as e:
        print(f"  [ERROR] Image download failed: {e}")
        return None

def get_all_diagrams(input_dir="공급사별_반려_처리"):
    """모든 다이어그램 추출 및 이미지 생성"""
    diagrams = []
    
    files = [
        "트립닷컴_반려처리.md",
        "JTR_반려처리.md",
        "KLOOK_반려처리.md",
        "링크티비티_반려처리.md",
        "레일유럽_반려처리.md",
        "BMG_반려처리.md",
        "GYG_반려처리.md",
        "VIATOR_반려처리.md",
        "TIQETS_반려처리.md",
        "USH_반려처리.md",
        "LA디즈니랜드_반려처리.md",
        "몽키트레블_반려처리.md",
        "KKDAY_반려처리.md"
    ]
    
    print("\n[1/4] Mermaid 다이어그램 추출 및 이미지 생성 중...")
    
    for filename in files:
        filepath = Path(input_dir) / filename
        if filepath.exists():
            mermaid_code = extract_mermaid(filepath)
            if mermaid_code:
                title = filename.replace("_반려처리.md", "")
                print(f"  처리 중: {title}")
                
                # 온라인 서비스로 이미지 URL 생성
                image_url = mermaid_to_image_url(mermaid_code)
                
                # 이미지 다운로드
                image_path = download_image(image_url, title)
                
                if image_path:
                    diagrams.append({
                        "title": title,
                        "image_path": image_path,
                        "filename": f"{title}.png"
                    })
                    print(f"    [OK] Image created")
                
                time.sleep(0.5)  # API 제한 방지
    
    return diagrams

def upload_attachment(url, email, api_token, page_id, file_path, filename):
    """Confluence에 첨부파일 업로드"""
    endpoint = f"{url}/wiki/rest/api/content/{page_id}/child/attachment"
    
    # 기존 첨부파일 확인
    response = requests.get(endpoint, auth=(email, api_token))
    existing = response.json().get("results", [])
    
    # 같은 이름의 파일이 있으면 업데이트
    for att in existing:
        if att["title"] == filename:
            att_id = att["id"]
            endpoint = f"{url}/wiki/rest/api/content/{page_id}/child/attachment/{att_id}/data"
            break
    
    # 파일 업로드
    with open(file_path, 'rb') as f:
        files = {'file': (filename, f, 'image/png')}
        headers = {"X-Atlassian-Token": "no-check"}
        response = requests.post(
            endpoint,
            auth=(email, api_token),
            headers=headers,
            files=files
        )
        response.raise_for_status()
    
    return response.json()

def generate_confluence_html(diagrams):
    """Confluence HTML 생성 (이미지 첨부 방식)"""
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
<li><a href="https://docs.google.com/spreadsheets/d/16c0vj5gC7gkYyi8bU_qfdBwqQxmqfMwe1wiGGCC78zw/edit#gid=0">반려 처리 시트</a></li>
<li><a href="https://docs.google.com/spreadsheets/d/1aRMZdr7tLbCqptVe8f5XRGUViRoUriXoPIgrBbNzlCI/edit?pli=1&gid=802671048#gid=802671048">공급사 어드민 계정 정보</a></li>
<li><a href="https://aicx-kr.slack.com/archives/C02D5KZLM1Q">모니터링 슬랙 채널</a></li>
</ul>

<hr />

<h2>📊 프로세스 플로우차트</h2>
"""
    
    # 각 다이어그램 이미지 추가
    for diagram in diagrams:
        html += f"""
<h3>{diagram['title']}</h3>

<p>
<ac:image ac:width="800">
<ri:attachment ri:filename="{diagram['filename']}" />
</ac:image>
</p>

<hr />

"""
    
    return html

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

def main():
    print("=" * 60)
    print("Confluence upload - Mermaid image version")
    print("=" * 60)
    
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\nAuthentication info missing")
        return
    
    print(f"\n[OK] Authentication confirmed")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - Page ID: {PAGE_ID}")
    
    try:
        # 1. 다이어그램 추출 및 이미지 생성
        diagrams = get_all_diagrams()
        print(f"\n  [OK] {len(diagrams)} images generated")
        
        if not diagrams:
            print("\n[ERROR] No images generated")
            return
        
        # 2. 이미지 업로드
        print("\n[2/4] Uploading images to Confluence...")
        for diagram in diagrams:
            print(f"  Uploading: {diagram['title']}")
            upload_attachment(
                CONFLUENCE_URL,
                CONFLUENCE_EMAIL,
                CONFLUENCE_API_TOKEN,
                PAGE_ID,
                diagram['image_path'],
                diagram['filename']
            )
            print(f"    [OK] Done")
        
        print(f"\n  [OK] {len(diagrams)} images uploaded")
        
        # 3. HTML 생성
        print("\n[3/4] Generating Confluence HTML...")
        html_content = generate_confluence_html(diagrams)
        print(f"  [OK] HTML generated")
        
        # 4. 페이지 업데이트
        print("\n[4/4] Updating page...")
        page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, PAGE_ID)
        current_version = page["version"]["number"]
        current_title = page["title"]
        
        result = update_page(
            CONFLUENCE_URL,
            CONFLUENCE_EMAIL,
            CONFLUENCE_API_TOKEN,
            PAGE_ID,
            current_title,
            html_content,
            current_version
        )
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Upload completed!")
        print(f"Page: {CONFLUENCE_URL}/wiki/spaces/aoh/pages/{PAGE_ID}")
        print(f"Version: {current_version} -> {result['version']['number']}")
        print(f"Images: {len(diagrams)}")
        print("=" * 60)
        
    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] HTTP error: {e}")
        if e.response:
            print(f"Response: {e.response.text[:500]}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
