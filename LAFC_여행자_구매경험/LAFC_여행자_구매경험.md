# LAFC_여행자_구매경험

## 프로세스 개요

LAFC 티켓 구매부터 현장 입장까지의 여행자 구매 경험 프로세스입니다.

## 프로세스 플로우차트

```mermaid
flowchart TD
    %% 시작 노드
    Start([온라인: 여행자 구매경험 시작]):::online

    %% 조건 분기 노드 (LAFC 마스터 계정 보유 여부)
    Cond1{온라인: LAFC 티켓 마스터 계정 보유 여부}:::online

    %% 여행자 - 마이리얼트립 결제단
    subgraph Traveler_Payment["여행자 - 마이리얼트립 결제단"]
        direction TB
        A1[온라인: 기존 계정주 이름, 이메일 입력]:::online
        A2[온라인: 신규 가입용 이름, 이메일 입력]:::online
        B1[온라인: 결제 진행]:::online
    end

    %% 마이리얼트립 시스템 - 발권
    subgraph MyTrip_Issue["마이리얼트립 시스템"]
        direction TB
        C1[온라인: 발권 처리]:::online
    end

    %% 티켓마스터 시스템 - 이메일 발송
    subgraph TicketMaster_Email["티켓마스터 시스템"]
        direction TB
        D1[온라인: 티켓 이메일 발송]:::online
    end

    %% 여행자 - 이메일 확인
    subgraph Traveler_Email["여행자 - 이메일"]
        direction TB
        E1[온라인: 티켓 수신 확인]:::online
        E2[온라인: ACCEPT 버튼 클릭]:::online
    end

    %% 티켓마스터 시스템 - 로그인 안내
    subgraph TicketMaster_Login["티켓마스터 시스템"]
        direction TB
        F1[온라인: 티켓마스터 계정 로그인 안내]:::online
    end

    %% 여행자 - 티켓 확인
    subgraph Traveler_Ticket["여행자 - 티켓마스터 앱"]
        direction TB
        G1[온라인: 티켓 확인]:::online
        G2[온라인: 바코드 표시]:::online
    end

    %% 현장 - 입장
    subgraph Venue_Entry["현장 스태프"]
        direction TB
        H1[온라인: 바코드 스캔]:::online
        H2[온라인: 입장 처리]:::online
    end

    %% 종료 노드
    End([온라인: 여행자 구매경험 종료]):::online

    %% 연결 흐름
    Start --> Cond1
    
    %% 계정 보유 여부에 따른 분기
    Cond1 -->|보유| A1
    Cond1 -->|미보유| A2
    
    %% 결제 진행
    A1 --> B1
    A2 --> B1
    
    %% 발권 및 티켓 발송
    B1 --> C1
    C1 --> D1
    
    %% 여행자 티켓 수신 및 승인
    D1 --> E1
    E1 --> E2
    
    %% 로그인 안내 및 티켓 확인
    E2 --> F1
    F1 --> G1
    G1 --> G2
    
    %% 현장 입장
    G2 --> H1
    H1 --> H2
    H2 --> End

    %% 스타일 정의
    classDef online fill:#FFF9C4,stroke:#FFD54F,stroke-width:2px,color:#000
    classDef offline fill:#FFE0B2,stroke:#FFB74D,stroke-width:2px,color:#000
```

## 프로세스 상세 설명

### 1. 결제 단계
- 여행자가 마이리얼트립 결제단에서 LAFC 티켓 마스터 계정 보유 여부를 확인합니다
- **기존 계정 보유**: 계정주 이름과 이메일을 입력합니다
- **계정 미보유**: 앞으로 가입할 이름과 이메일 주소를 입력합니다
- 입력 완료 후 결제를 진행합니다

### 2. 발권 및 티켓 발송
- 마이리얼트립에서 발권 처리를 진행합니다
- 티켓마스터 시스템에서 입력된 이메일로 티켓을 발송합니다

### 3. 티켓 승인 및 확인
- 여행자가 이메일로 티켓을 수신합니다
- ACCEPT 버튼을 클릭합니다
- 티켓마스터 계정 로그인 안내를 받습니다
- 티켓마스터 앱에서 로그인 후 티켓을 확인합니다

### 4. 현장 입장
- 여행자가 티켓 바코드를 표시합니다
- 현장 스태프가 바코드를 스캔합니다
- 입장 처리가 완료됩니다
