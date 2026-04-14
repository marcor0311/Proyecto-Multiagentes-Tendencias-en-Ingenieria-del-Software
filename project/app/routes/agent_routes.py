from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.request_model import RequestModel
from app.services.agent_service import AgentService

router = APIRouter()
agent_service = AgentService()

@router.post("/agent")
async def run_agent(data: RequestModel):
    return await agent_service.run(data.to_agent_payload())

@router.get("/agent/download/{project_name}")
async def download_generated_project(project_name: str):
    safe_name = "".join(char if char.isalnum() or char in ("-", "_") else "-" for char in project_name)
    zip_path = Path(__file__).resolve().parents[2] / "generated" / f"{safe_name}.zip"

    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Zip no encontrado para el proyecto solicitado.")

    return FileResponse(zip_path, filename=f"{safe_name}.zip", media_type="application/zip")
