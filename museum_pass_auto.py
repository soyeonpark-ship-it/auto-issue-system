# -*- coding: utf-8 -*-
"""
마이리얼트립 -> 파리 뮤지엄 패스 공급사 자동 발권 봇
2일권/4일권/6일권 자동 처리 및 이메일 발송
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

class MuseumPassBot:
    """파리 뮤지엄 패스 자동 발권 봇"""
    
    def __init__(self):
        print("=" * 60)
        print("[BOT] 파리 뮤지엄 패스 자동 발권 봇 초기화 중...")
        print("=" * 60)
        
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 10)
        
        # HTML 파일 경로
        self.mrt_url = f'file:///{os.path.abspath("museum_pass_mrt.html")}'
        self.supplier_url = f'file:///{os.path.abspath("museum_pass_supplier.html")}'
        
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
        
        email = self.wait.until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email.clear()
        email.send_keys("partner@myrealtrip.com")
        
        password = self.driver.find_element(By.ID, "password")
        password.clear()
        password.send_keys("demo1234")
        
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        
        time.sleep(1)
        self.log("마이리얼트립 로그인 성공!", "[OK]")
    
    def get_pending_orders(self):
        """미처리 주문 목록 가져오기"""
        self.log("미처리 주문 조회 중...", "[MRT]")
        
        orders = []
        
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".order-row[data-status='pending']")
        
        for row in rows:
            # 패스 종류 추출 (2일권/4일권/6일권)
            pass_text = row.find_element(By.CLASS_NAME, 'pass-type').text
            if '2일권' in pass_text:
                pass_type = '2DAY'
            elif '4일권' in pass_text:
                pass_type = '4DAY'
            elif '6일권' in pass_text:
                pass_type = '6DAY'
            else:
                pass_type = '2DAY'
            
            order = {
                'order_id': row.find_element(By.CLASS_NAME, 'order-id').text,
                'customer_name': row.find_element(By.CLASS_NAME, 'customer-name').text,
                'email': row.find_element(By.CLASS_NAME, 'email').text,
                'pass_type': pass_type,
                'quantity': row.find_element(By.CLASS_NAME, 'quantity').text,
                'order_date': row.find_element(By.CLASS_NAME, 'order-date').text
            }
            orders.append(order)
        
        self.log(f"{len(orders)}건의 미처리 주문 발견!", "[OK]")
        
        # 주문 목록 출력
        print("\n" + "=" * 60)
        for i, order in enumerate(orders, 1):
            pass_name = {'2DAY': '2일권', '4DAY': '4일권', '6DAY': '6일권'}[order['pass_type']]
            print(f"{i}. {order['order_id']} - {order['customer_name']} - {pass_name} x{order['quantity']}")
        print("=" * 60 + "\n")
        
        return orders
    
    # ========== 공급사 포털 관련 ==========
    
    def login_supplier(self):
        """공급사 포털 로그인"""
        self.log("공급사 포털 접속 중...", "[SUPPLIER]")
        self.driver.get(self.supplier_url)
        time.sleep(1)
        
        self.log("공급사 로그인 중...", "[SUPPLIER]")
        
        username = self.wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username.clear()
        username.send_keys("museum_partner")
        
        password = self.driver.find_element(By.ID, "password")
        password.clear()
        password.send_keys("paris2024")
        
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        
        time.sleep(1)
        self.log("공급사 로그인 성공!", "[OK]")
    
    def issue_voucher(self, order):
        """바우처 발급 및 이메일 발송"""
        self.log(f"바우처 발급 시작: {order['customer_name']}", "[VOUCHER]")
        
        try:
            # 고객명 (영문)
            customer_name = self.wait.until(
                EC.presence_of_element_located((By.ID, "customerName"))
            )
            customer_name.clear()
            customer_name.send_keys(order['customer_name'])
            self.log(f"  고객명: {order['customer_name']}", "  [OK]")
            
            # 이메일
            email = self.driver.find_element(By.ID, "email")
            email.clear()
            email.send_keys(order['email'])
            self.log(f"  이메일: {order['email']}", "  [OK]")
            
            # 패스 종류
            pass_type_select = Select(self.driver.find_element(By.ID, "passType"))
            pass_type_select.select_by_value(order['pass_type'])
            pass_name = {'2DAY': '2일권', '4DAY': '4일권', '6DAY': '6일권'}[order['pass_type']]
            self.log(f"  패스 종류: {pass_name}", "  [OK]")
            
            # 수량
            quantity = self.driver.find_element(By.ID, "quantity")
            quantity.clear()
            quantity.send_keys(order['quantity'])
            self.log(f"  수량: {order['quantity']}매", "  [OK]")
            
            self.log("  모든 정보 입력 완료", "  [OK]")
            
            # 발급 버튼 클릭
            issue_btn = self.driver.find_element(By.ID, "issueBtn")
            issue_btn.click()
            self.log("  바우처 발급 버튼 클릭 (이메일 발송 중...)", "  [WAIT]")
            
            # 발급 완료 대기
            time.sleep(3)
            
            # 바우처 코드 추출
            voucher_code = self.wait.until(
                EC.presence_of_element_located((By.ID, "voucherCode"))
            ).text
            
            self.log(f"바우처 발급 완료! 코드: {voucher_code}", "[SUCCESS]")
            self.log(f"이메일 발송 완료: {order['email']}", "[EMAIL]")
            
            # 스크린샷 저장
            screenshot_path = f"voucher_{order['order_id']}_{voucher_code}.png"
            self.driver.save_screenshot(screenshot_path)
            self.log(f"스크린샷 저장: {screenshot_path}", "[SAVE]")
            
            return {
                'success': True,
                'voucher_code': voucher_code,
                'order_id': order['order_id']
            }
            
        except Exception as e:
            self.log(f"발급 실패: {str(e)}", "[ERROR]")
            self.driver.save_screenshot(f"error_{order['order_id']}.png")
            return {
                'success': False,
                'error': str(e),
                'order_id': order['order_id']
            }
    
    # ========== 전체 프로세스 ==========
    
    def run_full_automation(self):
        """전체 자동화 프로세스 실행"""
        try:
            print("\n" + "=" * 60)
            print("   파리 뮤지엄 패스 자동 발권 프로세스 시작")
            print("=" * 60 + "\n")
            
            # STEP 1: 마이리얼트립에서 주문 정보 가져오기
            print("\n[STEP 1] 마이리얼트립 주문 조회")
            print("-" * 60)
            self.login_mrt()
            orders = self.get_pending_orders()
            
            if not orders:
                self.log("처리할 주문이 없습니다.", "[INFO]")
                return
            
            # 자동 진행
            print("\n" + "=" * 60)
            print(f"\n총 {len(orders)}건의 주문을 자동 발권합니다!")
            print("3초 후 시작...")
            time.sleep(3)
            
            # STEP 2: 공급사 포털에 로그인
            print("\n[STEP 2] 공급사 포털 로그인")
            print("-" * 60)
            self.login_supplier()
            
            # STEP 3: 각 주문 바우처 발급
            print("\n[STEP 3] 바우처 발급 및 이메일 발송")
            print("-" * 60)
            
            results = []
            for i, order in enumerate(orders, 1):
                print(f"\n>> [{i}/{len(orders)}] 처리 중...")
                result = self.issue_voucher(order)
                results.append(result)
                
                # 다음 주문 처리 전 대기
                if i < len(orders):
                    self.log("다음 주문 준비 중...", "[WAIT]")
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
            
            print("\n성공한 발급:")
            for r in results:
                if r['success']:
                    print(f"  - {r['order_id']}: {r['voucher_code']} (이메일 발송 완료)")
            
            if fail_count > 0:
                print("\n실패한 발급:")
                for r in results:
                    if not r['success']:
                        print(f"  - {r['order_id']}: {r['error']}")
            
            print("\n" + "=" * 60)
            print("[COMPLETE] 모든 주문 처리 완료!")
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
    
        파리 뮤지엄 패스 자동 발권 봇 (연습용 데모)
    
        마이리얼트립 -> 공급사 포털 자동화 시뮬레이션
        2일권 / 4일권 / 6일권 자동 발권 및 이메일 발송
    
    ===========================================================
    """)
    
    print("이 프로그램은:")
    print("1. 마이리얼트립에서 미처리 주문을 가져옵니다")
    print("2. 공급사 포털에 자동으로 로그인합니다")
    print("3. 고객명(영문), 이메일, 패스 종류, 수량을 자동 입력합니다")
    print("4. 바우처를 발급하고 고객 이메일로 자동 발송합니다\n")
    
    print("잠시 후 자동으로 시작합니다...\n")
    time.sleep(2)
    
    bot = MuseumPassBot()
    bot.run_full_automation()
