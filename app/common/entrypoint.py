"""
Entrypoint file: Load pdf(s), create embeddings, store indexing to ChromaDB
"""
from app.common.utils import DATA_DIR, CHROMA_DIR, get_embedding_model, load_vectorstore

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

def load_documents():
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

    loader = PyPDFDirectoryLoader(str(DATA_DIR))
    documents = loader.load()

    print(f"MetaData: {documents[0].metadata}")
    return documents

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""]
    )
    return splitter.split_documents(documents)

def create_vectorstore(docs, embedding_model):
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=str(CHROMA_DIR),
        collection_name="byld_survey"
    )
    return vectordb

def create_indexing_pipeline(embedding_model):
    print("Loading documents...")
    docs = load_documents()

    print("Splitting documents...")
    chunks = split_documents(docs)

    print("Creating vector store...")
    if CHROMA_DIR.exists():
        vectordb = load_vectorstore(embedding_model=embedding_model)
    else:
        vectordb = create_vectorstore(chunks, embedding_model)
    
    return vectordb

if __name__ == "__main__":
    embedding_model = get_embedding_model()
    docs = create_indexing_pipeline(embedding_model=embedding_model)