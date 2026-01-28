@echo off
echo ================================================
echo ngrok 간편 설치 가이드
echo ================================================
echo.
echo 1단계: ngrok 다운로드
echo    https://ngrok.com/download
echo    "Download for Windows" 클릭
echo.
echo 2단계: 압축 풀기
echo    다운받은 ngrok.zip 압축 풀기
echo    ngrok.exe 파일을 이 폴더에 복사
echo.
echo 3단계: ngrok 회원가입 (무료)
echo    https://dashboard.ngrok.com/signup
echo    GitHub로 간편 가입
echo.
echo 4단계: 인증 토큰 복사
echo    https://dashboard.ngrok.com/get-started/your-authtoken
echo    토큰 복사 후 아래 명령어 실행:
echo    ngrok config add-authtoken YOUR_TOKEN
echo.
echo 5단계: 실행!
echo    ngrok http 5000
echo.
echo ================================================
echo.
pause

start https://ngrok.com/download
