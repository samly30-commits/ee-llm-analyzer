# ee-llm-analyzer
# ⚡ LLM 기반 코딩 에이전트 활용 전기·전자 엔지니어링 분석 툴킷

**본 프로젝트는 Claude Code 및 Cursor AI를 활용하여 전기·전자 엔지니어링 현업의 페인 포인트를 해결하고 업무를 자동화한 실습 과제 결과물입니다.**

---

## 📌 1. 프로젝트 개요 (Project Overview)
*   **기획 의도:** 엔지니어가 수작업으로 진행하던 오실로스코프 파형 분석(FFT, 리플 계산)과 PCB 설계 사후 검증(Gerber 부품 부호와 구매용 BOM 매칭) 작업을 자동화하여 데이터 분석의 휴먼 에러를 방지하고 리드 타임을 단축하고자 합니다.
*   **발표 자료 안내:** 프로젝트 기획 의도, 시스템 구조, 시연 화면 등이 담긴 발표 자료는 레포지토리 내 `docs/프로젝트_발표자료.pptx`에서 확인하실 수 있습니다.

---

## ⚙️ 2. 주요 기능 (Core Features)

### 📊 파형 데이터 분석기 (`src/analyzer.py`)
*   오실로스코프 및 LTspice에서 추출한 CSV 파형 데이터를 파싱합니다.
*   주파수 도메인 분석(FFT)을 통해 하모닉 성분을 검출하고 Vpp, Vrms, 리플 전압을 자동 계산합니다.

### 🔍 Gerber/BOM 파일 정합성 검증 도구 (`src/bom_verifier.py`)
*   PCB Gerber 파일의 RefDes(부품 참조 부호)와 Excel BOM 리스트를 상호 대조합니다.
*   누락된 부품이나 패키지 명칭 불일치 오류를 정규 표현식을 통해 10초 만에 탐지합니다.

---

## 🤖 3. LLM 활용 및 문제 해결 과정 (Core Prompts)

개발 과정에서 LLM 에이전트(Claude 3.5 Sonnet)와 협업하며 발생한 주요 에러와 해결 프롬프트입니다.

### 💡 핵심 프롬프트 예시 (신호처리 오차 수정)
*   **문제 상황:** 최초 코드에서 FFT 변환 후 주파수 축(X축) 스케일이 실제 샘플링 레이트와 맞지 않아 하모닉 주파수가 왜곡됨.
*   **사용 프롬프트:**
    > "오실로스코프 CSV 데이터의 타임스탬프 간격($\Delta t$)을 계산해서 샘플링 주파수($f_s = 1/\Delta t$)를 동적으로 구하고, `scipy.fft.fftfreq`에 넘겨주도록 코드를 리팩토링해줘. Nyquist 주파수까지만 플롯팅해야 해."
*   **해결 결과:** LLM이 타임스탬프의 비균일성 가능성을 인지하고 `np.diff` 기반의 평균 샘플링 주파수 계산 및 예외 처리 로직을 자동 구현하여 오차를 해결함.

---

## 🚀 4. 실행 환경 설정 및 구동 명령어

본 프로젝트는 `data/` 폴더 내에 즉시 테스트 가능한 샘플 데이터(`sample_oscilloscope.csv`, `sample_bom.xlsx`)를 포함하고 있습니다 [0.1.1].

### 1) 환경 구축 및 의존성 패키지 설치
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 의존성 설치
pip install -r requirements.txt
