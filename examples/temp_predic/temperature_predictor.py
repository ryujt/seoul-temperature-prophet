#!/usr/bin/env python3
"""
서울 기온 예측 모델
Facebook Prophet을 사용하여 날짜와 시간을 기반으로 온도를 예측합니다.
"""

import json
import pickle
import os
import pandas as pd
from prophet import Prophet
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class TemperaturePredictor:
    def __init__(self, data_file='seoul_last_5years_hourly.jsonl', model_file=None):
        """
        온도 예측 모델 초기화
        
        Args:
            data_file: JSONL 데이터 파일 경로
            model_file: 저장된 모델 파일 경로 (있으면 로드)
        """
        self.data_file = data_file
        self.model_file = model_file
        self.model = None
        self.data = None
        self.metadata = None
        
        # 저장된 모델이 있으면 로드
        if model_file and os.path.exists(model_file):
            self.load_model(model_file)
        
    def load_data(self):
        """JSONL 파일에서 데이터 로드 및 전처리"""
        print("데이터 로드 중...")
        
        # JSONL 파일 읽기
        data_list = []
        with open(self.data_file, 'r', encoding='utf-8') as f:
            for line in f:
                data_list.append(json.loads(line))
        
        # DataFrame으로 변환
        df = pd.DataFrame(data_list)
        
        # Prophet에 필요한 형식으로 변환
        # ds: 날짜시간, y: 타겟 값 (온도)
        df['ds'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        df['y'] = df['temperature']
        
        # 필요한 컬럼만 선택
        self.data = df[['ds', 'y']].copy()
        
        # NaN 값 제거
        self.data = self.data.dropna()
        
        print(f"총 {len(self.data)}개의 데이터 로드 완료")
        print(f"데이터 기간: {self.data['ds'].min()} ~ {self.data['ds'].max()}")
        
        return self.data
    
    def train_model(self):
        """Prophet 모델 학습"""
        if self.data is None:
            self.load_data()
        
        print("\n모델 학습 중...")
        
        # Prophet 모델 초기화
        # 한국의 계절성을 고려한 설정
        self.model = Prophet(
            yearly_seasonality=True,  # 연간 계절성
            weekly_seasonality=True,  # 주간 계절성
            daily_seasonality=True,   # 일간 계절성
            changepoint_prior_scale=0.05,  # 트렌드 변화점 유연성
            seasonality_prior_scale=10.0,  # 계절성 강도
        )
        
        # 모델 학습
        self.model.fit(self.data)
        
        print("모델 학습 완료!")
        
    def predict_temperature(self, date_str, time_str):
        """
        특정 날짜와 시간의 온도 예측
        
        Args:
            date_str: 날짜 문자열 (예: "2024-12-25")
            time_str: 시간 문자열 (예: "14:00")
            
        Returns:
            예측된 온도 값
        """
        if self.model is None:
            raise ValueError("모델이 학습되지 않았습니다. train_model()을 먼저 실행하세요.")
        
        # 예측할 날짜시간 생성
        datetime_str = f"{date_str} {time_str}"
        future_date = pd.DataFrame({
            'ds': [pd.to_datetime(datetime_str)]
        })
        
        # 예측 수행
        forecast = self.model.predict(future_date)
        
        # 예측 결과 반환 (yhat: 예측값)
        predicted_temp = forecast['yhat'].iloc[0]
        
        # 불확실성 구간도 함께 반환
        lower_bound = forecast['yhat_lower'].iloc[0]
        upper_bound = forecast['yhat_upper'].iloc[0]
        
        return {
            'date': date_str,
            'time': time_str,
            'predicted_temperature': round(predicted_temp, 1),
            'lower_bound': round(lower_bound, 1),
            'upper_bound': round(upper_bound, 1)
        }
    
    def evaluate_model(self, test_size=100):
        """
        모델 성능 평가
        
        Args:
            test_size: 테스트에 사용할 최근 데이터 개수
        """
        if self.data is None:
            self.load_data()
        
        # 데이터가 충분한지 확인
        if len(self.data) < test_size + 100:
            print(f"경고: 데이터가 충분하지 않습니다. 전체 데이터 수: {len(self.data)}")
            return {'mae': float('nan'), 'rmse': float('nan')}
        
        # 학습/테스트 데이터 분할
        train_data = self.data[:-test_size].copy()
        test_data = self.data[-test_size:].copy()
        
        # 테스트 데이터에 NaN이 있는지 확인
        if test_data['y'].isna().any():
            print("경고: 테스트 데이터에 결측값이 있습니다.")
            test_data = test_data.dropna()
        
        if len(test_data) == 0:
            print("경고: 유효한 테스트 데이터가 없습니다.")
            return {'mae': float('nan'), 'rmse': float('nan')}
        
        # 학습 데이터로 모델 재학습
        temp_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0,
        )
        temp_model.fit(train_data)
        
        # 테스트 데이터에 대한 예측
        forecast = temp_model.predict(test_data[['ds']])
        
        # 예측값과 실제값 정렬
        forecast = forecast.set_index('ds')
        test_data = test_data.set_index('ds')
        
        # 같은 인덱스에 대해서만 비교
        common_index = forecast.index.intersection(test_data.index)
        
        if len(common_index) == 0:
            print("경고: 예측값과 실제값의 날짜가 일치하지 않습니다.")
            return {'mae': float('nan'), 'rmse': float('nan')}
        
        y_true = test_data.loc[common_index, 'y']
        y_pred = forecast.loc[common_index, 'yhat']
        
        # 평균 절대 오차(MAE) 계산
        mae = abs(y_pred - y_true).mean()
        
        # 평균 제곱근 오차(RMSE) 계산
        rmse = ((y_pred - y_true) ** 2).mean() ** 0.5
        
        print(f"\n모델 성능 평가 (최근 {len(common_index)}개 데이터):")
        print(f"평균 절대 오차(MAE): {mae:.2f}°C")
        print(f"평균 제곱근 오차(RMSE): {rmse:.2f}°C")
        
        return {'mae': mae, 'rmse': rmse}
    
    def save_model(self, model_file='trained_model.pkl', metadata_file='model_metadata.json'):
        """
        학습된 모델을 파일로 저장
        
        Args:
            model_file: 저장할 모델 파일 경로
            metadata_file: 저장할 메타데이터 파일 경로
        """
        if self.model is None:
            raise ValueError("저장할 모델이 없습니다. train_model()을 먼저 실행하세요.")
        
        # 모델 저장
        with open(model_file, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"모델 저장 완료: {model_file}")
        
        # 메타데이터 저장
        if self.data is not None:
            metadata = {
                'saved_at': datetime.now().isoformat(),
                'data_file': self.data_file,
                'data_count': len(self.data),
                'data_start': str(self.data['ds'].min()),
                'data_end': str(self.data['ds'].max()),
            }
        else:
            metadata = {
                'saved_at': datetime.now().isoformat(),
                'data_file': self.data_file,
            }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"메타데이터 저장 완료: {metadata_file}")
        
        self.metadata = metadata
        return model_file, metadata_file
    
    def load_model(self, model_file='trained_model.pkl', metadata_file='model_metadata.json'):
        """
        저장된 모델을 로드
        
        Args:
            model_file: 로드할 모델 파일 경로
            metadata_file: 로드할 메타데이터 파일 경로
        """
        if not os.path.exists(model_file):
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {model_file}")
        
        # 모델 로드
        with open(model_file, 'rb') as f:
            self.model = pickle.load(f)
        print(f"모델 로드 완료: {model_file}")
        
        # 메타데이터 로드 (있으면)
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            print(f"메타데이터 로드 완료: {metadata_file}")
            
            # 메타데이터 정보 출력
            if 'data_count' in self.metadata:
                print(f"  - 학습 데이터: {self.metadata['data_count']}개")
            if 'data_start' in self.metadata and 'data_end' in self.metadata:
                print(f"  - 데이터 기간: {self.metadata['data_start']} ~ {self.metadata['data_end']}")
        
        return self.model


def main():
    """메인 실행 함수"""
    # 예측 모델 초기화
    predictor = TemperaturePredictor('examples/archives/seoul_last_5years_hourly.jsonl')
    
    # 데이터 로드
    predictor.load_data()
    
    # 모델 학습
    predictor.train_model()
    
    # 모델 성능 평가
    predictor.evaluate_model()
    
    # 예측 테스트
    print("\n" + "="*50)
    print("온도 예측 테스트")
    print("="*50)
    
    # 테스트 케이스들
    test_cases = [
        ("2024-01-01", "00:00"),  # 새해 자정
        ("2024-06-15", "14:00"),  # 여름 오후
        ("2024-12-25", "08:00"),  # 크리스마스 아침
        ("2025-03-01", "12:00"),  # 봄 점심
    ]
    
    for date, time in test_cases:
        result = predictor.predict_temperature(date, time)
        print(f"\n날짜: {result['date']} {result['time']}")
        print(f"예측 온도: {result['predicted_temperature']}°C")
        print(f"예측 범위: {result['lower_bound']}°C ~ {result['upper_bound']}°C")
    
    # 대화형 예측
    print("\n" + "="*50)
    print("대화형 온도 예측 (종료하려면 'q' 입력)")
    print("="*50)
    
    while True:
        print("\n예측할 날짜와 시간을 입력하세요.")
        date_input = input("날짜 (YYYY-MM-DD 형식, 예: 2024-12-25): ").strip()
        
        if date_input.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
            
        time_input = input("시간 (HH:MM 형식, 예: 14:00): ").strip()
        
        if time_input.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
        
        try:
            result = predictor.predict_temperature(date_input, time_input)
            print(f"\n예측 결과:")
            print(f"날짜/시간: {result['date']} {result['time']}")
            print(f"예측 온도: {result['predicted_temperature']}°C")
            print(f"신뢰구간: {result['lower_bound']}°C ~ {result['upper_bound']}°C")
        except Exception as e:
            print(f"오류 발생: {e}")
            print("올바른 형식으로 다시 입력해주세요.")


if __name__ == "__main__":
    main()