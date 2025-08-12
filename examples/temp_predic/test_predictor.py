#!/usr/bin/env python3
"""
온도 예측 모델 테스트 스크립트
"""

import os
from temperature_predictor import TemperaturePredictor
import sys


def test_model():
    """모델 테스트 함수"""
    print("=" * 60)
    print("서울 기온 예측 모델 테스트")
    print("=" * 60)
    
    model_file = 'trained_model.pkl'
    
    # 저장된 모델이 있으면 로드, 없으면 학습
    if os.path.exists(model_file):
        print("\n저장된 모델을 사용합니다.")
        predictor = TemperaturePredictor(model_file=model_file)
        print("✓ 저장된 모델 로드 성공")
    else:
        print("\n모델 파일이 없어 새로 학습합니다.")
        # 예측 모델 초기화
        predictor = TemperaturePredictor('examples/archives/seoul_last_5years_hourly.jsonl')
        
        # 데이터 로드
        print("\n1. 데이터 로드 테스트")
        print("-" * 40)
        data = predictor.load_data()
        assert data is not None, "데이터 로드 실패"
        assert len(data) > 0, "데이터가 비어있음"
        print("✓ 데이터 로드 성공")
        
        # 모델 학습
        print("\n2. 모델 학습 테스트")
        print("-" * 40)
        predictor.train_model()
        assert predictor.model is not None, "모델 학습 실패"
        print("✓ 모델 학습 성공")
        
        # 모델 저장
        print("\n모델을 저장합니다...")
        predictor.save_model()
        print("✓ 모델 저장 완료")
    
    # 예측 테스트
    print("\n3. 온도 예측 테스트")
    print("-" * 40)
    
    test_cases = [
        ("2024-01-15", "09:00", "겨울 아침"),
        ("2024-04-20", "15:00", "봄 오후"),
        ("2024-07-30", "14:00", "여름 한낮"),
        ("2024-10-15", "18:00", "가을 저녁"),
        ("2024-12-31", "23:00", "연말 밤"),
        ("2025-02-14", "12:00", "발렌타인데이 점심"),
        ("2025-05-05", "10:00", "어린이날 오전"),
        ("2025-08-15", "06:00", "광복절 새벽"),
    ]
    
    for date, time, description in test_cases:
        try:
            result = predictor.predict_temperature(date, time)
            print(f"\n{description}")
            print(f"  날짜/시간: {date} {time}")
            print(f"  예측 온도: {result['predicted_temperature']}°C")
            print(f"  신뢰구간: [{result['lower_bound']}°C, {result['upper_bound']}°C]")
            
            # 합리적인 온도 범위 검증 (서울 기준: -20°C ~ 40°C)
            assert -20 <= result['predicted_temperature'] <= 40, f"비정상적인 온도 예측: {result['predicted_temperature']}°C"
            
        except Exception as e:
            print(f"  ❌ 예측 실패: {e}")
            return False
    
    print("\n✓ 모든 예측 테스트 성공")
    
    # 모델 성능 평가 (새로 학습한 경우에만)
    print("\n4. 모델 성능 평가")
    print("-" * 40)
    
    try:
        # 저장된 모델을 사용한 경우는 메타데이터에서 성능 정보 가져오기
        if predictor.metadata and 'performance' in predictor.metadata:
            metrics = predictor.metadata['performance']
            if metrics['mae'] is not None:
                print(f"저장된 모델의 성능 (학습 시 평가):")
                print(f"✓ MAE: {metrics['mae']:.2f}°C")
                print(f"✓ RMSE: {metrics['rmse']:.2f}°C")
            else:
                print("성능 평가 정보가 없습니다.")
        else:
            # 모델을 새로 학습한 경우에만 평가
            if predictor.data is not None:
                metrics = predictor.evaluate_model(test_size=100)
            else:
                print("데이터가 로드되지 않아 성능 평가를 건너뜁니다.")
                metrics = {'mae': None, 'rmse': None}
        
        # MAE와 RMSE가 있는 경우에만 평가
        if metrics.get('mae') is not None and metrics.get('rmse') is not None:
            # MAE와 RMSE가 합리적인 범위인지 확인
            # 일반적으로 기온 예측에서 MAE 2-4°C, RMSE 3-5°C 정도가 적절
            if metrics['mae'] > 0 and metrics['mae'] < 10:
                print(f"✓ MAE: {metrics['mae']:.2f}°C (양호)")
            else:
                print(f"⚠ MAE: {metrics['mae']:.2f}°C (확인 필요)")
                
            if metrics['rmse'] > 0 and metrics['rmse'] < 10:
                print(f"✓ RMSE: {metrics['rmse']:.2f}°C (양호)")
            else:
                print(f"⚠ RMSE: {metrics['rmse']:.2f}°C (확인 필요)")
            
    except Exception as e:
        print(f"⚠ 성능 평가 중 오류: {e}")
    
    print("\n" + "=" * 60)
    print("모든 테스트 완료!")
    print("=" * 60)
    
    return True


def interactive_prediction():
    """대화형 예측 함수"""
    print("\n" + "=" * 60)
    print("대화형 온도 예측 시스템")
    print("=" * 60)
    
    model_file = 'trained_model.pkl'
    
    # 저장된 모델이 있으면 로드, 없으면 학습
    if os.path.exists(model_file):
        print("\n저장된 모델을 로드합니다...")
        predictor = TemperaturePredictor(model_file=model_file)
        print("모델 준비 완료!\n")
    else:
        # 예측 모델 초기화 및 학습
        predictor = TemperaturePredictor('../archives/seoul_last_5years_hourly.jsonl')
        print("\n모델 준비 중...")
        predictor.load_data()
        predictor.train_model()
        predictor.save_model()
        print("모델 준비 완료!\n")
    
    print("날짜와 시간을 입력하면 예상 온도를 알려드립니다.")
    print("종료하려면 'q'를 입력하세요.\n")
    
    while True:
        try:
            date_input = input("날짜 입력 (YYYY-MM-DD): ").strip()
            if date_input.lower() == 'q':
                print("프로그램을 종료합니다.")
                break
                
            time_input = input("시간 입력 (HH:MM): ").strip()
            if time_input.lower() == 'q':
                print("프로그램을 종료합니다.")
                break
            
            result = predictor.predict_temperature(date_input, time_input)
            
            print("\n" + "-" * 40)
            print(f"예측 결과: {date_input} {time_input}")
            print(f"예상 온도: {result['predicted_temperature']}°C")
            print(f"예측 범위: {result['lower_bound']}°C ~ {result['upper_bound']}°C")
            print("-" * 40 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"\n오류: {e}")
            print("올바른 형식으로 다시 입력해주세요.\n")


if __name__ == "__main__":
    # 명령행 인자 확인
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_prediction()
    else:
        # 기본: 테스트 실행
        success = test_model()
        
        if success:
            print("\n대화형 모드를 실행하려면 다음 명령어를 사용하세요:")
            print("python3 test_predictor.py --interactive")
            sys.exit(0)
        else:
            sys.exit(1)