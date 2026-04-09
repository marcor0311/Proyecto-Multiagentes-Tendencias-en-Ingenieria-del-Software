from fastapi import APIRouter
from app.models.request_model import RequestModel
from app.services.agent_service import AgentService

router = APIRouter()
agent_service = AgentService()

@router.post("/agent")
async def run_agent(data: RequestModel):
    return await agent_service.run(data.dict())
