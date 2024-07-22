"""
project: Asynchrounous ChatAIModel
author: @dhanashree
date: 2022-07-22

description:
    - this file is used for anysnchrounous chat
    - In it defined everything in single file
"""
from typing import AsyncIterable
import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv('.env')

# Initialize the FastAPI application
app = FastAPI()

# CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_headers=['*'],
    allow_methods=['*']
)

# Define a Pydantic model for the message content
class Message(BaseModel):
    content: str

# Global variable to store chat history
chat_history = []
chat_history.append(SystemMessage(content="You are a very helpful assistant."))

# Asynchronous function to send messages to the AI model
async def send_message(content: str) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()
    model = ChatOpenAI(
        verbose=True,
        streaming=True,
        callbacks=[callback]
    )
    task = asyncio.create_task(
        model.invoke(content)
    )
    try:
        async for token in callback.aiter():
            yield token
    except Exception as e:
        print(f"Caught error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        callback.done.set()
        await task

# Endpoint to handle incoming messages and provide AI responses
@app.post('/chat')
async def get_response(msg: Message):
    global chat_history
    
    # Append the human message to chat history
    chat_history.append(HumanMessage(content=msg.content))
    
    # Send the current chat history to the AI model
    generator = send_message(chat_history)
    
    try:
        # Retrieve the AI response asynchronously
        ai_message = await generator.__anext__()
    except StopAsyncIteration:
        raise HTTPException(status_code=500, detail="No response from AI")
    
    # Append the AI message to chat history
    chat_history.append(AIMessage(content=ai_message))
    
    # Return a streaming response to the client
    return StreamingResponse(generator, media_type='text/event-stream')
