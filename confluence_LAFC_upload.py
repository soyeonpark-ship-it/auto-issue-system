import os
import requests
import base64
from pathlib import Path
import json

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
TARGET_PAGE_ID = "1193771247"
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
IMAGE_FOLDER = "mermaid_images"
IMAGE_FILENAME = "LAFC_issue_process.png"

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

def generate_confluence_html_with_image(image_filename, original_title, source_url):
    """Mermaid 이미지를 포함한 Confluence HTML 컨텐츠 생성"""
    html = f"""
    <h1>{original_title}</h1>

    <ac:structured-macro ac:name="toc" ac:schema-version="1">
      <ac:parameter ac:name="printable">true</ac:parameter>
      <ac:parameter ac:name="maxLevel">3</ac:parameter>
      <ac:parameter ac:name="minLevel">1</ac:parameter>
    </ac:structured-macro>

    <hr />

    <h2>참고 자료</h2>
    <ul>
    <li><a href="{source_url}">원본 페이지: {original_title}</a></li>
    <li><a href="https://docs.google.com/spreadsheets/d/1-ni8SI0_6r16tS2QwAc5X-dY_MeKdXDJT3AJgkqWcFk/edit?gid=766782155#gid=766782155">B2B 발권 시트 - 파트너사 전용</a></li>
    <li><a href="https://docs.google.com/spreadsheets/d/1-ni8SI0_6r16tS2QwAc5X-dY_MeKdXDJT3AJgkqWcFk/edit?gid=1107036574#gid=1107036574">B2C 발권 시트 - 일반 고객 전용</a></li>
    <li><a href="https://docs.google.com/presentation/d/1XF2OVRKjWk0dfqn1nIpC0VwyUCwFRL-zYBz2kzxwREw/edit?slide=id.p#slide=id.p">LAFC 수동발권 가이드</a></li>
    <li><a href="https://docs.google.com/spreadsheets/d/1dunk3lrSKQ-cMi1J8XF_B1eGUc7GOOHeGGqMiVn471E/edit?gid=1263566895#gid=1263566895">LAFC 수동발권 FAQ</a></li>
    <li><a href="https://drive.google.com/file/d/1l0faeBry1GxdRDACcwD0FiyPe8okCJYc/view?usp=drive_link">운영방식 시연 동영상</a></li>
    </ul>

    <hr />

    <h2>프로세스 플로우차트</h2>
    <p>
    <ac:image ac:width="1200">
    <ri:attachment ri:filename="{image_filename}" />
    </ac:image>
    </p>
    
    <hr />
    
    <h2>주요 정책</h2>
    <h3>기본 정책</h3>
    <ul>
    <li><strong>환불 불가</strong>: 확정 후 환불 불가</li>
    <li><strong>자리 배정</strong>: 발권 순서대로 자동 배정, 예외 요청/변경 불가
        <ul>
        <li>한 주문 내 수량은 연속 좌석 배정</li>
        <li>1장씩 따로 구매 시 연석 불가</li>
        </ul>
    </li>
    <li><strong>양도 가능</strong>: 고객끼리 양도 가능</li>
    </ul>
    
    <h3>운영 방식</h3>
    <ul>
    <li><strong>B2B</strong>: 파트너사에게 벌크 발권 → 파트너사가 고객에게 배부</li>
    <li><strong>B2C</strong>: 마리트가 고객에게 직접 발권</li>
    </ul>
    
    <h3>상태 흐름</h3>
    <p>예약접수 → 확정대기 → 확정완료 → 발권진행중 → 발권완료 → 티켓전달완료</p>
    
    <hr />
    
    <h2>주의사항</h2>
    <ol>
    <li><strong>B2B/B2C 시트 혼용 금지</strong></li>
    <li><strong>확정 후 환불/변경 불가</strong> - 사전 안내 필수</li>
    <li><strong>발권 순서 엄수</strong> - 접수 순서대로 처리</li>
    <li><strong>정보 정확성</strong> - 오류 시 재발권 불가</li>
    </ol>
    
    <h2>담당자 정보</h2>
    <ul>
    <li><strong>상품 관련</strong>: 미주태평양팀 김정환, 노경현, 이유진(APOC)</li>
    <li><strong>직사입 재고 관련</strong>: 커머스팀 조유진</li>
    </ul>
    """
    return html

def main():
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print(f"Confluence Wiki 생성 - LAFC 발권 프로세스")
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
        original_title = "LAFC 발권 프로세스"
        source_url = "https://mrtcx.atlassian.net/wiki/spaces/aoh/pages/1163952204/LAFC"

        html_content = generate_confluence_html_with_image(IMAGE_FILENAME, original_title, source_url)

        result = uploader.update_page(
            TARGET_PAGE_ID,
            original_title,
            html_content,
            current_version
        )

        print("\n" + "=" * 60)
        print("Confluence Wiki 생성 완료!")
        print("=" * 60)
        print(f"페이지: {CONFLUENCE_URL}/wiki/spaces/CD/pages/{TARGET_PAGE_ID}")
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
