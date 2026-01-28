# -*- coding: utf-8 -*-
"""
마이리얼트립 -> WAUG B2B 자동 발권 봇 (연습용)
실제와 동일한 코드 구조로 작성됨
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime

class AutoTicketBot:
    """자동 발권 봇"""
    
    def __init__(self):
        print("=" * 60)
        print("[BOT] 자동 발권 봇 초기화 중...")
        print("=" * 60)
        
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 10)
        
        # HTML 파일 경로
        self.mrt_url = f'file:///{os.path.abspath("mrt_mock.html")}'
        self.waug_url = f'file:///{os.path.abspath("waug_mock.html")}'
        
        print("[OK] 브라우저 준비 완료\n")
    
    def log(self, message, prefix="[LOG]"):
        """로그 출력"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"{prefix} [{timestamp}] {message}")
    
    # ========== 마이리얼트립 관련 ==========
    
    def login_mrt(self):
        """마이리얼트립 로그인"""
        self.log("마이리얼트립 접속 중...", "[MRT]")
        self.driver.get(self.mrt_url)
        time.sleep(1)
        
        self.log("로그인 중...", "[MRT]")
        
        # 이메일 입력
        email = self.wait.until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email.clear()
        email.send_keys("partner@myrealtrip.com")
        
        # 비밀번호 입력
        password = self.driver.find_element(By.ID, "password")
        password.clear()
        password.send_keys("demo1234")
        
        # 로그인 버튼 클릭
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        
        time.sleep(1)
        self.log("마이리얼트립 로그인 성공!", "[OK]")
    
    def get_pending_bookings(self):
        """미발권 예약 목록 가져오기"""
        self.log("미발권 예약 조회 중...", "[MRT]")
        
        bookings = []
        
        # 테이블에서 데이터 추출
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".booking-row[data-status='pending']")
        
        for row in rows:
            booking = {
                'id': row.find_element(By.CLASS_NAME, 'booking-id').text,
                'passenger_name': row.find_element(By.CLASS_NAME, 'passenger').text,
                'passport_number': row.find_element(By.CLASS_NAME, 'passport').text,
                'departure': row.find_element(By.CSS_SELECTOR, 'td:nth-child(4)').text.split('-')[0],
                'arrival': row.find_element(By.CSS_SELECTOR, 'td:nth-child(4)').text.split('-')[1],
                'flight_number': row.find_element(By.CLASS_NAME, 'flight').text,
                'departure_date': row.find_element(By.CLASS_NAME, 'date').text,
                'email': row.find_element(By.CLASS_NAME, 'email').text
            }
            bookings.append(booking)
        
        self.log(f"{len(bookings)}건의 미발권 예약 발견!", "[OK]")
        
        # 예약 목록 출력
        print("\n" + "=" * 60)
        for i, booking in enumerate(bookings, 1):
            print(f"{i}. {booking['id']} - {booking['passenger_name']} - {booking['flight_number']}")
        print("=" * 60 + "\n")
        
        return bookings
    
    # ========== WAUG B2B 관련 ==========
    
    def login_waug(self):
        """WAUG B2B 로그인"""
        self.log("WAUG B2B 접속 중...", "[WAUG]")
        self.driver.get(self.waug_url)
        time.sleep(1)
        
        self.log("WAUG 로그인 중...", "[WAUG]")
        
        # 아이디 입력
        username = self.wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username.clear()
        username.send_keys("waug_demo")
        
        # 비밀번호 입력
        password = self.driver.find_element(By.ID, "password")
        password.clear()
        password.send_keys("demo1234")
        
        # 로그인 버튼 클릭
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        
        time.sleep(1)
        self.log("WAUG 로그인 성공!", "[OK]")
    
    def issue_ticket(self, booking):
        """발권 처리 - 핵심 함수"""
        self.log(f"발권 시작: {booking['passenger_name']}", "[TICKET]")
        
        try:
            # 승객명
            passenger_name = self.wait.until(
                EC.presence_of_element_located((By.ID, "passengerName"))
            )
            passenger_name.clear()
            passenger_name.send_keys(booking['passenger_name'])
            self.log(f"  승객명: {booking['passenger_name']}", "  [OK]")
            
            # 여권번호
            passport = self.driver.find_element(By.ID, "passportNumber")
            passport.clear()
            passport.send_keys(booking['passport_number'])
            self.log(f"  여권번호: {booking['passport_number']}", "  [OK]")
            
            # 출발지
            departure_select = Select(self.driver.find_element(By.ID, "departure"))
            departure_select.select_by_value(booking['departure'])
            self.log(f"  출발지: {booking['departure']}", "  [OK]")
            
            # 도착지
            arrival_select = Select(self.driver.find_element(By.ID, "arrival"))
            arrival_select.select_by_value(booking['arrival'])
            self.log(f"  도착지: {booking['arrival']}", "  [OK]")
            
            # 항공편
            flight = self.driver.find_element(By.ID, "flightNumber")
            flight.clear()
            flight.send_keys(booking['flight_number'])
            self.log(f"  항공편: {booking['flight_number']}", "  [OK]")
            
            # 출발일
            departure_date = self.driver.find_element(By.ID, "departureDate")
            departure_date.clear()
            departure_date.send_keys(booking['departure_date'])
            self.log(f"  출발일: {booking['departure_date']}", "  [OK]")
            
            # 예약 클래스 (기본값 Y)
            class_select = Select(self.driver.find_element(By.ID, "bookingClass"))
            class_select.select_by_value('Y')
            
            self.log("  모든 정보 입력 완료", "  [OK]")
            
            # 발권 버튼 클릭
            issue_btn = self.driver.find_element(By.ID, "issueBtn")
            issue_btn.click()
            self.log("  발권 버튼 클릭 (처리 중...)", "  [WAIT]")
            
            # 발권 완료 대기 (3초)
            time.sleep(3)
            
            # 티켓 번호 추출
            ticket_number = self.wait.until(
                EC.presence_of_element_located((By.ID, "ticketNumber"))
            ).text
            
            self.log(f"발권 완료! 티켓번호: {ticket_number}", "[SUCCESS]")
            
            # 스크린샷 저장
            screenshot_path = f"ticket_{booking['id']}_{ticket_number}.png"
            self.driver.save_screenshot(screenshot_path)
            self.log(f"스크린샷 저장: {screenshot_path}", "[SAVE]")
            
            return {
                'success': True,
                'ticket_number': ticket_number,
                'booking_id': booking['id']
            }
            
        except Exception as e:
            self.log(f"발권 실패: {str(e)}", "[ERROR]")
            self.driver.save_screenshot(f"error_{booking['id']}.png")
            return {
                'success': False,
                'error': str(e),
                'booking_id': booking['id']
            }
    
    # ========== 전체 프로세스 ==========
    
    def run_full_automation(self):
        """전체 자동화 프로세스 실행"""
        try:
            print("\n" + "=" * 60)
            print("   자동 발권 프로세스 시작")
            print("=" * 60 + "\n")
            
            # STEP 1: 마이리얼트립에서 예약 정보 가져오기
            print("\n[STEP 1] 마이리얼트립 예약 조회")
            print("-" * 60)
            self.login_mrt()
            bookings = self.get_pending_bookings()
            
            if not bookings:
                self.log("처리할 예약이 없습니다.", "[INFO]")
                return
            
            # 자동 진행
            print("\n" + "=" * 60)
            print(f"\n총 {len(bookings)}건의 예약을 자동 발권합니다!")
            print("3초 후 시작...")
            time.sleep(3)
            
            # STEP 2: WAUG에 로그인
            print("\n[STEP 2] WAUG B2B 로그인")
            print("-" * 60)
            self.login_waug()
            
            # STEP 3: 각 예약 발권 처리
            print("\n[STEP 3] 발권 처리")
            print("-" * 60)
            
            results = []
            for i, booking in enumerate(bookings, 1):
                print(f"\n>> [{i}/{len(bookings)}] 처리 중...")
                result = self.issue_ticket(booking)
                results.append(result)
                
                # 다음 예약 처리 전 대기 (페이지 새로고침)
                if i < len(bookings):
                    self.log("다음 예약 준비 중...", "[WAIT]")
                    self.driver.refresh()
                    time.sleep(2)
            
            # STEP 4: 결과 요약
            print("\n" + "=" * 60)
            print("[결과 요약]")
            print("=" * 60)
            
            success_count = sum(1 for r in results if r['success'])
            fail_count = len(results) - success_count
            
            print(f"[OK] 성공: {success_count}건")
            print(f"[ERROR] 실패: {fail_count}건")
            print(f"[TOTAL] 전체: {len(results)}건")
            
            print("\n성공한 발권:")
            for r in results:
                if r['success']:
                    print(f"  - {r['booking_id']}: {r['ticket_number']}")
            
            if fail_count > 0:
                print("\n실패한 발권:")
                for r in results:
                    if not r['success']:
                        print(f"  - {r['booking_id']}: {r['error']}")
            
            print("\n" + "=" * 60)
            print("[COMPLETE] 자동 발권 프로세스 완료!")
            print("=" * 60 + "\n")
            
        except Exception as e:
            self.log(f"심각한 오류 발생: {str(e)}", "[CRITICAL]")
            self.driver.save_screenshot('critical_error.png')
        
        finally:
            self.log("5초 후 브라우저를 종료합니다...", "[INFO]")
            time.sleep(5)
            self.driver.quit()
            self.log("프로그램 종료", "[BYE]")

# ========== 메인 실행 ==========

if __name__ == "__main__":
    print("""
    ===========================================================
    
           자동 발권 봇 (연습용 데모)
    
       마이리얼트립 -> WAUG B2B 자동화 시뮬레이션
    
    ===========================================================
    """)
    
    print("이 프로그램은:")
    print("1. 마이리얼트립에서 미발권 예약을 가져옵니다")
    print("2. WAUG B2B에 자동으로 로그인합니다")
    print("3. 예약 정보를 자동으로 입력하고 발권합니다")
    print("4. 티켓 번호를 추출하고 결과를 보여줍니다\n")
    
    print("잠시 후 자동으로 시작합니다...\n")
    time.sleep(2)
    
    bot = AutoTicketBot()
    bot.run_full_automation()
