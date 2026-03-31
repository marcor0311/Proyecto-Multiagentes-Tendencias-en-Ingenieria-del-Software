from app.kernel.kernel import kernel

class EvaluatorAgent:

    async def run(self, input_text):
        result = await kernel.invoke("evaluator", input_text)
        return result