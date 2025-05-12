import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Notion credentials
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_ID = os.getenv('DATABASE_ID')

# Upstash Redis REST credentials
UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

# Validate environment variables
if not NOTION_TOKEN:
    raise ValueError("NOTION_TOKEN not found in .env file")
if not DATABASE_ID:
    raise ValueError("DATABASE_ID not found in .env file")
if not UPSTASH_REDIS_REST_URL or not UPSTASH_REDIS_REST_TOKEN:
    raise ValueError("Upstash Redis credentials not found in .env file")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def extract_notion_rows(notion_response):
    results = []

    for page in notion_response.get("results", []):
        page_data = {
            "id": page.get("id"),
            "properties": {}
        }
        properties = page.get("properties", {})

        for prop_name, prop_value in properties.items():
            if not isinstance(prop_value, dict) or "type" not in prop_value:
                continue

            prop_type = prop_value.get("type")

            try:
                if prop_type == "rich_text":
                    value = "".join([rt.get("plain_text", "") for rt in prop_value.get("rich_text", [])])
                elif prop_type == "title":
                    value = "".join([t.get("plain_text", "") for t in prop_value.get("title", [])])
                elif prop_type == "number":
                    value = prop_value.get("number")
                elif prop_type == "url":
                    value = prop_value.get("url")
                elif prop_type == "date":
                    value = prop_value.get("date")
                elif prop_type == "select":
                    value = prop_value.get("select", {}).get("name")
                elif prop_type == "multi_select":
                    value = [item.get("name") for item in prop_value.get("multi_select", [])]
                elif prop_type == "checkbox":
                    value = prop_value.get("checkbox")
                elif prop_type == "email":
                    value = prop_value.get("email")
                elif prop_type == "phone_number":
                    value = prop_value.get("phone_number")
                elif prop_type == "people":
                    value = [person.get("name", "") for person in prop_value.get("people", [])]
                elif prop_type == "files":
                    value = [f.get("name", "") for f in prop_value.get("files", [])]
                else:
                    value = f"Unsupported type: {prop_type}"
            except Exception:
                continue

            page_data["properties"][prop_name] = value

        results.append(page_data)

    return results

def save_to_upstash_redis(key, data):
    url = f"{UPSTASH_REDIS_REST_URL}/set/{key}"
    headers = {
        "Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json={"value": json.dumps(data)})
    if response.status_code != 200:
        raise Exception(f"Failed to store data in Upstash: {response.text}")
    print(f"Data successfully saved to Upstash under key: {key}")

def extract_pages(num_pages=None):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    page_size = 1000 if num_pages is None else num_pages
    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    notion_data = response.json()
    parsed_data = extract_notion_rows(notion_data)

    # Save to Upstash Redis instead of local file
    save_to_upstash_redis("notion_database", parsed_data)

    # Clean up env vars
    os.environ.pop("NOTION_TOKEN", None)
    os.environ.pop("DATABASE_ID", None)

# Run the function
if __name__ == "__main__":
    extract_pages()