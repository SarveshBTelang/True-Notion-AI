"""
Agentic AI Framework using CrewAI, langchains and RAG

This system performs the following:
1. Loads and processes a custom dataset stored in a YAML file.
2. Splits ("chunks") document texts using LangChain’s text splitter.
3. Embeds the document chunks using a local sentence-transformers embedding model.
4. Indexes these embeddings in a FAISS vectorstore.
5. Wraps the retrieval (RAG) functionality in a Tool that CrewAI agents can call.
6. Defines a Knowledge Analyst agent (with the option to add specialists later)
   whose role is to use the retrieval tool and then generate a response via an LLM.
7. Coordinates the agents in a Crew and prints the collaborative output.

Author: Sarvesh Telang
"""

from agents import data_analyst
from datetime import datetime
from crewai import Crew
from src import process
from tools import sentiment_analysis

# Performance parameters
k = 10
chunk_size = 1000
memory = 4                          

def initialize_agent():
    config_loader = data_analyst.ConfigLoader()
    llm_setup = data_analyst.LLMSetup()

    agent_factory = data_analyst.DataAnalysisAgentFactory(llm_setup.llm)
    data_analysis_agent = agent_factory.create_agent()

    task_factory = data_analyst.DataAnalysisTaskFactory(data_analysis_agent)
    data_analysis_task = task_factory.create_task()

    crew_instance = Crew(
        agents=[data_analysis_agent],
        tasks=[data_analysis_task],
        verbose=True
    )

    return crew_instance

def chat_loop(retriever, crew_instance):
    conversation_history = []

    print("\n=== Interactive AI Chatbot===")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("User: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Thanks for using. Have a nice day.. Goodbye!")
            break

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        retrieved_docs = retriever.get_relevant_documents(user_input)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        full_context = "\n".join([f"You: {q}\nAI: {a}" for q, a in conversation_history[-memory:]])
        full_context += f"\n\n{context}"

        inputs = {
            "user_question": user_input,
            "context": full_context,
            "timestamp": now_str,
        }

        result = crew_instance.kickoff(inputs=inputs)
        reply = result.tasks_output[0]

        print(f"\n TrueNotion: {reply}\n")
        conversation_history.append((user_input, reply))


def main():
    retriever = process.initialize_system(adjusted_k=k, adjusted_chunk_size=chunk_size)
    if retriever is None:
        return

    crew_instance = initialize_agent()
    chat_loop(retriever, crew_instance)


if __name__ == "__main__":
    main()
