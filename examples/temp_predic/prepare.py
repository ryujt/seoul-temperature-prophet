#!/usr/bin/env python3
"""
모델 학습 및 저장 스크립트
Prophet 모델을 학습하고 파일로 저장합니다.
"""

import json
import pickle
import pandas as pd
from prophet import Prophet
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')


def prepare_and_save_model(data_file='examples/archives/seoul_last_5years_hourly.jsonl',
                          model_file='trained_model.pkl',
                          metadata_file='model_metadata.json'):
    """
    데이터를 로드하고 모델을 학습한 후 저장합니다.
    
    Args:
        data_file: JSONL 데이터 파일 경로
        model_file: 저장할 모델 파일 경로
        metadata_file: 모델 메타데이터 파일 경로
    """
    
    print("="*60)
    print("Prophet 모델 학습 및 저장")
    print("="*60)
    
    # 1. 데이터 로드
    print("\n1. 데이터 로드 중...")
    data_list = []
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f:
            data_list.append(json.loads(line))
    
    df = pd.DataFrame(data_list)
    
    # Prophet 형식으로 변환
    df['ds'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    df['y'] = df['temperature']
    data = df[['ds', 'y']].copy()
    data = data.dropna()
    
    print(f"   - 총 {len(data)}개의 데이터 로드 완료")
    print(f"   - 데이터 기간: {data['ds'].min()} ~ {data['ds'].max()}")
    
    # 2. 모델 학습
    print("\n2. Prophet 모델 학습 중...")
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=True,
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10.0,
    )
    
    model.fit(data)
    print("   - 모델 학습 완료!")
    
    # 3. 모델 평가 (옵션)
    print("\n3. 모델 성능 평가...")
    test_size = 100
    
    if len(data) > test_size + 100:
        # 학습/테스트 데이터 분할
        train_data = data[:-test_size].copy()
        test_data = data[-test_size:].copy()
        
        # 평가용 모델 학습
        eval_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0,
        )
        eval_model.fit(train_data)
        
        # 예측 및 평가
        forecast = eval_model.predict(test_data[['ds']])
        forecast = forecast.set_index('ds')
        test_data = test_data.set_index('ds')
        
        common_index = forecast.index.intersection(test_data.index)
        if len(common_index) > 0:
            y_true = test_data.loc[common_index, 'y']
            y_pred = forecast.loc[common_index, 'yhat']
            
            mae = abs(y_pred - y_true).mean()
            rmse = ((y_pred - y_true) ** 2).mean() ** 0.5
            
            print(f"   - MAE: {mae:.2f}°C")
            print(f"   - RMSE: {rmse:.2f}°C")
        else:
            mae = rmse = None
            print("   - 평가 데이터 부족")
    else:
        mae = rmse = None
        print("   - 평가를 위한 데이터가 충분하지 않습니다")
    
    # 4. 모델 저장
    print(f"\n4. 모델 저장 중...")
    
    # 모델 파일 저장 (pickle)
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
    print(f"   - 모델 저장 완료: {model_file}")
    
    # 메타데이터 저장
    metadata = {
        'trained_at': datetime.now().isoformat(),
        'data_file': data_file,
        'data_count': len(data),
        'data_start': str(data['ds'].min()),
        'data_end': str(data['ds'].max()),
        'model_params': {
            'yearly_seasonality': True,
            'weekly_seasonality': True,
            'daily_seasonality': True,
            'changepoint_prior_scale': 0.05,
            'seasonality_prior_scale': 10.0,
        },
        'performance': {
            'mae': float(mae) if mae is not None else None,
            'rmse': float(rmse) if rmse is not None else None,
            'test_size': test_size if mae is not None else None
        }
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"   - 메타데이터 저장 완료: {metadata_file}")
    
    # 5. 결과 요약
    print("\n" + "="*60)
    print("학습 완료!")
    print("="*60)
    print(f"모델 파일: {model_file} ({os.path.getsize(model_file) / 1024 / 1024:.1f} MB)")
    print(f"메타데이터: {metadata_file}")
    
    if mae is not None:
        print(f"\n성능 지표:")
        print(f"  - MAE: {mae:.2f}°C")
        print(f"  - RMSE: {rmse:.2f}°C")
    
    print("\n이제 다음 명령으로 예측을 수행할 수 있습니다:")
    print("  python3 simple_predictor.py")
    print("  python3 test_predictor.py")
    
    return model, metadata


if __name__ == "__main__":
    import sys
    
    # 커맨드라인 인자 처리
    if len(sys.argv) > 1:
        model_file = sys.argv[1]
        print(f"모델을 {model_file}에 저장합니다.")
        prepare_and_save_model(model_file=model_file)
    else:
        # 기본 파일명 사용
        prepare_and_save_model()