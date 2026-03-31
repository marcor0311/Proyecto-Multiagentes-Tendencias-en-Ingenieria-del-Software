from app.kernel.kernel import kernel

class PlannerAgent:

    async def run(self, input_text):
        result = await kernel.invoke("planner", input_text)
        return result