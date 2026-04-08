class MockKernel:

    async def invoke(self, agent_name, input):
        return f"[{agent_name}] proceso: {input}"


kernel = MockKernel()
