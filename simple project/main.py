import os
from fastapi import FastAPI, UploadFile, File
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader,TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings,ChatOllama
import shutil
from tempfile import NamedTemporaryFile

app = FastAPI()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/upload/")
async def process_file( question: str,file: UploadFile = File(...)):
    try:
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(await file.read())
            temp_file_path=temp_file.name
        if file.filename.endswith('.pdf'):
            loader = PyPDFLoader(temp_file_path)
            text=loader.load_and_split()
        else:
            loader = TextLoader(temp_file_path)
            text=loader.load_and_split()


        # Split text using recursive splitter
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs=text_splitter.split_documents(text)
        print(docs[0].page_content)
        embedding_model=OllamaEmbeddings(model="tinyllama")
        file_name,_=file.filename.split(".")
        persist_directory=os.path.join(UPLOAD_FOLDER,"chroma_db",file_name)
        # Initialize the chroma db
        db=Chroma.from_documents(docs,embedding=embedding_model,persist_directory=persist_directory)

        # Query the db
        query = question
        docs = db.similarity_search(query)
        print(docs[0].page_content)
        chat_model=ChatOllama(model="tinyllama")
        chain=chat_model | StrOutputParser
        prompt=f"""
            system: You are Good Answerer. Your work is to make this answer more consise and proper. You will get the data from documents.
            dont make up any answer. You will get the data from documents.

            Question: {query}

            Context:{docs}
    """
        output=chain.invoke(prompt)
        print("-------------this is output---------------")
        print(output)
        return output
    except:
        pass

        
