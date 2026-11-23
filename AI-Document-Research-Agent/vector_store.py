
import os

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings
)

from langchain_community.vectorstores import FAISS


def create_embeddings():

    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001"
    )


def create_vector_store(documents):

    if not documents:
        raise ValueError(
            "No readable text found in uploaded documents."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("No text chunks were created.")

    embeddings = create_embeddings()

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    return vector_store, len(chunks)


def save_vector_store(vector_store):

    os.makedirs("faiss_index", exist_ok=True)

    vector_store.save_local(
        "faiss_index",
        safe_serialization=True
    )


def load_vector_store():

    embeddings = create_embeddings()

    return FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=False
    )
