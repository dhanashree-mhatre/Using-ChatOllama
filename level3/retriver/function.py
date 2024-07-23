from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

def load_data(data_directory):
    loader=TextLoader(data_directory)
    docs=loader.load()
    return docs

def textsplitter(data_directory):
    documents=load_data(data_directory)
    textsplitter=CharacterTextSplitter(chunk_size=1000,chunk_overlap=0)
    docs=textsplitter.split_documents(documents)
    return docs

def sentence_splitter(data):
    pass

def save_data_to_vector(data_directory,persist_directory):
    embedding_function=OllamaEmbeddings(model="tinyllama")
    docs=textsplitter(data_directory)
        
    db=Chroma.from_documents(docs,embedding_function,persist_directory=persist_directory)

def load_retriver(persist_directory,query):
    embedding_function=OllamaEmbeddings(model="tinyllama")
    db=Chroma(persist_directory=persist_directory,embedding_function=embedding_function)
    retriever = db.as_retriever(search_type="mmr")
    result=retriever.invoke(query)
    print(result[0])
    print("----- Retrived vector database -------")

    return result




