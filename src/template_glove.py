"""
GloVe model implementation (Template for loading text embedding models such as glove-gigaword-100, word2vec, or any Hugging Face-compatible embeddings.)

(For fully offline version implementation, refer to the 'True-Notion-Backend-Server' repo)

"""

import os
import json
import requests
from dotenv import load_dotenv
from src import connect_notion

# Custom Vectorstore
import faiss
import numpy as np
from gensim.models import KeyedVectors

# Define Document class
class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(metadata={self.metadata})"

# Load environment variables
load_dotenv()

UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

if not UPSTASH_REDIS_REST_URL or not UPSTASH_REDIS_REST_TOKEN:
    raise ValueError("Missing Upstash credentials in environment")

HEADERS = {
    "Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}"
}


def list_upstash_keys():
    """Fetch all keys from Upstash Redis, excluding 'agent_config' and 'rag_config'."""
    url = f"{UPSTASH_REDIS_REST_URL}"
    headers = {
        "Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = ["KEYS", "*"]

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to list keys: {response.text}")

    keys = response.json().get("result", [])

    # Exclude 'agent_config' and 'rag_config'
    exclude_keys = {"agent_config", "rag_config"}
    return [key for key in keys if key not in exclude_keys]


def get_upstash_json_by_key(key):
    """Get and parse JSON value for a specific key."""
    url = f"{UPSTASH_REDIS_REST_URL}/get/{key}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch key {key}: {response.text}")
    raw_value = response.json().get("result")
    return json.loads(raw_value) if raw_value else []


def load_dataset_from_upstash():
    """
    Loads and combines documents from all JSON values stored in Upstash Redis.
    """
    all_documents = []
    keys = list_upstash_keys()  # Fetch all keys

    for key in keys:
        try:
            json_data = get_upstash_json_by_key(key)['0']
        except KeyError:
            # Skipping the key if '0' is not present (Please ensure the file is in the correct format)
            continue

        data = json.loads(json_data)
        if not isinstance(data, list):
            raise ValueError(f"Expected a list from key {key}, got {type(data)}")

        for entry in data:
            text = json.dumps(entry['properties'], ensure_ascii=False, indent=2)
            doc = Document(
                page_content=text,
                metadata={
                    "id": entry.get("id", ""),
                    "source_key": key
                }
            )
            all_documents.append(doc)

    return all_documents, keys


def chunk_documents(documents, chunk_size=1000, chunk_overlap=50):
    """
    Splits documents into smaller chunks to improve retrieval performance.
    This implementation splits the text into fixed-size chunks with overlap.
    """
    chunked_docs = []
    for doc in documents:
        text = doc.page_content
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunked_docs.append(Document(page_content=chunk, metadata=doc.metadata))
            start += chunk_size - chunk_overlap
    return chunked_docs


# Define a VectorStore class using FAISS and Word2Vec based embeddings
class VectorStore:
    def __init__(self, index, documents, model, dim):
        self.index = index
        self.documents = documents
        self.model = model
        self.dim = dim

    def retrieve(self, query, k=10):
        # Compute the query embedding using our Word2Vec-based model
        query_embedding = self.model.encode(query)
        query_embedding = np.array(query_embedding, dtype="float32").reshape(1, self.dim)
        distances, indices = self.index.search(query_embedding, k)
        results = [self.documents[i] for i in indices[0] if i < len(self.documents)]
        return results

    def as_retriever(self, search_kwargs):
        k = search_kwargs.get("k", 10)
        return Retriever(vectorstore=self, k=k)


# Define a Retriever class to mimic LangChain's retriever interface
class Retriever:
    def __init__(self, vectorstore, k):
        self.vectorstore = vectorstore
        self.k = k

    def get_relevant_documents(self, query):
        return self.vectorstore.retrieve(query, self.k)


# Define a wrapper for Word2Vec embeddings to mimic SentenceTransformer's encode method
class Word2VecEmbeddings:
    def __init__(self, model):
        self.model = model
        self.dim = self.model.vector_size

    def encode(self, text):
        # Simple tokenization by splitting on whitespace; more advanced tokenizing may be used.
        tokens = text.split()
        vectors = []
        for token in tokens:
            # For gensim 4.x, check using key_to_index
            if token in self.model.key_to_index:
                vectors.append(self.model.get_vector(token))
        if not vectors:
            # Return a zero vector if no token is in the vocabulary
            return np.zeros(self.dim)
        return np.mean(vectors, axis=0)


def create_vectorstore(documents):
    """
    Creates a vectorstore by embedding document chunks using a local lightweight GloVe model.
    Uses FAISS for vector similarity search.
    This function no longer performs any remote server action.
    """
    # Load the local GloVe model from the designated directory.
    model_path = os.path.join("models", "glove-wiki-gigaword-50", "glove-wiki-gigaword-50.model")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Local model file not found at {model_path}")
    glove_model = KeyedVectors.load(model_path, mmap='r')
    model = Word2VecEmbeddings(glove_model)

    embeddings = []
    for doc in documents:
        embedding = model.encode(doc.page_content)
        embeddings.append(embedding)
    embeddings_np = np.array(embeddings, dtype="float32")
    if len(embeddings_np) == 0:
        raise ValueError("No embeddings to index.")
    dim = embeddings_np.shape[1]
    # Create a FAISS index with controlled (single-threaded) behavior.
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings_np)
    vectorstore = VectorStore(index=index, documents=documents, model=model, dim=dim)
    return vectorstore


def upload_agent_config_to_upstash(filepath="agents/agent_config.json", key="agent_config"):
    """
    Uploads a local JSON file to Upstash Redis under the specified key.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} not found")

    with open(filepath, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # Convert to string format required by Upstash
    json_str = json.dumps(json_data, ensure_ascii=False)

    # Prepare the request payload
    url = f"{UPSTASH_REDIS_REST_URL}"
    payload = ["SET", key, json_str]

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to upload config to Upstash: {response.text}")
    print(f"Successfully uploaded '{key}' to Upstash.")


def initialize_system(adjusted_k=10, adjusted_chunk_size=1000):
    """
    Loads documents, chunks them, and creates a vector store retriever.
    """
    # NOTE: If the extract_pages call is not needed for local vectorstore creation,
    # you may choose to remove or comment it out.
    connect_notion.extract_pages()

    data_folder = os.path.join(os.getcwd(), "data")
    json_files = [
        os.path.join(data_folder, f)
        for f in os.listdir(data_folder)
        if f.endswith(".json")
    ]

    if not json_files:
        print("No JSON files found in local 'data' directory... fetching from upstash")

    print("=== Loading Datasets ===")
    documents, keys = load_dataset_from_upstash()
    print(f"Loaded {len(documents)} documents.")

    if not documents and not json_files:
        raise RuntimeError("No data found. Please ensure data is available in the database.")

    print(f"\nUsing k={adjusted_k}, chunk_size={adjusted_chunk_size}.")
    print("\n=== Chunking Documents ===")
    chunked_docs = chunk_documents(documents, chunk_size=adjusted_chunk_size)
    print(f"Created {len(chunked_docs)} document chunks.")

    print("\n=== Creating Vectorstore ===")
    vectorstore = create_vectorstore(chunked_docs)
    retriever = vectorstore.as_retriever(search_kwargs={"k": adjusted_k})
    print("Vectorstore created and documents indexed.")

    return retriever, keys
