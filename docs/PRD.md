# PRD – Prophet 기반 실시간 이상탐지 시스템

## 1. 개요

본 시스템은 **Facebook Prophet** 라이브러리를 기반으로 실시간 이상탐지 기능을 구현한다.
시간 단위 데이터가 순차적으로 유입되며, 예측 범위를 벗어나는 이상치 발생 시 **알림**을 제공한다.

---

## 2. 목표

* 시간 단위 데이터 스트리밍 처리
* Prophet 기반 이상탐지 및 계절성(연간·주간) 처리
* 이상치 발생 시 `OnAnomaly` 이벤트 발생

---

## 3. 요구사항

### 3.1 데이터 컨트롤 모듈

* **책임**: 데이터 로딩 및 시간 단위 순차 출력
* **입력 파일**: `examples/archives/seoul_last_5years_hourly.jsonl`
* **기능**:
  1. 초기화 시 JSONL 파일 전체 로드
  2. `Start()` 호출 시 시간 단위 데이터 순차 제공
  3. 각 데이터는 이벤트(`OnData`)로 모델 컨트롤 모듈에 전달
  4. 데이터 재생 속도는 설정값으로 조절 가능 (예: 실시간, N배속)
* **출력 이벤트**:
  * `OnData`

---

### 3.2 모델 컨트롤 모듈

* **책임**: 예측, 이상치 탐지
* **입력 파일**: `trained_model.pkl`
* **기능**:
  1. Prophet 모델 초기화 (`yearly_seasonality=True`, `weekly_seasonality=True`)
  2. 예측 시점과 실제 데이터 비교
  4. 예측 범위(신뢰구간) 이탈 시 `OnAnomaly` 이벤트 발생
* **출력 이벤트**:
  * `OnAnomaly`

---

## 4. 데이터 흐름 (Job Flow Diagram)

```
master: DataController
Object: DataController, ModelController, AlertService

DataController.OnCreate --> DataController.LoadModel
DataController.Start --> DataController.RunTimer
DataController.OnData --> ModelController.Predict
ModelController.OnAnomaly --> AlertService.Notify
```

---

## 5. 구현 모듈 구조

```
src/
  data_controller.py      # 데이터 로딩 및 스트리밍
  model_controller.py     # Prophet 기반 학습/예측/이상탐지
  main.py                  # 시스템 초기화 및 실행
```

---

## 6. 기타

* 아래 가이드 라인을 항상 준수해줘.
  * 단일 책임 원칙
    - 파일 단위로 하나의 기능만 담당하도록 작성
    - 클래스 단위로 하나의 기능만 담당하도록 작성
  * 의존성 낮추기
    - 객체 간의 의존성을 낮추기 위해 직접 참조하지 않고 이벤트 기반으로 구현.