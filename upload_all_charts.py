#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 차트를 Confluence에 재업로드
"""

import os
import sys
import io
import subprocess

# UTF-8 출력 강제
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

UPLOAD_SCRIPTS = [
    {
        'name': '연동 예약 운영 모니터링',
        'script': 'confluence_monitoring_upload.py',
        'page_id': '1191477354'
    },
    {
        'name': '국내 연동 신규 상품 등록 (2.0)',
        'script': 'confluence_domestic_upload.py',
        'page_id': '1192394909'
    },
    {
        'name': 'T&A 입점 상품 검수',
        'script': 'confluence_ta_upload.py',
        'page_id': '1193836635'
    },
    {
        'name': '한인민박 파트너 검수',
        'script': 'confluence_hanin_upload.py',
        'page_id': '1194033239'
    },
    {
        'name': '한인민박 상품 등록',
        'script': 'confluence_hanin_product_upload.py',
        'page_id': '1193803904'
    }
]

def upload_to_confluence(item):
    """Confluence 업로드"""
    try:
        result = subprocess.run(
            ['python', item['script']],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"  ✓ 업로드 완료")
            return True
        else:
            print(f"  ❌ 업로드 실패")
            print(result.stderr[:200])
            return False
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return False

def main():
    print("=" * 60)
    print("모든 차트를 Confluence에 재업로드")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i, item in enumerate(UPLOAD_SCRIPTS, 1):
        print(f"\n[{i}/{len(UPLOAD_SCRIPTS)}] {item['name']}")
        print(f"  페이지 ID: {item['page_id']}")
        
        if upload_to_confluence(item):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 작업 완료: {success_count}개 성공, {fail_count}개 실패")
    print("=" * 60)
    
    print("\n📋 업로드된 페이지:")
    for item in UPLOAD_SCRIPTS:
        print(f"  - {item['name']}: https://mrtcx.atlassian.net/wiki/spaces/CD/pages/{item['page_id']}")

if __name__ == "__main__":
    main()
