from autogen_agentchat.agents import AssistantAgent
from src.core.model_client import create_default_client
from autogen_core.tools import FunctionTool
from src.services.retrieval_tool import retrieval_tool

def create_writing_agent(state_queue):
    
    model_client = create_default_client()

    writing_agent = AssistantAgent(
        name="writing_agent",
        state_queue=state_queue,
        description="一个写作助手。",
        model_client=model_client,
        system_message="你是一个写作助手，负责根据用户的指令创作文章。如果需要补充外部信息或数据，请回复了解的知识不足，需要检索外部资料。而不是随意生成",
    )
    return writing_agent