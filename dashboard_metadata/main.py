

from fastapi import FastAPI
from common.database import client, db, init_db 
from cross_agents_performance.api.router import router as cross_agents_router
from dashboard_metadata.src.api.router import router as dashboard_router

app = FastAPI(title="Interaction API", description="API for interaction data")
app.include_router(dashboard_router,prefix="/v1")


@app.get("/health")
async def health_check():

    try:

        

        await db.command("ping")  # Check with Motor
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}

@app.on_event("shutdown")  #Graceful Shutdown
async def shutdown_event():
    client.close()
    print("MongoDB connection closed.")