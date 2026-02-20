from src.agents.sub_writing_agent.writing_state_models import WritingState, SectionState
from typing import Dict, Any
from src.agents.sub_writing_agent.writing_chatGroup import create_writing_group
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, TextMessage,StructuredMessage,ModelClientStreamingChunkEvent,ThoughtEvent,ToolCallSummaryMessage,ToolCallExecutionEvent
from autogen_agentchat.base import TaskResult
from src.core.state_models import BackToFrontData,ExecutionState
import asyncio


async def parallel_writing_node(state: WritingState) -> Dict[str, Any]:
        """并行执行所有子任务"""
        
        async def run_single_subtask(task: Dict):
            nonlocal state
            """执行单个子任务"""            
            task_prompt = f"""请根据以下内容完成写作任务：
                用户的请求是：{task['user_request']}
                当前写作子任务: {task['section']}
                论文全局分析: {task['global_analyse']}

                请开始写作：
            """
            is_thinking = False
            cur_source = "user"
            try:
                task_group = create_writing_group()
                task_group.reset()
                async for chunk in task_group.run_stream(task=task_prompt):  # type: ignore
                    if isinstance(chunk, TaskResult):
                        continue
                    if chunk.source == "user":
                        continue
                    if chunk.type == "TextMessage" and chunk.source == "writing_agent":
                        state["sections"][task["index"]] = chunk.content
                        continue
                    if cur_source != chunk.source:
                        cur_source = chunk.source
                        str1,str2,str3 = "="*40, self.name, "="*40
                        splitStr = str1+str2+str3+"\n"
                        await state_queue.put(BackToFrontData(step=ExecutionState.SECTION_WRITING+"_"+str(task["index"]),state="generating",data=splitStr))
                    if chunk.type == "ModelClientStreamingChunkEvent":
                        if '<think>' in chunk.content:
                            is_thinking = True
                        elif '</think>' in chunk.content:
                            is_thinking = False
                            continue
                        if not is_thinking:
                            print(chunk.content,end="")
                            await state_queue.put(BackToFrontData(step=ExecutionState.SECTION_WRITING+"_"+str(task["index"]),state="generating",data=chunk.content))
                    if chunk.type == "ToolCallSummaryMessage":
                        await state_queue.put(BackToFrontData(step=ExecutionState.SECTION_WRITING+"_"+str(task["index"]),state="generating",data=chunk.content))

            except Exception as e:
                # 此处应该有重试机制
                await state_queue.put(BackToFrontData(step=ExecutionState.SECTION_WRITING+"_"+str(task["index"]),state="error",data=f"Section writing failed: {str(e)}"))
                # return state
        
        # 并行执行所有子任务
        state_queue=state["state_queue"]
        global_analyse = state["global_analysis"]
        user_request = state["user_request"]
        sections = state["sections"]
        subtasks = []
        for i in range(len(sections)):
            await state_queue.put(BackToFrontData(step=ExecutionState.SECTION_WRITING+"_"+str(i+1),state="initializing",data=None))
            dic = {
                "user_request": user_request,
                "global_analyse": global_analyse,
                "section": sections[i],
                "index": i+1
            }
            subtasks.append(dic)
        tasks = [run_single_subtask(task) for task in subtasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return state