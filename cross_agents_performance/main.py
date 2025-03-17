from fastapi import FastAPI
from common.database import init_db
from cross_agents_performance.api.router import router as cross_agent_router

# from   .api.router import router as interaction_router

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()  # Initialize Beanie

app.include_router(cross_agent_router, prefix="/v1/cross_agent")