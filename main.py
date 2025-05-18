#!/usr/bin/env python
import os
import json
from datetime import datetime

from crewai import Crew
from agents import load_default_agent
from src import process, data_loader
from src.banner import print_banner

# Global variables for conversation, retriever and crew instance
chat_history = []  # Each element is a tuple (user query, AI answer)
crew_instance = None
retriever = None
loaded_files_reference = []
k = None
chunk_size = None
memory = None  # Number of historical conversation pairs to include

def load_rag_config():
    """Load the RAG configuration from file. Fallback to default if any error occurs."""
    config_file = os.path.join('rag', 'rag_config.json')
    default_config_file = os.path.join('rag', 'default_rag_config.json')
    try:
        with open(config_file, 'r') as f:
            rag_parameters = json.load(f)
    except (Exception, KeyError) as e:
        print("Info: Could not load rag_config, using default config.")
        with open(default_config_file, 'r') as f:
            rag_parameters = json.load(f)
    # Write the parameters back to rag_config.json
    with open(config_file, "w") as f:
        json.dump(rag_parameters, f, indent=2)
    # Also upload the updated configuration to Upstash
    data_loader.upload_agent_config_to_upstash(filepath=config_file, key="rag_config")
    return rag_parameters

def initialize_agent():
    """Initializes and returns a Crew instance with the default data analysis agent."""
    load_default_agent.ConfigLoader()  # Loads any necessary config
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

def initialize_system(rag_parameters):
    """Initialize the retriever and log some configuration details."""
    global retriever, loaded_files_reference, k, chunk_size, memory
    k = rag_parameters.get("k")
    chunk_size = rag_parameters.get("chunk_size")
    memory = rag_parameters.get("memory")
    # This call is assumed to initialize and return the document retriever used to fetch context.
    retriever, loaded_files_reference = process.initialize_system(adjusted_k=k, adjusted_chunk_size=chunk_size)
    # Extend the log for reference (printed here for debugging purposes)
    loaded_files_reference.extend([
        "RAG Parameters:",
        f"Top-k value: {k}",
        f"Chunk size: {chunk_size}",
        f"Memory: {memory}"
    ])

def chat_loop():
    """Runs an interactive chat loop with the user."""
    global chat_history, crew_instance, retriever, memory
    
    print_banner()
    print("Welcome to TrueNotion AI chat!")
    print("\nType your question below. Type 'exit' to quit.\n")

    while True:
        user_input = input("User: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat. Thanks for using.. Goodbye!")
            break
        
        # Get the relevant documents (context) for the query
        try:
            retrieved_docs = retriever.get_relevant_documents(user_input)
            context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        except Exception as e:
            print("Error retrieving document context:", e)
            context = ""
        
        # Use only the most recent conversation turns as history (based on 'memory')
        history_str = "\n".join(
            [f"User: {q}\nTrueNotion AI: {a}" for q, a in chat_history[-memory:]]
        )
        
        # Build a prompt that includes the context and conversation history
        full_context = f"""Context:
{context}

Conversation History:
{history_str}"""
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        inputs = {
            "user_question": user_input,
            "context": full_context,
            "timestamp": now_str,
        }
        
        # Kick off the agent to get an answer
        try:
            result = crew_instance.kickoff(inputs=inputs)
            reply = result.tasks_output[0]
            safe_reply = str(reply) if reply is not None else "Sorry, something went wrong. Please try again."
        except Exception as e:
            safe_reply = f"Encountered an error: {e}"
        
        # Print the answer in the conversation format and update the chat history
        print(f"TrueNotion AI: {safe_reply}\n")
        chat_history.append((user_input, safe_reply))
        
def main():
    # Load the configuration parameters
    rag_parameters = load_rag_config()
    
    # Initialize the retriever and log file reference using configuration parameters
    initialize_system(rag_parameters)
    
    # Initialize the Crew instance (the agent)
    global crew_instance
    crew_instance = initialize_agent()
    
    # Start the interactive chat loop
    chat_loop()

if __name__ == '__main__':
    main()
