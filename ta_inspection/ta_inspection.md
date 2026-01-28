# T&A 입점 상품 검수 플로우차트

## 프로세스 플로우차트

```mermaid
flowchart TD
    %% 시작
    Start([시작:<br/>T&A 입점<br/>상품 검수]):::online

    %% 검색 및 필터
    subgraph Search["🔍 검색"]
        direction TB
        A1[상품 ID 검색]:::online
        A2[우선검수<br/>체크박스]:::online
        A3[나에게 할당된 상품<br/>체크박스]:::online
        A4[상태값 선택<br/>심사중/판매중<br/>판매대기/반려]:::online
    end

    %% 검수 유형 확인
    Cond1{검수<br/>유형}:::online

    %% 상세 페이지 진입
    subgraph Detail["📝 상세 페이지"]
        direction TB
        B1[상품 정보 확인]:::online
        B2[파트너ID/상품ID<br/>클릭하여<br/>매니저페이지 확인]:::online
    end

    %% 검수 시작
    subgraph AICheck["🤖 AI 검수"]
        direction TB
        C1[검수 시작<br/>클릭]:::online
        C2[AI 검수 진행]:::online
    end

    %% 검수 결과
    Cond2{AI 검수<br/>결과}:::online

    %% 반려 사유 확인
    subgraph Reject1["❌ 반려 사유"]
        direction TB
        D1[반려 사유 확인]:::online
        D2[이전 반려사유<br/>확인하기<br/>재검수인 경우]:::online
    end

    %% 반려 사유 수정
    Cond3{반려 사유<br/>수정 필요?}:::online

    subgraph Modify["✏️ 반려 사유 수정"]
        direction TB
        E1[삭제/수정<br/>버튼 클릭]:::online
        E2[반려사유 추가<br/>버튼 클릭]:::online
    end

    %% 수수료 확인
    subgraph Fee["💰 수수료 확인"]
        direction TB
        F1[판매 수수료율<br/>확인 기본 20%]:::online
        F2[별도 수수료 정책<br/>확인]:::online
    end

    Cond4{수수료<br/>수정 필요?}:::online

    subgraph FeeModify["💰 수수료 수정"]
        direction TB
        G1[수수료 수정하기<br/>클릭]:::online
        G2[매니저페이지<br/>이동하여 수정]:::online
    end

    %% 최종 처리
    Cond5{최종<br/>처리}:::online

    subgraph Approve["✅ 승인"]
        direction TB
        H1[판매 시작<br/>클릭]:::online
    end

    subgraph RejectFinal["❌ 반려"]
        direction TB
        I1[심사 반려<br/>클릭]:::online
    end

    subgraph Wait["⏸️ 대기"]
        direction TB
        J1[판매 대기<br/>클릭<br/>마이그레이션 상품]:::online
    end

    subgraph Business["📊 사업실"]
        direction TB
        K1[사업실 검수 요청<br/>클릭]:::online
    end

    subgraph Confirm["❓ 확인요청"]
        direction TB
        L1[확인요청<br/>체크박스<br/>엣지케이스 등]:::online
    end

    %% 완료
    End([완료]):::online

    %% ========== 연결 흐름 ==========
    Start --> A1
    A1 --> A2
    A2 --> A3
    A3 --> A4
    A4 --> Cond1

    Cond1 -->|신규 검수| B1
    Cond1 -->|재검수| B1

    B1 --> B2
    B2 --> C1
    C1 --> C2
    C2 --> Cond2

    Cond2 -->|반려 사항 있음| D1
    Cond2 -->|반려 사항 없음| F1

    D1 --> D2
    D2 --> Cond3

    Cond3 -->|필요| E1
    E1 --> E2
    E2 --> F1

    Cond3 -->|불필요| F1

    F1 --> F2
    F2 --> Cond4

    Cond4 -->|필요| G1
    G1 --> G2
    G2 --> Cond5

    Cond4 -->|불필요| Cond5

    Cond5 -->|판매 시작| H1
    Cond5 -->|심사 반려| I1
    Cond5 -->|판매 대기| J1
    Cond5 -->|사업실 요청| K1
    Cond5 -->|확인 요청| L1

    H1 --> End
    I1 --> End
    J1 --> End
    K1 --> End
    L1 --> End

    %% 스타일
    classDef online fill:#FFF9C4,stroke:#FFD54F,stroke-width:3px,color:#000,font-size:16px
    classDef offline fill:#FFE0B2,stroke:#FFB74D,stroke-width:3px,color:#000,font-size:16px
```

## 참고 자료

- **원본 페이지**: [T&A 입점 상품 검수](https://mrtcx.atlassian.net/wiki/spaces/aoh/pages/791707659/T+A)
- **자동화툴 다운로드**:
  - [AICX MANAGER v0.3.3 (macOS)](https://aicx-partner-app-release.s3.ap-northeast-2.amazonaws.com/AICX+MANAGER-0.3.3-universal.dmg)
  - [AICX MANAGER v0.3.3 (Windows x64)](https://aicx-partner-app-release.s3.ap-northeast-2.amazonaws.com/AICX+MANAGER+Setup+0.3.3.exe)
- **매뉴얼 슬라이드**: [구글 프레젠테이션](https://docs.google.com/presentation/d/1MaIVoXtc2Mrd-HL6kEzoyBTqMdNRrXgnkIFMIHMrzso/edit)
- **검수 가이드라인 시트**: [구글 시트](https://docs.google.com/spreadsheets/d/1FjqymMxV8VPM5EWvUX9HkQZuFVkt-Ecz66vT9YJfxec/edit)
- **동의서 응답시트**: [구글 시트](https://docs.google.com/spreadsheets/d/1Aq1Wiotw7PFHgIkE6QBwWU4EnyzHuXbaFTwORZ7Syz8/edit)
