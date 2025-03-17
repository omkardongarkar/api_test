from fastapi import FastAPI

from common.database import client, db, init_db  # Import the Motor client and database
from motor.motor_asyncio import AsyncIOMotorClient

from chat_analytics.routers import analytics_router
from user_engagement.api.router import router as engagement_router
from user_engagement.api.router import router as interaction_router

from cross_agents_performance.api.router import router as cross_agents_router
from dashboard_metadata.src.api.router import router as dashboard_router
from chatsee_users_roles.src.routes import auth as authentication_router
from user_groups.src.api.router import router as user_group_router


import asyncio





app = FastAPI(title="Interaction API", description="API for interaction data")


app.include_router(analytics_router.router,prefix="/v1")
app.include_router(interaction_router,prefix="/v1/user_engagement", tags=["User Engagement"])
app.include_router(cross_agents_router,prefix="/v1/cross_agents")
app.include_router(dashboard_router,prefix="/v1/cross_agents")
app.include_router(authentication_router.router,prefix="/v1/chatsee_user")
app.include_router(user_group_router)







@app.get("/health")
async def health_check():

    try:

        

        await db.command("ping")  # Check with Motor
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}


@app.on_event("shutdown")  # Graceful Shutdown
async def shutdown_event():
    client.close()
    print("MongoDB connection closed.")
