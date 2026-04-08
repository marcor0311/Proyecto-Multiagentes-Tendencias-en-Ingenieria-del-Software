from typing import Any, Dict

from app.orchestrator.orchestrator import Orchestrator


class AgentService:

    def __init__(self):
        self.orchestrator = Orchestrator()

    async def run(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.orchestrator.run(request_data)
