# agent.py
# Sets up the LangChain agent with Gemini as the LLM
# Uses two tools: job search (Adzuna API) and company info lookup

import os
from dotenv import load_dotenv

# NOTE: langchain 1.x moved AgentExecutor to langchain_classic
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

from tools.job_search import search_jobs_tool
from tools.company_info import company_info_tool

load_dotenv()


def build_agent(memory=None):
    """Build the LangChain ReAct agent. Returns (executor, memory)."""

    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY is missing. Please add it to your .env file."
        )

    # Using Gemini 1.5 Flash since it's free and fast enough for this use case
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.3,
        convert_system_message_to_human=True,
    )

    tools = [search_jobs_tool, company_info_tool]

    # Custom prompt for Indian job market context
    prompt = PromptTemplate.from_template(
        """You are CareerBot, an AI assistant specialised in the Indian job market.

You help with job search, company research, and career advice in India.
Always mention salary in LPA (Lakhs Per Annum). 1 LPA = 1,00,000 INR per year.
Key cities: Bangalore (IT), Mumbai (Finance), Hyderabad (IT/Pharma), Pune, Delhi/NCR.
Notice periods in India are usually 30, 60, or 90 days.

Tools available:
{tools}

Tool names: {tool_names}

Format:
Question: the user question
Thought: what should I do
Action: one of [{tool_names}]
Action Input: input to the action
Observation: result
... (repeat as needed)
Thought: I have enough info now
Final Answer: answer to the user

Chat history so far:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}"""
    )

    if memory is None:
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=6,
            return_messages=False,
        )

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=5,
        max_execution_time=45,
    )
    return executor, memory


def ask_agent(executor, question: str) -> str:
    """Run a question through the agent and return the response text."""
    try:
        result = executor.invoke({"input": question})
        return result.get("output", "Sorry, I couldn't process that. Please try again.")
    except Exception as e:
        return f"⚠️ Something went wrong: {e}\n\nTip: Check that your GOOGLE_API_KEY is correct."
