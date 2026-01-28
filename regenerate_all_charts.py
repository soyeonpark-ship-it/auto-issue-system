#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 Mermaid 차트를 동일한 해상도로 재생성
"""

import os
import subprocess

# 표준 차트 사이즈 설정
STANDARD_WIDTH = 2400
STANDARD_HEIGHT = 3000

# 재생성할 차트 목록
CHARTS = [
    {
        'name': '연동 예약 운영 모니터링',
        'mmd': 'mermaid_images/monitoring_flowchart.mmd',
        'png': 'mermaid_images/monitoring_flowchart.png'
    },
    {
        'name': '국내 연동 신규 상품 등록 (2.0)',
        'mmd': 'mermaid_images/domestic_product_register.mmd',
        'png': 'mermaid_images/domestic_product_register.png'
    },
    {
        'name': 'T&A 입점 상품 검수',
        'mmd': 'mermaid_images/ta_inspection.mmd',
        'png': 'mermaid_images/ta_inspection.png'
    },
    {
        'name': '한인민박 파트너 검수',
        'mmd': 'mermaid_images/hanin_partner_inspection.mmd',
        'png': 'mermaid_images/hanin_partner_inspection.png'
    },
    {
        'name': '한인민박 상품 등록',
        'mmd': 'mermaid_images/hanin_product_register.mmd',
        'png': 'mermaid_images/hanin_product_register.png'
    }
]

def regenerate_chart(chart):
    """차트 재생성"""
    if not os.path.exists(chart['mmd']):
        print(f"  ⚠️  .mmd 파일이 없습니다: {chart['mmd']}")
        return False
    
    cmd = [
        'npx', '-y', '@mermaid-js/mermaid-cli@latest',
        '-i', chart['mmd'],
        '-o', chart['png'],
        '-b', 'transparent',
        '-w', str(STANDARD_WIDTH),
        '-H', str(STANDARD_HEIGHT)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  ✓ 생성 완료: {chart['png']}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 생성 실패: {e}")
        return False

def main():
    print("=" * 60)
    print(f"Mermaid 차트 해상도 통일 작업")
    print(f"표준 해상도: {STANDARD_WIDTH}x{STANDARD_HEIGHT}px")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i, chart in enumerate(CHARTS, 1):
        print(f"\n[{i}/{len(CHARTS)}] {chart['name']}")
        if regenerate_chart(chart):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"작업 완료: ✓ {success_count}개 성공, ❌ {fail_count}개 실패")
    print("=" * 60)

if __name__ == "__main__":
    main()
