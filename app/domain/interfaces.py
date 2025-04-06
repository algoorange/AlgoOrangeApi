from abc import ABC, abstractmethod
from typing import Optional


class Agent(ABC):
    @abstractmethod
    async def handle_query(self, query: str,userContent: Optional[str] = None) -> str:
        pass
