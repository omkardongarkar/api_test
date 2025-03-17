from fastapi import FastAPI
from common.database import init_db

from user_engagement.api.router import router as interaction_router

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()  # Initialize Beanie

app.include_router(interaction_router, prefix="/v1/user_engagement")
