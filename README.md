<p align="center">
  <img src="logo.png" alt="Logo" width="500" />
</p>

<p align="center">
  <a href="https://www.apache.org/licenses/LICENSE-2.0">
    <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache-2.0" />
  </a>
  <img src="https://img.shields.io/github/repo-size/SarveshBTelang/True-Notion-AI" alt="Repo Size" />
  <img src="https://img.shields.io/github/last-commit/SarveshBTelang/True-Notion-AI" alt="Last Commit" />
  <img src="https://img.shields.io/github/issues/SarveshBTelang/True-Notion-AI" alt="Issues" />
  <img src="https://img.shields.io/github/issues-pr/SarveshBTelang/True-Notion-AI" alt="Pull Requests" />
  <img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg" alt="Contributions welcome" />
</p>

> **An open-source AI agent framework combining CrewAI, LangChain, and Agentic RAG, with full control over your data.**

> Ideal template for orchestrating intelligent multi-agent workflows across diverse applications—such as **AI chatbots**, **automated customer support**, **data analysis**, **sales profiling**, **web scraping and crawling bots**, **dynamic report generation**, **business scheduling**, and **financial planning**—powered by **cloud-hosted LLMs** like **Mistral**."

Author: [Sarvesh Telang](https://www.linkedin.com/in/sarvesh-telang-17916448/)

---

## 🔧 Overview

This repo empowers you to build your own **AI assistant** with:

- Knowledge from Notion
- Tools like CrewAI & LangChain
- Agentic Reasoning via RAG
- Self-hosting your application for **full data ownership**

---

## ⭐ Key Features

- **Fully Open Source:** Apache 2.0 licensed and free to extend (**Attribution Required**)
- **Modular Agents:** Easily configurable with CrewAI.
- **Data Ownership:** Full control of models, storage, and flow.
- **Notion Integration:** Use Notion as a structured data backend.
- **Prebuilt AI Assistant:** Plug-and-play example for common use cases.
- **Customize with adding NLP Tools:** Sentiment, semantic analyzers, web crawlers (TextBlob, FASS, Serper etc.).
- **Cloud-Ready Deployment:** Works with Vercel, Render, Railway, etc.

---

## How it Works:

- **Extract insights from Notion notes:** Sync personal or business documents into a Notion database that form the base of your **internal knowledge layer**.
- **Memory Routing via Upstash Redis:** Stores document/task metadata to support fast lookup, secure and persistent data retrieval.
- **Chunking & Embedding (LangChain):** Documents are split into RAG-optimized chunks with configurable top-K, chunk size, and window size.
- **Vectorization & Semantic Retrieval:** Uses local or API-based embeddings (e.g., Mistral) and indexes them into a **Vector Database** like FAISS or Upstash.
- **Tool Creation:** Tools such as VectorStoreTool and SummaryTool are created from the knowledge base and reused across different AI agents.
- **Multi-Agent Orchestration with CrewAI:** Starts with a **Knowledge Analyst** agent and is easily extendable with Web Search Agents (Serper), Sentiment Analyzers, and Domain Experts (e.g., Finance, Sales).
- **Response Generation via LLMs:** Uses **Mistral** or plugin-based LLM APIs with concurrent multi-model support for tailored responses.
- **FastAPI Backend + Optional Frontend:** Backend manages routing and conversations, with a frontend deployable on GitHub Pages, Vercel, or any static host.

---

## 🚀 Get Started

```bash
# 1. Fork the repository and clone it under your username
git clone https://github.com/SarveshBTelang/True-Notion-AI.git
cd True-Notion-AI

# 2. Install dependencies (Backend)
pip install -r requirements.txt

# 3. Set up environment variables

# NOTION DATABASE ID
Log in to your Notion account, Create a Database, Note down its ID from the browser URL.
The term before "?" is your database ID
https://www.notion.so/👉1f088b77abf28060xxxxxxxxxxxxxxxx👈?v=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# NOTION INTEGRATION TOKEN
Go to https://www.notion.so/profile/integrations, Log in to your Notion account, Select your workspace with created database and generate token
Note: Ensure the database is connected to your token by checking the "Connections" tab in Database settings.

# UPSTASH REDIS REST URL & REST TOKEN
Log in to your Upstash Redis account: https://console.upstash.com/login
Create Database and retrieve both REST URL and TOKEN under Python from "REST API" tab

# MISTRAL API (or any custom supported LLM for Crew AI agents)
Generate your Mistral API key at https://console.mistral.ai/api-keys
Note: For using custom LLM, configure your LLM code in /agents/load_default_agent.py
For more details on model support, visit https://docs.crewai.com/concepts/llms

# Save all the API keys in .env file
See .env-example.txt for more details

# 5. Run the app
You can run the app with python without deploying it on frontend:

python main.py   (standalone mode for testing)

uvicorn app:app --reload   (with fast api backend server)

# 6. Install dependencies (Frontend)







This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

