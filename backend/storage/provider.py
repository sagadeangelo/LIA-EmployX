from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class StorageProvider(ABC):
    """Abstract base class for all storage providers in LIA-EmployX."""
    
    @abstractmethod
    def save_mission(self, mission_data: Dict[str, Any]) -> None:
        pass
        
    @abstractmethod
    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def list_missions(self) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def save_event(self, event_data: Dict[str, Any]) -> None:
        pass
        
    @abstractmethod
    def get_mission_events(self, mission_id: str) -> List[Dict[str, Any]]:
        pass
