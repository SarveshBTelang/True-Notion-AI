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

import os
import yaml
#import logging
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
#from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.tools import Tool
from crewai import Agent, Crew, Task, LLM
from dotenv import dotenv_values
from crewai.tools import BaseTool
from textblob import TextBlob
import os
import re
#from crewai_tools import (
    #RagTool,
    #FileReadTool,
    #SerperDevTool,
    #WebsiteSearchTool
#)


# Load environment variables from .env
config = dotenv_values(".env")

os.environ["MISTRAL_API_KEY"] = config.get("MISTRAL_API_KEY", "")
#os.environ["SERPER_API_KEY"] = config.get("SERPER_API_KEY", "")
#os.environ["GROQ_API_KEY"] = config.get("GROQ_API_KEY", "")
#os.environ["GEMINI_API_KEY"] = config.get("GEMINI_API_KEY", "")

# Set logging level
#logging.basicConfig(level=logging.INFO)

def main():
    # Automatically load all YAML files in the current directory
    data_folder = os.path.join(os.getcwd(), "data")
    yaml_files = [
        os.path.join(data_folder, f)
        for f in os.listdir(data_folder)
        if f.endswith(".yaml") or f.endswith(".yml")
    ]
    if not yaml_files:
        print("No YAML files found in the 'data' directory.")
        return

    print("=== Loading Datasets ===")
    documents = load_dataset_from_multiple_files(yaml_files)
    print(f"Loaded {len(documents)} documents from {len(yaml_files)} file(s).")

    # Adjust parameters based on number of files
    num_files = len(yaml_files)
    adjusted_k = max(3, 10 // num_files)
    adjusted_chunk_size = max(300, 1000 // num_files)

    print(f"\nUsing k={adjusted_k}, chunk_size={adjusted_chunk_size} based on load.")

    print("\n=== Chunking Documents ===")
    chunked_docs = chunk_documents(documents, chunk_size=adjusted_chunk_size)
    print(f"Created {len(chunked_docs)} document chunks.")

    print("\n=== Creating Vectorstore ===")
    vectorstore = create_vectorstore(chunked_docs)
    retriever = vectorstore.as_retriever(search_kwargs={"k": adjusted_k})
    print("Vectorstore created and documents indexed.")

    print("\n=== Awaiting User Query ===")
    query = input("\nEnter your query: ")

    # Retrieve relevant documents using retriever
    retrieved_docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    inputs = {
        "user_question": query,
        "context": context
    }

    llm = LLM(
        model="mistral/mistral-large-latest",
        temperature=0.7,
        api_key=os.environ["MISTRAL_API_KEY"],
    )

    #sentiment_analysis_tool = SentimentAnalysisTool()      
    

    print("\n=== Defining Agents ===")
    # Define a Knowledge Analyst agent whose role is to use retrieval for answering queries.
    data_analysis_expert = Agent(
        name="AI Assistant",
        role="Expert in giving Strictly Data-driven Answers",
        goal="Answer user questions by analyzing available textual data, relying strictly on verified content and clearly indicating when information is inferred or not found.",
        backstory=(
            "You are a trusted expert in data analysis, responsible for extracting insights and answering "
            "queries using a diverse range of unstructured text documents like resumes, schedules, research notes, "
            "travel plans, and more. You must only use the data that is available, avoid assumptions based on foreign data, and explicitly state "
            "if information is inferred or missing."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

    data_analysis_task = Task(
        description=(
            "You are given a user question: '{user_question}' and a collection of unstructured documents below:\n\n"
            "{context}\n\n"
            "It might be a collection of text from unstructured documents such as notes, lists, resume, portfolio, meeting notes, schedules, "
            "trip plans, company profiles, or research papers.\n\n"
            "Your job is to carefully read the question, analyze all available documents, and determine which of the following analysis steps are needed "
            "to answer the query effectively. You may perform **one, several, or all** of these based on relevance:\n\n"
            
            "1. **Question Answering:** If the answer appears directly in the documents, retrieve it. If you can infer it based on strong contextual clues, do so — "
            "but clearly label it as **'(inferred from context)'**. If the data doesn't support an answer, reply with: **'Answer not found in the available data.'**\n\n"
            
            "2. **Data Extraction:** Extract and list relevant entities such as names, dates, organizations, locations, roles, relationships, or timelines "
            "to help clarify or support your answer. Use 'Not available' or 'Unclear' where data is missing.\n\n"
            
            "3. **Contextual Inference:** If the answer isn't explicitly stated but can be logically deduced (e.g., availability, intent), infer it using document clues. "
            "Clearly mark such answers as **'(inferred)'**. Never guess beyond what the documents justify.\n\n"
            
            "4. **Document Classification:** If needed, classify each document into categories like names, lists, portfolio, biodata, companies or any specific group, "
            "This may help you route and prioritize relevant information.\n\n"
            
            "5. **Timeline Construction:** If the question involves time (e.g., events, trips, job changes), build a chronological timeline based on document dates. "
            "Mark inferred events as **'(inferred)'**, and cite the document sources when possible.\n\n"
            
            "You are allowed and encouraged to use **multiple steps** when needed. However, do not perform irrelevant steps. "
            "Strictly rely on the content of the documents. Be honest: if something isn’t there, say so. "
            "Your final output should be clear, structured, and explicitly indicate whether any part is inferred."
        ),
        expected_output=(
            "A well-reasoned response to the user’s question strictly based on the available document content. "
            "Include entity lists, timelines, or classifications if helpful. "
            "Clearly indicate anything inferred with '(inferred)' or explicitly state when no data is available."
        ),
        #tools=[sentiment_analysis_tool],
        agent=data_analysis_expert,
    )


    # (Optional: Add additional agents with specialized functions, e.g., a summarizer or validator.)
    agents = [data_analysis_expert]

    # Create the CrewAI crew to coordinate the agents.
    #crew_instance = Crew(agents, verbose=True)

    crew_instance = Crew(
        agents=[data_analysis_expert],

        tasks=[data_analysis_task],

        verbose=True
    )

    print("\n=== Running Multi-Agent System ===")
    result = crew_instance.kickoff(inputs=inputs)

    print("\n=== Final Output ===")
    print(result.tasks_output[0])


if __name__ == "__main__":
    main()
