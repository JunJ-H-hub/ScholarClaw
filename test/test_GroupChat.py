import sys
import os
# 1. 获取当前test_script.py所在的目录（即test/目录）
current_test_dir = os.path.dirname(os.path.abspath(__file__))
# 2. 获取项目根目录（test/的上级目录，即your_project/）
project_root = os.path.dirname(current_test_dir)

# 3. 将项目根目录添加到Python的模块检索路径中
if project_root not in sys.path:
    sys.path.append(project_root)


from src.agents.sub_writing_agent.TrackableAssistant import TrackableAssistantAgent
from autogen_agentchat.agents import AssistantAgent
from src.core.model_client import create_default_client
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_core.tools import FunctionTool
from src.services.retrieval_tool import retrieval_tool
from autogen_agentchat.base import TaskResult

import asyncio

model_client = create_default_client()
# TrackableAssistantAgent
writing_agent = AssistantAgent(
    name="writing_agent",
    description="一个写作助手。",
    model_client=model_client,
    model_client_stream=True,
    system_message="你是一个写作助手，负责根据用户的指令创作文章。如果需要补充外部信息或数据，请回复了解的知识不足，需要检索外部资料。而不是随意生成",
)

from langchain_community.utilities import SerpAPIWrapper
def search_tool(query: str) -> str:
    """Search the web for information and return a summary."""
    search = SerpAPIWrapper(serpapi_api_key="4a0d7556aaa9bdf806083661d38e205c838fdae709e38a714b84e22315d3f1fa")
    return search.run(query)


searcher = FunctionTool(search_tool, description="用于联网查询外部资料，来辅助写作的工具")

retriever_agent = AssistantAgent(
    name="retriever_agent",
    description="一个检索助手，负责根据条件联网查询外部资料。",
    model_client=model_client,
    model_client_stream=True,
    system_message="""你是一个专业的检索助手，负责根据条件联网查询外部资料。""",
	tools=[searcher],
	reflect_on_tool_use=False,
)

review_agent = AssistantAgent(
    name="review_agent",
    description="一个审查助手。",
    model_client=model_client,
    model_client_stream=True,
    system_message="""你是一个专业的审查助手，负责审查文章质量。
    检查内容是否：1) 符合要求 2) 结构需要分条 3) 语言规范 4) 无明显错误
    审查通过时请明确使用"APPROVE"作为结束标志。""",
)

text_termination = TextMentionTermination("APPROVE")

# task_group = RoundRobinGroupChat(
#             participants=[writing_agent,retriever_agent,review_agent],
# 			termination_condition=text_termination,
#             max_turns=5,
#         )

selector_prompt = """请根据当前对话情境，从以下智能体中选择一个来执行下一步任务：

可用智能体：
{roles}

当前对话记录：
{history}

请在以下智能体中选择一位来执行下一步任务：{participants}。

选择逻辑请遵循以下工作流程：

初始任务应由 写作agent 开始。

当 写作agent 在执行过程中认为需要补充外部信息或数据时，应选择 检索agent。

当 写作agent 完成文章撰写后，应选择 审查agent 对文章进行审核。

若 审查agent 审核未通过，请根据审核反馈的原因决定后续选择：

如果审核未通过的原因是文章中存在事实性错误、缺少依据或需要外部资料验证，则应选择 检索agent。 进行信息检索；

如果审核未通过的原因是文章结构、格式、语言表达等问题，则应选择 写作agent 进行修改或重写。

请确保按照流程执行，每次仅选择一个智能体。"""

task_group = SelectorGroupChat(
    [writing_agent,retriever_agent,review_agent],
    model_client=model_client,
    termination_condition=text_termination,
    selector_prompt=selector_prompt,
    allow_repeated_speaker=False,  # Allow an agent to speak multiple turns in a row.
)
async def main():
    i = 0
    final_content = ""
    is_thinking = False
    cur_source = "user"
    async for chunk in task_group.run_stream(task="写一篇关于2025年的最近时事新闻的文章，要求是100字以内"):
        if isinstance(chunk, TaskResult):
            continue
        if chunk.source == "user":
            continue
        if chunk.type == "TextMessage" and chunk.source == "writing_agent":
            final_content = chunk.content
            continue
        if cur_source != chunk.source:
            cur_source = chunk.source
            str1, str2, str3 = "=" * 40, self.name, "=" * 40
            splitStr = str1 + str2 + str3 + "\n"
            print(splitStr)
        if chunk.type == "ModelClientStreamingChunkEvent":
            if '<think>' in chunk.content:
                is_thinking = True
            elif '</think>' in chunk.content:
                is_thinking = False
                continue
            if not is_thinking:
                print(chunk.content, end="")
        if chunk.type == "ToolCallSummaryMessage":
            print(chunk.content)
"""          
id='5ccc5a0a-3949-453f-9ed0-b699ad9faf99' source='user' models_usage=None metadata={} created_at=datetime.datetime(2026, 1, 12, 14, 40, 3, 259185, tzinfo=datetime.timezone.utc) content='写一篇关于2026年的最近时事新闻的文章，要求是100字以内' type='TextMessage'  
"""

if __name__ == "__main__":
    asyncio.run(main())