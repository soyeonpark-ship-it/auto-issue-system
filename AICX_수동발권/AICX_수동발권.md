# AICX_수동발권

## 프로세스 개요

AICX 수동발권매니저가 발권시트에서 예약을 확인하고 티켓마스터에서 수동 발권을 진행하는 프로세스입니다.

## 프로세스 플로우차트

```mermaid
flowchart TD
    %% 시작 노드
    Start([온라인: AICX 수동발권 시작]):::online

    %% AICX - 발권시트
    subgraph AICX_Sheet["AICX - 발권시트"]
        direction TB
        A1[온라인: 예약 내역 확인]:::online
        A2[온라인: 확정 버튼 클릭]:::online
    end

    %% AICX - 티켓마스터
    subgraph AICX_TicketMaster["AICX - 티켓마스터 시스템"]
        direction TB
        B1[온라인: 티켓마스터 로그인]:::online
        B2[온라인: 발권 처리]:::online
    end

    %% AICX - 발권시트 (정보 기입)
    subgraph AICX_Sheet_Update["AICX - 발권시트"]
        direction TB
        C1[온라인: 발권 정보 기입]:::online
    end

    %% 종료 노드
    End([온라인: AICX 수동발권 종료]):::online

    %% 연결 흐름
    Start --> A1
    A1 --> A2
    A2 --> B1
    B1 --> B2
    B2 --> C1
    C1 --> End

    %% 스타일 정의
    classDef online fill:#FFF9C4,stroke:#FFD54F,stroke-width:2px,color:#000
    classDef offline fill:#FFE0B2,stroke:#FFB74D,stroke-width:2px,color:#000
```

## 프로세스 상세 설명

### 1. 예약 확인 단계
- 수동발권매니저가 발권시트에서 예약 내역을 확인합니다
- 확정 버튼을 클릭합니다

### 2. 발권 처리 단계
- LAFC 티켓마스터에 로그인합니다
- 발권 처리를 진행합니다

### 3. 정보 기입 단계
- 발권 완료 후 발권시트에 발권 정보를 기입합니다
