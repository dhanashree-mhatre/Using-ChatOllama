from fastapi import FastAPI, File, UploadFile, HTTPException
from tempfile import NamedTemporaryFile
from pdfminer.high_level import extract_text
from docx import Document
import os
import uuid
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import chromadb
from chromadb import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

app = FastAPI()

# Temporary storage for uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize LangChain components
embeddings = OllamaEmbeddings(model="tinyllama")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

# Function to extract text from DOCX files
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

# Function to extract text from PDF files
def extract_text_from_pdf(file_path):
    return extract_text(file_path)

# Endpoint to upload a file
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to a temporary location
        file_location = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_location, "wb") as f:
            f.write(file.file.read())

        # Return a response
        return {"filename": file.filename, "file_path": file_location}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to process and store file content using LangChain
@app.post("/process/")
async def process_file(file_path: str):
    try:
        file_path="uploads/thebook.pdf"
        # Determine file type and extract text accordingly
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() == ".pdf":
            text_content = extract_text_from_pdf(file_path)
        elif file_extension.lower() == ".docx":
            text_content = extract_text_from_docx(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Split text into chunks using LangChain text splitter
        docs = text_splitter.split_text(text_content)

        # Initialize ChromaDB client and collection
        client = chromadb.PersistentClient(settings=Settings(allow_reset=True))
        client.reset()  # Reset the database if needed
        collection = client.create_collection("file_collection")

        # Add chunks to ChromaDB collection
        for doc in docs:
            collection.add(
                ids=[str(uuid.uuid1())],
                metadatas={},  # Add metadata if needed
                documents=doc
            )

        # Return a response
        return {"message": "File processed and stored successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to query text content using LangChain and ChromaDB
@app.get("/query/")
async def query_file_content(query: str):
    try:
        # Initialize Chroma for querying
        db = Chroma(
            client=client,
            collection_name="file_collection",
            embedding_function=embeddings
        )

        # Perform a similarity search based on the query
        context = db.similarity_search(query=query)

        # Return the result (example: first result)
        if context:
            return {"text_content": context[0].documents}
        else:
            raise HTTPException(status_code=404, detail="Query not found in any files")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
