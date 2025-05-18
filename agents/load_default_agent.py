import os
import requests
import json
from dotenv import load_dotenv, dotenv_values
from crewai import Agent, Task, LLM

# Load .env variables
load_dotenv()

UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")


def fetch_config_from_upstash(key: str) -> dict:
    url = f"{UPSTASH_REDIS_REST_URL}/get/{key}"
    headers = {"Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # response.json()["result"] can be None or missing, so check:
        result = response.json().get("result")
        if result:
            return json.loads(result)
        else:
            raise KeyError(f"No data found for key '{key}' in Upstash.")
    else:
        raise Exception(f"Failed to fetch config from Upstash: {response.text}")


def load_default_config() -> dict:
    default_path = "agents/default_agent.json"
    with open(default_path, "r") as f:
        return json.load(f)


# Try fetching the config from Upstash, fallback to default if not found or error
try:
    config_data = fetch_config_from_upstash("agent_config")
except (Exception, KeyError) as e:
    print(f"Warning: Could not load agent_config from Upstash due to {e}, loading default config.")
    config_data = load_default_config()

# Make sure the keys exist in config_data, fallback to default keys if not
agent_data = config_data.get("agent")
task_data = config_data.get("task")

if not agent_data or not task_data:
    print("Warning: agent or task config missing, loading default config from file.")
    config_data = load_default_config()
    agent_data = config_data["agent"]
    task_data = config_data["task"]

# Initialize LLM 
"""
You can use any supported or your custom Large Language Model (LLM) with Crew AI.

For more details on model support, refer to Crew AI's documentation: https://docs.crewai.com/concepts/llms

"""
llm = LLM(
    model="mistral/mistral-large-latest",
    temperature=0.7,
    api_key=os.environ["MISTRAL_API_KEY"],
)

class ConfigLoader:
    def __init__(self, env_path=".env"):
        self.config = dotenv_values(env_path)
        self.set_env_variables()

    def set_env_variables(self):
        os.environ["MISTRAL_API_KEY"] = self.config.get("MISTRAL_API_KEY", "")
        # Uncomment if needed
        # os.environ["SERPER_API_KEY"] = self.config.get("SERPER_API_KEY", "")
        # os.environ["GROQ_API_KEY"] = self.config.get("GROQ_API_KEY", "")
        # os.environ["GEMINI_API_KEY"] = self.config.get("GEMINI_API_KEY", "")

class LLMSetup:
    def __init__(self):
        self.llm = LLM(
            model="mistral/mistral-large-latest",
            temperature=0.7,
            api_key=os.environ["MISTRAL_API_KEY"],
        )

class DataAnalysisAgentFactory:
    def __init__(self, llm):
        self.llm = llm

    def create_agent(self):
        return Agent(
            name=agent_data["name"],
            role=agent_data["role"],
            goal=agent_data["goal"],
            backstory=agent_data["backstory"],
            allow_delegation=False,
            verbose=True,
            llm=self.llm
        )

class DataAnalysisTaskFactory:
    def __init__(self, agent):
        self.agent = agent

    def create_task(self):
        return Task(
            description=task_data["description"],
            expected_output=task_data["expected_output"],
            agent=self.agent
        )
