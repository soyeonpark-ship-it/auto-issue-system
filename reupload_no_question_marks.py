import os
import requests
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

# 업로드할 페이지와 이미지 매핑
uploads = [
    {"page_id": "1191707033", "image": "partner_inquiry_process.png", "name": "파트너 문의 처리"},
    {"page_id": "1193771247", "image": "LAFC_issue_process.png", "name": "LAFC 발권"},
    {"page_id": "1193803947", "image": "ta_partner_inspection.png", "name": "T&A 파트너 검수"},
    {"page_id": "1192394909", "image": "domestic_product_register.png", "name": "국내 상품 등록"},
    {"page_id": "1193803904", "image": "hanin_product_register.png", "name": "한인민박 상품 등록"},
    {"page_id": "1193836635", "image": "ta_inspection.png", "name": "T&A 입점 상품 검수"},
    {"page_id": "1191477354", "image": "monitoring_flowchart.png", "name": "연동 예약 모니터링"}
]

class ConfluenceUploader:
    def __init__(self, url, email, api_token):
        self.url = url
        self.auth = (email, api_token)
        
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

def main():
    print("=" * 60)
    print("물음표 제거된 이미지 재업로드")
    print("=" * 60)
    
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n인증 정보가 없습니다.")
        return
    
    uploader = ConfluenceUploader(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
    
    for item in uploads:
        page_id = item["page_id"]
        image_file = item["image"]
        name = item["name"]
        image_path = Path("mermaid_images") / image_file
        
        print(f"\n[{name}] 업로드 중...")
        print(f"  페이지 ID: {page_id}")
        print(f"  이미지: {image_file}")
        
        try:
            if image_path.exists():
                uploader.upload_attachment(page_id, str(image_path), image_file)
                print(f"  완료!")
            else:
                print(f"  이미지 파일 없음: {image_path}")
        except Exception as e:
            print(f"  실패: {e}")
    
    print("\n" + "=" * 60)
    print("모든 이미지 재업로드 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()
