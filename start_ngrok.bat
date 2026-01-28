@echo off
echo ================================================
echo ngrok 자동 실행 스크립트
echo ================================================
echo.
echo Flask 서버가 실행 중인지 확인하세요!
echo (python final_web_dashboard.py)
echo.
echo ngrok을 시작합니다...
echo 생성된 URL을 팀원들에게 공유하세요!
echo.
pause

REM ngrok 실행
ngrok http 5000
