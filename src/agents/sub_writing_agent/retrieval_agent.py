from autogen_agentchat.agents import AssistantAgent
from src.core.model_client import create_default_client
from autogen_core.tools import FunctionTool
from src.services.retrieval_tool import retrieval_tool
from src.core.prompts import retrieval_agent_prompt

def create_review_agent(state_queue):
    model_client = create_default_client()

    retriever = FunctionTool(retrieval_tool, description="用于从本地知识库中查询外部资料，来辅助写作的工具")

    review_agent = AssistantAgent(
        name="review_agent",
        state_queue=state_queue,
        description="一个检索助手，负责根据条件从本地知识库中查询外部资料。",
        model_client=model_client,
        system_message=retrieval_agent_prompt,
        tools=[retriever],
        reflect_on_tool_use=False #该参数控制Agent在调用工具后，是否会对工具的执行结果进行"反思"并生成更符合用户需求的最终回复。(如AI调用web_search工具查到一段资料后，会自动总结、归纳或用更友好的方式输出给用户，而不是直接返回原始结果。)
    )
    return review_agent
