# -*- coding: utf-8 -*-
"""
통합 웹 대시보드 - 실전용 완성 버전
팀원 누구나 브라우저로 접속해서 클릭 한 번으로 자동 발권
"""

from flask import Flask, render_template_string, jsonify, request
import threading
import time
from datetime import datetime
import os

# Selenium 관련
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# 전역 상태
status = {
    'is_running': False,
    'current_order': 0,
    'total_orders': 0,
    'processed_by': '',
    'start_time': None,
    'logs': [],
    'success_count': 0,
    'fail_count': 0
}

def add_log(message, level='INFO'):
    """로그 추가"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    status['logs'].append({
        'time': timestamp,
        'message': message,
        'level': level
    })
    print(f"[{timestamp}] {message}")

class AutoIssueBot:
    """자동 발권 봇"""
    
    def __init__(self):
        add_log("자동 발권 봇 초기화 중...")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        # options.add_argument('--headless')  # 백그라운드 실행 시
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 10)
        
        # HTML 파일 경로
        self.mrt_url = f'file:///{os.path.abspath("museum_pass_mrt.html")}'
        self.supplier_url = f'file:///{os.path.abspath("museum_pass_supplier.html")}'
        
        add_log("브라우저 준비 완료!", 'SUCCESS')
    
    def login_mrt(self):
        """마이리얼트립 로그인"""
        add_log("마이리얼트립 접속 중...")
        self.driver.get(self.mrt_url)
        time.sleep(1)
        
        email = self.wait.until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email.send_keys("partner@myrealtrip.com")
        
        password = self.driver.find_element(By.ID, "password")
        password.send_keys("demo1234")
        
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        
        time.sleep(1)
        add_log("마이리얼트립 로그인 성공!", 'SUCCESS')
    
    def get_orders(self):
        """주문 목록 가져오기"""
        add_log("주문 조회 중...")
        
        orders = []
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".order-row[data-status='pending']")
        
        for row in rows:
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
                'quantity': row.find_element(By.CLASS_NAME, 'quantity').text
            }
            orders.append(order)
        
        add_log(f"{len(orders)}건의 주문 발견!", 'SUCCESS')
        return orders
    
    def login_supplier(self):
        """공급사 포털 로그인"""
        add_log("공급사 포털 접속 중...")
        self.driver.get(self.supplier_url)
        time.sleep(1)
        
        username = self.wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username.send_keys("museum_partner")
        
        password = self.driver.find_element(By.ID, "password")
        password.send_keys("paris2024")
        
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        
        time.sleep(1)
        add_log("공급사 포털 로그인 성공!", 'SUCCESS')
    
    def issue_voucher(self, order):
        """바우처 발급"""
        try:
            # 고객명
            customer_name = self.wait.until(
                EC.presence_of_element_located((By.ID, "customerName"))
            )
            customer_name.clear()
            customer_name.send_keys(order['customer_name'])
            
            # 이메일
            email = self.driver.find_element(By.ID, "email")
            email.clear()
            email.send_keys(order['email'])
            
            # 패스 종류
            pass_type_select = Select(self.driver.find_element(By.ID, "passType"))
            pass_type_select.select_by_value(order['pass_type'])
            
            # 수량
            quantity = self.driver.find_element(By.ID, "quantity")
            quantity.clear()
            quantity.send_keys(order['quantity'])
            
            # 발급 버튼
            issue_btn = self.driver.find_element(By.ID, "issueBtn")
            issue_btn.click()
            
            time.sleep(3)
            
            # 바우처 코드 추출
            voucher_code = self.wait.until(
                EC.presence_of_element_located((By.ID, "voucherCode"))
            ).text
            
            return {
                'success': True,
                'voucher_code': voucher_code
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def close(self):
        """브라우저 종료"""
        time.sleep(2)
        self.driver.quit()

def run_automation(user_name):
    """백그라운드에서 자동화 실행"""
    status['is_running'] = True
    status['processed_by'] = user_name
    status['start_time'] = datetime.now()
    status['current_order'] = 0
    status['total_orders'] = 0
    status['success_count'] = 0
    status['fail_count'] = 0
    status['logs'] = []
    
    bot = None
    
    try:
        add_log(f"[{user_name}] 자동 발권 프로세스 시작", 'INFO')
        
        # 봇 초기화
        bot = AutoIssueBot()
        
        # 1. 마이리얼트립에서 주문 가져오기
        bot.login_mrt()
        orders = bot.get_orders()
        
        status['total_orders'] = len(orders)
        
        if not orders:
            add_log("처리할 주문이 없습니다.", 'WARNING')
            return
        
        # 2. 공급사 포털 로그인
        bot.login_supplier()
        
        # 3. 각 주문 처리
        for i, order in enumerate(orders, 1):
            status['current_order'] = i
            
            pass_name = {'2DAY': '2일권', '4DAY': '4일권', '6DAY': '6일권'}[order['pass_type']]
            add_log(f"[{i}/{len(orders)}] {order['customer_name']} - {pass_name} x{order['quantity']} 처리 중...", 'INFO')
            
            result = bot.issue_voucher(order)
            
            if result['success']:
                status['success_count'] += 1
                add_log(f"✓ {order['order_id']}: {result['voucher_code']} (이메일 발송 완료)", 'SUCCESS')
            else:
                status['fail_count'] += 1
                add_log(f"✗ {order['order_id']}: 실패 - {result['error']}", 'ERROR')
            
            time.sleep(2)
        
        add_log(f"[{user_name}] 모든 주문 처리 완료! (성공: {status['success_count']}, 실패: {status['fail_count']})", 'SUCCESS')
        
    except Exception as e:
        add_log(f"오류 발생: {str(e)}", 'ERROR')
    
    finally:
        if bot:
            bot.close()
        status['is_running'] = False
        add_log("브라우저 종료", 'INFO')

# HTML 템플릿
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>마이리얼트립 자동 발권 시스템</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
            font-size: 32px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .status-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .status-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
        }
        .status-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .status-value.success {
            color: #28a745;
        }
        .status-value.error {
            color: #dc3545;
        }
        .status-value.running {
            color: #667eea;
        }
        .progress {
            background: #e9ecef;
            border-radius: 10px;
            height: 40px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-bar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 16px;
        }
        .name-input {
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 15px;
            width: 100%;
        }
        .name-input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn-start {
            width: 100%;
            padding: 20px;
            font-size: 20px;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn-start:hover:not(:disabled) {
            transform: translateY(-2px);
        }
        .btn-start:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .logs {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 10px;
            height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin-top: 20px;
        }
        .log-entry {
            margin: 5px 0;
            padding: 5px 0;
        }
        .log-time {
            color: #858585;
        }
        .log-success {
            color: #4ec9b0;
        }
        .log-error {
            color: #f48771;
        }
        .log-warning {
            color: #dcdcaa;
        }
        .log-info {
            color: #d4d4d4;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 마이리얼트립 자동 발권 시스템</h1>
        <p class="subtitle">팀원 누구나 클릭 한 번으로 자동 발권</p>
        
        <div class="status-grid">
            <div class="status-card">
                <div class="status-label">현재 상태</div>
                <div class="status-value" id="status">대기 중</div>
            </div>
            <div class="status-card">
                <div class="status-label">처리자</div>
                <div class="status-value" id="processor">-</div>
            </div>
            <div class="status-card">
                <div class="status-label">처리 진행</div>
                <div class="status-value running" id="progress">0 / 0</div>
            </div>
            <div class="status-card">
                <div class="status-label">성공 / 실패</div>
                <div class="status-value">
                    <span class="success" id="successCount">0</span> / 
                    <span class="error" id="failCount">0</span>
                </div>
            </div>
        </div>
        
        <div class="progress">
            <div class="progress-bar" id="progressBar" style="width: 0%">0%</div>
        </div>
        
        <input type="text" id="userName" class="name-input" placeholder="👤 본인 이름을 입력하세요 (예: 홍길동)">
        
        <button class="btn-start" id="startBtn" onclick="startAutomation()">
            🚀 자동 발권 시작
        </button>
        
        <div class="logs" id="logs">
            <div class="log-entry log-info">
                <span class="log-time">[시스템]</span> 준비 완료. 이름을 입력하고 버튼을 클릭하여 시작하세요.
            </div>
        </div>
    </div>
    
    <script>
        let isRunning = false;
        let statusCheckInterval = null;
        
        function startAutomation() {
            const userName = document.getElementById('userName').value.trim();
            
            if (!userName) {
                alert('⚠️ 이름을 입력해주세요!');
                document.getElementById('userName').focus();
                return;
            }
            
            if (isRunning) {
                alert('⚠️ 이미 처리 중입니다!');
                return;
            }
            
            if (!confirm(`${userName}님, 자동 발권을 시작하시겠습니까?`)) {
                return;
            }
            
            // 버튼 비활성화
            const btn = document.getElementById('startBtn');
            btn.disabled = true;
            btn.textContent = '⏳ 처리 중...';
            
            // 서버에 시작 요청
            fetch('/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user_name: userName})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    isRunning = true;
                    statusCheckInterval = setInterval(updateStatus, 1000);
                } else {
                    alert('❌ ' + data.message);
                    resetButton();
                }
            })
            .catch(error => {
                alert('❌ 서버 연결 실패: ' + error);
                resetButton();
            });
        }
        
        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    // 상태 업데이트
                    document.getElementById('status').textContent = 
                        data.is_running ? '처리 중 🟢' : '완료 ✅';
                    document.getElementById('processor').textContent = 
                        data.processed_by || '-';
                    document.getElementById('progress').textContent = 
                        `${data.current_order} / ${data.total_orders}`;
                    document.getElementById('successCount').textContent = data.success_count;
                    document.getElementById('failCount').textContent = data.fail_count;
                    
                    // 진행률
                    const percent = data.total_orders > 0 
                        ? Math.round((data.current_order / data.total_orders) * 100)
                        : 0;
                    const progressBar = document.getElementById('progressBar');
                    progressBar.style.width = percent + '%';
                    progressBar.textContent = percent + '%';
                    
                    // 로그 업데이트
                    const logsDiv = document.getElementById('logs');
                    logsDiv.innerHTML = data.logs.map(log => {
                        const levelClass = 'log-' + log.level.toLowerCase();
                        return `<div class="log-entry ${levelClass}"><span class="log-time">[${log.time}]</span> ${log.message}</div>`;
                    }).join('');
                    logsDiv.scrollTop = logsDiv.scrollHeight;
                    
                    // 완료되면 업데이트 중지
                    if (!data.is_running && isRunning) {
                        clearInterval(statusCheckInterval);
                        resetButton();
                        
                        if (data.total_orders > 0) {
                            alert(`✅ 처리 완료!\\n성공: ${data.success_count}건\\n실패: ${data.fail_count}건`);
                        }
                    }
                })
                .catch(error => {
                    console.error('상태 업데이트 실패:', error);
                });
        }
        
        function resetButton() {
            isRunning = false;
            const btn = document.getElementById('startBtn');
            btn.disabled = false;
            btn.textContent = '🚀 자동 발권 시작';
        }
        
        // 페이지 로드 시 상태 확인
        window.onload = function() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    if (data.is_running) {
                        isRunning = true;
                        document.getElementById('startBtn').disabled = true;
                        document.getElementById('startBtn').textContent = '⏳ 처리 중...';
                        statusCheckInterval = setInterval(updateStatus, 1000);
                    }
                });
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """메인 페이지"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/start', methods=['POST'])
def start_automation():
    """자동화 시작"""
    if status['is_running']:
        return jsonify({'success': False, 'message': '이미 처리 중입니다!'})
    
    data = request.json
    user_name = data.get('user_name', '익명')
    
    # 백그라운드 스레드로 실행
    thread = threading.Thread(target=run_automation, args=(user_name,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': '시작되었습니다'})

@app.route('/status')
def get_status():
    """현재 상태 조회"""
    return jsonify(status)

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("[SERVER] 마이리얼트립 자동 발권 시스템 시작!")
    print("=" * 60)
    print("\n[INFO] 브라우저에서 접속:")
    print("   - 로컬: http://localhost:5000")
    print("   - 팀 공유: http://[이 PC의 IP]:5000")
    print("\n[TIP] 팀원들에게 위 주소를 공유하세요!")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
