#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Confluence Wiki 생성 - Mermaid 플로우차트 포함
"""

import os
import sys
import io
import requests
import re
import base64
import urllib.parse

# UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
TARGET_PAGE_ID = "1194000407"  # CD space

CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

def extract_mermaid(md_file):
    """마크다운에서 Mermaid 코드 추출"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def mermaid_to_image_url(mermaid_code):
    """Mermaid 코드를 mermaid.ink 이미지 URL로 변환"""
    # JSON 형식으로 감싸기
    mermaid_json = {
        "code": mermaid_code,
        "mermaid": {"theme": "default"}
    }
    
    import json
    json_str = json.dumps(mermaid_json)
    
    # Base64 인코딩
    encoded = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    # URL 생성
    return f"https://mermaid.ink/img/{encoded}"

def download_image(url, output_path):
    """이미지 다운로드"""
    response = requests.get(url)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    return output_path

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

<h2>📊 프로세스 플로우차트</h2>

<p>
<ac:image ac:width="1000">
<ri:attachment ri:filename="{}" />
</ac:image>
</p>

<hr />

<h2>🔗 참고 자료</h2>
<ul>
<li><strong>3.0 이관 공급사</strong> (2025-12-09 기준): KKDAY, 몽키트래블_태국 &amp; 베트남</li>
<li><strong>공급사 상품 페이지</strong>: Sanctum에서 바로 진입 가능</li>
</ul>

<hr />

<h2>📋 주요 단계 요약</h2>

<h3>1단계: 매니저 접근</h3>
<ul>
<li>T&amp;A 연동 상품 메뉴에서 공급사 선택</li>
</ul>

<h3>2단계: 공급사 상품 가져오기</h3>
<ul>
<li>원본 ID 입력 (1개 또는 여러개)</li>
<li>중복 체크</li>
</ul>

<h3>3단계: 마리트 상품 생성</h3>
<ul>
<li>표준 카테고리 필수 선택</li>
</ul>

<h3>4단계: 상품 상세 정보 입력</h3>
<ul>
<li>대표도시, 상품명, 상품사진 (최소 4장)</li>
<li>상품 소개, 이동수단, 소요시간</li>
<li>만나는 장소, 포함/불포함 사항</li>
</ul>

<h3>5단계: 심사 요청</h3>
<ul>
<li>버튼 상태에 따라 절차 다름</li>
</ul>

<h3>6단계: 매니저 최종 설정</h3>
<ul>
<li>예약 정보 설정</li>
<li>취소/환불 정보 수정</li>
</ul>

<h3>7단계: 공급사별 처리</h3>
<ul>
<li><strong>KKDAY</strong>: 대표가 등록 필요 → 슬랙 노티</li>
<li><strong>KLOOK</strong>: 판매가 정책 없이 바로 진행</li>
<li><strong>기타</strong>: 일반 심사 요청</li>
</ul>

<h3>8단계: 판매 시작</h3>
<ul>
<li>판매 시작 버튼 클릭</li>
</ul>
""".format(image_filename)
    
    return html

def main():
    print("=" * 60)
    print("Confluence Wiki 생성 - Mermaid 플로우차트")
    print("=" * 60)
    
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n인증 정보가 없습니다.")
        return
    
    print(f"\n✓ 인증 정보 확인")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - 대상 페이지: {TARGET_PAGE_ID}")
    
    try:
        # 1. Mermaid 코드 추출
        print("\n[1/5] Mermaid 코드 추출...")
        md_file = "연동_신규_상품_등록_3.0/연동_신규_상품_등록_3.0_플로우차트.md"
        mermaid_code = extract_mermaid(md_file)
        if not mermaid_code:
            print("  ✗ Mermaid 코드를 찾을 수 없습니다")
            return
        print(f"  ✓ Mermaid 코드 추출 완료 ({len(mermaid_code)} chars)")
        
        # 2. 이미지 URL 생성
        print("\n[2/5] 이미지 URL 생성...")
        image_url = mermaid_to_image_url(mermaid_code)
        print(f"  ✓ URL: {image_url[:80]}...")
        
        # 3. 이미지 다운로드
        print("\n[3/5] 이미지 다운로드...")
        os.makedirs("mermaid_images", exist_ok=True)
        image_path = "mermaid_images/연동_신규_상품_등록_3.0_플로우차트.png"
        download_image(image_url, image_path)
        print(f"  ✓ 이미지 저장: {image_path}")
        
        # 4. Confluence에 이미지 업로드
        print("\n[4/5] Confluence에 이미지 업로드...")
        upload_attachment(
            CONFLUENCE_URL,
            CONFLUENCE_EMAIL,
            CONFLUENCE_API_TOKEN,
            TARGET_PAGE_ID,
            image_path
        )
        print(f"  ✓ 이미지 업로드 완료")
        
        # 5. 페이지 업데이트
        print("\n[5/5] 페이지 업데이트...")
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
        print(f"🖼️  이미지: 1개")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
