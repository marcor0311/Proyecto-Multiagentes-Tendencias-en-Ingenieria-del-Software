from fastapi import APIRouter
from app.models.request_model import RequestModel
from app.orchestrator.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()

@router.post("/agent")
async def run_agent(data: RequestModel):
    return await orchestrator.run(data.message)