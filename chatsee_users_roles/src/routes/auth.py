from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from common.constants import Messages, StatusCode
from chatsee_users_roles.src.db.models import AllUserResponse, TokenData, UserCreate, UserResponse, UserToken
from chatsee_users_roles.src.utils.utils import get_password_hash, get_user, verify_password, create_access_token, get_role, ACCESS_TOKEN_EXPIRE_MINUTES ,get_agent
from datetime import timedelta
from typing import List
from common.database import role_collections,agent_collection,user_collections

router = APIRouter(tags=["User Registration and Login"])
# router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    from chatsee_users_roles.src.utils.utils import decode_token #prevent circular import.
    user={}
    payload = await decode_token(token)
    username: str = payload.get("sub")
    role: str = payload.get("role")
    

    
    user["user"]=user
    user["role"]=role
    

    assigned_agents: List[str] = payload.get("assigned_agents")
    user["assigned_agents"]=assigned_agents
    
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    token_data = TokenData(username=username, role=role, assigned_agents=assigned_agents)
    user = await get_user(username=token_data.username)
    
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return user

@router.post("/login", response_model=UserToken)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    print(user)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    role = await get_role(user["role_id"])
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    agent_names = []
    for agent_id in user.get("assigned_agents",[]):
        agent = await get_agent(agent_id)
        if agent:
           agent_names.append(agent["agent_name"])

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": role["name"], "assigned_agents": agent_names}, expires_delta=access_token_expires
    )

    return UserToken(status_code=StatusCode.SUCCESS,status_message=Messages.CREATED,access_token= access_token)
    

@router.post("/create_chatsee_user/") 
async def create_user(user: UserCreate):
    try:
        role_id = user.role_id 
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Role ID format")

    role_id = await role_collections.find_one({"_id": ObjectId(role_id)},{"_id":1})  # ✅ Fix Role Query
    user.role_id = role_id["_id"] 
    if not user.role_id:
        raise HTTPException(status_code=404, detail="Role not found")

    assigned_agents = []
    for agent_id in user.assigned_agents:
        
        try:
            results =  agent_collection.find_one({"_id": ObjectId(agent_id)})
            
            if results:
                
                assigned_agents.append(ObjectId(agent_id))
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Invalid agent ID format")

    user.assigned_agents=assigned_agents
    hashed_password = get_password_hash(user.password)
    user.password = hashed_password


    
    
    
    user_all_info = user.dict()

    await user_collections.insert_one(user_all_info)
    
    
    
    

    return UserResponse(
        status_message = "User Created Successfully",
        status_code=200,
        
    )


@router.post("/fetch_all_users/", response_model=AllUserResponse)
async def get_users():
    users = await user_collections.find({},{"_id":1,"username":1,"email":1,"role_id":1,"assigned_agents":1,"created_on":1}).to_list() #removed the agention argument.
    # print(users)
    user_list = []

    for user in users:
        # print(user)
        # Fetch Role details
        role = await role_collections.find_one({"_id": user.get("role_id")})
        # print("role is",role)
        role_data = {"_id": str(role.get("_id")), "name": role.get("name")} if role else None

        # Fetch agent details
        agent_list = []
        if user.get("assigned_agents"):
            
            agent_ids = [pid for pid in user.get("assigned_agents")]
            
            agents = await agent_collection.find({"_id": {"$in": agent_ids}}).to_list()
            agent_list = [{"_id": str(agent.get("_id")), "agent_name": agent.get("agent_name")} for agent in agents]
            # print(agent_list)

        user_list.append({
                         "id":str(user.get("_id")),
                "username":user.get("username"),
                "email":user.get("email"),
                "role":role_data,
                "assigned_agents":agent_list,
        }
        )
    print(user_list)

    return AllUserResponse(status_code=StatusCode.SUCCESS,status_message=Messages.CREATED,data=user_list)


"""
{
  "username": "mandarkulkarni",
  "email": "mandarkulkarni@example.com",
  "password": "mandarkulkarni",
  "role_id": "string",
  "assigned_agents": ["67b6d310f1239fa69e963e83"],
  "created_on": "2025-03-11T02:56:25.008Z",
  "modified_on": "2025-03-11T02:56:25.008Z",
  "is_deleted": false
}
"""