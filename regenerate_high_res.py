#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 플로우차트를 T&A와 동일한 큰 해상도로 재생성
"""

import subprocess

# 더 큰 해상도로 설정
WIDTH = 3000
HEIGHT = 4000

CHARTS = [
    ("monitoring_flowchart", "연동 예약 운영 모니터링"),
    ("domestic_product_register", "국내 연동 신규 상품 등록"),
    ("hanin_partner_inspection", "한인민박 파트너 검수"),
    ("hanin_product_register", "한인민박 상품 등록"),
    ("product_register_3.0", "해외 연동 신규 상품 등록 3.0"),
    ("overseas_product_register_2.0", "해외 연동 신규 상품 등록 2.0"),
    ("ta_inspection", "T&A 입점 상품 검수")
]

print("=" * 70)
print(f"모든 플로우차트를 고해상도로 재생성 ({WIDTH}x{HEIGHT}px)")
print("=" * 70)

for chart_name, display_name in CHARTS:
    print(f"\n[{CHARTS.index((chart_name, display_name)) + 1}/{len(CHARTS)}] {display_name}")
    
    mmd_file = f"mermaid_images/{chart_name}.mmd"
    png_file = f"mermaid_images/{chart_name}.png"
    
    cmd = [
        "npx", "-y", "@mermaid-js/mermaid-cli@latest",
        "-i", mmd_file,
        "-o", png_file,
        "-b", "transparent",
        "-w", str(WIDTH),
        "-H", str(HEIGHT)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"  ✓ 생성 완료")
        else:
            print(f"  ❌ 실패: {result.stderr}")
    except Exception as e:
        print(f"  ❌ 오류: {e}")

print("\n" + "=" * 70)
print("✅ 재생성 완료!")
print("=" * 70)
