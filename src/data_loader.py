import os
import json
import requests
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# Load environment variables
load_dotenv()

UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

if not UPSTASH_REDIS_REST_URL or not UPSTASH_REDIS_REST_TOKEN:
    raise ValueError("Missing Upstash credentials in environment")

HEADERS = {
    "Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}"
}

def list_upstash_keys(prefix="notion_"):
    """Fetch all keys matching a prefix using Upstash Redis REST API."""
    url = f"{UPSTASH_REDIS_REST_URL}"  # No /keys route!
    headers = {
        "Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = ["KEYS", f"{prefix}*"]

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to list keys: {response.text}")
    
    return response.json().get("result", [])

def get_upstash_json_by_key(key):
    """Get and parse JSON value for a specific key."""
    url = f"{UPSTASH_REDIS_REST_URL}/get/{key}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch key {key}: {response.text}")
    raw_value = response.json().get("result")
    return json.loads(raw_value) if raw_value else []

def load_dataset_from_upstash(prefix="notion_"):
    """
    Loads and combines documents from multiple JSON values stored in Upstash Redis.
    """
    all_documents = []
    keys = list_upstash_keys(prefix=prefix)

    for key in keys:
        json_data = get_upstash_json_by_key(key)['value']
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

    return all_documents

def chunk_documents(documents, chunk_size=1000, chunk_overlap=50):
    """
    Splits documents into smaller chunks to improve retrieval performance.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunked_docs = []
    for doc in documents:
        splits = text_splitter.split_text(doc.page_content)
        for chunk in splits:
            chunked_docs.append(Document(page_content=chunk, metadata=doc.metadata))
    return chunked_docs


def create_vectorstore(documents):
    """
    Creates a vectorstore by embedding document chunks using a local sentence-transformers model.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore