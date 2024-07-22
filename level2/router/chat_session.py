from fastapi import APIRouter,Cookie, Request, Response
from sqlalchemy.orm import Session
from db.crud import get_current_session, create_session
from db.crud import UserChatSession, get_db
from langchain_ollama import ChatOllama  # Adjust import based on actual module structure
import uuid

router = APIRouter(
    tags=["functions"],
    prefix="/api/functions",
    responses={404: {"description": "Not found"}},
)

# Simulated database or session storage
fake_db = {}

# Endpoint to set a session ID cookie
# @router.get("/set_session_id/{session_id}")
def set_session_id(session_id: str, response: Response):
    response.set_cookie(key="session_id", value=session_id)
    return session_id

# Endpoint to check session ID cookie
# @router.get("/check_session_id")
async def check_session_id(response: Response, session_id: str = Cookie(None)):
    if session_id == "":
        print("No session ID cookie found")
        return None
    else:
        return session_id

async def send_message(content: list):
    model = ChatOllama(model="tinyllama")
    result = model.invoke(content)
    return result
