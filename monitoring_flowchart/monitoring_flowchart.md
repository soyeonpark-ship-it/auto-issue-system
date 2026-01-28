# 연동 예약 운영 모니터링 플로우차트

## 프로세스 플로우차트

```mermaid
flowchart TD
    %% 시작 노드
    Start([온라인: 연동 예약 운영 모니터링 시작]):::online

    %% 모니터링 채널 선택
    Cond1{온라인: 모니터링 채널 선택}:::online

    %% === 1번 채널: 국내예약실패 ===
    subgraph Domestic["슬랙 - 국내예약실패 채널"]
        direction TB
        D1[온라인: 모니터링_공급사연동_국내예약실패<br/>채널 확인]:::online
    end

    %% 자동 취소 세트 확인
    Cond2{온라인: 자동 취소 메시지<br/>세트 여부}:::online

    %% 연락처 오류 처리
    subgraph ContactError["운영 - 연락처 오류 처리"]
        direction TB
        E1[온라인: 예약자 정보 내 연락처 확인<br/>+82 10~ 형식 여부]:::online
        E2[온라인: 여행자에게 연락처 수정<br/>및 재예약 권유 문자 발송]:::online
    end

    %% 공급사 확인 필요
    subgraph SupplierCheck["운영 - 공급사 확인"]
        direction TB
        F1[온라인: 모니터링 시트에 기재<br/>및 체크 이모지]:::online
        F2[온라인: 3.0 내 상태 확인]:::online
        F3[온라인: 공급사에 예약 상태<br/>확인 요청 및 처리]:::online
        F4[온라인: 시트에 처리 상황 업데이트]:::online
    end

    %% === 2번 채널: 해외공통 ===
    subgraph Overseas["슬랙 - 해외공통 채널"]
        direction TB
        G1[온라인: 모니터링_공급사연동_해외공통<br/>채널 확인]:::online
        G2[온라인: 예약 연동 결과 반영 실패<br/>알럿 검색]:::online
    end

    %% 예외 케이스 확인
    Cond3{온라인: 몽키트래블<br/>wait_confirm<br/>cancel alert}:::online

    %% 예외 처리
    subgraph Exception["운영 - 예외 처리"]
        direction TB
        H1[온라인: 체크 이모지만 추가<br/>시트 기재 불필요]:::online
    end

    %% 취소 접수 처리
    subgraph CancelProcess["운영 - 취소 접수"]
        direction TB
        I1[온라인: 모니터링 시트에 기재<br/>및 체크 이모지]:::online
        I2[온라인: 3.0 상태 확인]:::online
        I3[온라인: 공급사에 취소 접수]:::online
        I4[온라인: 시트에 처리 상황 업데이트]:::online
    end

    %% === 3번 채널: 해외예약실패 ===
    subgraph OverseasFail["슬랙 - 해외예약실패 채널"]
        direction TB
        J1[온라인: 모니터링_공급사연동_해외예약실패<br/>채널 확인]:::online
    end

    %% 자동 취소 세트 확인 2
    Cond4{온라인: 자동 취소 메시지<br/>세트 여부}:::online

    %% 해외 예약 실패 처리
    subgraph OverseasProcess["운영 - 해외 예약 실패 처리"]
        direction TB
        K1[온라인: 모니터링 시트에 기재<br/>및 체크 이모지]:::online
        K2[온라인: 반려시트/ZD/슬랙에서<br/>중복 내용 확인]:::online
    end

    %% 공급사별 확인 조건
    Cond5{온라인: 공급사 선택}:::online

    %% KLOOK 처리
    subgraph Klook["운영 - KLOOK"]
        direction TB
        L1[온라인: 알럿 내 취소 사유 확인]:::online
        L2[온라인: 사유 명확 시 안내 후 취소<br/>불명확 시 생텀에서 확인]:::online
    end

    %% BMG 처리
    subgraph BMG["운영 - BMG"]
        direction TB
        M1[온라인: 여행자 영문 성함으로<br/>BMP에서 검색]:::online
        M2[온라인: Reject/Payment Pending<br/>확인 후 처리]:::online
    end

    %% JTR 처리
    subgraph JTR["운영 - JTR"]
        direction TB
        N1[온라인: 공급사 어드민에서<br/>여행자 연락처로 검색]:::online
        N2[온라인: 부분 확정 시 바우처<br/>수기 업로드 및 환불 처리]:::online
    end

    %% 기타 공급사 처리
    subgraph Others["운영 - 기타 공급사"]
        direction TB
        O1[온라인: GYG/티켓츠/링크티비티/<br/>트립닷컴 등 처리]:::online
        O2[온라인: 각 공급사별 가이드에<br/>따라 확인 및 처리]:::online
    end

    %% 최종 처리
    subgraph FinalProcess["운영 - 최종 처리"]
        direction TB
        P1[온라인: 3.0 확정 또는 취소 처리]:::online
        P2[온라인: 여행자에게 안내 문자 발송]:::online
        P3[온라인: 시트에 처리 내용 업데이트]:::online
    end

    %% === 4번: GYG 쿼리 모니터링 ===
    subgraph GYGQuery["리대쉬 - GYG 쿼리 모니터링"]
        direction TB
        Q1[온라인: 리대쉬 페이지 접속<br/>및 Refresh]:::online
        Q2[온라인: refund status 정렬<br/>공백 건 확인]:::online
        Q3[온라인: 모니터링 시트에 기재]:::online
        Q4[온라인: Price adjusted 메일에서<br/>환불 금액 확인]:::online
        Q5[온라인: ZD 중복 여부 확인]:::online
    end

    %% 티켓 생성 조건
    Cond6{온라인: 티켓 생성<br/>필요 여부}:::online

    %% 티켓 생성
    subgraph TicketCreate["ZD - 티켓 생성"]
        direction TB
        R1[온라인: 당일/전일 등<br/>신속 안내 필요 시 티켓 생성]:::online
        R2[온라인: 메일 및 문자 모두 발송]:::online
    end

    %% 간단 안내
    subgraph SimpleGuide["운영 - 간단 안내"]
        direction TB
        S1[온라인: 3.0 처리 및 문자 안내만]:::online
    end

    %% 종료 노드
    End([온라인: 연동 예약 운영 모니터링 완료]):::online

    %% === 연결 흐름 ===
    Start --> Cond1

    %% 1번 채널 플로우
    Cond1 -->|국내예약실패| D1
    D1 --> Cond2
    
    Cond2 -->|자동 취소 세트| E1
    E1 --> E2
    E2 --> End

    Cond2 -->|일반 알럿| F1
    F1 --> F2
    F2 --> F3
    F3 --> F4
    F4 --> End

    %% 2번 채널 플로우
    Cond1 -->|해외공통| G1
    G1 --> G2
    G2 --> Cond3

    Cond3 -->|예외| H1
    H1 --> End

    Cond3 -->|일반| I1
    I1 --> I2
    I2 --> I3
    I3 --> I4
    I4 --> End

    %% 3번 채널 플로우
    Cond1 -->|해외예약실패| J1
    J1 --> Cond4

    Cond4 -->|자동 취소 세트| End
    Cond4 -->|일반 알럿| K1
    K1 --> K2
    K2 --> Cond5

    Cond5 -->|KLOOK| L1
    L1 --> L2
    L2 --> P1

    Cond5 -->|BMG| M1
    M1 --> M2
    M2 --> P1

    Cond5 -->|JTR| N1
    N1 --> N2
    N2 --> P1

    Cond5 -->|기타| O1
    O1 --> O2
    O2 --> P1

    P1 --> P2
    P2 --> P3
    P3 --> End

    %% 4번 GYG 쿼리 플로우
    Cond1 -->|GYG 쿼리| Q1
    Q1 --> Q2
    Q2 --> Q3
    Q3 --> Q4
    Q4 --> Q5
    Q5 --> Cond6

    Cond6 -->|필요| R1
    R1 --> R2
    R2 --> End

    Cond6 -->|불필요| S1
    S1 --> End

    %% 스타일 정의
    classDef online fill:#FFF9C4,stroke:#FFD54F,stroke-width:2px,color:#000
    classDef offline fill:#FFE0B2,stroke:#FFB74D,stroke-width:2px,color:#000
```

## 참고 자료

- **업무 시트**: [연동 모니터링 시트](https://docs.google.com/spreadsheets/d/1BUPeouUqtWm_ZrQZGIX3yf8fKtx25zj1kl6dlXtMx14/edit?gid=511658573#gid=511658573)
- **모니터링 알럿 정리**: [모니터링 알럿 정리 시트](https://docs.google.com/spreadsheets/d/1oJfPrbFKQf2TxqjunJAR4pQcUuBdQiE6dE1ZGY7zDoo/edit?gid=866584764#gid=866584764)
- **공급사 정보**: [공급사 어드민 및 이메일 계정 정보](https://docs.google.com/spreadsheets/d/1aRMZdr7tLbCqptVe8f5XRGUViRoUriXoPIgrBbNzlCI/edit?pli=1&gid=802671048#gid=802671048)
- **GYG 쿼리**: [리대쉬 페이지](https://redash.myrealtrip.net/queries/14902?p_type=ALL)

## 주요 채널

1. **#모니터링_공급사연동_국내예약실패**
2. **#모니터링_공급사연동_해외공통**
3. **#모니터링_공급사연동_해외예약실패**

## 모니터링 목적

- **예약 실패 건 자동 환불 불가**: 여러 사유로 예약이 실패되는데, 시스템적으로 자동 환불되고 있지 않아 수기로 환불 처리 필요
