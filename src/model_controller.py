"""
ModelController: Prophet 기반 학습/예측/이상탐지 모듈
- 책임: 데이터 학습, 예측, 이상치 탐지, 모델 저장
- 출력 이벤트: OnAnomaly, OnModelUpdated
"""

import pandas as pd
from prophet import Prophet
from typing import Callable, Optional, Dict, Any, List
from datetime import datetime, timedelta
import pickle
import os


class ModelController:
    def __init__(self, confidence_interval: float = 0.95):
        """
        Args:
            confidence_interval: 예측 신뢰구간 (default: 95%)
        """
        self.confidence_interval = confidence_interval
        self.model: Optional[Prophet] = None
        self.training_data: List[Dict[str, Any]] = []
        self.last_training_time: Optional[datetime] = None
        self.training_phase = 0  # 0: 초기, 1: 1일 학습 완료, 2: 1주 학습 완료, 3: 1개월 단위
        
        # 이벤트 핸들러
        self.on_anomaly: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_model_updated: Optional[Callable[[str], None]] = None
        
        # 학습 데이터 임계값 (시간 단위)
        self.HOURLY_THRESHOLD_DAY = 24      # 1일 = 24시간
        self.HOURLY_THRESHOLD_WEEK = 168    # 1주 = 168시간
        self.HOURLY_THRESHOLD_MONTH = 720   # 1개월 = 약 720시간 (30일 기준)
    
    def _initialize_model(self):
        """Prophet 모델 초기화"""
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,  # 시간 단위 데이터는 일간 계절성 제외
            interval_width=self.confidence_interval,
            changepoint_prior_scale=0.05  # 변화점 감지 민감도
        )
    
    def predict(self, data: Dict[str, Any]):
        """
        새로운 데이터 포인트 처리
        - 학습 데이터 축적
        - 주기별 학습 수행
        - 이상치 탐지
        """
        # 데이터 축적
        self.training_data.append(data)
        
        # 학습 주기 확인 및 학습 수행
        should_train = self._check_training_schedule()
        if should_train:
            self._train_model()
        
        # 모델이 학습된 경우에만 예측 수행
        if self.model is not None and self.training_phase > 0:
            self._detect_anomaly(data)
    
    def _check_training_schedule(self) -> bool:
        """학습 주기 확인"""
        data_count = len(self.training_data)
        
        if self.training_phase == 0 and data_count >= self.HOURLY_THRESHOLD_DAY:
            # 1단계: 1일치 데이터로 최초 학습
            return True
        elif self.training_phase == 1 and data_count >= self.HOURLY_THRESHOLD_WEEK:
            # 2단계: 1주치 데이터로 재학습
            return True
        elif self.training_phase >= 2:
            # 3단계 이후: 매월 재학습
            # 마지막 학습 이후 1개월치 데이터가 쌓였는지 확인
            last_trained_count = self._get_last_trained_count()
            if data_count - last_trained_count >= self.HOURLY_THRESHOLD_MONTH:
                return True
        
        return False
    
    def _get_last_trained_count(self) -> int:
        """마지막 학습 시점의 데이터 개수 계산"""
        if self.training_phase == 1:
            return self.HOURLY_THRESHOLD_DAY
        elif self.training_phase == 2:
            return self.HOURLY_THRESHOLD_WEEK
        else:
            # 3단계 이후는 마지막 학습 시점 계산
            return self.HOURLY_THRESHOLD_WEEK + (self.training_phase - 2) * self.HOURLY_THRESHOLD_MONTH
    
    def _train_model(self):
        """Prophet 모델 학습"""
        if not self.training_data:
            return
        
        print(f"Training model with {len(self.training_data)} data points (Phase {self.training_phase + 1})")
        
        # DataFrame 변환
        df = pd.DataFrame(self.training_data)
        
        # Prophet 형식으로 변환 (ds: 시간, y: 값)
        df_prophet = pd.DataFrame({
            'ds': pd.to_datetime(df['timestamp']),
            'y': df['temperature']
        })
        
        # 모델 초기화 및 학습 (전체 데이터로 재학습)
        self._initialize_model()
        self.model.fit(df_prophet)
        
        # 학습 완료 정보 업데이트
        self.last_training_time = datetime.now()
        self.training_phase += 1
        
        # 모델 및 학습 데이터 저장 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_filename = f"model_{timestamp}.pkl"
        data_filename = f"training_data_{timestamp}.pkl"
        
        # OnModelUpdated 이벤트 발생 (모델과 데이터 파일명 모두 전달)
        if self.on_model_updated:
            self.on_model_updated({
                'model_file': model_filename,
                'data_file': data_filename,
                'training_data': self.training_data.copy(),  # 현재 학습 데이터 복사본
                'phase': self.training_phase
            })
        
        print(f"Model training completed (Phase {self.training_phase})")
    
    def _detect_anomaly(self, data: Dict[str, Any]):
        """이상치 탐지"""
        if self.model is None:
            return
        
        # 예측을 위한 DataFrame 생성
        future_df = pd.DataFrame({
            'ds': [pd.to_datetime(data['timestamp'])]
        })
        
        # 예측 수행
        try:
            forecast = self.model.predict(future_df)
            
            # 실제 값과 예측 범위 비교
            actual_value = data['temperature']
            lower_bound = forecast['yhat_lower'].iloc[0]
            upper_bound = forecast['yhat_upper'].iloc[0]
            predicted_value = forecast['yhat'].iloc[0]
            
            # 신뢰구간 벗어나면 이상치로 판단
            if actual_value < lower_bound or actual_value > upper_bound:
                anomaly_info = {
                    'timestamp': data['timestamp'],
                    'actual_value': actual_value,
                    'predicted_value': predicted_value,
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound,
                    'deviation': abs(actual_value - predicted_value),
                    'anomaly_type': 'above_threshold' if actual_value > upper_bound else 'below_threshold'
                }
                
                # OnAnomaly 이벤트 발생
                if self.on_anomaly:
                    self.on_anomaly(anomaly_info)
                
                print(f"Anomaly detected at {data['timestamp']}: {actual_value:.2f} (expected: {predicted_value:.2f} [{lower_bound:.2f}, {upper_bound:.2f}])")
        
        except Exception as e:
            print(f"Error during anomaly detection: {e}")
    
    def save_model(self, filepath: str):
        """모델을 파일로 저장"""
        if self.model is None:
            print("No model to save")
            return
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'training_phase': self.training_phase,
                    'training_data_count': len(self.training_data),
                    'training_data': self.training_data,  # 학습 데이터도 함께 저장
                    'last_training_time': self.last_training_time
                }, f)
            print(f"Model saved to {filepath}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self, filepath: str):
        """저장된 모델 로드"""
        try:
            with open(filepath, 'rb') as f:
                saved_data = pickle.load(f)
                self.model = saved_data['model']
                self.training_phase = saved_data['training_phase']
                self.last_training_time = saved_data.get('last_training_time')
                # 저장된 학습 데이터가 있으면 로드
                if 'training_data' in saved_data:
                    self.training_data = saved_data['training_data']
            print(f"Model loaded from {filepath}")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            'training_phase': self.training_phase,
            'data_count': len(self.training_data),
            'model_trained': self.model is not None,
            'last_training_time': self.last_training_time.isoformat() if self.last_training_time else None
        }