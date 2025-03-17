
from fastapi import FastAPI, HTTPException

from chatsee_users_roles.src.db.models import AllUserResponse, FetchUsers, USerAllList, Users, UserCreate, UserResponse, Role, Agent


from chatsee_users_roles.src.routes import auth

app = FastAPI()




app.include_router(auth.router)







    