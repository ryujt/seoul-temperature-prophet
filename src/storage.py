"""
Storage: 모델 파일 저장 모듈
- 책임: Prophet 모델 파일 관리 및 저장
"""

import os
import pickle
from datetime import datetime
from typing import Any, Optional, List


class Storage:
    def __init__(self, storage_path: str = 'models'):
        """
        Args:
            storage_path: 모델 파일 저장 경로
        """
        self.storage_path = storage_path
        self._ensure_storage_path()
    
    def _ensure_storage_path(self):
        """저장 경로 생성"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)
            print(f"Created storage directory: {self.storage_path}")
    
    def save_model(self, model_data: Any, filename: str):
        """
        모델 파일 저장
        
        Args:
            model_data: 저장할 모델 데이터
            filename: 파일명 (날짜 형식 포함)
        """
        filepath = os.path.join(self.storage_path, filename)
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            print(f"Model saved successfully: {filepath}")
            
            # 저장 후 파일 정리 (최근 5개만 유지)
            self._cleanup_old_models()
            
        except Exception as e:
            print(f"Error saving model to {filepath}: {e}")
    
    def save_training_data(self, training_data: List[Any], filename: str):
        """
        학습 데이터 파일 저장
        
        Args:
            training_data: 저장할 학습 데이터
            filename: 파일명 (날짜 형식 포함)
        """
        filepath = os.path.join(self.storage_path, filename)
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'training_data': training_data,
                    'saved_at': datetime.now(),
                    'data_count': len(training_data)
                }, f)
            print(f"Training data saved successfully: {filepath}")
            
            # 저장 후 파일 정리 (최근 5개만 유지)
            self._cleanup_old_training_data()
            
        except Exception as e:
            print(f"Error saving training data to {filepath}: {e}")
    
    def load_training_data(self, filename: str) -> Optional[List[Any]]:
        """
        학습 데이터 파일 로드
        
        Args:
            filename: 로드할 파일명
            
        Returns:
            로드된 학습 데이터 또는 None
        """
        filepath = os.path.join(self.storage_path, filename)
        
        if not os.path.exists(filepath):
            print(f"Training data file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            print(f"Training data loaded successfully: {filepath}")
            return data['training_data']
        except Exception as e:
            print(f"Error loading training data from {filepath}: {e}")
            return None
    
    def load_model(self, filename: str) -> Optional[Any]:
        """
        모델 파일 로드
        
        Args:
            filename: 로드할 파일명
            
        Returns:
            로드된 모델 데이터 또는 None
        """
        filepath = os.path.join(self.storage_path, filename)
        
        if not os.path.exists(filepath):
            print(f"Model file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            print(f"Model loaded successfully: {filepath}")
            return model_data
        except Exception as e:
            print(f"Error loading model from {filepath}: {e}")
            return None
    
    def get_latest_model(self) -> Optional[str]:
        """
        가장 최근 모델 파일명 반환
        
        Returns:
            최신 모델 파일명 또는 None
        """
        model_files = self._get_model_files()
        
        if not model_files:
            return None
        
        # 파일명 기준 정렬 (최신순)
        model_files.sort(reverse=True)
        return model_files[0]
    
    def _get_model_files(self) -> List[str]:
        """
        저장된 모델 파일 목록 반환
        
        Returns:
            모델 파일명 리스트
        """
        if not os.path.exists(self.storage_path):
            return []
        
        files = []
        for filename in os.listdir(self.storage_path):
            if filename.startswith('model_') and filename.endswith('.pkl'):
                files.append(filename)
        
        return files
    
    def _get_training_data_files(self) -> List[str]:
        """
        저장된 학습 데이터 파일 목록 반환
        
        Returns:
            학습 데이터 파일명 리스트
        """
        if not os.path.exists(self.storage_path):
            return []
        
        files = []
        for filename in os.listdir(self.storage_path):
            if filename.startswith('training_data_') and filename.endswith('.pkl'):
                files.append(filename)
        
        return files
    
    def _cleanup_old_models(self, keep_count: int = 5):
        """
        오래된 모델 파일 정리 (최근 N개만 유지)
        
        Args:
            keep_count: 유지할 파일 개수
        """
        model_files = self._get_model_files()
        
        if len(model_files) <= keep_count:
            return
        
        # 파일명 기준 정렬 (최신순)
        model_files.sort(reverse=True)
        
        # 삭제할 파일들
        files_to_delete = model_files[keep_count:]
        
        for filename in files_to_delete:
            filepath = os.path.join(self.storage_path, filename)
            try:
                os.remove(filepath)
                print(f"Deleted old model: {filename}")
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
    
    def _cleanup_old_training_data(self, keep_count: int = 5):
        """
        오래된 학습 데이터 파일 정리 (최근 N개만 유지)
        
        Args:
            keep_count: 유지할 파일 개수
        """
        data_files = self._get_training_data_files()
        
        if len(data_files) <= keep_count:
            return
        
        # 파일명 기준 정렬 (최신순)
        data_files.sort(reverse=True)
        
        # 삭제할 파일들
        files_to_delete = data_files[keep_count:]
        
        for filename in files_to_delete:
            filepath = os.path.join(self.storage_path, filename)
            try:
                os.remove(filepath)
                print(f"Deleted old training data: {filename}")
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
    
    def get_storage_info(self) -> dict:
        """
        저장소 정보 반환
        
        Returns:
            저장소 상태 정보
        """
        model_files = self._get_model_files()
        data_files = self._get_training_data_files()
        
        total_size = 0
        for filename in model_files + data_files:
            filepath = os.path.join(self.storage_path, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
        
        return {
            'storage_path': self.storage_path,
            'model_count': len(model_files),
            'training_data_count': len(data_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'latest_model': self.get_latest_model(),
            'model_files': model_files[:5],  # 최근 5개만
            'training_data_files': data_files[:5]  # 최근 5개만
        }