import os
import requests
import base64
from pathlib import Path
import json

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
TARGET_PAGE_ID = "1191707033"
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
IMAGE_FOLDER = "mermaid_images"
IMAGE_FILENAME = "partner_inquiry_process.png"

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
    <h1>파트너 문의 처리 프로세스</h1>

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
    
    <h2>주요 문의 유형</h2>
    
    <h3>1. 상품 정보 수정</h3>
    <ul>
    <li><strong>파트너 직접 수정 가능</strong>: 대표사진, 불포함사항, 기타 예약정보, 취소환불규정</li>
    <li><strong>예외 처리 필요</strong>: 예외 환불 규정 희망 시 PO 전달</li>
    </ul>
    
    <h3>2. 환불 요청</h3>
    <ul>
    <li>부분환불 요청</li>
    <li>전액환불 요청 (여행완료 건)</li>
    </ul>
    
    <h3>3. 양수양도</h3>
    <ul>
    <li>파트너 간 권리 이전 처리</li>
    </ul>
    
    <h3>4. 정보 변경</h3>
    <ul>
    <li>계좌 변경 요청</li>
    <li>각종 정보 변경 요청</li>
    <li><strong>주의</strong>: 사업자 주소 변경 불가</li>
    </ul>
    
    <h3>5. 상품 페이지</h3>
    <ul>
    <li>파트너 정보 노출 관련</li>
    <li>상품 페이지 수정 요청</li>
    </ul>
    
    <h3>6. 시스템 관련</h3>
    <ul>
    <li>시스템 오류 확인</li>
    <li>개발팀 또는 관련팀 전달</li>
    </ul>
    
    <h3>7. 상품 노출 관련</h3>
    <ul>
    <li>상품 노출 상태 확인</li>
    <li>노출 설정 조정</li>
    </ul>
    
    <h3>8. AI 후기 요약</h3>
    <ul>
    <li>AI 후기 요약 이슈</li>
    <li><strong>현재</strong>: 고도화 미완료로 삭제 처리</li>
    </ul>
    
    <h3>9. 핑퐁 케이스</h3>
    <ul>
    <li>추가 정보 요청</li>
    <li>파트너 응답 대기</li>
    <li>재확인 및 처리</li>
    </ul>
    
    <h3>10. 타 부서 전달</h3>
    <ul>
    <li><strong>정산 관련</strong>: 매출관리팀, 자금팀</li>
    <li><strong>사업실</strong></li>
    <li><strong>서비스운영실</strong></li>
    <li><strong>담당 PO</strong></li>
    </ul>
    
    <hr />
    
    <h2>문의 유입 경로</h2>
    
    <h3>이메일</h3>
    <ul>
    <li>guide@myrealtrip.com 으로 접수</li>
    <li>젠데스크 티켓 자동 생성</li>
    </ul>
    
    <h3>홈페이지</h3>
    <ul>
    <li>마리트 홈페이지 문의하기</li>
    <li>젠데스크 티켓 자동 생성</li>
    </ul>
    
    <hr />
    
    <h2>티켓 형식</h2>
    <ul>
    <li><strong>메일 형식</strong>: 일반 이메일 스레드</li>
    <li><strong>메시징 형식</strong>: 채팅 형태의 대화</li>
    </ul>
    
    <hr />
    
    <h2>처리 흐름</h2>
    <p>문의 유입 → 젠데스크 티켓 생성 → 파트너지원 처리중 → 유형 분류 → 처리 → 완료</p>
    """
    return html

def main():
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print(f"Confluence Wiki 생성 - 파트너 문의 처리 프로세스")
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
        original_title = "파트너 문의 처리 프로세스"

        html_content = generate_confluence_html_with_image(IMAGE_FILENAME)

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
