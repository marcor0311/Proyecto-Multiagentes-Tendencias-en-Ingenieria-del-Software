from app.agents.planner_agent import PlannerAgent

class AgentService:
    """
    Servicio central que orquesta qué agente se usa
    y devuelve una respuesta procesada.
    """

    def __init__(self):
        # Por ahora solo usamos un agente (Planner)
        self.planner = PlannerAgent()

    async def run(self, message: str) -> str:
        """
        Ejecuta el agente planner (por ahora)
        y devuelve la respuesta generada por Azure OpenAI.
        """
        result = self.planner.process(message)
        return result