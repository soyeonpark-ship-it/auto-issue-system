@echo off
REM 자동 발권 프로그램 실행기
title 마이리얼트립 자동 발권 봇

echo ================================================
echo    마이리얼트립 자동 발권 시스템
echo ================================================
echo.
echo 프로그램을 시작합니다...
echo.

REM Python 프로그램 실행
python "%~dp0museum_pass_auto.py"

echo.
echo 프로그램이 종료되었습니다.
pause
