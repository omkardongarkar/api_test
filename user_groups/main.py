from fastapi import FastAPI
from common.database import init_db

from user_groups.src.api.router import router as user_group_router

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()  # Initialize Beanie

app.include_router(user_group_router, prefix="/v1/user_group_router")
