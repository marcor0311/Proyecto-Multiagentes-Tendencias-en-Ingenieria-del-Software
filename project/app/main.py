from fastapi import FastAPI
from app.routes.agent_routes import router

app = FastAPI(
    title="Proyecto Multiagentes API",
    description="API de ejemplo para orquestar agentes de planeacion, recuperacion, generacion y evaluacion.",
    version="0.1.0",
)

app.include_router(router)
