from langchain_ollama import ChatOllama,OllamaEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter,CharacterTextSplitter,SentenceTransformersTokenTextSplitter 
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from fastapi import FastAPI,UploadFile,HTTPException,Response
from typing import Annotated
from tempfile import NamedTemporaryFile
import shutil
import os

app=FastAPI()

current_dir=os.path.dirname(os.path.abspath(__file__))
vector_data_directory=os.path.join(current_dir,"level4","vector_db")

def create_vector_store(docs,persist_directory,embedding_function):
    print("--------- start vectorization of data -----------")
    Chroma.from_documents(docs,embedding_function,persist_directory=persist_directory)
    print("--------- completed vectorization of data -----------")

def create_retriver(persist_directory,embedding_function,search_type,search_kwargs):
    db=Chroma(persist_directory=persist_directory,embedding_function=embedding_function)
    retriver=db.as_retriever(search_type=search_type,search_kwargs=search_kwargs)
    return retriver


def split_docs(docs,type,chunk_size=1000,chunk_overlap=0):
    text_split_list=['character','token','sentence','recursive','custom']
    if type not in text_split_list:
        return Exception("You have to use the type from these 'character','token','sentence','recursive','custom' and if you choose custom please pass the object iteself.")
    if type == "character":
        text_splitter=CharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
    elif type == "sentence":
        text_splitter=SentenceTransformersTokenTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
    elif type == "recursive":
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
    else:
        return Exception("You have to use the type from these 'character','token','sentence','recursive','custom' and if you choose custom please pass the object iteself.")
    documents=text_splitter.split_documents(docs)
    return documents


@app.post("/upload_file/")
async def upload_file():
    pass

