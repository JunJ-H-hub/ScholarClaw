from autogen_agentchat.agents import AssistantAgent
from src.core.model_client import create_default_client
from src.core.prompts import review_agent_prompt


def create_review_agent(state_queue):
    model_client = create_default_client()

    review_agent = AssistantAgent(
        name="review_agent",
        state_queue=state_queue,
        description="一个审查助手。",
        model_client=model_client,
        system_message=review_agent_prompt,
        tools=[]
    )
    return review_agent