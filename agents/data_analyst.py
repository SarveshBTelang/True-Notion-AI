import os
from dotenv import dotenv_values
from crewai import Agent, Task, LLM

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
            name="Data Analyst",
            role="Expert in giving Strictly Data-driven Answers",
            goal=(
                "Answer user questions by analyzing available textual data, relying strictly on verified content "
                "and clearly indicating when information is inferred or not found."
            ),
            backstory=(
                "You are a trusted expert in data analysis, responsible for extracting insights and answering "
                "queries using a diverse range of unstructured text documents like resumes, schedules, research notes, "
                "travel plans, and more. You must only use the data that is available, avoid assumptions based on foreign data, "
                "and explicitly state if information is inferred or missing."
            ),
            allow_delegation=False,
            verbose=True,
            llm=self.llm
        )


class DataAnalysisTaskFactory:
    def __init__(self, agent):
        self.agent = agent

    def create_task(self):
        return Task(
            description=(
                "You are given a user question: '{user_question}' and a collection of unstructured documents below:\n\n"
                "{context}\n\n"
                "It might be a collection of text from unstructured documents such as notes, lists, resume, portfolio, meeting notes, schedules, "
                "trip plans, company profiles, or research papers.\n\n"
                "Your job is to carefully read the question, analyze all available documents, and determine which of the following analysis steps are needed "
                "to answer the query effectively. You may perform **one, several, or all** of these based on relevance:\n\n"
                "Mark inferred events as **'(inferred)'**, and cite the document sources when possible.\n\n"
                
                "1. **Question Answering:** If the answer appears directly in the documents, retrieve it. If you can infer it based on strong contextual clues, do so — "
                "but clearly label it as **'(inferred from context)'**. If the data doesn't support an answer, reply with: **'Answer not found in the available data.'**\n\n"
                
                "2. **Data Extraction:** Extract and list relevant entities such as names, dates, organizations, locations, roles, relationships, or timelines "
                "to help clarify or support your answer. Use 'Not available' or 'Unclear' where data is missing.\n\n"
                
                "3. **Contextual Inference:** If the answer isn't explicitly stated but can be logically deduced (e.g., availability, intent), infer it using document clues. "
                "Clearly mark such answers as **'(inferred)'**. Never guess beyond what the documents justify.\n\n"
                
                "4. **Document Classification:** If needed, classify each document into categories like names, lists, portfolio, biodata, companies or any specific group, "
                "This may help you route and prioritize relevant information.\n\n"
                
                "You are allowed and encouraged to use **multiple steps** when needed. However, do not perform irrelevant steps. "
                "Strictly rely on the content of the documents. Be honest: if something isn’t there, say so. "
                "Your final output should be clear, structured, and explicitly indicate whether any part is inferred."
            ),
            expected_output=(
                "A well-reasoned response to the user’s question strictly based on the available document content. "
                "If the answer requires a date or time, first analyze the events with respect to today's date and time: {timestamp}, "
                "and ensure that the date or time is not in the past (e.g., for planning, schedules, events, or trips)."
                "Do not consider past events when the question is about future planning."
                "Include entity lists, timelines, or classifications if helpful. "
                "Clearly indicate anything inferred with '(inferred)' or explicitly state when no data is available."
            ),
            agent=self.agent
        )