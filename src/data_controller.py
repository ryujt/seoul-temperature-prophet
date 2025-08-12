"""
DataController: 데이터 로딩 및 시간 단위 순차 출력 모듈
- 책임: JSONL 파일 로드 및 시간 단위 스트리밍
- 출력 이벤트: OnData
"""

import json
import time
import threading
from typing import Callable, Optional, List, Dict, Any
from datetime import datetime


class DataController:
    def __init__(self, file_path: str = 'examples/archives/seoul_last_5years_hourly.jsonl', speed: float = 1.0):
        """
        Args:
            file_path: JSONL 파일 경로
            speed: 데이터 재생 속도 (1.0 = 실시간, 10.0 = 10배속)
        """
        self.file_path = file_path
        self.speed = speed
        self.data: List[Dict[str, Any]] = []
        self.current_index = 0
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # 이벤트 핸들러
        self.on_data: Optional[Callable[[Dict[str, Any]], None]] = None
        
        # 초기화 시 데이터 로드
        self._load_data()
    
    def _load_data(self):
        """JSONL 파일 전체 로드"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        # date와 time 필드를 timestamp로 결합
                        if 'date' in record and 'time' in record:
                            record['timestamp'] = f"{record['date']} {record['time']}"
                        self.data.append(record)
            print(f"Loaded {len(self.data)} records from {self.file_path}")
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            self.data = []
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = []
    
    def start(self):
        """시간 단위 데이터 순차 제공 시작"""
        if not self.data:
            print("No data to stream")
            return
        
        self.running = True
        self.current_index = 0
        self.thread = threading.Thread(target=self._stream_data)
        self.thread.daemon = True
        self.thread.start()
        print("Data streaming started")
    
    def stop(self):
        """스트리밍 중지"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("Data streaming stopped")
    
    def _stream_data(self):
        """시간 단위로 데이터를 순차적으로 제공"""
        while self.running and self.current_index < len(self.data):
            record = self.data[self.current_index]
            
            # OnData 이벤트 발생
            if self.on_data:
                self.on_data(record)
            
            self.current_index += 1
            
            # 다음 데이터까지 대기 (속도 조절)
            if self.current_index < len(self.data) and self.speed > 0:
                # 실제로는 1시간 간격이지만, 시뮬레이션을 위해 짧은 간격 사용
                sleep_time = 1.0 / self.speed  # 1초를 speed로 나눔
                time.sleep(sleep_time)
        
        if self.current_index >= len(self.data):
            print("All data has been streamed")
            self.running = False
    
    def reset(self):
        """스트리밍 위치 초기화"""
        self.current_index = 0
        print("Data controller reset")
    
    def get_progress(self) -> Dict[str, Any]:
        """현재 진행 상황 반환"""
        return {
            'current_index': self.current_index,
            'total_records': len(self.data),
            'progress_percent': (self.current_index / len(self.data) * 100) if self.data else 0,
            'is_running': self.running
        }