"""
project: ChatAIModel
author: @dhanashree
date: 2022-07-22

description:
    - this file is used for continue chat
    - It includes sqlite database and model creation and save chat history
"""
import asyncio
from typing import AsyncIterable
from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.orm import sessionmaker,Session
import sqlalchemy
import sqlalchemy.orm

from dotenv import load_dotenv
from fastapi import FastAPI,Depends
from langchain_ollama import ChatOllama
#from langchain.schema import HumanMessage,SystemMessage,AIMessage
from pydantic import BaseModel

load_dotenv('.env')
app=FastAPI()

database_url="sqlite:///./database.db"
engine=create_engine(database_url)
SessionLocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)
Base=sqlalchemy.orm.declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ChatSession(Base):
    __tablename__="chat_sessions"
    id=Column(Integer,index=True,primary_key=True)
    session_id=Column(String,unique=True)
    chat_history=Column(String,unique=True)

Base.metadata.create_all(bind=engine)

# def create_session(db:Session=get_db):
#     user_session=ChatSession(session_id="user111111",chat_history="[]")
#     db.add(user_session)
#     db.commit()
#     db.refresh(user_session)
#     return user_session.session_id
# create_session(db=Session(bind=engine))

def get_current_session(session_id:str,db:Session=get_db):
    return db.query(ChatSession).filter(ChatSession.session_id==session_id).first()


class Message(BaseModel):
    content:str

# chat_history=[]
#chat_history.append(("system","You are very supportive medical assistant."))


async def send_message(content:list):
    model=ChatOllama(model="tinyllama")
    result=model.invoke(content)
    #print(result)
    return result


@app.post("/chat-api/")
async def stream_chat(message: Message, db: Session = Depends(get_db)):
    session_id = "user111111"
    
    # Fetch current chat history for the session_id
    current_session = get_current_session(session_id=session_id, db=db)
    if current_session:
        chat_history = eval(current_session.chat_history)  # Convert string back to list
    else:
        chat_history = []

    # Append human message to chat history
    chat_history.append(("human", message.content))

    # Send message to AI model asynchronously
    ai_msg = await send_message(chat_history)

    # Append AI message to chat history
    chat_history.append(("ai", ai_msg.content))

    # Update chat session with new chat history
    if current_session:
        current_session.chat_history = str(chat_history)
    else:
        chat_session = ChatSession(session_id=session_id, chat_history=str(chat_history))
        db.add(chat_session)

    db.commit()

    return {"message": ai_msg}


