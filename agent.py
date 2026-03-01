# agent.py
# Implements a linear, deterministic AI pipeline to eliminate API looping and quota issues.

import os
import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from tools.job_search import search_jobs_tool
from tools.company_info import company_info_tool
from tools.market_trends import market_trends_tool

from composio_langchain import LangchainProvider
from composio import Composio

load_dotenv()

class LinearCareerAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        if not self.api_key:
            raise EnvironmentError("GOOGLE_API_KEY is missing. Please add it to your environment variables.")

        # Main summarizer LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.3,
        )

        # Fast router LLM
        self.router_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.0,
        )

        # Init Composio
        self.composio_error = None
        composio_api_key = os.getenv("COMPOSIO_API_KEY")
        if composio_api_key:
            composio_api_key = composio_api_key.strip()
            try:
                # Direct SDK initialization is more stable than high-level wrappers
                self.composio_sdk = Composio(api_key=composio_api_key)
                self.langchain_provider = LangchainProvider()
                
                # Fetch all tools for the LinkedIn app to find the correct one dynamically
                # This is more robust than guessing the slug string
                tools = self.composio_sdk.tools.get(user_id="default_user", toolkits=["linkedin"])
                
                if not tools:
                    # Try alternate toolkit names if 'linkedin' didn't work
                    tools = self.composio_sdk.tools.get(user_id="default_user", toolkits=["linkedin_profile"])
                
                if not tools:
                    available_toolkits = [t.slug for t in self.composio_sdk.toolkits.get()]
                    raise RuntimeError(f"No tools found for toolkit 'linkedin'. Available: {available_toolkits[:5]}...")

                # Wrap tools for Langchain
                self.linkedin_tools = self.langchain_provider.wrap_tools(
                    tools=tools,
                    execute_tool=self.composio_sdk.tools.execute
                )
            except Exception as e:
                self.composio_error = f"Composio initialization error: {str(e)}"
                self.linkedin_tools = None
        else:
            self.composio_error = "COMPOSIO_API_KEY is not configured in Hugging Face Space Secrets."
            self.linkedin_tools = None

    async def ask(self, user_query: str, chat_history: list = None) -> str:
        """
        The main linear pipeline: Route -> Fetch (Optional) -> Summarize
        """
        try:
            # Step 1: Route the query
            intent, extraction_arg = await self._route_query(user_query)

            # Step 2: Fetch raw data exactly once based on intent
            raw_data = ""
            if intent == "job_search":
                raw_data = await search_jobs_tool.ainvoke(extraction_arg)
            elif intent == "company_info":
                raw_data = await company_info_tool.ainvoke(extraction_arg)
            elif intent == "linkedin_profile":
                if self.linkedin_tools:
                    # Composio returns a list of tools, we want the first one (GET_PROFILE)
                    profile_tool = self.linkedin_tools[0]
                    # Composio expects a specific payload format depending on the action schema
                    # For a profile URL, we pass it under the 'url' arg or let ainovke handle it if it expects a dict
                    raw_data = await profile_tool.ainvoke({"url": extraction_arg, "username": extraction_arg})
                else:
                    raw_data = json.dumps({"error": self.composio_error or "Unknown Composio error"})
            elif intent == "market_trends":
                raw_data = await market_trends_tool.ainvoke(extraction_arg)

            # Step 3: Summarize and respond
            return await self._generate_final_response(user_query, intent, raw_data, chat_history)

        except Exception as e:
            return f"⚠️ Something went wrong in the async pipeline: {e}"

    async def _route_query(self, query: str):
        """
        Deterministically decides which tool to use.
        Returns: Tuple(intent_name, argument_for_tool)
        """
        routing_prompt = f"""
        You are a smart router for a career application.
        Analyze the user's query and decide which specific tool to use.
        
        Available tools:
        - job_search: For finding actual job listings. You MUST extract a JSON representing the filter criteria, e.g '{{"title": "python", "location": "Bangalore"}}'. If the user provides a raw JSON string of filters, just output that exact JSON string.
        - company_info: For researching a specific company. Arg: The company name.
        - linkedin_profile: For summarizing a specific person's linkedin URL. Arg: The URL.
        - market_trends: For general knowledge about hiring. Arg: The local market/city.
        - none: For general chit-chat. Arg: none.

        Query: "{query}"
        
        Output strictly in this format: INTENT | ARGUMENT
        Example 1: job_search | {{"title": "developer", "location": "mumbai"}}
        Example 2: company_info | TCS
        Example 3: linkedin_profile | https://www.linkedin.com/in/billgates
        Example 4: none | none
        """
        
        route_decision = await self.router_llm.ainvoke(routing_prompt)
        route_text = route_decision.content.strip()
        
        try:
            intent, arg = route_text.split(" | ")
            return intent.strip(), arg.strip()
        except Exception:
            # Fallback
            return "none", "none"

    async def _generate_final_response(self, query: str, intent: str, raw_data: str, chat_history: list) -> str:
        """
        Takes the raw data and the user query, and generates a warm, final response.
        """
        system_instructions = """
        You are CareerBot, your friendly and proactive career companion. You specialize in the Indian job market.
        
        Guidelines:
        1. Warm & Natural: Speak like a trusted mentor.
        2. Indian Market Expert: Always mention salary in LPA (Lakhs Per Annum). 1 LPA = 1,00,000 INR per year.
        3. Structured formatting: If you receive RAW JSON data, you MUST include that RAW JSON data exactly as provided somewhere in your response (usually at the very bottom) so the UI can parse it into cards. Do not omit the JSON if it is provided.
        """

        if intent == "linkedin_profile":
            prompt = f"""
            User Query: {query}
            Intent Detected: {intent}
            Raw LinkedIn Data: 
            {raw_data if raw_data else 'No data retrieved.'}
            
            You are acting as an expert Career Coach for the Indian Job Market.
            Based on the LinkedIn Profile data above, provide a comprehensive analysis with these EXACT sections:
            
            1. **Executive Summary**: A professional 2-3 sentence overview of the person's identity and career stage.
            2. **Plus Points (Core Strengths)**: 3-4 bullet points highlighting their unique skills, experience, and certifications.
            3. **Minus Points (Gaps/Areas for Improvement)**: 2-3 bullet points on what's missing or how they can improve their profile for the Indian market.
            4. **Best Job Roles**: 3 specific roles they should target (e.g. 'Senior Frontend Engineer').
            5. **Where to Apply**: Types of companies or specific Indian companies (e.g. Zomato, Swiggy, TCS, Startups) that would value this profile.
            
            Ensure you mention salary expectations in **LPA (Lakhs Per Annum)**.
            """
        else:
            prompt = f"""
            User Query: {query}
            Intent Detected: {intent}
            Raw Data from API: 
            {raw_data if raw_data else 'No extra API data pulled for this query.'}
            
            Please provide a helpful, warm response to the user based on the raw data above.
            If the intent is a job search or company info, ensure you append the RAW API JSON Data to your response so the frontend can render it visually.
            """

        messages = [SystemMessage(content=system_instructions)]
        
        if chat_history:
            # We assume chat_history is a list of dicts: [{'role': 'user', 'content': 'hi'}]
            # We'll truncate to last 4 for context window safety
            for msg in chat_history[-4:]:
                if msg.get('role') == 'user':
                    messages.append(HumanMessage(content=msg.get('content', '')))
                else:
                    # assistant
                    messages.append(SystemMessage(content=msg.get('content', '')))
                    
        messages.append(HumanMessage(content=prompt))

        response = await self.llm.ainvoke(messages)
        return response.content

def build_agent(memory=None):
    """
    Adapter function to maintain compatibility with app.py.
    Returns the linear agent instance.
    """
    return LinearCareerAgent(), memory

async def ask_agent_async(agent_instance, question: str, chat_history: list = None) -> str:
    """
    Adapter function to trigger the async pipeline.
    """
    return await agent_instance.ask(question, chat_history)
