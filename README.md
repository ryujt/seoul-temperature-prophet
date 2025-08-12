# Prophet 기반 실시간 이상탐지 시스템

Facebook Prophet 라이브러리를 활용한 시계열 데이터 실시간 이상탐지 시스템입니다.

## 시스템 개요

본 시스템은 시간 단위로 유입되는 데이터를 실시간으로 처리하며, Prophet 모델을 통해 학습하고 예측 범위를 벗어나는 이상치를 자동으로 탐지합니다.

## 시스템 구조

```
src/
├── data_controller.py    # 데이터 로딩 및 스트리밍
├── model_controller.py   # Prophet 모델 학습/예측/이상탐지
├── storage.py           # 모델 파일 저장 관리
├── alert_service.py     # 이상치 알림 처리
└── main.py             # 시스템 초기화 및 실행
```

## Job Flow Diagram

```
master: DataController
Object: DataController, ModelController, Storage, AlertService

DataController.Start --> DataController.RunTimer
DataController.OnData --> ModelController.Predict
ModelController.OnAnomaly --> AlertService.Notify
ModelController.OnModelUpdated --> Storage.SaveModel
```

## 주요 기능

### 1. 데이터 스트리밍
- JSONL 파일에서 시간 단위 데이터를 순차적으로 읽어 처리
- 재생 속도 조절 가능 (실시간, N배속)

### 2. 학습 전략
- **1단계**: 1일치 데이터(24시간) 수집 후 최초 학습
- **2단계**: 1주치 데이터(168시간) 수집 후 재학습
- **3단계 이후**: 매월(720시간) 단위로 재학습

### 3. 이상탐지
- Prophet 모델의 예측 신뢰구간(95%) 벗어나는 값을 이상치로 탐지
- 편차에 따라 INFO, WARNING, CRITICAL 수준으로 분류

### 4. 알림 시스템
- 이상치 발생 시 실시간 알림
- 로그 파일 저장 (JSONL 형식)
- Critical 알림 시 추가 처리

## 설치 방법

### 1. 가상환경 생성 및 활성화
```bash
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# 또는
.venv\Scripts\activate  # Windows
```

### 2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

또는 개별 설치:
```bash
pip install prophet==1.1.5 pandas numpy
```

## 사용 방법

### 기본 실행 (최고 속도)
```bash
python3 src/main.py
```

### 속도 조절 실행
```bash
python3 src/main.py --speed 100.0  # 100배속
python3 src/main.py --speed 10.0   # 10배속
python3 src/main.py --speed 1.0    # 실시간 속도
```

### 다른 데이터 파일 사용
```bash
python3 src/main.py --data path/to/your/data.jsonl
```

### 명령줄 옵션
- `--data`: 입력 데이터 파일 경로 (기본값: `examples/archives/seoul_last_5years_hourly.jsonl`)
- `--speed`: 데이터 재생 속도 (기본값: 0.0 = 최고속도, 1.0 = 실시간)

### 시스템 중지
`Ctrl+C`를 눌러 시스템을 안전하게 중지할 수 있습니다.

## 출력 디렉토리

- `models/`: 학습된 Prophet 모델 파일 저장
  - 파일명 형식: `model_YYYYMMDD_HHMMSS.pkl`
  - 최근 5개 모델만 유지 (자동 정리)
- `logs/`: 이상치 알림 로그 저장
  - 파일명 형식: `alerts_YYYYMMDD.jsonl`

## 데이터 형식

입력 JSONL 파일은 각 줄이 다음 형식의 JSON 객체여야 합니다:
```json
{"timestamp": "2020-01-01 00:00:00", "temperature": 1.5}
```

## 모니터링

시스템 실행 중 10초마다 다음 정보가 출력됩니다:
- 데이터 처리 진행률
- 모델 학습 단계 및 상태
- 탐지된 이상치 통계
- 저장된 모델 정보

### 상태 출력 예시
```
============================================================
SYSTEM STATUS
============================================================
Data Progress: 168/43848 (0.4%)
Model Phase: 2, Data Count: 168, Model Trained: True
Total Alerts: 42
Alert Levels: {'CRITICAL': 30, 'WARNING': 10, 'INFO': 2}
Models Saved: 2, Storage Used: 1.5 MB
============================================================
```

## 테스트 실행

### 시스템 테스트
```bash
python3 test_system.py
```

테스트 스크립트는 다음을 검증합니다:
- 개별 모듈 기능 테스트
- 통합 시스템 테스트
- 이상치 탐지 기능 확인

## 시스템 아키텍처

### 이벤트 기반 설계
- 모듈 간 느슨한 결합을 위해 이벤트 기반 아키텍처 적용
- 각 모듈은 독립적으로 동작하며 이벤트를 통해 통신

### 모듈별 책임
- **DataController**: 데이터 스트리밍 및 타이밍 제어
- **ModelController**: Prophet 모델 관리 및 예측/탐지
- **Storage**: 모델 파일 영속성 관리
- **AlertService**: 알림 처리 및 로깅

## 성능 고려사항

- **메모리 사용**: 데이터가 누적되므로 장기 실행 시 메모리 모니터링 필요
- **모델 학습 시간**: 데이터가 증가할수록 학습 시간 증가
- **스트리밍 속도**: 높은 배속 사용 시 CPU 사용률 증가

## 데이터

- 데이터 파일: `examples/archives/seoul_last_5years_hourly.jsonl`
- 기간: 최근 5년간 시간별 데이터
- 형식: JSONL (JSON Lines)
- 필드: timestamp, temperature