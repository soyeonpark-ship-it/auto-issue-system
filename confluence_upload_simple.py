#!/usr/bin/env python3
"""
Confluence 간단 업로드 스크립트 (Mermaid 이미지 변환 없이)
"""

import os
import requests
import json

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
PAGE_ID = "1177321493"
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

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
    print("Confluence 업로드 (간단 버전)")
    print("=" * 60)
    
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n인증 정보가 없습니다.")
        return
    
    print(f"\n인증 정보 확인 완료")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - Page ID: {PAGE_ID}")
    
    try:
        # 페이지 정보 가져오기
        print("\n페이지 정보 가져오는 중...")
        page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, PAGE_ID)
        current_version = page["version"]["number"]
        current_title = page["title"]
        print(f"  현재 버전: {current_version}")
        print(f"  제목: {current_title}")
        
        # Confluence HTML 컨텐츠 생성
        content = """
<h1>공급사별 반려 처리 가이드</h1>

<ac:structured-macro ac:name="info">
<ac:rich-text-body>
<p>이 페이지는 자동으로 생성되었습니다. 각 공급사별 상세 처리 방법을 확인하세요.</p>
</ac:rich-text-body>
</ac:structured-macro>

<h2>목차</h2>
<ac:structured-macro ac:name="toc" ac:schema-version="1">
  <ac:parameter ac:name="printable">true</ac:parameter>
  <ac:parameter ac:name="style">disc</ac:parameter>
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
  <ac:parameter ac:name="minLevel">1</ac:parameter>
  <ac:parameter ac:name="class">bigpanel</ac:parameter>
  <ac:parameter ac:name="exclude" />
  <ac:parameter ac:name="type">list</ac:parameter>
  <ac:parameter ac:name="outline">clear</ac:parameter>
  <ac:parameter ac:name="include" />
</ac:structured-macro>

<h2>📋 개요</h2>
<p>예약 취소 시 자동 연동이 실패하거나 수동 처리가 필요한 경우, 공급사별로 다른 확인 수단과 소통 방법을 통해 반려 처리를 진행합니다.</p>

<h2>🔗 참고 자료</h2>
<ul>
<li><a href="https://docs.google.com/spreadsheets/d/16c0vj5gC7gkYyi8bU_qfdBwqQxmqfMwe1wiGGCC78zw/edit#gid=0">반려 처리 시트</a></li>
<li><a href="https://docs.google.com/spreadsheets/d/1aRMZdr7tLbCqptVe8f5XRGUViRoUriXoPIgrBbNzlCI/edit?pli=1&gid=802671048#gid=802671048">공급사 어드민 및 이메일 계정 정보</a></li>
<li><a href="https://aicx-kr.slack.com/archives/C02D5KZLM1Q">모니터링_공급사연동_예약취소반려 슬랙 채널</a></li>
</ul>

<hr />

<h2>📚 공급사별 반려 처리 방법</h2>

<h3>이메일 기반 공급사</h3>
<table>
<thead>
<tr>
<th>공급사</th>
<th>확인 수단</th>
<th>소통 수단</th>
<th>주요 반려 사유</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>트립닷컴</strong></td>
<td>이메일</td>
<td>이메일</td>
<td>취소 환불 연동 실패</td>
</tr>
<tr>
<td><strong>GYG</strong></td>
<td>이메일</td>
<td>WHATSAPP</td>
<td>공급사 발 취소건 연동 실패</td>
</tr>
<tr>
<td><strong>VIATOR</strong></td>
<td>이메일</td>
<td>이메일</td>
<td>시스템 연동 오류</td>
</tr>
<tr>
<td><strong>TIQETS</strong></td>
<td>이메일</td>
<td>이메일</td>
<td>유효기간 확인 필요</td>
</tr>
</tbody>
</table>

<h3>어드민 기반 공급사</h3>
<table>
<thead>
<tr>
<th>공급사</th>
<th>확인 수단</th>
<th>소통 수단</th>
<th>주요 반려 사유</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>JTR</strong></td>
<td>어드민</td>
<td>위챗</td>
<td>공급사 발 취소 연동 불가, 유효기간 확인</td>
</tr>
<tr>
<td><strong>KLOOK</strong></td>
<td>어드민</td>
<td>이메일</td>
<td>취소 환불 자동 연동</td>
</tr>
<tr>
<td><strong>링크티비티</strong></td>
<td>어드민</td>
<td>이메일</td>
<td>미사용 확인, 수수료 공제 필요</td>
</tr>
<tr>
<td><strong>레일유럽</strong></td>
<td>어드민</td>
<td>-</td>
<td>수수료 공제, 연동 불가</td>
</tr>
<tr>
<td><strong>BMG</strong></td>
<td>어드민</td>
<td>슬랙</td>
<td>수수료 공제 필요</td>
</tr>
<tr>
<td><strong>USH</strong></td>
<td>예약 확인 링크</td>
<td>어드민</td>
<td>시스템 연동 오류</td>
</tr>
</tbody>
</table>

<h3>슬랙 기반 공급사</h3>
<table>
<thead>
<tr>
<th>공급사</th>
<th>확인 수단</th>
<th>소통 수단</th>
<th>주요 반려 사유</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>몽키트레블 VN & TH</strong></td>
<td>슬랙</td>
<td>슬랙</td>
<td>기타 이슈 발생</td>
</tr>
</tbody>
</table>

<h3>사업실 협업 공급사</h3>
<table>
<thead>
<tr>
<th>공급사</th>
<th>확인 수단</th>
<th>소통 수단</th>
<th>주요 반려 사유</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>LA 디즈니랜드</strong></td>
<td>이메일</td>
<td>이메일, 사업실</td>
<td>기타 이슈 발생</td>
</tr>
<tr>
<td><strong>KKDAY</strong></td>
<td>슬랙</td>
<td>슬랙, 사업실</td>
<td>기타 이슈 발생</td>
</tr>
</tbody>
</table>

<hr />

<h2>🚨 공통 반려 사유</h2>
<ol>
<li><strong>자동 수수료 공제 불가</strong>: 수수료가 부과되는 상품의 자동 환불 기능 미개발</li>
<li><strong>취소 환불 연동 불가</strong>: 마리트에서는 취소/환불 처리되었으나 공급사로 취소 불가</li>
<li><strong>미사용 시 환불 가능 규정</strong>: 미사용 여부를 시스템적으로 자동 필터링 불가</li>
<li><strong>유효기간 내 환불 가능 규정</strong>: 각 예약 건당 유효기간을 시스템적으로 자동 필터링 불가</li>
<li><strong>기타 이슈 발생</strong></li>
</ol>

<hr />

<h2>📌 처리 프로세스 요약</h2>
<ac:structured-macro ac:name="code">
<ac:plain-text-body><![CDATA[반려 알럿 수신 
  → 반려 시트 확인 
    → 공급사 확인 
      → 해당 공급사 프로세스맵 참조 
        → 확인 수단으로 상태 조회 
          → 소통 수단으로 처리 요청 (필요 시)
            → 3.0 매니저 최종 처리]]></ac:plain-text-body>
</ac:structured-macro>

<hr />

<h2>💡 빠른 검색 가이드</h2>

<h3>상황별 공급사 찾기</h3>

<p><strong>수수료 공제가 필요한 경우:</strong></p>
<ul>
<li>링크티비티, 레일유럽, BMG, KLOOK (규정 상이 시)</li>
</ul>

<p><strong>이메일 확인이 필요한 경우:</strong></p>
<ul>
<li>트립닷컴, GYG, VIATOR, TIQETS</li>
</ul>

<p><strong>어드민 로그인이 필요한 경우:</strong></p>
<ul>
<li>JTR, KLOOK, 링크티비티, 레일유럽, BMG, USH</li>
</ul>

<p><strong>슬랙 소통이 필요한 경우:</strong></p>
<ul>
<li>BMG, 몽키트레블, KKDAY</li>
</ul>

<p><strong>사업실 협업이 필요한 경우:</strong></p>
<ul>
<li>LA 디즈니랜드, KKDAY</li>
</ul>

<hr />

<ac:structured-macro ac:name="info">
<ac:rich-text-body>
<p><strong>📂 상세 프로세스맵</strong></p>
<p>각 공급사별 상세 Mermaid 다이어그램과 처리 방법은 <code>공급사별_반려_처리</code> 폴더의 개별 파일을 참조하세요.</p>
<ul>
<li>트립닷컴_반려처리.md</li>
<li>JTR_반려처리.md</li>
<li>KLOOK_반려처리.md</li>
<li>링크티비티_반려처리.md</li>
<li>레일유럽_반려처리.md</li>
<li>BMG_반려처리.md</li>
<li>GYG_반려처리.md</li>
<li>VIATOR_반려처리.md</li>
<li>TIQETS_반려처리.md</li>
<li>USH_반려처리.md</li>
<li>LA디즈니랜드_반려처리.md</li>
<li>몽키트레블_반려처리.md</li>
<li>KKDAY_반려처리.md</li>
</ul>
</ac:rich-text-body>
</ac:structured-macro>
"""
        
        # 페이지 업데이트
        print("\n페이지 업데이트 중...")
        result = update_page(
            CONFLUENCE_URL,
            CONFLUENCE_EMAIL,
            CONFLUENCE_API_TOKEN,
            PAGE_ID,
            current_title,
            content,
            current_version
        )
        
        print("\n" + "=" * 60)
        print("✅ 페이지 업데이트 완료!")
        print(f"📄 페이지 확인: {CONFLUENCE_URL}/wiki/spaces/aoh/pages/{PAGE_ID}")
        print(f"📊 새 버전: {result['version']['number']}")
        print("=" * 60)
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ 오류 발생: {e}")
        if e.response:
            print(f"응답: {e.response.text}")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
