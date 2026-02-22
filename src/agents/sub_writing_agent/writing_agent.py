from autogen_agentchat.agents import AssistantAgent
from src.core.model_client import create_default_client
from autogen_core.tools import FunctionTool
from src.services.retrieval_tool import retrieval_tool
from src.core.prompts import writing_agent_prompt

def create_writing_agent():
    
    model_client = create_default_client()

    writing_agent = AssistantAgent(
        name="writing_agent",
        description="一个写作助手。",
        model_client=model_client,
        system_message=writing_agent_prompt,
    )
    return writing_agent
