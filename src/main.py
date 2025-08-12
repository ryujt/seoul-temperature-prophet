"""
Main: 시스템 초기화 및 실행
- 책임: 모든 모듈 초기화 및 이벤트 연결
"""

import signal
import sys
import time
from typing import Dict, Any
from data_controller import DataController
from model_controller import ModelController
from storage import Storage
from alert_service import AlertService


class AnomalyDetectionSystem:
    """Prophet 기반 실시간 이상탐지 시스템"""
    
    def __init__(self, data_file: str = 'examples/archives/seoul_last_5years_hourly.jsonl', 
                 speed: float = 100.0):
        """
        Args:
            data_file: 입력 데이터 파일 경로
            speed: 데이터 재생 속도 (1.0 = 실시간, 100.0 = 100배속)
        """
        print("=" * 80)
        print("Prophet-based Real-time Anomaly Detection System")
        print("=" * 80)
        
        # 모듈 초기화
        self.data_controller = DataController(file_path=data_file, speed=speed)
        self.model_controller = ModelController(confidence_interval=0.95)
        self.storage = Storage(storage_path='models')
        self.alert_service = AlertService(log_path='logs', threshold_deviation=5.0)
        
        # 이벤트 연결 (Job Flow Diagram 구현)
        self._connect_events()
        
        # 시스템 상태
        self.is_running = False
        
        # 시그널 핸들러 설정
        signal.signal(signal.SIGINT, self._signal_handler)
        
        print("System initialized successfully")
    
    def _connect_events(self):
        """이벤트 핸들러 연결 (Job Flow Diagram 구현)"""
        
        # DataController.OnData --> ModelController.Predict
        self.data_controller.on_data = self._handle_on_data
        
        # ModelController.OnAnomaly --> AlertService.Notify
        self.model_controller.on_anomaly = self._handle_on_anomaly
        
        # ModelController.OnModelUpdated --> Storage.SaveModel
        self.model_controller.on_model_updated = self._handle_on_model_updated
        
        print("Event handlers connected")
    
    def _handle_on_data(self, data: Dict[str, Any]):
        """DataController.OnData 이벤트 처리"""
        # ModelController.Predict 호출
        self.model_controller.predict(data)
    
    def _handle_on_anomaly(self, anomaly_info: Dict[str, Any]):
        """ModelController.OnAnomaly 이벤트 처리"""
        # AlertService.Notify 호출
        self.alert_service.notify(anomaly_info)
    
    def _handle_on_model_updated(self, filename: str):
        """ModelController.OnModelUpdated 이벤트 처리"""
        # Storage.SaveModel 호출
        model_data = {
            'model': self.model_controller.model,
            'training_phase': self.model_controller.training_phase,
            'training_data_count': len(self.model_controller.training_data),
            'last_training_time': self.model_controller.last_training_time
        }
        self.storage.save_model(model_data, filename)
    
    def start(self):
        """시스템 시작"""
        print("\nStarting anomaly detection system...")
        print(f"Data streaming speed: {self.data_controller.speed}x")
        print("Press Ctrl+C to stop\n")
        
        self.is_running = True
        
        # 이전 모델 로드 시도
        self._load_previous_model()
        
        # 데이터 스트리밍 시작
        self.data_controller.start()
        
        # 메인 루프
        try:
            while self.is_running:
                # 상태 출력 (10초마다)
                time.sleep(10)
                if self.is_running:
                    self._print_status()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """시스템 중지"""
        print("\n\nStopping anomaly detection system...")
        self.is_running = False
        self.data_controller.stop()
        
        # 최종 통계 출력
        self._print_final_statistics()
        
        print("System stopped successfully")
    
    def _load_previous_model(self):
        """이전 모델 로드 시도"""
        latest_model = self.storage.get_latest_model()
        if latest_model:
            print(f"Found previous model: {latest_model}")
            model_data = self.storage.load_model(latest_model)
            if model_data:
                self.model_controller.model = model_data['model']
                self.model_controller.training_phase = model_data['training_phase']
                self.model_controller.last_training_time = model_data.get('last_training_time')
                print("Previous model loaded successfully")
        else:
            print("No previous model found. Starting fresh.")
    
    def _print_status(self):
        """현재 상태 출력"""
        if not self.is_running:
            return
        
        print("\n" + "=" * 60)
        print("SYSTEM STATUS")
        print("=" * 60)
        
        # DataController 상태
        dc_status = self.data_controller.get_progress()
        print(f"Data Progress: {dc_status['current_index']}/{dc_status['total_records']} "
              f"({dc_status['progress_percent']:.1f}%)")
        
        # ModelController 상태
        mc_status = self.model_controller.get_status()
        print(f"Model Phase: {mc_status['training_phase']}, "
              f"Data Count: {mc_status['data_count']}, "
              f"Model Trained: {mc_status['model_trained']}")
        
        # AlertService 상태
        alert_stats = self.alert_service.get_alert_statistics()
        print(f"Total Alerts: {alert_stats['total_alerts']}")
        if alert_stats['by_level']:
            print(f"Alert Levels: {alert_stats['by_level']}")
        
        # Storage 상태
        storage_info = self.storage.get_storage_info()
        print(f"Models Saved: {storage_info['model_count']}, "
              f"Storage Used: {storage_info['total_size_mb']} MB")
        
        print("=" * 60)
    
    def _print_final_statistics(self):
        """최종 통계 출력"""
        print("\n" + "=" * 80)
        print("FINAL STATISTICS")
        print("=" * 80)
        
        # 데이터 처리 통계
        dc_status = self.data_controller.get_progress()
        print(f"Total Data Processed: {dc_status['current_index']}/{dc_status['total_records']}")
        
        # 모델 학습 통계
        mc_status = self.model_controller.get_status()
        print(f"Final Model Phase: {mc_status['training_phase']}")
        print(f"Total Training Data: {mc_status['data_count']} records")
        
        # 알림 통계
        alert_stats = self.alert_service.get_alert_statistics()
        print(f"\nTotal Anomalies Detected: {alert_stats['total_alerts']}")
        if alert_stats['by_level']:
            print("Alerts by Level:")
            for level, count in alert_stats['by_level'].items():
                print(f"  - {level}: {count}")
        if alert_stats['by_type']:
            print("Alerts by Type:")
            for atype, count in alert_stats['by_type'].items():
                print(f"  - {atype}: {count}")
        
        # 최근 알림 출력
        if alert_stats['recent_alerts']:
            print("\nRecent Alerts:")
            for alert in alert_stats['recent_alerts']:
                print(f"  - {alert['timestamp']}: {alert['level']} "
                      f"(Deviation: {alert['deviation']:.2f}°C)")
        
        print("=" * 80)
    
    def _signal_handler(self, sig, frame):
        """시그널 핸들러"""
        print("\nReceived interrupt signal...")
        self.stop()
        sys.exit(0)


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Prophet-based Real-time Anomaly Detection System')
    parser.add_argument('--data', type=str, 
                       default='examples/archives/seoul_last_5years_hourly.jsonl',
                       help='Path to input data file (JSONL format)')
    parser.add_argument('--speed', type=float, default=100.0,
                       help='Data streaming speed (1.0 = real-time, 100.0 = 100x speed)')
    
    args = parser.parse_args()
    
    # 시스템 초기화 및 실행
    system = AnomalyDetectionSystem(data_file=args.data, speed=args.speed)
    system.start()


if __name__ == "__main__":
    main()