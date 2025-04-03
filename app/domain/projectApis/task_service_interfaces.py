from abc import ABC, abstractmethod
from typing import Dict, Optional

class TaskServiceInterface(ABC):
    @abstractmethod
    async def GetTasks(projectIds: Optional[list] = None) -> list:
        pass
    @abstractmethod
    async def CreateTasks(self, Task_data: Dict) -> Dict:
        pass