import os
import requests
import base64
from pathlib import Path
import json

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
TARGET_PAGE_ID = "1192395072"
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
IMAGE_FOLDER = "mermaid_images"
IMAGE_FILENAME = "domestic_hotel_update.png"

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

    def upload_attachment(self, page_id, file_path, filename):
        """이미지 첨부 파일 업로드"""
        endpoint = f"{self.url}/wiki/rest/api/content/{page_id}/child/attachment"

        response = requests.get(endpoint, auth=self.auth)
        existing_attachments = response.json().get("results", [])

        attachment_id = None
        for attachment in existing_attachments:
            if attachment["title"] == filename:
                attachment_id = attachment["id"]
                break

        if attachment_id:
            upload_endpoint = f"{self.url}/wiki/rest/api/content/{page_id}/child/attachment/{attachment_id}/data"
        else:
            upload_endpoint = f"{self.url}/wiki/rest/api/content/{page_id}/child/attachment"

        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'image/png')}
            headers = {"X-Atlassian-Token": "no-check"}
            response = requests.post(
                upload_endpoint,
                auth=self.auth,
                headers=headers,
                files=files
            )
            response.raise_for_status()
            return response.json()

def generate_confluence_html_with_image(image_filename):
    """Mermaid 이미지를 포함한 Confluence HTML 컨텐츠 생성"""
    html = f"""
    <h1>국내 호텔 정보 수정 프로세스</h1>

    <ac:structured-macro ac:name="toc" ac:schema-version="1">
      <ac:parameter ac:name="printable">true</ac:parameter>
      <ac:parameter ac:name="maxLevel">3</ac:parameter>
      <ac:parameter ac:name="minLevel">1</ac:parameter>
    </ac:structured-macro>

    <hr />

    <h2>프로세스 플로우차트</h2>
    <p>
    <ac:image ac:width="1200">
    <ri:attachment ri:filename="{image_filename}" />
    </ac:image>
    </p>
    
    <hr />
    
    <h2>주요 단계</h2>
    
    <h3>1. Stay실 국내사업팀 - 기술서 작성 (1단계)</h3>
    <ul>
    <li><strong>숙소 정보 시트 작성</strong>: 기술서 작성</li>
    </ul>
    
    <h3>2. AICX - 정보 등록 (2단계)</h3>
    <ul>
    <li><strong>옵션 정보 등록</strong>: 숙소 정보 시트에 적힌 옵션 정보 등록</li>
    <li><strong>나머지 정보는 호텔이 CMS로 설정</strong>:
        <ul>
        <li>객실</li>
        <li>재고</li>
        <li>요금</li>
        <li>기간</li>
        </ul>
    </li>
    </ul>
    
    <h4>예외: 아트파라디소 호텔</h4>
    <ul>
    <li><strong>AICX가 위탁관리하는 호텔</strong></li>
    <li><strong>모든 정보를 AICX가 직접 입력</strong></li>
    <li><strong>CMS 사용 안 함</strong></li>
    </ul>
    
    <h3>3. AICX - 작업 완료 회신 (3단계)</h3>
    <ul>
    <li><strong>젠데스크 티켓으로 국내사업팀에게 완료 회신</strong></li>
    </ul>
    
    <h3>4. AICX - 호텔 메일 발송 (4단계)</h3>
    <ul>
    <li><strong>호텔에 메일로 등록 작업 완료 발송</strong></li>
    </ul>
    
    <hr />
    
    <h2>주요 시스템</h2>
    <ul>
    <li><strong>숙소 정보 시트 (기술서)</strong>: 호텔 정보 및 옵션 정보</li>
    <li><strong>젠데스크</strong>: 티켓 관리 시스템</li>
    <li><strong>CMS</strong>: 채널 매니저 시스템 (호텔이 객실/재고/요금/기간 설정)</li>
    <li><strong>파트너 페이지</strong>: 파트너용 상품 관리 페이지</li>
    </ul>
    
    <hr />
    
    <h2>일반 호텔 vs 아트파라디소</h2>
    <table>
    <thead>
    <tr>
    <th>구분</th>
    <th>일반 호텔</th>
    <th>아트파라디소</th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td>옵션 정보</td>
    <td>AICX 등록</td>
    <td>AICX 등록</td>
    </tr>
    <tr>
    <td>객실/재고/요금/기간</td>
    <td>호텔이 CMS로 설정</td>
    <td>AICX가 직접 입력</td>
    </tr>
    <tr>
    <td>CMS 사용 여부</td>
    <td>사용</td>
    <td>미사용</td>
    </tr>
    <tr>
    <td>관리 주체</td>
    <td>호텔 자체 관리</td>
    <td>AICX 위탁관리</td>
    </tr>
    </tbody>
    </table>
    
    <hr />
    
    <h2>프로세스 흐름</h2>
    <p>숙소정보작성 → 옵션정보등록 → 작업완료회신 → 호텔메일발송 → 완료</p>
    """
    return html

def main():
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print(f"Confluence Wiki 생성 - 국내 호텔 정보 수정")
    print("=" * 60)

    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n인증 정보가 없습니다.")
        return

    print(f"\n인증 정보 확인")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - 대상 페이지: {TARGET_PAGE_ID}")

    uploader = ConfluenceUploader(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
    image_path = Path(IMAGE_FOLDER) / IMAGE_FILENAME

    try:
        print("\n[1/2] Mermaid 플로우차트 이미지 업로드...")
        if image_path.exists():
            uploader.upload_attachment(TARGET_PAGE_ID, str(image_path), IMAGE_FILENAME)
            print(f"  이미지 업로드 완료: {IMAGE_FILENAME}")
        else:
            print(f"  이미지 파일이 없습니다: {image_path}")
            return

        print("\n[2/2] 페이지 업데이트...")
        page = uploader.get_page(TARGET_PAGE_ID)
        current_version = page["version"]["number"]
        original_title = page["title"]  # 기존 제목 유지

        html_content = generate_confluence_html_with_image(IMAGE_FILENAME)

        result = uploader.update_page(
            TARGET_PAGE_ID,
            original_title,  # 기존 제목 그대로 사용
            html_content,
            current_version
        )

        print("\n" + "=" * 60)
        print("Confluence Wiki 생성 완료!")
        print("=" * 60)
        print(f"페이지: {CONFLUENCE_URL}/wiki/spaces/CD/pages/{TARGET_PAGE_ID}")
        print(f"제목: {original_title}")
        print(f"버전: {current_version} → {result['version']['number']}")
        print(f"플로우차트: {IMAGE_FILENAME}")
        print("=" * 60)

    except requests.exceptions.HTTPError as e:
        print(f"\nHTTP 오류: {e}")
        if e.response:
            print(f"응답: {e.response.text[:500]}")
    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
