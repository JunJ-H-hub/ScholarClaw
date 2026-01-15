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
import asyncio

model_client = create_default_client()

agent = TrackableAssistantAgent(
    name="writing_agent",
    description="一个智能助手。",
    model_client=model_client,
    system_message="你是一个智能助手，回答用户的任何问题",
)

agent_test = AssistantAgent(
    name="writing_agent",
    description="一个智能助手。",
    model_client=model_client,
    system_message="你是一个智能助手，回答用户的任何问题",
)

def main():
    print("开始执行任务...")			
    async def run_task():
        async for chunk in agent_test.run_stream(task="请给我写一篇50字的关于春天的文章"):
            print(chunk.content,end="")
    asyncio.run(run_task())
    print("任务结束")

if __name__ == "__main__":
    main()
