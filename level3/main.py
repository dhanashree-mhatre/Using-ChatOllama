from fastapi import FastAPI, Depends
from retriver.function import save_data_to_vector,load_retriver
import os 
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from database.models import create_session,get_current_session,get_db
from sqlalchemy.orm import Session 
import sqlalchemy


app=FastAPI()

current_dir=os.path.dirname(os.path.abspath('__file__'))
persistent_directory_path=os.path.join(current_dir,"level3","db_chroma","health_db")
document_directory_path=os.path.join(current_dir,"level3","docs","healthy_habits.txt")


@app.get("/")
async def root(query:str,session_id:str=None,db:Session=Depends(get_db)):
    if not os.path.exists(persistent_directory_path):
        save_data_to_vector(document_directory_path,persistent_directory_path)
    context=load_retriver(persistent_directory_path,query)
    model=ChatOllama(model="tinyllama")
    session=get_current_session(session_id,db)
    if session is None:
        session_id=create_session(db)
        session=get_current_session(session_id,db)
    if session:
        chat_history = eval(session.chat_history)
    else:
        chat_history=[]

    template ="""
    You are an health assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
        previous chats:{chat_history}
        Question: {query} 
        Context: {context} 
        Answer:
    """

    rag_prompt_custom = PromptTemplate(
        template=template,
        input_variables=["context", "query" "chat_history"],
    )
    output_parser = StrOutputParser()
    chain=rag_prompt_custom | model | output_parser
    output=chain.invoke({"context":context,"query":query,"chat_history":chat_history})

    chat_history.append(("human",query))
    chat_history.append(("ai",output))

    if session:
        session.chat_history=str(chat_history)
    try:
        db.commit()
    finally:
        db.close()    

    return {"message": output}