# sonnet_테스트_발권_프로세스

## 프로세스 개요

VOF 시스템에서 자동 확정 가능 여부를 판단한 후, 불가능한 경우 운영팀이 항공사 일치 여부, 금액 일치 여부, 스탑오버 횟수, 증빙서류 필요 여부를 각각 확인하여 처리하는 발권 프로세스입니다.

## 프로세스 플로우차트

```mermaid
flowchart TD
    %% 시작 노드
    Start([온라인: sonnet_테스트_발권_프로세스 시작]):::online

    %% VOF 시스템 - 자동 확정 판단
    subgraph VOF_Auto["VOF 시스템"]
        direction TB
        A1{온라인: 자동 확정 가능 여부 판단}:::online
        A2[온라인: 자동 확정 처리]:::online
        A3[온라인: 결제 및 발권]:::online
    end

    %% 운영팀 - VOF 시스템 (초기 검토)
    subgraph OPS_VOF_Review["운영팀 - VOF 시스템"]
        direction TB
        B1[온라인: 미확정 사유 확인]:::online
        B2[온라인: 코멘트 검토]:::online
    end

    %% 조건 분기 노드들 (subgraph 외부, 병렬)
    Cond1{온라인: 출국 귀국 항공사 동일 여부}:::online
    Cond2{온라인: 예약 금액과 발권 금액 동일 여부}:::online
    Cond3{온라인: 스탑오버 2회 이상 여부}:::online
    Cond4{온라인: 증빙서류 필요 여부}:::online

    %% ===== 분기 경로 1: 항공사 상이 처리 =====
    %% C1(VOF) → D1(GDS) → E1(VOF)
    %% 중간에 GDS가 끼어있으므로 VOF 분리
    subgraph OPS_VOF_Schedule["운영팀 - VOF 시스템"]
        direction TB
        C1[온라인: 여행 일정 확인]:::online
    end

    subgraph OPS_GDS_Reserve["운영팀 - GDS 시스템"]
        direction TB
        D1[온라인: 확정 가능한 예약인지 조회]:::online
    end

    subgraph OPS_VOF_Reserve["운영팀 - VOF 시스템"]
        direction TB
        E1[온라인: 예약 확정 또는 취소 처리]:::online
    end

    %% ===== 분기 경로 2: 금액 상이 처리 =====
    %% F1(VOF) → G1(ZD) → H1(여행자) → I1(GDS) → J1(VOF)
    %% 중간에 다른 시스템이 끼어있으므로 각각 분리
    subgraph OPS_VOF_TL["운영팀 - VOF 시스템"]
        direction TB
        F1[온라인: TL 연장]:::online
    end

    subgraph OPS_ZD_Price["운영팀 - ZD 이메일"]
        direction TB
        G1[온라인: 금액 상이 안내 발송]:::online
    end

    subgraph Traveler_Confirm["여행자"]
        direction TB
        H1[온라인: 컨펌 회신]:::online
    end

    subgraph OPS_GDS_Price["운영팀 - GDS 시스템"]
        direction TB
        I1[온라인: 최종 금액 재확인]:::online
    end

    subgraph OPS_VOF_PriceConfirm["운영팀 - VOF 시스템"]
        direction TB
        J1[온라인: 확정 처리]:::online
    end

    %% ===== 분기 경로 3: 스탑오버 처리 =====
    %% K1(GDS) → K2(GDS) → L1(VOF) → M1(VOF)
    %% 연속된 GDS는 통합, 연속된 VOF는 통합
    subgraph OPS_GDS_Stopover["운영팀 - GDS 시스템"]
        direction TB
        K1[온라인: 운임 규정 확인]:::online
        K2[온라인: 스탑오버 가능 여부 확인]:::online
    end

    subgraph OPS_VOF_Stopover["운영팀 - VOF 시스템"]
        direction TB
        L1[온라인: 사용 가능한 일정 재확인]:::online
        M1[온라인: 확정 또는 취소 처리]:::online
    end

    %% ===== 분기 경로 4: 증빙서류 처리 =====
    %% N1(ZD) → O1(마이트립) → P1(VOF) → Q1(VOF)
    %% 연속된 VOF는 통합
    subgraph OPS_ZD_Doc["운영팀 - ZD 이메일"]
        direction TB
        N1[온라인: 서류 제출 요청 발송]:::online
    end

    subgraph Traveler_MyTrip["여행자 - 마이트립 내여행"]
        direction TB
        O1[온라인: 서류 업로드]:::online
    end

    subgraph OPS_VOF_Doc["운영팀 - VOF 시스템"]
        direction TB
        P1[온라인: 서류 확인]:::online
        Q1[온라인: 확정 진행]:::online
    end

    %% 종료 노드
    End([온라인: sonnet_테스트_발권_프로세스 종료]):::online

    %% 연결 흐름 - 자동 확정 분기
    Start --> A1
    A1 -->|가능| A2
    A1 -->|불가| B1
    A2 --> A3
    A3 --> End
    
    %% 수동 처리 흐름
    B1 --> B2

    %% 코멘트 검토 후 병렬 분기
    B2 --> Cond1
    B2 --> Cond2
    B2 --> Cond3
    B2 --> Cond4

    %% 각 조건별 처리 - 해당하는 경우만
    Cond1 -->|다름| C1 --> D1 --> E1 --> End
    Cond2 -->|다름| F1 --> G1 --> H1 --> I1 --> J1 --> End
    Cond3 -->|2회 이상| K1 --> K2 --> L1 --> M1 --> End
    Cond4 -->|필요| N1 --> O1 --> P1 --> Q1 --> End

    %% 스타일 정의
    classDef online fill:#90EE90,stroke:#2E8B57,stroke-width:3px,color:#000
    classDef offline fill:#ADD8E6,stroke:#4682B4,stroke-width:3px,color:#000
```

## 프로세스 상세 설명

### 1. 자동 확정 판단 단계
- VOF 시스템에서 자동 확정 가능 여부를 판단합니다
- 가능한 경우: 자동 확정 처리 후 결제 및 발권까지 진행하고 프로세스 종료
- 불가능한 경우: 운영팀의 수동 처리로 진행

### 2. 수동 처리 초기 검토
- 운영팀이 VOF에서 미확정 사유를 확인합니다
- 코멘트를 검토한 후 4가지 조건을 병렬로 확인합니다

### 3. 병렬 조건 확인 및 처리

#### 3.1 항공사 일치 여부
- 출국 항공사와 귀국 항공사가 다른 경우
- 운영팀이 여행 일정 확인 → GDS에서 예약 조회 → 확정/취소 처리

#### 3.2 금액 일치 여부
- 예약 금액과 발권 금액이 다른 경우
- TL 연장 → 여행자에게 안내 → 컨펌 회신 → 최종 금액 재확인 → 확정 처리

#### 3.3 스탑오버 횟수
- 스탑오버가 2회 이상인 경우
- GDS에서 운임 규정 및 가능 여부 확인 → VOF에서 일정 재확인 → 확정/취소 처리

#### 3.4 증빙서류 필요 여부
- 서류 제출이 필요한 경우
- 여행자에게 요청 발송 → 여행자 업로드 → 운영팀 확인 → 확정 진행

### 4. 프로세스 종료
모든 처리가 완료되면 발권 프로세스가 종료됩니다.










