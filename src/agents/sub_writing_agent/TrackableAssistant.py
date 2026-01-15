# from autogen_agentchat.agents import AssistantAgent
# from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, TextMessage,StructuredMessage,ModelClientStreamingChunkEvent,ThoughtEvent,ToolCallSummaryMessage
# from src.core.state_models import BackToFrontData
# from src.core.state_models import ExecutionState
# from autogen_core import CancellationToken, RoutedAgent
# from autogen_agentchat.base import Response
# from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Sequence,TypeAlias
# from autogen_agentchat.base import TaskResult

# from src.utils.tool_utils import handlerChunk
# import asyncio


# class TrackableAssistantAgent(AssistantAgent):
#     """可追踪的智能体基类"""
    
#     def __init__(self, name: str, state_queue: asyncio.Queue = None, **kwargs):
#         super().__init__(name=name,model_client_stream=True, **kwargs)
#         self.original_on_messages_stream = self.on_messages_stream
#         self.on_messages_stream = self._on_messages_stream
#         self.state_queue = state_queue
#         self.is_thinking = False
#         # 包装on_messages_stream方法以捕获交互
#     async def _on_messages_stream(
# 		self,
# 		messages: Sequence[BaseChatMessage],
# 		cancellation_token: CancellationToken,
# 	) -> AsyncGenerator[Union[BaseAgentEvent, BaseChatMessage, Response], None]:
#         str1,str2,str3 = "="*40, self.name, "="*40
#         splitStr = str1+str2+str3+"\n"
#         await self.state_queue.put(BackToFrontData(step=ExecutionState.SECTION_WRITING,state="generating",data=splitStr))
#         content = ""
#         async for chunk in self.original_on_messages_stream(messages, cancellation_token):
#             yield chunk
#             if isinstance(chunk, ToolCallSummaryMessage):
#                 print(chunk)
#             if isinstance(chunk, ModelClientStreamingChunkEvent):
#                 if '<think>' in chunk.content:
#                     self.is_thinking = True
#                 elif '</think>' in chunk.content:
#                     self.is_thinking = False
#                     continue
#                 if not self.is_thinking:
#                     print(chunk.content,end="")
#                     await self.state_queue.put(BackToFrontData(step=ExecutionState.SECTION_WRITING,state="generating",data=chunk.content))
#                     content += chunk.content
#         print("\n")
#         self.is_thinking = False