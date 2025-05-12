# True-Notion-RAG-based-Agentic-AI-Framework-with-Internal-Knowledgebase-context

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
