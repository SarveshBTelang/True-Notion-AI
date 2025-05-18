from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # ✅ Import CORS
from pydantic import BaseModel
from crewai import Crew
from agents import load_default_agent
from src import process
from src import data_loader
from datetime import datetime
import os
import json

app = FastAPI()

# Enable CORS for frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    with open('rag/rag_config.json','r') as f:
        rag_parameters = json.load(f)
except (Exception, KeyError) as e:
    print(f"Info: Could not load rag_config, using default config.")
    with open('rag/default_rag_config.json','r') as f:
        rag_parameters = json.load(f)

file_path = os.path.join(os.getcwd(), "rag/rag_config.json")
with open(file_path, "w") as f:
    json.dump(rag_parameters, f, indent=2)

data_loader.upload_agent_config_to_upstash(filepath="rag/rag_config.json", key="rag_config")

k = rag_parameters.get("k")
chunk_size = rag_parameters.get("chunk_size")
memory = rag_parameters.get("memory")

# logging on frontend
retriever, loaded_files_reference = process.initialize_system(adjusted_k=k, adjusted_chunk_size=chunk_size)

loaded_files_reference.extend([
    "RAG Parameters: ",
    f"Top-k value: {k}",
    f"Chunk size: {chunk_size}",
    f"Memory: {memory}"
])

crew_instance = None

class Query(BaseModel):
    question: str
    history: list[list[str]] = []

@app.on_event("startup")
def startup_event():
    global crew_instance
    crew_instance = initialize_agent()

def initialize_agent():
    load_default_agent.ConfigLoader()
    llm_setup = load_default_agent.LLMSetup()
    agent_factory = load_default_agent.DataAnalysisAgentFactory(llm_setup.llm)
    data_analysis_agent = agent_factory.create_agent()
    task_factory = load_default_agent.DataAnalysisTaskFactory(data_analysis_agent)
    data_analysis_task = task_factory.create_task()
    return Crew(
        agents=[data_analysis_agent],
        tasks=[data_analysis_task],
        verbose=True
    )

@app.post("/chat")
def chat_api(query: Query):
    user_input = query.question
    conversation_history = query.history

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # document context
    retrieved_docs = retriever.get_relevant_documents(user_input)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    # conversation history
    history_str = "\n".join([f"You: {q}\nAI: {a}" for q, a in conversation_history[-memory:]])

    # prompt structure
    full_context = f"""Context:
{context}

Conversation History:
{history_str}"""

    inputs = {
        "user_question": user_input,
        "context": full_context,
        "timestamp": now_str,
    }

    result = crew_instance.kickoff(inputs=inputs)
    reply = result.tasks_output[0]

    safe_reply = str(reply) if reply is not None else "Sorry, something went wrong. Please try again.."

    return {"answer": safe_reply}

# -----------------------------
# NEW ENDPOINT: Save Agent Configuration
# -----------------------------
class AgentConfig(BaseModel):
    agent: dict
    task: dict

@app.post("/save-agent-config")
def save_agent_config(config: AgentConfig):
    try:
        # Define the file path where the configuration will be saved. Here, we save the file in the backend folder.
        file_path = os.path.join(os.getcwd(), "agents/agent_config.json")
        with open(file_path, "w") as f:
            json.dump(config.dict(), f, indent=2)
        data_loader.upload_agent_config_to_upstash(filepath="agents/agent_config.json", key="agent_config")
        return {"message": "Agent configuration saved successfully.", "file_path": file_path}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/loaded-files-reference")
def get_loaded_files_reference():
    try:
        return {"loaded_files_reference": loaded_files_reference}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/initialize")
def reset_backend_state():
    global loaded_files_reference
    try:
        rag_parameters = load_default_agent.fetch_config_from_upstash("rag_config")
        file_path = os.path.join(os.getcwd(), "rag/rag_config.json")
        with open(file_path, "w") as f:
            json.dump(rag_parameters, f, indent=2)

        k = rag_parameters.get("k")
        chunk_size = rag_parameters.get("chunk_size")
        memory = rag_parameters.get("memory")

        # logging on frontend
        retriever, loaded_files_reference = process.initialize_system(adjusted_k=k, adjusted_chunk_size=chunk_size)

        loaded_files_reference.extend([
            "RAG Parameters: ",
            f"Top-k value: {k}",
            f"Chunk size: {chunk_size}",
            f"Memory: {memory}"
        ])
    
    except (Exception, KeyError) as e:
        print(f"Info: Could not load rag_config, using default config.")
        with open('rag/default_rag_config.json','r') as f:
            rag_parameters = json.load(f)

        k = rag_parameters.get("k")
        chunk_size = rag_parameters.get("chunk_size")
        memory = rag_parameters.get("memory")

        # logging on frontend
        retriever, loaded_files_reference = process.initialize_system(adjusted_k=k, adjusted_chunk_size=chunk_size)

        loaded_files_reference.extend([
            "",
            f"Top-k value: {k}",
            f"Chunk size: {chunk_size}",
            f"Memory: {memory}"
        ])

    return {"status": "backend state reset"}
