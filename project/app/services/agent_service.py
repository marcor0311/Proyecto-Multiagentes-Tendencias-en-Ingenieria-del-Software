from app.orchestrator.orchestrator import Orchestrator
from app.utils.logger import get_logger


class AgentService:

    def __init__(self):
        self.orchestrator = Orchestrator()
        self.logger = get_logger("app.agent_service")

    async def run(self, message: str):
        self.logger.info("Inicio del flujo multiagente")
        self.logger.info("Mensaje recibido: %s", message)

        result = await self.orchestrator.run(message)

        self.logger.info("Fin del flujo multiagente")
        return result
