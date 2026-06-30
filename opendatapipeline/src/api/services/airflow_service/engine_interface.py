from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger(__name__)


EngineType = Enum('EngineType', {'DLT': 'dlt', 'SPARK': 'spark'})


class RunEngine(ABC):
    """
    Abstract base class for execution engines
    """
    
    def __init__(self):
        self._engine_types = EngineType
        pass
    
    @abstractmethod
    def required_arguments(self) -> list:
        '''
        required job arguments to run a particular engine
        '''
        pass
    
    @abstractmethod
    def engine_type(self) -> EngineType:
        pass


class SparkEngine(RunEngine):
    """Spark execution engine implementation"""
    
    def required_arguments(self) -> list:
        '''required job arguments to run a particular engine'''
        return []  
    
    def engine_type(self) -> EngineType:
        return EngineType.SPARK


class DLTEngine(RunEngine):
    """DLT execution engine implementation"""
    
    def required_arguments(self) -> list:
        '''required job arguments to run a particular engine'''
        return []  
    
    def engine_type(self) -> EngineType:
        return EngineType.DLT


def get_engine(run_engine_type: str = None) -> Optional[RunEngine]:
    """
    Get engine instance based on run_engine_type
    
    Args:
        run_engine_type: Engine type string ('spark', 'dlt', or None)
        
    Returns:
        Optional[RunEngine]: Engine instance or None for default (Spark)
    """
    if run_engine_type and run_engine_type.lower() in ['dlt', 'spark']:
        if run_engine_type.lower() == 'dlt':
            return DLTEngine()
        elif run_engine_type.lower() == 'spark':
            return SparkEngine()
    
    # Default to Spark engine
    return SparkEngine()
