from app.agents.planner_agent import PlannerAgent
from app.agents.evaluator_agent import EvaluatorAgent
from app.agents.generator_agent import GeneratorAgent
from app.agents.retriever_agent import RetrieverAgent

class Orchestrator:

    def __init__(self):
        self.planner = PlannerAgent()
        self.retriever = RetrieverAgent()
        self.generator = GeneratorAgent()
        self.evaluator = EvaluatorAgent()

    async def run(self, input_text):

        plan = await self.planner.run(input_text)
        retrieval = await self.retriever.run(input_text, plan)
        generation = await self.generator.run(input_text, plan, retrieval)
        validation = await self.evaluator.run(
            {
                "input": input_text,
                "plan": plan,
                "retrieval": retrieval,
                "generation": generation,
            }
        )

        return {
            "input": input_text,
            "plan": plan,
            "retrieval": retrieval,
            "generation": generation,
            "validation": validation
        }
