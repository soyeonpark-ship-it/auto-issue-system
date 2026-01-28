# -*- coding: utf-8 -*-
"""
PyInstaller로 exe 파일 만들기
"""

# 1. PyInstaller 설치
# pip install pyinstaller

# 2. 명령어 실행:
# pyinstaller --onefile --windowed --name="마이리얼트립_자동발권" --icon=icon.ico museum_pass_auto.py

# 옵션 설명:
# --onefile: 하나의 exe 파일로 패키징
# --windowed: 콘솔 창 숨김 (GUI만 표시)
# --name: exe 파일 이름
# --icon: 아이콘 파일 (선택사항)

# 3. 생성된 파일:
# dist/마이리얼트립_자동발권.exe  ← 이 파일을 배포

print("PyInstaller 설정 파일")
