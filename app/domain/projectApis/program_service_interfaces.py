from abc import ABC, abstractmethod
from typing import Dict, Optional

class ProgramServiceInterface(ABC):
    @abstractmethod
    async def GetPrograms(programIds: Optional[list] = None) -> list:
        pass
    @abstractmethod
    async def CreateProgram(self, program_data: Dict) -> Dict:
        pass 
    @abstractmethod
    async def GetProgramsByPortfolio(portfolioIds: list) -> list:
        pass