# 서울 기온 예측 프로그램

Facebook Prophet을 사용하여 서울의 시간별 기온을 예측하는 프로그램입니다.

## 설치 방법

### 1. 가상환경 생성 및 활성화
```bash
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# 또는
.venv\Scripts\activate  # Windows
```

### 2. 필요한 라이브러리 설치
```bash
pip install prophet pandas jsonlines matplotlib
```

### 3. 모델 학습 및 저장 (최초 1회)
```bash
python3 examples/temp_predic/prepare.py
```
이 명령을 실행하면 `trained_model.pkl`과 `model_metadata.json` 파일이 생성됩니다.

## 사용 방법

### 간단한 예제 실행
```bash
python3 examples/temp_predic/simple_predictor.py
```

### 전체 테스트 실행
```bash
python3 examples/temp_predic/test_predictor.py
```

### 대화형 모드 실행
```bash
python3 examples/temp_predic/est_predictor.py --interactive
```

## 파일 구조

- `prepare.py`: 모델 학습 및 저장 스크립트
  - 데이터 로드 및 전처리
  - Prophet 모델 학습
  - 모델과 메타데이터 저장

- `temperature_predictor.py`: 메인 예측 클래스
  - Prophet 모델 학습 및 예측
  - 모델 저장/로드 기능
  - 데이터 로드 및 전처리
  - 모델 성능 평가

- `test_predictor.py`: 테스트 스크립트
  - 모든 기능 테스트
  - 대화형 예측 모드
  - 저장된 모델 자동 사용

- `simple_predictor.py`: 간단한 사용 예시
  - 저장된 모델 자동 사용

## 주요 기능

- 과거 5년간의 서울 시간별 기온 데이터 학습
- 날짜와 시간 입력시 예상 기온 예측
- 예측 신뢰구간 제공
- 계절성 패턴 학습 (연간, 주간, 일간)

## 성능

- 평균 절대 오차(MAE): 약 2.85°C
- 평균 제곱근 오차(RMSE): 약 3.26°C

## 데이터

- 데이터 파일: `examples/archives/seoul_last_5years_hourly.jsonl`
- 기간: 2022-01-01 ~ 2025-08-09
- 형식: JSONL (JSON Lines)
- 필드: date, time, temperature, humidity, precip_probability, is_rain, is_snow

## Python 코드 예시

### 저장된 모델 사용 (빠른 예측)
```python
from temperature_predictor import TemperaturePredictor

# 저장된 모델 로드
predictor = TemperaturePredictor(model_file='trained_model.pkl')

# 온도 예측
result = predictor.predict_temperature("2024-12-25", "14:00")
print(f"예상 온도: {result['predicted_temperature']}°C")
print(f"예측 범위: {result['lower_bound']}°C ~ {result['upper_bound']}°C")
```

### 새로 학습하기
```python
from temperature_predictor import TemperaturePredictor

# 모델 초기화 및 학습
predictor = TemperaturePredictor('../archives/seoul_last_5years_hourly.jsonl')
predictor.load_data()
predictor.train_model()

# 모델 저장
predictor.save_model()

# 온도 예측
result = predictor.predict_temperature("2024-12-25", "14:00")
print(f"예상 온도: {result['predicted_temperature']}°C")
print(f"예측 범위: {result['lower_bound']}°C ~ {result['upper_bound']}°C")
```