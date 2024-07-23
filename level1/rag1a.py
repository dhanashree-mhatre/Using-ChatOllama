"""
This Program is to try RAG basic assessments.
"""

from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
import os
from langchain.memory import ChatMessageHistory
from fastapi import FastAPI



#embeddings=OllamaEmbeddings(model="tinyllama")
currentdir=os.path.dirname(os.path.abspath('__file__'))
file_path=os.path.join(currentdir,"level1","docs","one_piece.txt")
persistent_dir=os.path.join(currentdir,"level1","db","chroma_db")
print(file_path)

if not os.path.exists(file_path):
    print("File not found")
else:
    if not os.path.exists(persistent_dir):
        loader=TextLoader(file_path)
        documentss=loader.load()
        text_splitter=CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
        docs=text_splitter.split_documents(documentss)
        
        embedding_function=OllamaEmbeddings(model="tinyllama")
        print("text_splitted")
        
        db=Chroma.from_documents(docs,embedding_function,persist_directory=persistent_dir)
print("----- created vector database -------")

def load_search(directory,embedding_function):
    db=Chroma(persist_directory=directory,embedding_function=embedding_function)
    print("----- Loaded search -------")
    return db

def retrive(query:str):
    embedding_function=OllamaEmbeddings(model="tinyllama")
    db=load_search(persistent_dir,embedding_function)
    #retriever = db.as_retriever(search_type="mmr")
    result=db.similarity_search(query)
    #result=retriever.invoke(query)
    print(result[0])
    print("----- Retrived vector database -------")
    return result

def chat(query:str):
    # history=ChatMessageHistory()
    # history.add_user_message(query)
    context=retrive(query)
    prompt=f"""
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

        Question: {query} 

        Context: {context} 

        Answer:
"""
   
    model=ChatOllama(model="tinyllama")
    ai_msg=model.invoke(prompt)
    # history.add_ai_message(ai_msg.content)
    print(ai_msg.content) 

chat("Did Elara met phoenix creature?")






