# LAFC_수동발권_v2

## 프로세스 개요

AICX 수동발권매니저가 시트에서 예약 확인 후 마이리얼트립 확정, LAFC 사이트 발권, 좌석 정보 기입까지의 전체 프로세스입니다.

## 프로세스 플로우차트

```mermaid
flowchart TD
    %% 시작 노드
    Start([온라인: LAFC 수동발권 시작]):::online

    %% AICX - 발권시트 확인
    subgraph AICX_Sheet_Check["AICX - 발권시트"]
        direction TB
        A1[온라인: 예약 내역 확인]:::online
        A2[온라인: 고객 정보, 구매옵션, 예약 수량 확인]:::online
    end

    %% AICX - 마이리얼트립 확정 처리
    subgraph AICX_MyTrip["AICX - 마이리얼트립 시스템"]
        direction TB
        B1[온라인: 확정대기 → 확정 처리]:::online
    end

    %% 조건 분기 노드 (연석 지정 가능 여부)
    Cond1{온라인: B2C 배정 시 연석 지정 가능 여부}:::online

    %% 연석 지정 불가 경로
    subgraph AICX_MyTrip_Wait["AICX - 마이리얼트립 시스템"]
        direction TB
        C1[온라인: 확정대기 상태 유지]:::online
    end

    subgraph AICX_Contact["AICX - 고객 안내"]
        direction TB
        D1[온라인: 여행자에게 확정 최대 1일 소요 안내]:::online
    end

    subgraph AICX_Inquiry["AICX - 사업실 문의"]
        direction TB
        E1[온라인: 재고 이동 관련 사업실 담당자 문의]:::online
        E2[온라인: 조유진, 김정환, 노경현, 이유진 님]:::online
    end

    subgraph AICX_Final["AICX - 마이리얼트립 시스템"]
        direction TB
        F1[온라인: 확정 또는 취소 처리]:::online
    end

    %% AICX - 발권 전 준비
    subgraph AICX_Sheet_Track["AICX - 발권시트"]
        direction TB
        G1[온라인: 재고 트래킹 영역 확인]:::online
        G2[온라인: B2B, B2C 티켓 좌석 확인]:::online
        G3[온라인: 필요 상태값 정보 기입]:::online
    end

    %% AICX - LAFC 사이트 발권
    subgraph AICX_LAFC["AICX - LAFC 티켓마스터 사이트"]
        direction TB
        H1[온라인: VPN OFF]:::online
        H2[온라인: 발권 사이트 접속]:::online
        H3[온라인: 로그인]:::online
        H4[온라인: 발권 실행]:::online
        H5[온라인: 티켓 전달]:::online
    end

    %% AICX - 좌석 정보 기입
    subgraph AICX_Sheet_Record["AICX - 발권시트"]
        direction TB
        I1[온라인: 티켓번호 기입]:::online
        I2[온라인: Section, Row, Seat 기입]:::online
        I3[온라인: 발권 일시 기입]:::online
        I4[온라인: 발송여부, 확정여부 기입]:::online
    end

    %% 종료 노드
    End([온라인: LAFC 수동발권 종료]):::online

    %% 연결 흐름
    Start --> A1
    A1 --> A2
    A2 --> B1
    B1 --> Cond1

    %% 연석 지정 가능 여부 분기
    Cond1 -->|가능| G1
    Cond1 -->|불가| C1
    
    %% 연석 지정 불가 경로
    C1 --> D1
    D1 --> E1
    E1 --> E2
    E2 --> F1
    F1 --> End

    %% 연석 지정 가능 경로 (발권 진행)
    G1 --> G2
    G2 --> G3
    G3 --> H1
    H1 --> H2
    H2 --> H3
    H3 --> H4
    H4 --> H5
    H5 --> I1
    I1 --> I2
    I2 --> I3
    I3 --> I4
    I4 --> End

    %% 스타일 정의
    classDef online fill:#FFF9C4,stroke:#FFD54F,stroke-width:2px,color:#000
    classDef offline fill:#FFE0B2,stroke:#FFB74D,stroke-width:2px,color:#000
```

## 프로세스 상세 설명

### 1. 예약 내역 확인
- 발권시트에서 예약 내역을 확인합니다
- 고객 정보, 구매옵션, 예약 수량을 상세히 확인합니다

### 2. 마이리얼트립 확정 처리
- 확정대기 상태에서 확정 상태로 변경합니다
- **확정을 먼저 눌러주는 이유**: 확정대기 상태에서 여행자가 취소하면 수동 발권 도중일 수 있으므로 먼저 확정합니다
- 티켓마스터에 존재하는 재고만큼 상품에 재고가 업로드됩니다
- **주의**: 티켓마스터 사이트 접속 시 VPN OFF가 필요하므로 매니저 페이지 확정 후 처리합니다

### 3. 연석 지정 가능 여부 판단

#### 3-1. 연석 지정 불가능한 경우
- 확정대기 상태를 유지합니다
- 여행자에게 확정까지 최대 ~1일 소요될 수 있음을 안내합니다
- 재고 이동 관련하여 사업실 담당자(조유진, 김정환, 노경현, 이유진 님)에게 문의합니다
- 최종적으로 확정 또는 취소 처리합니다

#### 3-2. 연석 지정 가능한 경우 (발권 진행)

### 4. 발권 전 준비
- 발권시트의 재고 트래킹 영역을 확인합니다
- B2B, B2C 티켓 좌석 확인이 필요한 상태값 정보를 기입합니다

### 5. LAFC 사이트 발권
- VPN을 OFF로 설정합니다
- 발권 사이트에 접속합니다
- 로그인합니다
- 발권을 실행합니다
- 티켓을 전달합니다

### 6. 좌석 정보 기입
- 발권시트에 다음 정보를 기록합니다:
  - 티켓번호
  - Section, Row, Seat
  - 발권 일시
  - 발송여부
  - 확정여부
