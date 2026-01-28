# -*- coding: utf-8 -*-
"""
Railway 클라우드 배포용 - 자동 발권 시스템 (데모 버전)
Playwright 없이 순수 Flask로 동작
"""

from flask import Flask, render_template_string, jsonify, request
import threading
import time
import os
from datetime import datetime
from collections import deque

app = Flask(__name__)

# ========== 전역 상태 관리 ==========
class SystemStatus:
    def __init__(self):
        self.is_running = False
        self.current_task = None
        self.queue = deque()
        self.history = []
        self.logs = []
        self.lock = threading.Lock()
    
    def add_to_queue(self, task):
        with self.lock:
            task['id'] = f"TASK-{int(time.time())}"
            task['status'] = 'waiting'
            task['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.queue.append(task)
            return task['id']
    
    def get_next_task(self):
        with self.lock:
            if self.queue:
                return self.queue.popleft()
            return None
    
    def add_log(self, message, level='INFO'):
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
        with self.lock:
            self.history.insert(0, result)
            if len(self.history) > 50:
                self.history = self.history[:50]
    
    def to_dict(self):
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

# ========== 데모 자동화 ==========
def run_demo_automation(task):
    """데모 모드: 실제 자동화 시뮬레이션"""
    status.is_running = True
    status.current_task = task
    
    try:
        status.add_log(f"[{task['user']}] 작업 시작", "INFO")
        
        # 데모 주문 데이터
        demo_orders = [
            {'order_id': 'MRT-001', 'customer_name': 'HONG GILDONG', 'email': 'hong@test.com', 'pass_type': '2DAY', 'quantity': '2'},
            {'order_id': 'MRT-002', 'customer_name': 'KIM YOUNGHI', 'email': 'kim@test.com', 'pass_type': '4DAY', 'quantity': '1'},
            {'order_id': 'MRT-003', 'customer_name': 'LEE MINSOO', 'email': 'lee@test.com', 'pass_type': '6DAY', 'quantity': '3'},
            {'order_id': 'MRT-004', 'customer_name': 'PARK JISOO', 'email': 'park@test.com', 'pass_type': '2DAY', 'quantity': '1'},
            {'order_id': 'MRT-005', 'customer_name': 'CHOI YUNA', 'email': 'choi@test.com', 'pass_type': '4DAY', 'quantity': '2'},
        ]
        
        status.add_log("마이리얼트립 파트너센터 접속 중...", "INFO")
        time.sleep(1.5)
        status.add_log("마이리얼트립 로그인 성공!", "SUCCESS")
        
        status.add_log(f"{len(demo_orders)}건의 미발권 주문 발견!", "SUCCESS")
        time.sleep(1)
        
        status.add_log("공급사 포털 접속 중...", "INFO")
        time.sleep(1.5)
        status.add_log("공급사 포털 로그인 성공!", "SUCCESS")
        
        results = []
        success_count = 0
        
        for i, order in enumerate(demo_orders, 1):
            pass_name = {'2DAY': '2일권', '4DAY': '4일권', '6DAY': '6일권'}[order['pass_type']]
            status.add_log(f"[{i}/{len(demo_orders)}] {order['customer_name']} - {pass_name} x{order['quantity']} 처리 중...", "INFO")
            
            time.sleep(2)  # 처리 시뮬레이션
            
            voucher_code = f"PMP-{order['pass_type']}-{int(time.time())}"
            success_count += 1
            
            status.add_log(f"[OK] 바우처 발급: {voucher_code}", "SUCCESS")
            status.add_log(f"[EMAIL] {order['email']}로 바우처 발송 완료", "SUCCESS")
            
            results.append({
                'order_id': order['order_id'],
                'customer_name': order['customer_name'],
                'voucher_code': voucher_code,
                'status': 'success'
            })
            
            time.sleep(0.5)
        
        # 작업 이력 저장
        task_result = {
            'task_id': task['id'],
            'user': task['user'],
            'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(demo_orders),
            'success': success_count,
            'failed': 0,
            'results': results
        }
        status.add_history(task_result)
        
        status.add_log(f"작업 완료! (성공: {success_count}건, 실패: 0건)", "SUCCESS")
        
    except Exception as e:
        status.add_log(f"오류 발생: {str(e)}", "ERROR")
    
    finally:
        status.is_running = False
        status.current_task = None

def worker_thread():
    while True:
        if not status.is_running:
            task = status.get_next_task()
            if task:
                run_demo_automation(task)
        time.sleep(1)

worker = threading.Thread(target=worker_thread, daemon=True)
worker.start()

# ========== HTML 템플릿 ==========
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>자동 발권 시스템</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Noto Sans KR', sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 8px; font-size: 26px; font-weight: 700; }
        .subtitle { text-align: center; color: #888; margin-bottom: 25px; font-size: 13px; }
        .demo-badge {
            display: inline-block;
            background: linear-gradient(135deg, #ff6b6b, #ee5a5a);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            margin-left: 10px;
            font-weight: 500;
        }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
        .card {
            background: rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
        }
        .card h2 { margin-bottom: 18px; font-size: 15px; color: #4ecdc4; font-weight: 600; }
        .status-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 20px; }
        .status-item {
            background: rgba(255,255,255,0.04);
            padding: 16px;
            border-radius: 12px;
            text-align: center;
        }
        .status-label { font-size: 11px; color: #777; margin-bottom: 6px; }
        .status-value { font-size: 24px; font-weight: 700; }
        .status-value.running { color: #4ecdc4; animation: pulse 1.5s infinite; }
        .status-value.waiting { color: #ffd93d; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
        .input-group { margin-bottom: 16px; }
        .input-group label { display: block; margin-bottom: 8px; color: #999; font-size: 13px; }
        .input-group input {
            width: 100%;
            padding: 14px 16px;
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 10px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 15px;
            transition: all 0.2s;
        }
        .input-group input:focus { outline: none; border-color: #4ecdc4; background: rgba(78,205,196,0.1); }
        .input-group input::placeholder { color: #555; }
        .input-group small { color: #555; font-size: 11px; margin-top: 6px; display: block; }
        .btn {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
            color: #fff;
        }
        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(78, 205, 196, 0.35);
        }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .queue-item {
            padding: 12px 14px;
            background: rgba(255,255,255,0.04);
            border-radius: 8px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }
        .queue-item .user { color: #4ecdc4; font-weight: 500; }
        .queue-item .time { color: #555; font-size: 11px; }
        .logs {
            background: #0a0d12;
            border-radius: 12px;
            padding: 16px;
            height: 380px;
            overflow-y: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            line-height: 1.6;
        }
        .logs::-webkit-scrollbar { width: 6px; }
        .logs::-webkit-scrollbar-track { background: transparent; }
        .logs::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
        .log-entry { margin: 2px 0; }
        .log-time { color: #444; }
        .log-SUCCESS { color: #6bcb77; }
        .log-ERROR { color: #ff6b6b; }
        .log-WARNING { color: #ffd93d; }
        .log-INFO { color: #58a6ff; }
        .history-item {
            padding: 14px;
            background: rgba(255,255,255,0.04);
            border-radius: 10px;
            margin-bottom: 10px;
            font-size: 13px;
        }
        .history-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
        .history-user { color: #4ecdc4; font-weight: 600; }
        .history-time { color: #555; font-size: 11px; }
        .history-stats { display: flex; gap: 16px; }
        .history-stats span { font-size: 12px; }
        .history-stats .success { color: #6bcb77; }
        .history-stats .failed { color: #ff6b6b; }
        .empty-msg { color: #444; text-align: center; padding: 25px; font-size: 13px; }
        .footer { text-align: center; margin-top: 30px; color: #444; font-size: 11px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>자동 발권 시스템 <span class="demo-badge">DEMO</span></h1>
        <p class="subtitle">클라우드 배포 | 다중 사용자 지원 | 24시간 운영</p>
        
        <div class="grid">
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
                        <input type="text" id="userName" placeholder="예: 홍길동">
                        <small>* 고객 정보는 마이리얼트립에서 자동으로 가져옵니다</small>
                    </div>
                    
                    <button class="btn btn-primary" onclick="submitTask()">
                        작업 요청
                    </button>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <h2>대기열</h2>
                    <div id="queueList">
                        <p class="empty-msg">대기 중인 작업 없음</p>
                    </div>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <h2>최근 작업 이력</h2>
                    <div id="historyList">
                        <p class="empty-msg">작업 이력 없음</p>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>실시간 로그</h2>
                <div class="logs" id="logs">
                    <div class="log-entry log-INFO">
                        <span class="log-time">[시스템]</span> 클라우드 서버 준비 완료 - 작업 요청을 기다리는 중...
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            Powered by Railway | Auto Issue System v1.0
        </div>
    </div>
    
    <script>
        function submitTask() {
            const userName = document.getElementById('userName').value.trim();
            if (!userName) {
                alert('담당자 이름을 입력해주세요!');
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
                    document.getElementById('userName').value = '';
                }
            });
        }
        
        function updateStatus() {
            fetch('/status')
                .then(res => res.json())
                .then(data => {
                    const statusEl = document.getElementById('currentStatus');
                    if (data.is_running) {
                        statusEl.textContent = '처리 중';
                        statusEl.className = 'status-value running';
                    } else {
                        statusEl.textContent = '대기 중';
                        statusEl.className = 'status-value';
                    }
                    
                    document.getElementById('queueCount').textContent = data.queue_count;
                    
                    const queueList = document.getElementById('queueList');
                    if (data.queue.length > 0) {
                        queueList.innerHTML = data.queue.map(task => 
                            '<div class="queue-item"><span class="user">담당: ' + task.user + '</span><span class="time">' + task.created_at + '</span></div>'
                        ).join('');
                    } else {
                        queueList.innerHTML = '<p class="empty-msg">대기 중인 작업 없음</p>';
                    }
                    
                    const logsEl = document.getElementById('logs');
                    if (data.logs.length > 0) {
                        logsEl.innerHTML = data.logs.map(log => 
                            '<div class="log-entry log-' + log.level + '"><span class="log-time">[' + log.time + ']</span> ' + log.message + '</div>'
                        ).join('');
                        logsEl.scrollTop = logsEl.scrollHeight;
                    }
                    
                    const historyEl = document.getElementById('historyList');
                    if (data.history.length > 0) {
                        historyEl.innerHTML = data.history.map(h => 
                            '<div class="history-item"><div class="history-header"><span class="history-user">담당: ' + h.user + '</span><span class="history-time">' + h.completed_at + '</span></div><div class="history-stats"><span>총 ' + h.total + '건</span><span class="success">성공 ' + h.success + '</span><span class="failed">실패 ' + h.failed + '</span></div></div>'
                        ).join('');
                    }
                });
        }
        
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
    data = request.json
    user = data.get('user', '익명')
    
    task_id = status.add_to_queue({
        'user': user,
        'type': 'auto_issue'
    })
    
    status.add_log(f"[{user}] 작업 요청 (ID: {task_id})", "INFO")
    
    return jsonify({
        'success': True,
        'task_id': task_id
    })

@app.route('/status')
def get_status():
    return jsonify(status.to_dict())

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

# ========== 메인 ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[Railway] Auto Issue System")
    print(f"[INFO] Server running on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
