import os

from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings 


current_dir=os.path.dirname(os.path.abspath('__file__'))
db_dir=os.path.join(current_dir,"level1","db")
persistent_directory=os.path.join("chroma_db_apple")

urls=["https://www.apple.com/"]

loader=WebBaseLoader(urls)
documents=loader.load()

text_splitter=CharacterTextSplitter(chunk_size=1000,chunk_overlap=0)
docs = text_splitter.split_documents(documents)

print("\n ----- Documents Chunks Information --------")
print(f"Number of chunks: {len(docs)}")
#print(f"sample chunks: \n {docs[0].page_content}")

embeddings=OllamaEmbeddings(model="tinyllama")

if not os.path.exists(persistent_directory):
    print(f" \n  ----Creating Vector store in {persistent_directory}---")
    db=Chroma.from_documents(docs,embeddings,persist_directory=persistent_directory)
    print("-----Finished creating Vector Database----")
else:
    print(f"Vectorstore {persistent_directory} already exist.")
    db=Chroma(embedding_function=embeddings,persist_directory=persistent_directory)

retriver=db.as_retriever(
    search_type="similarity",
    search_kwargs={'k':3}
)

query="what new products announced by apple?"

relavant_docs=retriver.invoke(query)
print("\n ---- Relavant Documents----")
for i ,docs in enumerate(relavant_docs):
    print(f"Document {i} \n  {docs.page_content}\n")
    if docs.metadata:
        print(f"Source: {docs.metadata.get('source','Unknown')}\n")




