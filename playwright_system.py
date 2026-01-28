# -*- coding: utf-8 -*-
"""
Playwright 버전 - 다중 사용자 자동 발권 시스템
여러 명이 동시에 사용 가능!
"""

from flask import Flask, render_template_string, jsonify, request
from playwright.sync_api import sync_playwright
import threading
import time
import json
import os
from datetime import datetime
from queue import Queue
from collections import deque

app = Flask(__name__)

# ========== 전역 상태 관리 ==========
class SystemStatus:
    def __init__(self):
        self.is_running = False
        self.current_task = None
        self.queue = deque()  # 대기열
        self.history = []  # 작업 이력 (최근 50개)
        self.logs = []
        self.lock = threading.Lock()
    
    def add_to_queue(self, task):
        """대기열에 작업 추가"""
        with self.lock:
            task['id'] = f"TASK-{int(time.time())}"
            task['status'] = 'waiting'
            task['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.queue.append(task)
            return task['id']
    
    def get_next_task(self):
        """다음 작업 가져오기"""
        with self.lock:
            if self.queue:
                return self.queue.popleft()
            return None
    
    def add_log(self, message, level='INFO'):
        """로그 추가"""
        with self.lock:
            self.logs.append({
                'time': datetime.now().strftime('%H:%M:%S'),
                'message': message,
                'level': level
            })
            if len(self.logs) > 100:
                self.logs = self.logs[-100:]
        print(f"[{level}] {message}")
    
    def add_history(self, result):
        """작업 이력 추가"""
        with self.lock:
            self.history.insert(0, result)
            if len(self.history) > 50:
                self.history = self.history[:50]
    
    def to_dict(self):
        """상태를 딕셔너리로 변환"""
        with self.lock:
            return {
                'is_running': self.is_running,
                'current_task': self.current_task,
                'queue': list(self.queue),
                'queue_count': len(self.queue),
                'history': self.history[:10],
                'logs': self.logs[-30:]
            }

status = SystemStatus()

# ========== Playwright 자동화 봇 ==========
class PlaywrightBot:
    """Playwright 기반 자동 발권 봇"""
    
    def __init__(self, headless=False):
        status.add_log("Playwright 봇 초기화 중...", "INFO")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            slow_mo=100  # 동작 사이 100ms 딜레이 (안정성)
        )
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        self.page = self.context.new_page()
        status.add_log("Playwright 봇 준비 완료!", "SUCCESS")
    
    def login_mrt(self, mrt_url):
        """마이리얼트립 로그인"""
        status.add_log("마이리얼트립 접속 중...", "INFO")
        self.page.goto(mrt_url)
        self.page.wait_for_load_state('networkidle')
        
        # 로그인 폼 입력
        self.page.fill('#email', 'partner@myrealtrip.com')
        self.page.fill('#password', 'demo1234')
        self.page.click('button[type="submit"]')
        
        # 로그인 완료 대기
        self.page.wait_for_timeout(1000)
        status.add_log("마이리얼트립 로그인 성공!", "SUCCESS")
    
    def get_orders(self):
        """주문 목록 가져오기"""
        status.add_log("주문 조회 중...", "INFO")
        
        orders = []
        rows = self.page.query_selector_all('.order-row[data-status="pending"]')
        
        for row in rows:
            pass_text = row.query_selector('.pass-type').inner_text()
            if '2일권' in pass_text:
                pass_type = '2DAY'
            elif '4일권' in pass_text:
                pass_type = '4DAY'
            elif '6일권' in pass_text:
                pass_type = '6DAY'
            else:
                pass_type = '2DAY'
            
            order = {
                'order_id': row.query_selector('.order-id').inner_text(),
                'customer_name': row.query_selector('.customer-name').inner_text(),
                'email': row.query_selector('.email').inner_text(),
                'pass_type': pass_type,
                'quantity': row.query_selector('.quantity').inner_text()
            }
            orders.append(order)
        
        status.add_log(f"{len(orders)}건의 주문 발견!", "SUCCESS")
        return orders
    
    def login_supplier(self, supplier_url):
        """공급사 포털 로그인"""
        status.add_log("공급사 포털 접속 중...", "INFO")
        self.page.goto(supplier_url)
        self.page.wait_for_load_state('networkidle')
        
        self.page.fill('#username', 'museum_partner')
        self.page.fill('#password', 'paris2024')
        self.page.click('button[type="submit"]')
        
        self.page.wait_for_timeout(1000)
        status.add_log("공급사 포털 로그인 성공!", "SUCCESS")
    
    def issue_voucher(self, order):
        """바우처 발급"""
        try:
            # 폼 초기화 대기
            self.page.wait_for_selector('#customerName', state='visible')
            
            # 고객 정보 입력
            self.page.fill('#customerName', order['customer_name'])
            self.page.fill('#email', order['email'])
            self.page.select_option('#passType', order['pass_type'])
            self.page.fill('#quantity', str(order['quantity']))
            
            # 발급 버튼 클릭
            self.page.click('#issueBtn')
            
            # 결과 대기
            self.page.wait_for_selector('#voucherCode', state='visible', timeout=10000)
            voucher_code = self.page.inner_text('#voucherCode')
            
            # 스크린샷 저장
            screenshot_path = f"screenshots/voucher_{order['order_id']}.png"
            os.makedirs('screenshots', exist_ok=True)
            self.page.screenshot(path=screenshot_path)
            
            # 폼 초기화 대기 (다음 발권을 위해)
            self.page.wait_for_timeout(2500)
            
            return {
                'success': True,
                'voucher_code': voucher_code,
                'screenshot': screenshot_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def close(self):
        """브라우저 종료"""
        self.context.close()
        self.browser.close()
        self.playwright.stop()
        status.add_log("브라우저 종료", "INFO")

# ========== 작업 처리 함수 ==========
def process_task(task):
    """작업 처리"""
    status.is_running = True
    status.current_task = task
    
    bot = None
    results = []
    
    try:
        # HTML 파일 경로
        mrt_url = f'file:///{os.path.abspath("museum_pass_mrt.html")}'
        supplier_url = f'file:///{os.path.abspath("museum_pass_supplier.html")}'
        
        # 봇 초기화
        bot = PlaywrightBot(headless=False)
        
        # 마이리얼트립 로그인 및 주문 가져오기
        bot.login_mrt(mrt_url)
        orders = bot.get_orders()
        
        if not orders:
            status.add_log("처리할 주문이 없습니다.", "WARNING")
            return
        
        # 공급사 포털 로그인
        bot.login_supplier(supplier_url)
        
        # 각 주문 처리
        success_count = 0
        fail_count = 0
        
        for i, order in enumerate(orders, 1):
            pass_name = {'2DAY': '2일권', '4DAY': '4일권', '6DAY': '6일권'}[order['pass_type']]
            status.add_log(f"[{i}/{len(orders)}] {order['customer_name']} - {pass_name} 처리 중...", "INFO")
            
            result = bot.issue_voucher(order)
            
            if result['success']:
                success_count += 1
                status.add_log(f"[OK] {order['order_id']}: {result['voucher_code']}", "SUCCESS")
                results.append({
                    'order_id': order['order_id'],
                    'customer_name': order['customer_name'],
                    'voucher_code': result['voucher_code'],
                    'status': 'success'
                })
            else:
                fail_count += 1
                status.add_log(f"[FAIL] {order['order_id']}: {result['error']}", "ERROR")
                results.append({
                    'order_id': order['order_id'],
                    'customer_name': order['customer_name'],
                    'error': result['error'],
                    'status': 'failed'
                })
            
            time.sleep(1)
        
        # 작업 이력 저장
        task_result = {
            'task_id': task['id'],
            'user': task['user'],
            'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(orders),
            'success': success_count,
            'failed': fail_count,
            'results': results
        }
        status.add_history(task_result)
        
        status.add_log(f"작업 완료! (성공: {success_count}, 실패: {fail_count})", "SUCCESS")
        
    except Exception as e:
        status.add_log(f"오류 발생: {str(e)}", "ERROR")
    
    finally:
        if bot:
            bot.close()
        status.is_running = False
        status.current_task = None

def worker_thread():
    """백그라운드 워커 - 대기열 처리"""
    while True:
        if not status.is_running:
            task = status.get_next_task()
            if task:
                process_task(task)
        time.sleep(1)

# 워커 스레드 시작
worker = threading.Thread(target=worker_thread, daemon=True)
worker.start()

# ========== HTML 템플릿 ==========
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>자동 발권 시스템 (Playwright)</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            margin-bottom: 10px;
            font-size: 32px;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        @media (max-width: 1000px) {
            .grid { grid-template-columns: 1fr; }
        }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h2 {
            margin-bottom: 20px;
            font-size: 18px;
            color: #4ecdc4;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .status-item {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .status-label {
            font-size: 12px;
            color: #888;
            margin-bottom: 5px;
        }
        .status-value {
            font-size: 24px;
            font-weight: bold;
        }
        .status-value.running { color: #4ecdc4; }
        .status-value.waiting { color: #ffd93d; }
        .status-value.success { color: #6bcb77; }
        .status-value.error { color: #ff6b6b; }
        .input-group {
            margin-bottom: 15px;
        }
        .input-group label {
            display: block;
            margin-bottom: 8px;
            color: #888;
        }
        .input-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 16px;
        }
        .input-group input:focus {
            outline: none;
            border-color: #4ecdc4;
        }
        .btn {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
            color: #fff;
        }
        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(78, 205, 196, 0.4);
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .queue-list {
            max-height: 200px;
            overflow-y: auto;
        }
        .queue-item {
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 5px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
        }
        .queue-item .user { color: #4ecdc4; }
        .queue-item .time { color: #888; font-size: 12px; }
        .logs {
            background: #0d1117;
            border-radius: 10px;
            padding: 15px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }
        .log-entry { margin: 4px 0; }
        .log-time { color: #666; }
        .log-SUCCESS { color: #6bcb77; }
        .log-ERROR { color: #ff6b6b; }
        .log-WARNING { color: #ffd93d; }
        .log-INFO { color: #58a6ff; }
        .history-item {
            padding: 12px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .history-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        .history-user { color: #4ecdc4; font-weight: bold; }
        .history-time { color: #888; font-size: 12px; }
        .history-stats {
            display: flex;
            gap: 15px;
            font-size: 14px;
        }
        .history-stats .success { color: #6bcb77; }
        .history-stats .failed { color: #ff6b6b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 자동 발권 시스템</h1>
        <p class="subtitle">Playwright 기반 | 다중 사용자 지원</p>
        
        <div class="grid">
            <!-- 왼쪽: 상태 및 작업 요청 -->
            <div>
                <div class="card">
                    <h2>시스템 상태</h2>
                    <div class="status-grid">
                        <div class="status-item">
                            <div class="status-label">현재 상태</div>
                            <div class="status-value" id="currentStatus">대기 중</div>
                        </div>
                        <div class="status-item">
                            <div class="status-label">대기열</div>
                            <div class="status-value waiting" id="queueCount">0</div>
                        </div>
                    </div>
                    
                    <div class="input-group">
                        <label>발권 담당자 (매니저)</label>
                        <input type="text" id="userName" placeholder="예: 홍길동 (본인 이름)">
                    </div>
                    <p style="color: #666; font-size: 12px; margin-bottom: 15px;">
                        ※ 고객 정보는 마이리얼트립에서 자동으로 가져옵니다
                    </p>
                    
                    <button class="btn btn-primary" id="submitBtn" onclick="submitTask()">
                        작업 요청
                    </button>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <h2>대기열</h2>
                    <div class="queue-list" id="queueList">
                        <p style="color: #666; text-align: center;">대기 중인 작업 없음</p>
                    </div>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <h2>최근 작업 이력</h2>
                    <div id="historyList">
                        <p style="color: #666; text-align: center;">작업 이력 없음</p>
                    </div>
                </div>
            </div>
            
            <!-- 오른쪽: 실시간 로그 -->
            <div class="card">
                <h2>실시간 로그</h2>
                <div class="logs" id="logs">
                    <div class="log-entry log-INFO">
                        <span class="log-time">[시스템]</span> 시스템 준비 완료
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function submitTask() {
            const userName = document.getElementById('userName').value.trim();
            if (!userName) {
                alert('이름을 입력해주세요!');
                return;
            }
            
            fetch('/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user: userName})
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert('작업이 대기열에 추가되었습니다!\\n작업 ID: ' + data.task_id);
                } else {
                    alert('오류: ' + data.message);
                }
            });
        }
        
        function updateStatus() {
            fetch('/status')
                .then(res => res.json())
                .then(data => {
                    // 현재 상태
                    const statusEl = document.getElementById('currentStatus');
                    if (data.is_running) {
                        statusEl.textContent = '처리 중';
                        statusEl.className = 'status-value running';
                    } else {
                        statusEl.textContent = '대기 중';
                        statusEl.className = 'status-value';
                    }
                    
                    // 대기열 카운트
                    document.getElementById('queueCount').textContent = data.queue_count;
                    
                    // 대기열 목록
                    const queueList = document.getElementById('queueList');
                    if (data.queue.length > 0) {
                        queueList.innerHTML = data.queue.map(task => `
                            <div class="queue-item">
                                <span class="user">담당: ${task.user}</span>
                                <span class="time">${task.created_at}</span>
                            </div>
                        `).join('');
                    } else {
                        queueList.innerHTML = '<p style="color: #666; text-align: center;">대기 중인 작업 없음</p>';
                    }
                    
                    // 로그
                    const logsEl = document.getElementById('logs');
                    logsEl.innerHTML = data.logs.map(log => `
                        <div class="log-entry log-${log.level}">
                            <span class="log-time">[${log.time}]</span> ${log.message}
                        </div>
                    `).join('');
                    logsEl.scrollTop = logsEl.scrollHeight;
                    
                    // 작업 이력
                    const historyEl = document.getElementById('historyList');
                    if (data.history.length > 0) {
                        historyEl.innerHTML = data.history.map(h => `
                            <div class="history-item">
                                <div class="history-header">
                                    <span class="history-user">담당: ${h.user}</span>
                                    <span class="history-time">${h.completed_at}</span>
                                </div>
                                <div class="history-stats">
                                    <span>총 ${h.total}건</span>
                                    <span class="success">성공 ${h.success}</span>
                                    <span class="failed">실패 ${h.failed}</span>
                                </div>
                            </div>
                        `).join('');
                    }
                });
        }
        
        // 1초마다 상태 업데이트
        setInterval(updateStatus, 1000);
        updateStatus();
    </script>
</body>
</html>
'''

# ========== Flask 라우트 ==========
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit_task():
    """작업 요청"""
    data = request.json
    user = data.get('user', '익명')
    
    task_id = status.add_to_queue({
        'user': user,
        'type': 'auto_issue'
    })
    
    status.add_log(f"[{user}] 작업 요청 (ID: {task_id})", "INFO")
    
    return jsonify({
        'success': True,
        'task_id': task_id,
        'message': '대기열에 추가되었습니다'
    })

@app.route('/status')
def get_status():
    """시스템 상태 조회"""
    return jsonify(status.to_dict())

# ========== 메인 ==========
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("[Playwright] 다중 사용자 자동 발권 시스템")
    print("=" * 60)
    print("\n[INFO] 브라우저에서 접속:")
    print("   - 로컬: http://localhost:5000")
    print("   - 팀 공유: http://[IP]:5000")
    print("\n[INFO] 여러 사용자가 동시 접속 가능!")
    print("[INFO] 작업은 대기열에서 순차 처리됩니다.")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
