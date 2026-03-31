from app.agents.planner_agent import PlannerAgent
from app.agents.evaluator_agent import EvaluatorAgent

class Orchestrator:

    def __init__(self):
        self.planner = PlannerAgent()
        self.evaluator = EvaluatorAgent()

    async def run(self, input_text):

        plan = await self.planner.run(input_text)

        validation = await self.evaluator.run(plan)

        return {
            "plan": plan,
            "validation": validation
        }