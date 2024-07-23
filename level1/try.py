from langchain_ollama import ChatOllama

from fastapi import FastAPI ,Depends,Cookie
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session, sessionmaker
import uuid
import sqlalchemy.orm 

from pydantic import BaseModel 

app=FastAPI()

#Database Configuration 
database_url = "sqlite:///./try.db"

engine=create_engine(database_url)
SessionLocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)

Base=sqlalchemy.orm.declarative_base()

#dunction to get db
def get_db():
    db=SessionLocal()
    try:
        yield db 
    finally:
        db.close()

#DataBase Models
class UserChatSession(Base):
    __tablename__="user_chat_sessions"
    id=Column(Integer,primary_key=True,index=True)
    session_id=Column(String,index=True)
    chat_history=Column(String)

Base.metadata.create_all(bind=engine)

# Schemas
class Message(BaseModel):
    content:str


#Functions
def check_session(session_id:str=None,db:Session=Depends(get_db)):
    session =db.query(UserChatSession).filter(UserChatSession.session_id==session_id).first()
    print(session)
    if session is not None:
        return session
    else:
        return None
    
def create_session(db:Session=Depends(get_db)):
    session_id=str(uuid.uuid4())
    session=UserChatSession(session_id=session_id,chat_history="[]")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

async def send_message(content:list):
    model=ChatOllama(model="tinyllama")
    result=model.invoke(content)
    #print(result)
    return result

@app.post('/chat')
async def chat(query:str,session_id:str=None,db:Session=Depends(get_db)):
    try:
        session =check_session(session_id,db)
        if session is None:
            session=create_session(db)
    except:
        session=create_session(db)
    
    chat_history=eval(session.chat_history)

    chat_history.append(("human",query))

    response=await send_message(chat_history)
    ai_msg=response.content

    chat_history.append(("ai",ai_msg))
    if session:
        session.chat_history = str(chat_history)
    db.commit()

    return ai_msg



