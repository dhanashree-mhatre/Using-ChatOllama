from fastapi import FastAPI, Depends, Response,Cookie
from typing import Annotated
from sqlalchemy.orm import Session
from db.crud import get_db, create_session, get_current_session
from db.Schema import Message
from router.chat_session import router as functions, set_session_id, check_session_id, send_message
from db.crud import UserChatSession
import json 

app = FastAPI()

# Include functions router
app.include_router(functions)

@app.post("/root/")
async def hello():
    return {"message": "Hello, World!"} 

@app.post("/chat")
async def chat(message: Message, response: Response, session_id: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    
    if session_id is not None:
        current_session = get_current_session(session_id=session_id, db=db)
    else:
        session_id = create_session(db=db)
        set_session_id(session_id, response)
        current_session = get_current_session(session_id=session_id, db=db)

    # Fetch current chat history for the session_id
    if current_session:
        chat_history = json.loads(current_session.chat_history)  # Convert JSON string to list
    else:
        chat_history = []
    print(chat_history)

    # Append human message to chat history
    chat_history.append(("human", message.content))

    # Send message to AI model asynchronously
    ai_msg = await send_message(chat_history)

    # Append AI message to chat history
    chat_history.append(("ai", ai_msg.content))

    # Update chat session with new chat history
    if current_session:
        current_session.chat_history = json.dumps(chat_history)  # Convert list to JSON string
    else:
        chat_session = UserChatSession(session_id=session_id, chat_history=json.dumps(chat_history))
        db.add(chat_session)

    try:
        db.commit()
    finally:
        db.close()

    return {"message": ai_msg}