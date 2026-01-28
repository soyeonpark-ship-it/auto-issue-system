import os
import requests
import json
import base64
from urllib.parse import urlparse, parse_qs

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

def get_page_id_from_url(url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split('/')
    try:
        for segment in reversed(path_segments):
            if segment.isdigit():
                return segment
        if 'pages' in path_segments:
            idx = path_segments.index('pages')
            if idx + 1 < len(path_segments):
                if path_segments[idx+1].isdigit():
                    return path_segments[idx+1]
    except ValueError:
        pass
    return None

def get_page_content(url, email, api_token, page_id):
    endpoint = f"{url}/wiki/rest/api/content/{page_id}?expand=body.storage,version,space"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {base64.b64encode(f'{email}:{api_token}'.encode()).decode()}"
    }
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    source_page_url = "https://mrtcx.atlassian.net/wiki/spaces/aoh/pages/1163952204/LAFC"
    source_page_id = get_page_id_from_url(source_page_url)
    
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("인증 정보가 없습니다. 환경 변수를 설정하세요.")
        return
    
    print(f"원본 페이지 가져오는 중... (ID: {source_page_id})")
    try:
        page_data = get_page_content(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, source_page_id)
        title = page_data['title']
        space_key = page_data['space']['key']
        content_html = page_data['body']['storage']['value']
        
        print(f"제목: {title}")
        print(f"Space: {space_key}")
        
        print("\n페이지 내용을 저장합니다...")
        with open(f"confluence_source_{source_page_id}.json", "w", encoding="utf-8") as f:
            json.dump(page_data, f, ensure_ascii=False, indent=2)
        print(f"confluence_source_{source_page_id}.json 저장 완료")
        
        with open(f"confluence_source_{source_page_id}.html", "w", encoding="utf-8") as f:
            f.write(content_html)
        print(f"confluence_source_{source_page_id}.html 저장 완료")
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 오류: {e}")
        if e.response:
            print(f"응답: {e.response.text[:500]}")
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    main()
