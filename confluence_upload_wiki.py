#!/usr/bin/env python3
"""
Confluence Wiki 업로드 스크립트
"""

import os
import requests

CONFLUENCE_URL = "https://mrtcx.atlassian.net"
PAGE_ID = "1176109101"  # 대상 페이지 ID
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

def generate_confluence_html():
    """Confluence HTML 생성"""
    html = """
<p><em>2025.11 이경진 작성 완료</em></p>

<hr />

<h2>📋 참고 자료</h2>
<ul>
<li><a href="https://docs.google.com/presentation/d/1czhDT8hFfZsgfPPjsWyj9dxaLm3dZrIRtufQkEUolmg/edit?slide=id.g127afeea6f6_0_288#slide=id.g127afeea6f6_0_288">2.0 상품 등록 매뉴얼 (V2)</a></li>
<li><a href="https://docs.google.com/presentation/d/1o1OaWjbPQN3ks51SxGQ12KDFtYprDPLsDFyv5hRR8rg/edit?slide=id.g2c8a6d7a29c_1_74#slide=id.g2c8a6d7a29c_1_74">상품관리 교육자료</a></li>
<li><a href="https://docs.google.com/spreadsheets/d/1WE4yB_-9s0ZKDSB0-4EYkhuoeV97AnUJNzgj8WOmhAE/edit?gid=1004454496#gid=1004454496">해외연동 상품 검수 템플릿</a></li>
<li><a href="https://docs.google.com/spreadsheets/d/1e048A8pk1SrXAkj4N-58Oe_9vQc1gYZoOr-aXo-gmrs/edit?pli=1&gid=2054470221#gid=2054470221">표준 카테고리 기준 표</a></li>
<li><a href="https://docs.google.com/spreadsheets/d/1FjqymMxV8VPM5EWvUX9HkQZuFVkt-Ecz66vT9YJfxec/edit?gid=301657446#gid=301657446">도시별 노출 카테고리 기준 표</a></li>
<li><a href="https://docs.google.com/spreadsheets/d/1WE4yB_-9s0ZKDSB0-4EYkhuoeV97AnUJNzgj8WOmhAE/edit?gid=174453439#gid=174453439">커미션 정책</a></li>
</ul>

<hr />

<h2>🎯 등록 기준</h2>
<ul>
<li><strong>캘린더 3개월 이상 오픈</strong> 여부
  <ul><li>단, 특별한 상황의 경우, 3개월 이내로 오픈 되어있어도 등록 가능</li></ul>
</li>
<li><strong>영어 or 한국어 지원</strong> 여부
  <ul><li>둘 중 하나의 언어라도 지원해야 검수 가능</li></ul>
</li>
<li><strong>즉시 확정 상품 우선 등록</strong>
  <ul><li>※ 필요 시, 비즉시 확정 상품 보완용 허용</li></ul>
</li>
</ul>

<hr />

<h2>📊 상품 등록 방법</h2>

<table>
<thead>
<tr>
<th>순서</th>
<th>상세 내용</th>
</tr>
</thead>
<tbody>

<tr>
<td><strong>1단계</strong></td>
<td>
<h4>생텀(Sanctum) — 공급사 상품 가져오기 + MRT ID 생성</h4>
<p><strong>작업 순서:</strong></p>
<ol>
<li>생텀 → 좌측 메뉴 &gt; 공급사 선택</li>
<li>오른쪽 하단 파란 말줄임표 → 초록 가방 아이콘 <strong>[공급사에서 상품 가져오기]</strong> 클릭</li>
<li>공급사 원본 ID 입력 후 등록</li>
<li>팝업창에서 <strong>[생성]</strong> 클릭 → Offer ID 생성</li>
<li>팝업 확인 후 자동 매핑 <strong>[선택 적용]</strong> : 공급사 &gt; 생텀 까지 전달된 상품 페이지 정보를 2.0으로 적용</li>
</ol>
<p><strong>선택적용 목록:</strong> 어떤 항목이 적용 되는지 확인 가능</p>
<p>📌 <strong>중요:</strong></p>
<ul>
<li>GYG, VIATOR, TIQETS, LINKTIVITY, BMG 는 <strong>전체적용</strong> 후 검수 시작 (대표사진 자동적용)</li>
<li>🔑 <a href="https://docs.google.com/presentation/d/1o1OaWjbPQN3ks51SxGQ12KDFtYprDPLsDFyv5hRR8rg/edit?slide=id.g2c8a6d7a29c_1_74#slide=id.g2c8a6d7a29c_1_74">상품관리 교육자료</a> 81page 참고</li>
</ul>
</td>
</tr>

<tr>
<td><strong>2단계</strong></td>
<td>
<h4>2.0 매니저 검수 시작 - 도시 선택 / 정보 수정</h4>
<p><strong>2.0 매니저 페이지 접속하기:</strong></p>
<ul>
<li>주소 창에서 오퍼 번호 자리에 생성한 <strong>OFFER ID</strong> 입력</li>
<li>예시: 102193</li>
</ul>
<p><strong>도시 선택:</strong> 도시 리스트 및 대표 도시 설정</p>
<p><strong>정보 수정:</strong></p>
<table>
<tr><th>항목</th><th>설정 방법</th></tr>
<tr><td>표준 카테고리 (필수)</td><td><a href="https://docs.google.com/spreadsheets/d/1e048A8pk1SrXAkj4N-58Oe_9vQc1gYZoOr-aXo-gmrs/edit?pli=1&gid=2054470221#gid=2054470221">표준 카테고리 기준 표</a> 참고하여 선택</td></tr>
<tr><td>1·2차 노출 카테고리</td><td><a href="https://docs.google.com/spreadsheets/d/1FjqymMxV8VPM5EWvUX9HkQZuFVkt-Ecz66vT9YJfxec/edit?gid=301657446#gid=301657446">도시별 노출 카테고리 기준 표</a> 참고하여 선택</td></tr>
<tr><td>예약 가능 시간</td><td>0 (즉시 확정)</td></tr>
<tr><td>예약 패스</td><td>✅ 확정 대기 자동 패스 (여행자 사이드 확정 대기 노출 안됨)</td></tr>
<tr><td>취소/환불 가능 여부</td><td>✅ 여행자 사이드 취소 요청 버튼 노출 됨<br/>※ 취/환불 불가 상품은 V 해제 필요</td></tr>
<tr><td>상품 상세 페이지에서 옵션 노출</td><td>유효기간 내 사용하는 상품의 경우 ✅</td></tr>
<tr><td>상품 만료 기한 &amp; 구매일로 부터 N일</td><td>유효기간 기재</td></tr>
</table>
<p>→ <strong>[적용]</strong> 버튼 클릭하여 저장</p>
</td>
</tr>

<tr>
<td><strong>3단계</strong></td>
<td>
<h4>기본 정보 등록 - 어드민에서 상품 수정하기 1</h4>
<p><strong>공지 사항 등록:</strong> 부가 정보 옆 <strong>연필모양</strong> 버튼 클릭</p>
<p><strong>상품 상세 페이지 수정/등록 시작:</strong> 기본정보 옆 <strong>수정</strong> 버튼 클릭</p>
</td>
</tr>

<tr>
<td><strong>4단계</strong></td>
<td>
<h4>기본 정보 등록 - 어드민에서 상품 수정하기 2</h4>
<p>※ <a href="https://docs.google.com/spreadsheets/d/1WE4yB_-9s0ZKDSB0-4EYkhuoeV97AnUJNzgj8WOmhAE/edit?gid=1004454496#gid=1004454496">해외연동 상품 검수 템플릿 참고</a></p>
<p><strong>★ 상품 이름:</strong> 명확하고 간결하게 작성</p>
<p><strong>★ 한 줄 요약:</strong> 상품의 핵심과 특징을 한 줄로 간단하게 요약</p>
<p><strong>여행 소개</strong></p>
<p><strong>[이 티켓/투어/액티비티의 매력포인트!]</strong></p>
<ul>
<li>상품의 셀링 포인트 세 가지 정도 기재</li>
<li>공급사마다 활용할 수 있는 bullet point 번역</li>
</ul>
<p><strong>여행 상세</strong></p>
<p><strong>[옵션 안내]:</strong> 옵션명만으로는 각 옵션의 차이를 알기 힘들때 사용</p>
<p><strong>만나는 시간:</strong> 만나는 시간이 딱 하나 명확한 경우 기재</p>
<p><strong>만나는 시간 추가 정보:</strong></p>
<ul>
<li>픽업 시 만나는 시간 조율이 필요한 경우</li>
<li>만나는 시간이 하나 이상이고 선택할 경우</li>
<li>옵션마다 만나는 시간이 상이한 경우</li>
<li>픽업 장소에 따라 만나는 시간이 상이한 경우</li>
<li>문구는 템플릿 활용 바람</li>
</ul>
</td>
</tr>

<tr>
<td><strong>5단계</strong></td>
<td>
<h4>기본 정보 등록 - 어드민에서 상품 수정하기 3</h4>
<p><strong>이동 수단:</strong> 차량 이동 / 도보 이동 / 그 외 중 선택 (투어/액티비티/픽업 상품만 선택)</p>
<p><strong>★ 소요 시간</strong></p>
<table>
<tr><th>기간</th><th>설정 방법</th></tr>
<tr><td>30분</td><td>minute 설정 후 30 기재</td></tr>
<tr><td>1시간</td><td>hour 설정 후 1 기재</td></tr>
<tr><td>1일</td><td>day 설정 후 1 기재</td></tr>
<tr><td>소요 시간 노출을 원하지 않는 경우</td><td>flexible 설정 후 0 기재</td></tr>
</table>
<p>⚠️ <strong>빈칸으로 비워두면 저장이 되지 않으니 유의</strong></p>
<p><strong>여행 규모:</strong> 일행끼리 참여하는 프라이빗 상품의 경우에만 체크 박스 설정<br/>디폴트값으로 체크되어 오픈됨 - 체크 해제 필요</p>
</td>
</tr>

<tr>
<td><strong>6단계</strong></td>
<td>
<h4>기본 정보 등록 - 어드민에서 상품 수정하기 4</h4>
<p><strong>포함 사항:</strong></p>
<ul>
<li>가격에 포함된 사항 입력</li>
<li>옵션별 포함 사항이 여행 소개 내 [옵션 설명]에 기재가 되어 있다면,</li>
<li>※ "옵션 별 포함 사항은 [ 옵션 안내 ]란을 확인해 주세요." 문구 작성</li>
</ul>
<p><strong>불포함 사항:</strong> 가격에 포함되지 않은 사항이 있을 경우 입력</p>
<p><strong>★ 사용 방법</strong></p>
<ul>
<li>공급사별 템플릿과 상품별 사용 방법에 맞게 기재</li>
<li>※ <a href="https://docs.google.com/spreadsheets/d/1WE4yB_-9s0ZKDSB0-4EYkhuoeV97AnUJNzgj8WOmhAE/edit?gid=1004454496#gid=1004454496">해외연동 상품 검수 템플릿 참고</a></li>
</ul>
<p><strong>티켓 사용 방법 명시:</strong></p>
<table>
<tr><th>티켓 유형</th><th>설명</th></tr>
<tr><td>e-티켓</td><td>모바일로 제시해 바로 입장 가능한 티켓<br/>e-티켓은 이용 방법이 무조건 바로 입장</td></tr>
<tr><td>실물 티켓</td><td>바우처 제시 후 실물 티켓으로 교환해야 하는 티켓<br/>실물 티켓은 입장 방법이 무조건 실물 티켓 교환</td></tr>
</table>
<p><strong>투어 / 액티비티 카테고리:</strong></p>
<ul>
<li>템플릿 공통 내용 &amp; 상품 내 꼭 알아야 할 중요한 내용 명시</li>
<li>호텔 픽업의 경우, 호텔 픽업에 대한 공통 내용 추가 필요</li>
<li>미팅 장소 픽업 시, 만나는 장소 추가 안내 추가 필요</li>
</ul>
</td>
</tr>

<tr>
<td><strong>7단계</strong></td>
<td>
<h4>기본 정보 등록 - 어드민에서 상품 수정하기 5</h4>
<p><strong>태그 리스트:</strong> 상품과 관련된 태그 설정 필요<br/>※ 관련 태그 없으면 등록하지 않아도 상품 판매 가능</p>
<p><strong>만나는 장소:</strong></p>
<ol>
<li>업체 정보에 적힌 상품 주소를 구글지도에 검색</li>
<li>만나는 장소 정보 (구글 지도 상 주소)<br/>예시: 파리 에펠탑 (Champ de Mars, 5 Av. Anatole France, 75007 Paris, 프랑스)</li>
<li>※ "바우처 상의 만나는 장소를 꼭 확인 해 주세요" <strong>필수 기재</strong></li>
</ol>
<p><strong>위도/경도:</strong> 구글 맵에서 빨간색 핀 우클릭 시 가장 상단에 위/경도 정보 복사</p>
<p><strong>체크박스:</strong></p>
<table>
<tr><th>항목</th><th>설명</th></tr>
<tr><td>바우처</td><td>실물 티켓 교환 필요하다면 체크</td></tr>
<tr><td>해피콜</td><td>사용 X</td></tr>
<tr><td>호텔 픽업</td><td>호텔 픽업 제공하는 상품 시 체크<br/>단 만나는 장소와 위도 경도 정보를 비워두어야 함<br/>(진행 x, 위도 경도 정보 반드시 기재 필요하며, 문구는 검수 템플릿 활용)</td></tr>
</table>
<p><strong>추가 정보:</strong> 기재하지 않음</p>
</td>
</tr>

<tr>
<td><strong>8단계</strong></td>
<td>
<h4>기본 정보 등록 - 어드민에서 상품 수정하기 6</h4>
<p><strong>취소/환불 규정 입력:</strong></p>
<ol>
<li>공급사 취소 환불 규정 꼼꼼히 확인 후 해당 내용에 맞는 자동 환불 템플릿 설정</li>
<li>해당하는 자동 환불 템플릿 없는 경우 수기로 기재</li>
</ol>
<p><strong>취소/환불 기준 일: 공급사 기준 + 1일로 설정</strong></p>
<p>예시: 공급사 : 2일 전 전액 환불 → MRT : 3일 전 전액 환불</p>
<p><strong>★ 노출 가격 / 노출 통화</strong></p>
<p>생텀에서 선택 적용 눌렀다면 자동으로 대표가+통화 기준 따라옴</p>
</td>
</tr>

<tr>
<td><strong>9단계</strong></td>
<td>
<h4>기본 정보 등록 - 어드민에서 상품 수정하기 7</h4>
<p><strong>★ 여행 사진</strong></p>
<p><strong>업로드 방법:</strong></p>
<ol>
<li>여행사진 추가 &gt; 파일선택 &gt; 업로드</li>
<li>※ position 숫자 : 사진 노출 순서 지정 가능</li>
</ol>
<p><strong>대표 사진 정책:</strong></p>
<ul>
<li>여행자 페이지에 노출되는 상품 대표 사진 정책상 <strong>글자 없는 이미지만 가능</strong></li>
<li>따로 전달받은 기본 이미지가 없는 경우: 해당 상품 상세 페이지를 캡쳐해서 사용</li>
</ul>
<p><strong>※ 최소한 4장의 대표사진을 등록해야 온세일 가능</strong></p>
</td>
</tr>

<tr>
<td><strong>10단계</strong></td>
<td>
<h4>커미션 설정 / 구글 폼 등록</h4>
<p><strong>공급사 별 커미션 률 확인 및 등록:</strong></p>
<p><a href="https://docs.google.com/spreadsheets/d/1WE4yB_-9s0ZKDSB0-4EYkhuoeV97AnUJNzgj8WOmhAE/edit?gid=174453439#gid=174453439">커미션 정책</a> 참고</p>
<p><strong>작업 순서:</strong></p>
<ol>
<li>2.0 가이드 링크 (공급사 파트너 페이지) &gt; 파트너 정보수정 클릭</li>
<li>투어.티켓 상품(구) 클릭</li>
<li>검수 중인 상품 수정 클릭</li>
<li>커미션 기입 후 변경 클릭하여 저장</li>
</ol>
<p><strong>구글 폼 등록 (속성 필터 링크 모음)</strong></p>
<table>
<tr><th>카테고리</th><th>링크</th></tr>
<tr><td>투어</td><td><a href="https://forms.gle/E1bvvBELB5JKJ561A">https://forms.gle/E1bvvBELB5JKJ561A</a></td></tr>
<tr><td>클래스</td><td><a href="https://forms.gle/inhUtGHAhVDVcwaw6">https://forms.gle/inhUtGHAhVDVcwaw6</a></td></tr>
<tr><td>스냅</td><td><a href="https://forms.gle/RsFVf7kTsCusiygp8">https://forms.gle/RsFVf7kTsCusiygp8</a></td></tr>
<tr><td>액티비티</td><td><a href="https://forms.gle/t5vYeTmR8s26RZHdA">https://forms.gle/t5vYeTmR8s26RZHdA</a></td></tr>
<tr><td>티켓</td><td><a href="https://forms.gle/6FxoPRGX3toZQjnz8">https://forms.gle/6FxoPRGX3toZQjnz8</a></td></tr>
<tr><td>티켓 &gt; 스파-마사지/식사/미식</td><td><a href="https://forms.gle/rgNX7K2C4vf9d6xFA">https://forms.gle/rgNX7K2C4vf9d6xFA</a></td></tr>
<tr><td>여행편의 &gt; 유심/이심/와이파이</td><td><a href="https://forms.gle/x7oUN116BweY8yoR6">https://forms.gle/x7oUN116BweY8yoR6</a></td></tr>
<tr><td>여행편의 &gt; 이동편의</td><td><a href="https://forms.gle/odhBUzMdB9GxaYSf8">https://forms.gle/odhBUzMdB9GxaYSf8</a></td></tr>
</table>
</td>
</tr>

<tr>
<td><strong>11단계</strong></td>
<td>
<h4>판매 시작 (온세일)</h4>
<p><strong>최종 확인 체크리스트:</strong></p>
<ol>
<li>앞서 진행한 상품 등록 과정 중 빠진 것이 없는지 꼼꼼히 확인</li>
<li>특히 <strong>취소 환불 규정</strong> 반드시 확인할 것!</li>
<li>검수가 끝났다면 <strong>"판매시작"</strong> 버튼 클릭</li>
<li>여행자 페이지에서 <strong>실제 노출/결제 테스트</strong> 진행</li>
</ol>
</td>
</tr>

</tbody>
</table>

<hr />

<h2>✅ 완료</h2>
<p>모든 단계를 완료하면 상품이 정상적으로 판매 시작됩니다.</p>
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
    print("Confluence Wiki Upload")
    print("=" * 60)
    
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        print("\n[ERROR] Authentication info missing")
        return
    
    print(f"\n[OK] Authentication confirmed")
    print(f"  - Email: {CONFLUENCE_EMAIL}")
    print(f"  - Page ID: {PAGE_ID}")
    
    try:
        print("\n[1/3] Generating HTML content...")
        html_content = generate_confluence_html()
        print("  [OK] HTML generated")
        
        print("\n[2/3] Getting page info...")
        page = get_page(CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, PAGE_ID)
        current_version = page["version"]["number"]
        current_title = page["title"]
        print(f"  [OK] Current version: {current_version}")
        print(f"  [OK] Current title: {current_title}")
        
        print("\n[3/3] Updating page...")
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
        print("[SUCCESS] Wiki upload completed!")
        print(f"Page: {CONFLUENCE_URL}/wiki/spaces/aoh/pages/{PAGE_ID}")
        print(f"Version: {current_version} -> {result['version']['number']}")
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
