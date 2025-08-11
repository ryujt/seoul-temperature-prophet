#!/usr/bin/env python3
"""
간단한 온도 예측 프로그램
날짜와 시간을 입력받아 온도를 예측합니다.
"""

import os
from temperature_predictor import TemperaturePredictor


def predict_temperature_simple(date_str, time_str):
    """
    간단한 온도 예측 함수
    
    Args:
        date_str: 날짜 (예: "2024-12-25")
        time_str: 시간 (예: "14:00")
    
    Returns:
        예측된 온도 값
    """
    # 저장된 모델이 있으면 로드, 없으면 학습
    model_file = 'trained_model.pkl'
    
    if os.path.exists(model_file):
        # 저장된 모델 사용
        print("저장된 모델을 사용합니다.")
        predictor = TemperaturePredictor(model_file=model_file)
        # 모델이 이미 로드됨
    else:
        # 새로 학습
        print("모델이 없어 새로 학습합니다.")
        predictor = TemperaturePredictor('examples/archives/seoul_last_5years_hourly.jsonl')
        predictor.load_data()
        predictor.train_model()
        # 모델 저장
        predictor.save_model()
    
    # 예측 수행
    result = predictor.predict_temperature(date_str, time_str)
    
    return result


# 사용 예시
if __name__ == "__main__":
    # 예시 1: 2024년 크리스마스 오후 2시
    result = predict_temperature_simple("2024-12-25", "14:00")
    print(f"2024-12-25 14:00 예상 온도: {result['predicted_temperature']}°C")
    print(f"예측 범위: {result['lower_bound']}°C ~ {result['upper_bound']}°C")
    
    print()
    
    # 예시 2: 
    date_str = "2025-08-12"
    time_str = "12:00"
    result = predict_temperature_simple(date_str, time_str)
    print(f"{date_str} {time_str} 예상 온도: {result['predicted_temperature']}°C")
    print(f"예측 범위: {result['lower_bound']}°C ~ {result['upper_bound']}°C")