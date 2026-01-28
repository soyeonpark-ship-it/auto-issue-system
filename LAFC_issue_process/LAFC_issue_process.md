# LAFC 발권 프로세스

## 프로세스 개요

LAFC (손흥민 로스앤젤레스 풋볼 클럽) 직사입 티켓 발권 운영 프로세스

## 프로세스 플로우차트

```mermaid
flowchart TD
    Start([시작: 예약 접수])
    
    %% 초기 확인 단계
    subgraph Sheet["시트 확인"]
        A1[예약 내역 확인<br/>고객정보, 구매옵션, 수량]
    end
    
    %% B2B/B2C 분기
    CondType{운영 방식 확인}
    
    %% B2B 프로세스
    subgraph B2B_Process["B2B 파트너사 발권"]
        B1[파트너사용 벌크 발권 준비]
        B2[B2B 발권 시트 확인]
        B3[벌크 발권 실행]
    end
    
    %% B2C 프로세스
    subgraph B2C_Process["B2C 고객 직접 발권"]
        C1[B2C 발권 시트 확인]
        C2[연석 배정 가능 여부 확인]
    end
    
    %% 연석 배정 분기
    CondSeat{연석 배정 가능?}
    
    %% 연석 배정 불가 처리
    subgraph Wait_Process["재고 이동 처리"]
        D1[확정대기 상태 유지]
        D2[여행자에게 최대 1일 소요 안내]
        D3[사업실 팀원 문의<br/>조유진, 김정환, 노경현, 이유진]
    end
    
    CondFinal{확정 가능?}
    
    %% 확정 처리
    subgraph Confirm_Process["마리트 확정 처리"]
        E1[확정대기 → 확정 상태 변경]
        E2[확정 이유: 여행자 취소 방지]
    end
    
    %% LAFC 발권 실행
    subgraph LAFC_Issue["LAFC 사이트 발권"]
        F1[LAFC 발권 사이트 접속<br/>VPN OFF 필요]
        F2[로그인]
        F3[발권 시트 재고 트래킹 확인<br/>좌석 정보 확인]
        F4[발권 실행]
        F5[티켓 전달]
    end
    
    %% 좌석 정보 기록
    subgraph Record["시트 기록"]
        G1[티켓번호, Section, Row, Seat 기입]
        G2[발권 일시, 발송여부, 확정여부 기입]
    end
    
    %% 완료
    End([완료: 티켓 전달 완료])
    
    %% 취소 처리
    Cancel([취소 처리])
    
    %% 흐름 연결
    Start --> A1
    A1 --> CondType
    
    %% B2B 경로
    CondType -->|B2B| B1
    B1 --> B2
    B2 --> B3
    B3 --> E1
    
    %% B2C 경로
    CondType -->|B2C| C1
    C1 --> C2
    C2 --> CondSeat
    
    %% 연석 배정 가능
    CondSeat -->|가능| E1
    
    %% 연석 배정 불가
    CondSeat -->|불가| D1
    D1 --> D2
    D2 --> D3
    D3 --> CondFinal
    
    CondFinal -->|확정| E1
    CondFinal -->|취소| Cancel
    
    %% 확정 후 발권
    E1 --> E2
    E2 --> F1
    F1 --> F2
    F2 --> F3
    F3 --> F4
    F4 --> F5
    F5 --> G1
    G1 --> G2
    G2 --> End
    
    %% 스타일 정의
    classDef process fill:#FFF9C4,stroke:#FFD54F,stroke-width:2px,color:#000
    classDef decision fill:#E1BEE7,stroke:#9C27B0,stroke-width:2px,color:#000
    classDef start fill:#C8E6C9,stroke:#4CAF50,stroke-width:2px,color:#000
    classDef end fill:#FFCDD2,stroke:#F44336,stroke-width:2px,color:#000
    
    class A1,B1,B2,B3,C1,C2,D1,D2,D3,E1,E2,F1,F2,F3,F4,F5,G1,G2 process
    class CondType,CondSeat,CondFinal decision
    class Start start
    class End,Cancel end
```

## 주요 정책

### 기본 정책
- **환불 불가**: 확정 후 환불 불가
- **자리 배정**: 발권 순서대로 자동 배정, 예외 요청/변경 불가
  - 한 주문 내 수량은 연속 좌석 배정
  - 1장씩 따로 구매 시 연석 불가
- **양도 가능**: 고객끼리 양도 가능

### 운영 방식
- **B2B**: 파트너사에게 벌크 발권 → 파트너사가 고객에게 배부
- **B2C**: 마리트가 고객에게 직접 발권

## 상태 흐름

```
예약접수 → 확정대기 → 확정완료 → 발권진행중 → 발권완료 → 티켓전달완료
```

## 참고 자료

- [B2B 발권 시트 - 파트너사 전용](https://docs.google.com/spreadsheets/d/1-ni8SI0_6r16tS2QwAc5X-dY_MeKdXDJT3AJgkqWcFk/edit?gid=766782155#gid=766782155)
- [B2C 발권 시트 - 일반 고객 전용](https://docs.google.com/spreadsheets/d/1-ni8SI0_6r16tS2QwAc5X-dY_MeKdXDJT3AJgkqWcFk/edit?gid=1107036574#gid=1107036574)
- [LAFC 수동발권 가이드 - 상세 발권 절차](https://docs.google.com/presentation/d/1XF2OVRKjWk0dfqn1nIpC0VwyUCwFRL-zYBz2kzxwREw/edit?slide=id.p#slide=id.p)
- [LAFC 수동발권 FAQ - 문제 해결](https://docs.google.com/spreadsheets/d/1dunk3lrSKQ-cMi1J8XF_B1eGUc7GOOHeGGqMiVn471E/edit?gid=1263566895#gid=1263566895)
- [운영방식 시연 동영상](https://drive.google.com/file/d/1l0faeBry1GxdRDACcwD0FiyPe8okCJYc/view?usp=drive_link)

## 주의사항

1. **B2B/B2C 시트 혼용 금지**
2. **확정 후 환불/변경 불가** - 사전 안내 필수
3. **발권 순서 엄수** - 접수 순서대로 처리
4. **정보 정확성** - 오류 시 재발권 불가

## 담당자 정보

- **상품 관련**: 미주태평양팀 김정환, 노경현, 이유진(APOC)
- **직사입 재고 관련**: 커머스팀 조유진
