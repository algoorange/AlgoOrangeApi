from abc import ABC, abstractmethod
from typing import Dict, Optional

class ProjectServiceInterface(ABC):
    @abstractmethod
    async def GetProjects(projectIds: Optional[list] = None) -> list:
        pass
    @abstractmethod
    async def CreateProject(self, project_data: Dict) -> Dict:
        pass
    @abstractmethod
    async def GetProjectsByProgram(programIds: list) -> list:
        pass
    @abstractmethod
    async def GetProjectsByPortfolio(portfolioIds: list) -> list:
        pass