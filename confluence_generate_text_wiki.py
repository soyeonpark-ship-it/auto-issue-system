#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Confluence Wiki 생성 - 텍스트 기반 (이미지 없이)
"""

import os
import sys
import io
import requests

# UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
TARGET_PAGE_ID = "1194000407"  # CD space

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

def generate_confluence_html():
    """Confluence HTML 생성"""
    html = """
<h2>목차</h2>
<ac:structured-macro ac:name="toc" ac:schema-version="1">
  <ac:parameter ac:name="printable">true</ac:parameter>
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
  <ac:parameter ac:name="minLevel">1</ac:parameter>
</ac:structured-macro>

<hr />

<h2>📋 프로세스 개요</h2>
<p><strong>3.0 이관 공급사</strong> (2025-12-09 기준): KKDAY, 몽키트래블_태국 &amp; 베트남</p>

<hr />

<h2>📊 상품 등록 절차</h2>

<h3>1단계: 매니저 T&amp;A 연동 상품 접근</h3>
<ul>
<li>[T&amp;A 연동 상품] 버튼 클릭</li>
<li>검수가 필요한 상품의 공급사 선택</li>
</ul>

<h3>2단계: 공급사 상품 가져오기</h3>
<ul>
<li>[공급사 상품 가져오기] 버튼 클릭</li>
<li>공급사 원본 ID 입력
  <ul>
    <li>1개 가져오기: 단일 ID 입력</li>
    <li>여러개 가져오기: , 로 구분하여 입력</li>
  </ul>
</li>
<li><strong>중복 체크</strong>: 이미 등록된 상품일 경우 에러 메시지 노출</li>
</ul>

<h3>3단계: 마리트 상품 생성</h3>
<ul>
<li>상품 등록 완료 후 연동 상품 ID 검색</li>
<li>[마리트 상품 생성] 버튼 클릭</li>
<li><strong>표준 카테고리 선택</strong> (필수)</li>
<li>[연동 상품 등록하기] 버튼 클릭</li>
</ul>

<h3>4단계: 파트너 페이지에서 상품 상세 정보 입력</h3>
<p>마리트 상품 ID 클릭하여 파트너 페이지로 이동</p>

<h4>필수 입력 항목:</h4>
<ul>
<li><strong>대표 도시</strong></li>
<li><strong>상품명</strong></li>
<li><strong>상품 사진</strong>
  <ul>
    <li>최소 4장 (~9/1 까지)</li>
    <li>최소 1장 (9/1부터~)</li>
  </ul>
</li>
<li><strong>상품 소개</strong>
  <ul>
    <li>공급사 페이지 내용 복사 붙여넣기</li>
    <li>온세일 시트에 "상세 내용 이미지" 체크된 경우: 간략하게만 작성</li>
  </ul>
</li>
<li><strong>이동 수단</strong> (투어)</li>
<li><strong>총 소요시간</strong> (투어)</li>
<li><strong>사용 언어</strong> (투어)</li>
<li><strong>공지사항/이벤트</strong></li>
<li><strong>만나는 시간</strong></li>
<li><strong>예약 마감 시간</strong></li>
<li><strong>만나는 장소</strong></li>
<li><strong>포함 사항</strong></li>
<li><strong>불포함 사항</strong></li>
<li><strong>필수 안내 사항</strong></li>
</ul>

<h3>5단계: 심사 요청</h3>
<p><ac:emoticon ac:name="blue-star" /> <strong>중요</strong>: 버튼 상태에 따라 절차가 다릅니다</p>
<ul>
<li><strong>버튼 2개 노출 시</strong>: 
  <ol>
    <li>[상품 정보 수정] 버튼 클릭</li>
    <li>[심사요청] 버튼 클릭</li>
  </ol>
</li>
<li><strong>버튼 1개 노출 시</strong>:
  <ol>
    <li>[심사요청] 버튼 클릭</li>
  </ol>
</li>
</ul>
<p>완료되면 매니저 페이지에서 "심사중" 상태로 변경됨을 확인</p>

<h3>6단계: 매니저 3.0 최종 설정</h3>

<h4>예약 정보 설정</h4>
<ul>
<li><strong>예약 가능 시간</strong>: 즉시 확정이라면 <strong>0</strong>으로 설정</li>
<li><strong>예약 확정 방식</strong>: "바로 예약"</li>
<li><strong>결제수단 나중결제 가능 여부</strong>: "사용 불가"</li>
<li><strong>예약 시 본인 인증 필요여부</strong>: "불필요"</li>
<li><strong>현금 영수증 발행 여부</strong>: "미발행"</li>
</ul>

<h4>취소/환불 정보 수정</h4>
<ul>
<li><strong>취소/환불 템플릿</strong>: "미사용"
  <ul>
    <li>공급사와 동일한 취소환불 정책으로 운영하기 때문에 템플릿을 사용하지 않음</li>
  </ul>
</li>
<li><strong>취소/환불 문구</strong>: <code>옵션 별로 취소/환불 정책이 상이할 수 있습니다. 옵션 선택 후 상세 정책을 확인해주세요.</code></li>
<li><strong>취소 요청 가능 여부</strong>:
  <ul>
    <li>"취소 불가": 확정 후 환불 불가 규정</li>
    <li>"취소 가능": 확정 후 환불 가능 규정</li>
  </ul>
</li>
</ul>

<h3>7단계: 공급사별 대표가 설정</h3>
<ul>
<li><strong>KKDAY</strong>: 사업실에서 설정
  <ul>
    <li>온세일 시트 L열에 "상품조성완료 → 대표가 등록필요" 기재</li>
    <li>슬랙 스레드에 노티</li>
  </ul>
</li>
<li><strong>KLOOK</strong>: 판매가 정책 등록 없이 바로 진행
  <ul>
    <li>상품 조성 완료 후 바로 <strong>심사 요청 → 판매 시작</strong></li>
  </ul>
</li>
</ul>

<h3>8단계: 판매 시작</h3>
<ul>
<li>[판매시작] 버튼 클릭</li>
<li>여행자 페이지에서 <strong>실제 노출/결제 테스트</strong> 진행</li>
</ul>

<hr />

<h2>🔗 참고 자료</h2>

<ac:structured-macro ac:name="expand" ac:schema-version="1">
<ac:parameter ac:name="title">📍공급사 별 B2B/B2C 상품 페이지 리스트</ac:parameter>
<ac:rich-text-body>
<table>
<tbody>
<tr><th>공급사</th><th>B2B 페이지</th><th>B2C 페이지</th></tr>
<tr>
  <td>KLOOK</td>
  <td>https://klook.klktech.com/activity/(원본ID)</td>
  <td>https://www.klook.com/ko/activity/(원본ID)</td>
</tr>
<tr>
  <td>GYG</td>
  <td>https://www.getyourguide.com/ko-kr/.../t(원본ID)</td>
  <td>B2C 페이지 동일</td>
</tr>
<tr>
  <td>VIATOR</td>
  <td>https://www.viator.com/tours/.../d4474-(원본ID)</td>
  <td>B2C 페이지 동일</td>
</tr>
<tr>
  <td>TRIP.COM</td>
  <td>https://piaovip.ctrip.com/ttddist/act/dest/t(원본ID)</td>
  <td>상품 제목으로 구글 검색</td>
</tr>
<tr>
  <td>TIQETS</td>
  <td>https://www.tiqets.com/en/.../p(원본ID)</td>
  <td>B2C 페이지 동일</td>
</tr>
<tr>
  <td>몽키트레블 태국</td>
  <td>https://www.winwintravel.com/th/ko/tour/.../product_id=(원본ID)</td>
  <td>B2C 페이지 따로 조회하지 않음</td>
</tr>
<tr>
  <td>몽키트레블 베트남</td>
  <td>https://www.winwintravel.com/vn/ko/tour/.../product_id=(원본ID)</td>
  <td>B2C 페이지 따로 조회하지 않음</td>
</tr>
</tbody>
</table>
</ac:rich-text-body>
</ac:structured-macro>
"""
    
    return html

def main():
    print("=" * 60)
    print("Confluence Wiki 생성")
    print("=" * 60)
    
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n인증 정보가 없습니다.")
        return
    
    print(f"\n✓ 인증 정보 확인")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - 대상 페이지: {TARGET_PAGE_ID}")
    
    try:
        # 1. HTML 생성
        print("\n[1/2] HTML 생성...")
        html_content = generate_confluence_html()
        print("  ✓ HTML 생성 완료")
        
        # 2. 페이지 업데이트
        print("\n[2/2] 페이지 업데이트...")
        page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, TARGET_PAGE_ID)
        current_version = page["version"]["number"]
        current_title = page["title"]
        
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
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
