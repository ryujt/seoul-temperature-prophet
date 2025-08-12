"""
AlertService: 이상치 알림 처리 모듈
- 책임: 이상치 발생 시 알림 처리 및 로깅
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum


class AlertLevel(Enum):
    """알림 수준 정의"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertService:
    def __init__(self, log_path: str = 'logs', threshold_deviation: float = 5.0):
        """
        Args:
            log_path: 알림 로그 저장 경로
            threshold_deviation: 기본 임계 편차 (동적 임계값이 없을 때 사용)
        """
        self.log_path = log_path
        self.default_threshold_deviation = threshold_deviation
        self.alert_history: List[Dict[str, Any]] = []
        self._ensure_log_path()
        
        # 로그 파일 초기화
        self.log_filename = os.path.join(
            self.log_path, 
            f"alerts_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )
    
    def _ensure_log_path(self):
        """로그 경로 생성"""
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path, exist_ok=True)
            print(f"Created log directory: {self.log_path}")
    
    def notify(self, anomaly_info: Dict[str, Any]):
        """
        이상치 알림 처리
        
        Args:
            anomaly_info: 이상치 정보
                - timestamp: 발생 시간
                - actual_value: 실제 값
                - predicted_value: 예측 값
                - lower_bound: 하한선
                - upper_bound: 상한선
                - deviation: 편차
                - anomaly_type: 이상치 유형
        """
        # 알림 수준 결정
        alert_level = self._determine_alert_level(anomaly_info)
        
        # 알림 레코드 생성
        alert_record = {
            'alert_id': self._generate_alert_id(),
            'timestamp': anomaly_info['timestamp'],
            'detected_at': datetime.now().isoformat(),
            'alert_level': alert_level.value,
            'actual_value': anomaly_info['actual_value'],
            'predicted_value': anomaly_info['predicted_value'],
            'lower_bound': anomaly_info['lower_bound'],
            'upper_bound': anomaly_info['upper_bound'],
            'deviation': anomaly_info['deviation'],
            'anomaly_type': anomaly_info['anomaly_type'],
            'message': self._generate_alert_message(anomaly_info, alert_level)
        }
        
        # 알림 처리
        self._process_alert(alert_record)
        
        # 히스토리 저장
        self.alert_history.append(alert_record)
        
        # 로그 파일에 기록
        self._write_to_log(alert_record)
    
    def _determine_alert_level(self, anomaly_info: Dict[str, Any]) -> AlertLevel:
        """
        알림 수준 결정 (학습 데이터 기반 동적 임계값 사용)
        
        Returns:
            AlertLevel 열거형 값
        """
        deviation = anomaly_info['deviation']
        
        # 동적 임계값이 있는 경우 사용
        if 'thresholds' in anomaly_info and anomaly_info['thresholds'] is not None:
            thresholds = anomaly_info['thresholds']
            
            if deviation >= thresholds['critical_threshold']:
                return AlertLevel.CRITICAL
            elif deviation >= thresholds['warning_threshold']:
                return AlertLevel.WARNING
            else:
                return AlertLevel.INFO
        else:
            # 기본 임계값 사용 (하위 호환성)
            if deviation >= self.default_threshold_deviation:
                return AlertLevel.CRITICAL
            elif deviation >= self.default_threshold_deviation * 0.5:
                return AlertLevel.WARNING
            else:
                return AlertLevel.INFO
    
    def _generate_alert_id(self) -> str:
        """
        고유 알림 ID 생성
        
        Returns:
            알림 ID
        """
        return f"ALERT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.alert_history) + 1:04d}"
    
    def _generate_alert_message(self, anomaly_info: Dict[str, Any], alert_level: AlertLevel) -> str:
        """
        알림 메시지 생성
        
        Returns:
            알림 메시지
        """
        if alert_level == AlertLevel.CRITICAL:
            prefix = "🚨 CRITICAL ANOMALY"
        elif alert_level == AlertLevel.WARNING:
            prefix = "⚠️ WARNING"
        else:
            prefix = "ℹ️ INFO"
        
        message = (
            f"{prefix}: Temperature anomaly detected at {anomaly_info['timestamp']}. "
            f"Actual: {anomaly_info['actual_value']:.2f}°C, "
            f"Expected: {anomaly_info['predicted_value']:.2f}°C "
            f"(Range: {anomaly_info['lower_bound']:.2f} - {anomaly_info['upper_bound']:.2f}), "
            f"Deviation: {anomaly_info['deviation']:.2f}°C"
        )
        
        return message
    
    def _process_alert(self, alert_record: Dict[str, Any]):
        """
        알림 처리 (콘솔 출력, 외부 시스템 연동 등)
        
        Args:
            alert_record: 알림 레코드
        """
        # 콘솔 출력
        print(f"\n{alert_record['message']}\n")
        
        # Critical 알림인 경우 추가 처리
        if alert_record['alert_level'] == AlertLevel.CRITICAL.value:
            self._handle_critical_alert(alert_record)
    
    def _handle_critical_alert(self, alert_record: Dict[str, Any]):
        """
        Critical 알림 추가 처리
        
        Args:
            alert_record: 알림 레코드
        """
        print("=" * 80)
        print("CRITICAL ALERT - Immediate attention required!")
        print(f"Alert ID: {alert_record['alert_id']}")
        print(f"Timestamp: {alert_record['timestamp']}")
        print(f"Deviation: {alert_record['deviation']:.2f}°C")
        print("=" * 80)
        
        # 여기에 이메일, SMS, Slack 등 외부 알림 시스템 연동 가능
    
    def _write_to_log(self, alert_record: Dict[str, Any]):
        """
        로그 파일에 기록
        
        Args:
            alert_record: 알림 레코드
        """
        try:
            with open(self.log_filename, 'a', encoding='utf-8') as f:
                f.write(json.dumps(alert_record, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """
        알림 통계 반환
        
        Returns:
            알림 통계 정보
        """
        if not self.alert_history:
            return {
                'total_alerts': 0,
                'by_level': {},
                'by_type': {}
            }
        
        # 수준별 집계
        by_level = {}
        by_type = {}
        
        for alert in self.alert_history:
            level = alert['alert_level']
            anomaly_type = alert['anomaly_type']
            
            by_level[level] = by_level.get(level, 0) + 1
            by_type[anomaly_type] = by_type.get(anomaly_type, 0) + 1
        
        # 최근 알림
        recent_alerts = self.alert_history[-5:] if len(self.alert_history) >= 5 else self.alert_history
        
        return {
            'total_alerts': len(self.alert_history),
            'by_level': by_level,
            'by_type': by_type,
            'recent_alerts': [
                {
                    'alert_id': a['alert_id'],
                    'timestamp': a['timestamp'],
                    'level': a['alert_level'],
                    'deviation': a['deviation']
                }
                for a in recent_alerts
            ]
        }
    
    def clear_history(self):
        """알림 히스토리 초기화"""
        self.alert_history.clear()
        print("Alert history cleared")