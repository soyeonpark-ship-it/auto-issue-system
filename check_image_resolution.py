#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 PNG 이미지의 실제 해상도 확인
"""

import os
from PIL import Image

IMAGE_FOLDER = "mermaid_images"

# CD space에 업로드된 플로우차트 이미지들
CHART_IMAGES = [
    "monitoring_flowchart.png",
    "domestic_product_register.png",
    "ta_inspection.png",
    "hanin_partner_inspection.png",
    "hanin_product_register.png",
    "product_register_3.0.png",
    "overseas_product_register_2.0.png"
]

print("=" * 70)
print("CD Space 플로우차트 이미지 해상도 확인")
print("=" * 70)

for img_name in CHART_IMAGES:
    img_path = os.path.join(IMAGE_FOLDER, img_name)
    try:
        with Image.open(img_path) as img:
            width, height = img.size
            print(f"{img_name:40s} | {width:5d} x {height:5d}")
    except Exception as e:
        print(f"{img_name:40s} | ERROR: {e}")

print("=" * 70)
