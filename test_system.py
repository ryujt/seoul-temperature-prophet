"""
간단한 시스템 테스트 스크립트
"""

import json
import os
import time
from datetime import datetime, timedelta


def create_test_data():
    """테스트용 데이터 생성"""
    print("Creating test data...")
    
    # 테스트 데이터 디렉토리 생성
    os.makedirs('examples/archives', exist_ok=True)
    
    # 테스트 데이터 생성 (200시간 분량)
    test_data = []
    base_time = datetime(2024, 1, 1, 0, 0, 0)
    
    for hour in range(200):
        timestamp = base_time + timedelta(hours=hour)
        
        # 기본 온도 패턴 (일간/주간 변화 시뮬레이션)
        base_temp = 10.0
        daily_variation = 5.0 * ((hour % 24) / 12 - 1) ** 2  # 일간 변화
        weekly_variation = 2.0 * ((hour % 168) / 84 - 1)  # 주간 변화
        
        # 정상 온도
        temperature = base_temp + daily_variation + weekly_variation
        
        # 일부 이상치 추가 (5% 확률)
        if hour > 50 and hour % 20 == 0:
            temperature += 15.0  # 이상치
        
        test_data.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': round(temperature, 2)
        })
    
    # JSONL 파일로 저장
    filepath = 'examples/archives/test_data.jsonl'
    with open(filepath, 'w') as f:
        for record in test_data:
            f.write(json.dumps(record) + '\n')
    
    print(f"Test data created: {filepath} ({len(test_data)} records)")
    return filepath


def test_modules():
    """개별 모듈 테스트"""
    print("\n" + "=" * 60)
    print("Testing individual modules...")
    print("=" * 60)
    
    # DataController 테스트
    print("\n1. Testing DataController...")
    from src.data_controller import DataController
    
    data_file = create_test_data()
    dc = DataController(file_path=data_file, speed=1000.0)
    
    # 데이터 로드 확인
    assert len(dc.data) > 0, "Data loading failed"
    print(f"   ✓ Loaded {len(dc.data)} records")
    
    # ModelController 테스트
    print("\n2. Testing ModelController...")
    from src.model_controller import ModelController
    
    mc = ModelController()
    print("   ✓ ModelController initialized")
    
    # Storage 테스트
    print("\n3. Testing Storage...")
    from src.storage import Storage
    
    storage = Storage(storage_path='test_models')
    print("   ✓ Storage initialized")
    
    # AlertService 테스트
    print("\n4. Testing AlertService...")
    from src.alert_service import AlertService
    
    alert = AlertService(log_path='test_logs')
    
    # 테스트 알림
    test_anomaly = {
        'timestamp': '2024-01-01 12:00:00',
        'actual_value': 25.0,
        'predicted_value': 15.0,
        'lower_bound': 10.0,
        'upper_bound': 20.0,
        'deviation': 10.0,
        'anomaly_type': 'above_threshold'
    }
    alert.notify(test_anomaly)
    print("   ✓ Alert notification tested")
    
    # 정리
    import shutil
    if os.path.exists('test_models'):
        shutil.rmtree('test_models')
    if os.path.exists('test_logs'):
        shutil.rmtree('test_logs')
    
    print("\nAll module tests passed! ✓")


def test_integration():
    """통합 테스트 (짧은 실행)"""
    print("\n" + "=" * 60)
    print("Testing system integration...")
    print("=" * 60)
    
    import sys
    sys.path.insert(0, 'src')
    from main import AnomalyDetectionSystem
    
    # 테스트 데이터 생성
    test_file = create_test_data()
    
    # 시스템 초기화
    system = AnomalyDetectionSystem(data_file=test_file, speed=10000.0)
    
    # 짧은 시간 실행
    print("\nRunning system for 5 seconds...")
    system.data_controller.start()
    
    time.sleep(5)
    
    system.data_controller.stop()
    
    # 상태 확인
    dc_status = system.data_controller.get_progress()
    mc_status = system.model_controller.get_status()
    
    print(f"\nProcessed {dc_status['current_index']} records")
    print(f"Model phase: {mc_status['training_phase']}")
    
    print("\nIntegration test completed! ✓")


if __name__ == "__main__":
    print("=" * 60)
    print("Prophet Anomaly Detection System - Test Suite")
    print("=" * 60)
    
    # 모듈 테스트
    test_modules()
    
    # 통합 테스트
    test_integration()
    
    print("\n" + "=" * 60)
    print("All tests completed successfully! ✓")
    print("=" * 60)