from app.agents.planner_agent import PlannerAgent
from app.agents.generator_agent import GeneratorAgent
from app.agents.retriever_agent import RetrieverAgent
from app.agents.builder_agent import BuilderAgent

class Orchestrator:

    def __init__(self):
        self.planner = PlannerAgent()
        self.retriever = RetrieverAgent()
        self.generator = GeneratorAgent()
        self.builder = BuilderAgent()

    async def run(self, request_data):
        plan = await self.planner.run(request_data)
        retrieval = await self.retriever.run(request_data, plan)
        generation = await self.generator.run(request_data, plan, retrieval)
        build = await self.builder.run(request_data, plan, generation)

        return {
            "input": request_data,
            "plan": plan,
            "retrieval": retrieval,
            "generation": generation,
            "build": build,
        }
