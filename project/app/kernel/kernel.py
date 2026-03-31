class MockKernel:

    async def invoke(self, agent_name, input):
        return f"[{agent_name}] procesó: {input}"

kernel = MockKernel()