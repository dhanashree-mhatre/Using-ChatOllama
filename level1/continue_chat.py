"""
project: ChatAIModel
author: @dhanashree
date: 2022-07-22

description:
    - this file is used for continue chat
    - In it defined everything in single file
"""
import asyncio
from typing import AsyncIterable

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_ollama import ChatOllama
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage,SystemMessage,AIMessage
from pydantic import BaseModel

load_dotenv('.env')
app=FastAPI()


class Message(BaseModel):
    content:str

chat_history=[]
chat_history.append(SystemMessage(content="You are very supportive medical assistant."))

async def send_message(content:list):
    model=ChatOllama(model="tinyllama")
    result=model.invoke(content)
    print(result)
    return result


@app.post("/chat-api/")
async def stream_chat(message:Message):
    chat_history.append(HumanMessage(content=message.content))
    print(chat_history)
    ai_msg=await send_message(chat_history)
    chat_history.append(AIMessage(content=ai_msg.content))
    return {"message":ai_msg}

