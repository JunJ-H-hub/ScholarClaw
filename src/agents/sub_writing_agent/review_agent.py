from autogen_agentchat.agents import AssistantAgent
from src.core.model_client import create_default_client


def create_review_agent(state_queue):
    model_client = create_default_client()

    review_agent = AssistantAgent(
        name="review_agent",
        state_queue=state_queue,
        description="一个审查助手。",
        model_client=model_client,
        system_message="""你是一个专业的审查助手，负责审查文章质量。
        检查内容是否：1) 符合要求 2) 结构合理 3) 语言规范 4) 无明显错误
        审查通过时请明确使用"APPROVE"作为结束标志。""",
        tools=[]
    )
    return review_agent