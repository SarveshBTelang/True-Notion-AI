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
    Loads and combines documents from all JSON values stored in Upstash Redis
    """
    all_documents = []
    keys = list_upstash_keys()  # Fetch all keys

    for key in keys:
        try:
            json_data = get_upstash_json_by_key(key)['0']
        except KeyError:
            # Skipping the key if '0' is not present (Please ensure the file is in correct format)'
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

