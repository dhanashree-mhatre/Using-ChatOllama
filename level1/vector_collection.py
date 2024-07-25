import uuid
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import chromadb
from chromadb import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# URLs to load and process
urls = ["https://stackoverflow.com/questions/76633836/what-does-langchain-charactertextsplitters-chunk-size-param-even-do"]

# Initialize HTML loader and converter
loader = AsyncHtmlLoader(urls)
docs = loader.load()
html2text = Html2TextTransformer()
formatted_docs = html2text.transform_documents(docs)

# Initialize Ollama embeddings
embeddings = OllamaEmbeddings(model="tinyllama",dimension=384)

# Split documents into chunks using RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(formatted_docs)

# Initialize ChromaDB client and collection
client = chromadb.PersistentClient(settings=Settings(allow_reset=True))
client.reset()  # Reset the database if needed
collection = client.create_collection("stack_chat1",dimensionality=384)

# Add documents to ChromaDB collection
for doc in docs:
    collection.add(
        ids=[str(uuid.uuid1())],
        metadatas=doc.metadata,
        documents=doc.page_content
    )

# Initialize Chroma for querying
db = Chroma(
    client=client,
    collection_name="stack_chat1",
    embedding_function=embeddings
)

# Perform a similarity search based on a query
query = "what is chunk size?"
context = db.similarity_search(query=query)
print(context[0].page_content)  # Print the content of the most similar document

