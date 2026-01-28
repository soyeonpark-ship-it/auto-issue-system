# -*- coding: utf-8 -*-
"""
Flask 웹 대시보드 - 팀원 누구나 사용 가능
"""

from flask import Flask, render_template, jsonify, request
import threading
import time
from datetime import datetime

app = Flask(__name__)

# 전역 상태
processing_status = {
    'is_running': False,
    'current_order': 0,
    'total_orders': 0,
    'processed_by': '',
    'start_time': None,
    'logs': []
}

def log(message):
    """로그 추가"""
    processing_status['logs'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message
    })

def run_automation(user_name):
    """백그라운드에서 자동화 실행"""
    processing_status['is_running'] = True
    processing_status['processed_by'] = user_name
    processing_status['start_time'] = datetime.now()
    processing_status['logs'] = []
    
    try:
        log(f"[{user_name}] 자동 발권 시작")
        
        # 실제 자동화 코드 (museum_pass_auto.py의 로직)
        from museum_pass_auto import MuseumPassBot
        
        bot = MuseumPassBot()
        
        # 1. 마이리얼트립에서 주문 가져오기
        log("마이리얼트립 로그인 중...")
        bot.login_mrt()
        
        log("주문 조회 중...")
        orders = bot.get_pending_orders()
        
        processing_status['total_orders'] = len(orders)
        log(f"{len(orders)}건의 주문 발견")
        
        # 2. 공급사 포털 로그인
        log("공급사 포털 로그인 중...")
        bot.login_supplier()
        
        # 3. 각 주문 처리
        for i, order in enumerate(orders, 1):
            processing_status['current_order'] = i
            log(f"[{i}/{len(orders)}] {order['customer_name']} 처리 중...")
            
            result = bot.issue_voucher(order)
            
            if result['success']:
                log(f"✓ {order['order_id']} 발권 완료: {result['voucher_code']}")
            else:
                log(f"✗ {order['order_id']} 실패: {result['error']}")
            
            time.sleep(2)
        
        log(f"[{user_name}] 모든 주문 처리 완료!")
        
    except Exception as e:
        log(f"오류 발생: {str(e)}")
    
    finally:
        processing_status['is_running'] = False

@app.route('/')
def index():
    """메인 페이지"""
    return '''
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
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }
        .status-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .status-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #dee2e6;
        }
        .status-row:last-child {
            border-bottom: none;
        }
        .status-label {
            font-weight: 600;
            color: #666;
        }
        .status-value {
            color: #333;
            font-weight: bold;
        }
        .btn-start {
            width: 100%;
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn-start:hover {
            transform: translateY(-2px);
        }
        .btn-start:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .logs {
            background: #1e1e1e;
            color: #00ff00;
            padding: 20px;
            border-radius: 10px;
            height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            margin-top: 20px;
        }
        .log-entry {
            margin: 5px 0;
        }
        .progress {
            background: #e9ecef;
            border-radius: 10px;
            height: 30px;
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
        }
        .name-input {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 16px;
            margin-bottom: 20px;
            width: 100%;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 마이리얼트립 자동 발권 시스템</h1>
        
        <div class="status-card">
            <div class="status-row">
                <span class="status-label">현재 상태:</span>
                <span class="status-value" id="status">대기 중</span>
            </div>
            <div class="status-row">
                <span class="status-label">처리자:</span>
                <span class="status-value" id="processor">-</span>
            </div>
            <div class="status-row">
                <span class="status-label">처리 진행:</span>
                <span class="status-value" id="progress">0 / 0</span>
            </div>
        </div>
        
        <div class="progress">
            <div class="progress-bar" id="progress-bar" style="width: 0%">0%</div>
        </div>
        
        <input type="text" id="userName" class="name-input" placeholder="본인 이름을 입력하세요 (예: 홍길동)">
        
        <button class="btn-start" id="startBtn" onclick="startAutomation()">
            자동 발권 시작
        </button>
        
        <div class="logs" id="logs">
            <div class="log-entry">시스템 준비 완료. 버튼을 클릭하여 시작하세요.</div>
        </div>
    </div>
    
    <script>
        let isRunning = false;
        
        function startAutomation() {
            const userName = document.getElementById('userName').value.trim();
            
            if (!userName) {
                alert('이름을 입력해주세요!');
                return;
            }
            
            if (isRunning) {
                alert('이미 처리 중입니다!');
                return;
            }
            
            if (!confirm(`${userName}님, 자동 발권을 시작하시겠습니까?`)) {
                return;
            }
            
            // 버튼 비활성화
            document.getElementById('startBtn').disabled = true;
            document.getElementById('startBtn').textContent = '처리 중...';
            
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
                    checkStatus();
                } else {
                    alert(data.message);
                    resetButton();
                }
            });
        }
        
        function checkStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    // 상태 업데이트
                    document.getElementById('status').textContent = 
                        data.is_running ? '처리 중' : '완료';
                    document.getElementById('processor').textContent = 
                        data.processed_by || '-';
                    document.getElementById('progress').textContent = 
                        `${data.current_order} / ${data.total_orders}`;
                    
                    // 진행률
                    const percent = data.total_orders > 0 
                        ? Math.round((data.current_order / data.total_orders) * 100)
                        : 0;
                    document.getElementById('progress-bar').style.width = percent + '%';
                    document.getElementById('progress-bar').textContent = percent + '%';
                    
                    // 로그 업데이트
                    const logsDiv = document.getElementById('logs');
                    logsDiv.innerHTML = data.logs.map(log => 
                        `<div class="log-entry">[${log.time}] ${log.message}</div>`
                    ).join('');
                    logsDiv.scrollTop = logsDiv.scrollHeight;
                    
                    // 계속 업데이트
                    if (data.is_running) {
                        setTimeout(checkStatus, 1000);
                    } else {
                        resetButton();
                    }
                });
        }
        
        function resetButton() {
            isRunning = false;
            document.getElementById('startBtn').disabled = false;
            document.getElementById('startBtn').textContent = '자동 발권 시작';
        }
        
        // 페이지 로드 시 상태 확인
        window.onload = function() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    if (data.is_running) {
                        isRunning = true;
                        document.getElementById('startBtn').disabled = true;
                        document.getElementById('startBtn').textContent = '처리 중...';
                        checkStatus();
                    }
                });
        };
    </script>
</body>
</html>
    '''

@app.route('/start', methods=['POST'])
def start_automation():
    """자동화 시작"""
    if processing_status['is_running']:
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
    return jsonify(processing_status)

if __name__ == '__main__':
    print("=" * 60)
    print("웹 대시보드 서버 시작!")
    print("브라우저에서 접속: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
