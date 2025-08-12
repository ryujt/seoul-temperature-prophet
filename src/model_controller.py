"""
ModelController: Prophet 기반 예측/이상탐지 모듈
- 책임: 사전 훈련된 모델을 사용한 예측 및 이상치 탐지
- 출력 이벤트: OnAnomaly
"""

import pandas as pd
from prophet import Prophet
from typing import Callable, Optional, Dict, Any
from datetime import datetime
import pickle
import os


class ModelController:
    def __init__(self, confidence_interval: float = 0.95, model_file: str = 'trained_model.pkl'):
        """
        Args:
            confidence_interval: 예측 신뢰구간 (default: 95%)
            model_file: 사전 훈련된 모델 파일 경로
        """
        self.confidence_interval = confidence_interval
        self.model: Optional[Prophet] = None
        self.model_file = model_file
        
        # 이벤트 핸들러
        self.on_anomaly: Optional[Callable[[Dict[str, Any]], None]] = None
    
    def load_trained_model(self) -> bool:
        """사전 훈련된 모델 로드"""
        try:
            if not os.path.exists(self.model_file):
                print(f"Model file not found: {self.model_file}")
                return False
            
            with open(self.model_file, 'rb') as f:
                saved_data = pickle.load(f)
                
                # 모델 데이터 구조 확인 및 로드
                if isinstance(saved_data, dict) and 'model' in saved_data:
                    self.model = saved_data['model']
                else:
                    # 직접 모델 객체가 저장된 경우
                    self.model = saved_data
                
            print(f"Trained model loaded successfully from {self.model_file}")
            return True
            
        except Exception as e:
            print(f"Error loading trained model: {e}")
            return False
    
    def predict(self, data: Dict[str, Any]):
        """
        새로운 데이터 포인트 처리 및 이상치 탐지
        """
        if self.model is None:
            print("Warning: No trained model loaded. Cannot perform prediction.")
            return
        
        # 이상치 탐지 수행
        self._detect_anomaly(data)
    
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
    
    def get_status(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            'model_loaded': self.model is not None,
            'model_file': self.model_file
        }