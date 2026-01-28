# auto_발권_프로세스

## 프로세스 개요

발권 프로세스는 VOF 시스템에서 자동 확정 가능 여부를 먼저 판단하고, 자동 확정이 불가능한 경우 운영팀이 수동으로 여러 조건을 검토하여 발권을 진행하는 프로세스입니다.

## 프로세스 플로우차트

```mermaid
flowchart TD
    %% 시작 노드
    Start([온라인: 발권 프로세스 시작]):::online

    %% VOF 시스템 - 자동 확정 판단 (연속된 흐름이므로 통합)
    subgraph VOF_Auto["VOF 시스템"]
        direction TB
        A1{온라인: 자동 확정 가능 여부 판단}:::online
        A2[온라인: 자동 확정 처리]:::online
        A3[온라인: 자동 확정 불가 수동 처리 필요]:::online
        B1[온라인: 결제 및 발권]:::online
    end

    %% 운영팀 - VOF 시스템 (초기 검토 - 연속된 흐름이므로 통합)
    subgraph OPS_VOF_Review["운영팀 - VOF 시스템"]
        direction TB
        C1[온라인: 미확정 사유 확인]:::online
        C2[온라인: 코멘트 검토]:::online
    end

    %% 조건 분기 노드들 (subgraph 외부, 병렬 분기)
    Cond1{온라인: 출국 항공사와 귀국 항공사 서로 다른지 여부}:::online
    Cond2{온라인: 예약 금액과 발권 금액 동일 여부}:::online
    Cond3{온라인: 스탑오버 2회 이상 여부}:::online
    Cond4{온라인: 증빙서류 필요 여부}:::online

    %% ===== 분기 경로 1: 항공사 상이 처리 =====
    %% I1(VOF) → J1(GDS) → K1(VOF)
    %% 중간에 GDS가 끼어있으므로 VOF 분리

    subgraph OPS_VOF_Schedule["운영팀 - VOF 시스템"]
        direction TB
        I1[온라인: 여행 일정 확인]:::online
    end

    subgraph OPS_GDS_Reserve["운영팀 - GDS 시스템"]
        direction TB
        J1[온라인: 확정 가능한 예약 조회]:::online
    end

    subgraph OPS_VOF_Reserve["운영팀 - VOF 시스템"]
        direction TB
        K1[온라인: 예약 확정 또는 취소 처리]:::online
    end

    %% ===== 분기 경로 2: 금액 상이 처리 =====
    %% D1(VOF) → E1(ZD) → F1(여행자) → G1(GDS) → H1(VOF)
    %% 중간에 다른 시스템이 끼어있으므로 각각 분리

    subgraph OPS_VOF_TL["운영팀 - VOF 시스템"]
        direction TB
        D1[온라인: TL 연장]:::online
    end

    subgraph OPS_ZD_Price["운영팀 - ZD 이메일"]
        direction TB
        E1[온라인: 금액 상이 안내 발송]:::online
    end

    subgraph Traveler_Confirm["여행자"]
        direction TB
        F1[온라인: 컨펌 회신]:::online
    end

    subgraph OPS_GDS_Price["운영팀 - GDS 시스템"]
        direction TB
        G1[온라인: 최종 금액 재확인]:::online
    end

    subgraph OPS_VOF_Confirm["운영팀 - VOF 시스템"]
        direction TB
        H1[온라인: 확정 처리]:::online
    end

    %% ===== 분기 경로 3: 스탑오버 처리 =====
    %% L1(GDS) → L2(GDS) → M1(VOF) → N1(VOF)
    %% 연속된 GDS는 통합, 연속된 VOF는 통합

    subgraph OPS_GDS_Fare["운영팀 - GDS 시스템"]
        direction TB
        L1[온라인: 운임 규정 확인]:::online
        L2[온라인: 스탑오버 가능 여부 확인]:::online
    end

    subgraph OPS_VOF_Stopover["운영팀 - VOF 시스템"]
        direction TB
        M1[온라인: 사용 가능한 일정 재확인]:::online
        N1[온라인: 예약 확정 또는 취소 처리]:::online
    end

    %% ===== 분기 경로 4: 증빙서류 처리 =====
    %% O1(ZD) → P1(여행자) → Q1(VOF) → R1(VOF)
    %% 연속된 VOF는 통합

    subgraph OPS_ZD_Doc["운영팀 - ZD 이메일"]
        direction TB
        O1[온라인: 서류 제출 요청 발송]:::online
    end

    subgraph Traveler_MyTrip["여행자 - 마이트립 내여행"]
        direction TB
        P1[온라인: 서류 업로드]:::online
    end

    subgraph OPS_VOF_Doc["운영팀 - VOF 시스템"]
        direction TB
        Q1[온라인: 서류 확인]:::online
        R1[온라인: 확정 진행]:::online
    end

    %% 종료 노드
    End([온라인: 발권 프로세스 종료]):::online

    %% 연결 흐름 - 자동 확정 분기
    Start --> A1
    A1 -->|가능| A2
    A1 -->|불가| A3
    A2 --> B1
    B1 --> End
    A3 --> C1
    C1 --> C2

    %% 코멘트 검토 후 4개 조건으로 병렬 분기
    C2 --> Cond1
    C2 --> Cond2
    C2 --> Cond3
    C2 --> Cond4

    %% 각 조건별 처리 - 해당하는 경우만 (미해당 경로 없음)
    Cond1 -->|다름| I1 --> J1 --> K1 --> End
    Cond2 -->|다름| D1 --> E1 --> F1 --> G1 --> H1 --> End
    Cond3 -->|2회 이상| L1 --> L2 -->|필요 시| M1 --> N1 --> End
    Cond4 -->|필요| O1 --> P1 --> Q1 --> R1 --> End

    %% 스타일 정의
    classDef online fill:#90EE90,stroke:#2E8B57,stroke-width:3px,color:#000
    classDef offline fill:#ADD8E6,stroke:#4682B4,stroke-width:3px,color:#000
```

## 프로세스 상세 설명

### 1. 자동 확정 단계
- VOF 시스템에서 자동 확정 가능 여부를 판단합니다.
- 자동 확정이 가능한 경우, 자동으로 확정 처리하고 결제 및 발권까지 진행한 후 프로세스가 종료됩니다.
- 자동 확정이 불가능한 경우, 수동 처리 단계로 진행합니다.

### 2. 수동 처리 단계
- 운영팀이 VOF에서 미확정 사유를 확인하고 코멘트를 검토합니다.
- 검토 후 4가지 조건을 병렬로 확인합니다.

### 3. 케이스별 처리

#### 케이스1: 항공사 상이 처리
- 출국 항공사와 귀국 항공사가 서로 다른 경우
- 운영팀이 VOF에서 여행 일정을 확인하고, GDS에서 확정 가능한 예약을 조회한 후, VOF에서 예약을 확정하거나 취소 처리합니다.

#### 케이스2: 금액 상이 처리
- 예약 금액과 발권 금액이 다른 경우
- 운영팀이 VOF에서 TL을 연장하고, ZD이메일로 여행자에게 금액 상이 안내를 발송합니다.
- 여행자의 컨펌 회신을 받은 후, 운영팀이 GDS에서 최종 금액을 재확인하고 VOF에서 확정을 진행합니다.

#### 케이스3: 스탑오버 처리
- 스탑오버가 2회 이상인 경우
- 운영팀이 GDS에서 운임 규정과 스탑오버 가능 여부를 확인합니다.
- 필요한 경우 운영팀이 VOF에서 사용 가능한 일정을 재확인합니다.
- 조건이 충족되면 운영팀이 VOF에서 확정 또는 취소 처리합니다.

#### 케이스4: 증빙서류 처리
- 증빙서류가 필요한 경우
- 운영팀이 ZD이메일로 여행자에게 서류 제출 요청을 발송합니다.
- 여행자가 마이트립 내여행에 서류를 업로드하면, 운영팀이 VOF에서 서류를 확인하고 확정을 진행합니다.

### 4. 프로세스 종료
- 모든 과정이 문제 없이 완료되면 발권 프로세스가 종료됩니다.










