"""
Template- Langchain standalone implementation (Just a merged verion of data_loader.py + process.py).

"""

import os
import json
import requests
from dotenv import load_dotenv
from src import connect_notion

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# Define our own Document class to replace LangChain's Document
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
            # Skipping the key if '0' is not present (Please ensure the file is in correct format)
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

def create_vectorstore(documents):
    """
    Creates a vectorstore by embedding document chunks using a HuggingFaceEmbeddings model from LangChain.
    Uses FAISS for vector similarity search.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(documents, embeddings)
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
