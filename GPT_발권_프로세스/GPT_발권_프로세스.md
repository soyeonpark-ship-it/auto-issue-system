# gpt_발권_프로세스

## 프로세스 개요

VOF에서 자동 확정 가능 여부를 우선 판단하고, 불가 시 운영팀이 VOF/GDS/ZD 이메일 및 여행자 응대를 통해 조건별 검토(항공사, 금액, 스탑오버, 증빙서류)를 병렬로 확인하여 해당 케이스만 처리하는 프로세스입니다.

## 프로세스 플로우차트

```mermaid
flowchart TD
    %% 시작/종료 노드 (subgraph 외부)
    Start([온라인: gpt_발권_프로세스 시작]):::online
    End([온라인: gpt_발권_프로세스 종료]):::online

    %% 조건 분기 노드 (subgraph 외부)
    CondAuto{온라인: 자동 확정 가능 여부 판단}:::online
    CondAirline{온라인: 출국/귀국 항공사 동일 여부}:::online
    CondPrice{온라인: 예약 금액과 발권 금액 동일 여부}:::online
    CondStopover{온라인: 스탑오버 2회 이상 여부 확인}:::online
    CondDocs{온라인: 증빙서류 필요 여부}:::online

    %% ===== 자동 확정(시스템) =====
    subgraph VOF_Auto["VOF 시스템"]
        direction TB
        A2[온라인: 자동 확정 처리]:::online
        A3[온라인: 결제 및 발권 진행]:::online
    end

    %% ===== 운영팀 - VOF 초기 검토 =====
    subgraph OPS_VOF_Review["운영팀 - VOF 시스템"]
        direction TB
        B1[온라인: 미확정 사유 확인]:::online
        B2[온라인: 코멘트 검토]:::online
    end

    %% ===== 항공사 상이 시 처리 (VOF -> GDS -> VOF) =====
    subgraph OPS_VOF_Schedule["운영팀 - VOF 시스템"]
        direction TB
        C1[온라인: 여행 일정 확인]:::online
    end

    subgraph OPS_GDS_Reserve["운영팀 - GDS 시스템"]
        direction TB
        C2[온라인: 확정 가능 예약 조회]:::online
    end

    subgraph OPS_VOF_Reserve["운영팀 - VOF 시스템"]
        direction TB
        C3[온라인: 예약 확정 또는 취소 처리]:::online
    end

    %% ===== 금액 상이 시 처리 (VOF -> ZD -> 여행자 -> GDS -> VOF) =====
    subgraph OPS_VOF_TL["운영팀 - VOF 시스템"]
        direction TB
        D1[온라인: TL 연장]:::online
    end

    subgraph OPS_ZD_Price["운영팀 - ZD 이메일"]
        direction TB
        D2[온라인: 금액 상이 안내 발송]:::online
    end

    subgraph Traveler_Confirm["여행자"]
        direction TB
        D3[온라인: 컨펌 회신]:::online
    end

    subgraph OPS_GDS_Price["운영팀 - GDS 시스템"]
        direction TB
        D4[온라인: 최종 금액 재확인]:::online
    end

    subgraph OPS_VOF_ConfirmPrice["운영팀 - VOF 시스템"]
        direction TB
        D5[온라인: 확정 진행]:::online
    end

    %% ===== 스탑오버 2회 이상 시 처리 (GDS -> (선택) VOF -> VOF) =====
    subgraph OPS_GDS_Stopover["운영팀 - GDS 시스템"]
        direction TB
        E1[온라인: 운임 규정 확인]:::online
        E2[온라인: 스탑오버 가능 여부 확인]:::online
    end

    %% 스탑오버 분기 내 VOF 작업은 연속 흐름이므로 하나의 subgraph로 통합
    subgraph OPS_VOF_Stopover["운영팀 - VOF 시스템"]
        direction TB
        E3[온라인: 사용 가능한 일정 재확인]:::online
        E4[온라인: 확정 또는 취소 처리]:::online
    end

    %% ===== 증빙서류 필요 시 처리 (ZD -> 여행자 -> VOF) =====
    subgraph OPS_ZD_Docs["운영팀 - ZD 이메일"]
        direction TB
        F1[온라인: 서류 제출 요청 발송]:::online
    end

    subgraph Traveler_MyTrip["여행자 - 마리트 내여행"]
        direction TB
        F2[온라인: 서류 업로드]:::online
    end

    subgraph OPS_VOF_Docs["운영팀 - VOF 시스템"]
        direction TB
        F3[온라인: 서류 확인]:::online
        F4[온라인: 확정 진행]:::online
    end

    %% =======================
    %% 연결 흐름 (병렬 분기)
    %% =======================
    Start --> CondAuto

    %% 자동 확정 분기
    CondAuto -->|가능| A2 --> A3 --> End
    CondAuto -->|불가| B1 --> B2

    %% 코멘트 검토 후 4개 조건으로 병렬 분기
    B2 --> CondAirline
    B2 --> CondPrice
    B2 --> CondStopover
    B2 --> CondDocs

    %% 각 조건별 처리 - 해당하는 경우만 (미해당 경로 없음)
    CondAirline -->|다름| C1 --> C2 --> C3 --> End
    CondPrice -->|다름| D1 --> D2 --> D3 --> D4 --> D5 --> End
    CondStopover -->|2회 이상| E1 --> E2 -->|필요 시| E3 --> E4 --> End
    CondDocs -->|필요| F1 --> F2 --> F3 --> F4 --> End

    %% 스타일 정의
    classDef online fill:#90EE90,stroke:#2E8B57,stroke-width:3px,color:#000
    classDef offline fill:#ADD8E6,stroke:#4682B4,stroke-width:3px,color:#000
```

## 프로세스 상세 설명

- **자동 확정 판단(VOF)**: 자동 확정 가능 시 VOF가 자동으로 확정 처리 후 결제 및 발권까지 진행하고 종료합니다.
- **수동 처리(운영팀)**: 자동 확정 불가 시 운영팀이 VOF에서 미확정 사유 및 코멘트를 확인한 뒤, 항공사/금액/스탑오버/증빙서류를 병렬로 확인하여 해당 케이스만 처리합니다.
- **항공사 상이(해당 시)**: 운영팀이 VOF에서 일정 확인 → GDS에서 예약 조회 → VOF에서 확정 또는 취소 처리합니다.
- **금액 상이(해당 시)**: VOF에서 TL 연장 → ZD 이메일로 금액 상이 안내 → 여행자 컨펌 회신 → GDS 최종 금액 재확인 → VOF 확정 진행합니다.
- **스탑오버 2회 이상(해당 시)**: GDS에서 운임 규정/스탑오버 가능 여부 확인 후, 필요 시 VOF에서 사용 가능한 일정 재확인 → VOF 확정 또는 취소 처리합니다.
- **증빙서류 필요(해당 시)**: ZD 이메일로 제출 요청 → 여행자가 마리트 내여행에 서류 업로드 → VOF에서 서류 확인 및 확정 진행합니다.


