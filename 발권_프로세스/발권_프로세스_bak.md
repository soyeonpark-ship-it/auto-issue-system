# 발권_프로세스

## 프로세스 개요

이 프로세스는 VOF 시스템에서 항공권 예약의 자동/수동 확정 및 발권까지의 전체 흐름을 나타냅니다. 자동 확정이 불가한 경우 운영팀이 미확정 사유를 확인하고, 항공사 일치 여부, 금액 확인, 스탑오버 횟수, 증빙서류 제출 등을 단계별로 처리하여 최종 발권을 완료합니다.

## 프로세스 플로우차트

```mermaid
flowchart TD
    %% 시작
    START([온라인: 발권 프로세스 시작]):::online
    
    %% VOF 시스템
    subgraph VOF["VOF 시스템"]
        direction TB
        AUTO_CHECK{온라인: 자동 확정<br/>가능 여부 판단}:::online
        AUTO_YES[온라인: 자동 확정 처리]:::online
        AUTO_NO[온라인: 자동 확정 불가<br/>수동 처리 필요]:::online
        V1[온라인: 결제 및 발권]:::online
    end
    
    %% 운영팀 - VOF 시스템 (공통)
    subgraph OPS_VOF_0["운영팀 - VOF 시스템"]
        direction TB
        B1[온라인: 미확정 사유 확인]:::online
        B2[온라인: 코멘트 검토]:::online
    end
    
    %% 운영팀 - VOF 시스템 (케이스 1)
    subgraph OPS_VOF_1["운영팀 - VOF 시스템"]
        direction TB
        B3_1[온라인: 여행 일정 확인]:::online
        B3_2[온라인: 예약 확정 또는<br/>취소 처리]:::online
    end
    
    %% 운영팀 - VOF 시스템 (케이스 2)
    subgraph OPS_VOF_2["운영팀 - VOF 시스템"]
        direction TB
        B4_1[온라인: TL 연장]:::online
        B4_2[온라인: 확정 처리]:::online
    end
    
    %% 운영팀 - VOF 시스템 (케이스 3)
    subgraph OPS_VOF_3["운영팀 - VOF 시스템"]
        direction TB
        B6_1[온라인: 사용 가능한<br/>일정 재확인]:::online
        B6_2[온라인: 예약 확정 또는<br/>취소 처리]:::online
    end
    
    %% 운영팀 - VOF 시스템 (케이스 4)
    subgraph OPS_VOF_4["운영팀 - VOF 시스템"]
        direction TB
        B8_1[온라인: 서류 확인]:::online
        B8_2[온라인: 확정 진행]:::online
    end
    
    %% 운영팀 - GDS 시스템 (케이스 1)
    subgraph OPS_GDS_1["운영팀 - GDS 시스템"]
        direction TB
        C1_1[온라인: 확정 가능<br/>예약 조회]:::online
    end
    
    %% 운영팀 - GDS 시스템 (케이스 2)
    subgraph OPS_GDS_2["운영팀 - GDS 시스템"]
        direction TB
        C3_1[온라인: 최종 금액<br/>재확인]:::online
    end
    
    %% 운영팀 - GDS 시스템 (케이스 3)
    subgraph OPS_GDS_3["운영팀 - GDS 시스템"]
        direction TB
        C4_1[온라인: 운임 규정 확인]:::online
        C4_2[온라인: 스탑오버<br/>가능 여부 확인]:::online
    end
    
    %% 운영팀 - ZD 이메일 (케이스 2)
    subgraph OPS_EMAIL_2["운영팀 - ZD 이메일"]
        direction TB
        D1[온라인: 금액 상이<br/>안내 발송]:::online
    end
    
    %% 운영팀 - ZD 이메일 (케이스 4)
    subgraph OPS_EMAIL_4["운영팀 - ZD 이메일"]
        direction TB
        D2[온라인: 서류 제출<br/>요청 발송]:::online
    end
    
    %% 여행자 (케이스 2)
    subgraph TRAVELER_2["여행자"]
        direction TB
        E1[온라인: 컨펌 회신]:::online
    end
    
    %% 여행자 - 마리트 내여행 (케이스 4)
    subgraph TRAVELER_MERIT_4["여행자 - 마리트 내여행"]
        direction TB
        E2[온라인: 서류 업로드]:::online
    end
    
    %% 분기점들
    BRANCH1{온라인: 출국·귀국<br/>항공사 동일 여부}:::online
    BRANCH2{온라인: 예약 금액과<br/>발권 금액 동일 여부}:::online
    BRANCH3{온라인: 스탑오버<br/>2회 이상 여부}:::online
    BRANCH4{온라인: 증빙서류<br/>필요 여부}:::online
    
    %% 종료
    END([온라인: 발권 프로세스 종료]):::online
    
    %% ========== 자동 확정 흐름 ==========
    START --> AUTO_CHECK
    AUTO_CHECK -->|가능| AUTO_YES
    AUTO_YES --> V1
    V1 --> END
    
    %% ========== 수동 처리 시작 ==========
    AUTO_CHECK -->|불가| AUTO_NO
    AUTO_NO --> B1
    B1 --> B2
    
    %% ========== 케이스 1: 항공사 불일치 ==========
    B2 --> BRANCH1
    BRANCH1 -->|다름| B3_1
    B3_1 --> C1_1
    C1_1 --> B3_2
    B3_2 --> END
    
    %% ========== 케이스 2: 금액 불일치 ==========
    B2 --> BRANCH2
    BRANCH2 -->|다름| B4_1
    B4_1 --> D1
    D1 --> E1
    E1 --> C3_1
    C3_1 --> B4_2
    B4_2 --> END
    
    %% ========== 케이스 3: 스탑오버 2회 이상 ==========
    B2 --> BRANCH3
    BRANCH3 -->|2회 이상| C4_1
    C4_1 --> C4_2
    C4_2 --> B6_1
    B6_1 --> B6_2
    B6_2 --> END
    
    %% ========== 케이스 4: 증빙서류 필요 ==========
    B2 --> BRANCH4
    BRANCH4 -->|필요| D2
    D2 --> E2
    E2 --> B8_1
    B8_1 --> B8_2
    B8_2 --> END
    
    %% 스타일 정의
    classDef online fill:#90EE90,stroke:#2E8B57,stroke-width:3px,color:#000
    classDef offline fill:#ADD8E6,stroke:#4682B4,stroke-width:3px,color:#000
```

## 프로세스 상세 설명

### 1단계: 자동 확정 판단
- VOF 시스템이 예약 건에 대해 자동 확정 가능 여부를 판단합니다
- 자동 확정 가능 시: VOF가 자동으로 확정 → 결제 → 발권 → 프로세스 종료
- 자동 확정 불가 시: 운영팀의 수동 처리로 이동

### 2단계: 미확정 사유 확인
- 운영팀이 VOF에서 미확정 사유를 확인하고 코멘트를 검토합니다

### 3단계: 항공사 일치 여부 확인
- 출국 항공사와 귀국 항공사가 다른 경우:
  - VOF에서 여행 일정 확인
  - GDS에서 확정 가능한 예약인지 조회
  - 예약 확정 또는 취소 처리

### 4단계: 금액 일치 여부 확인
- 예약 금액과 발권 금액이 다른 경우:
  - VOF에서 TL(Time Limit) 연장
  - ZD 이메일로 여행자에게 금액 상이 안내 발송
  - 여행자의 컨펌 회신 대기
  - 운영팀이 확정 진행
  - GDS에서 최종 금액 재확인

### 5단계: 스탑오버 확인
- 스탑오버가 2회 이상인 경우:
  - GDS에서 운임 규정 확인
  - 스탑오버 가능 여부 확인
  - 필요 시 VOF에서 사용 가능한 일정 재확인
  - 조건 충족 시 확정 처리

### 6단계: 증빙서류 확인
- 증빙서류 제출이 필요한 경우:
  - ZD 이메일로 여행자에게 서류 제출 요청
  - 여행자가 서류 업로드
  - 운영팀이 VOF에서 서류 확인 후 확정 진행

### 7단계: 프로세스 종료
- 모든 단계가 정상적으로 완료되면 발권 프로세스가 종료됩니다

