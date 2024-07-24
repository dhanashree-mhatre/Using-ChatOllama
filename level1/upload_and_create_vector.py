from fastapi import FastAPI,File,UploadFile ,HTTPException,Response
from typing import Annotated
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
import os
import shutil
from tempfile import NamedTemporaryFile


app=FastAPI()

current_dirname=os.path.dirname(os.path.abspath("__file__"))
database_dir=os.path.join(current_dirname,"level1","db")

def create_vector_store(docs,persistent_directory):
    embedding_function=OllamaEmbeddings(model="tinyllama")
    db=Chroma.from_documents(docs,embedding_function,persist_directory=persistent_directory)
    print("----added to vectorstore----")
    return {"message":"success"}

@app.post("/uploadfile/")
async def create_file(response:Response,file: UploadFile | None = None):
    if not file:
        return {"message": "No upload file sent"}
    try:
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(await file.read())
            temp_file_path=temp_file.name

        #content = await file.read() 
        loader=TextLoader(temp_file_path)
        documents=loader.load()
        text_spliter=CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
        docs=text_spliter.split_documents(documents)
        persistent_dir=os.path.join(database_dir,"loaded_data")
        create_vector_store(docs,persistent_directory=persistent_dir)
        response.set_cookie(key="session_id", value=persistent_dir)
        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.post("/query")
async def chat(query:str):
    persistent_dir=os.path.join(database_dir,"loaded_data")
    shutil.rmtree(persistent_dir)
