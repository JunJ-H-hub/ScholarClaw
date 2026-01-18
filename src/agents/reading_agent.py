from autogen_agentchat.agents import AssistantAgent
from pydantic import BaseModel, Field
from typing import List, Optional,Dict,Any
from src.utils.log_utils import setup_logger
from src.core.prompts import reading_agent_prompt
from src.core.model_client import create_default_client, create_reading_model_client
from src.core.state_models import BackToFrontData
from src.core.state_models import State,ExecutionState
from src.services.chroma_client import ChromaClient
from src.knowledge.knowledge import knowledge_base
from src.core.config import config

import asyncio
import json

logger = setup_logger(__name__)

class KeyMethodology(BaseModel):
    name: Optional[str] = Field(default=None, description="方法名称（如“Transformer-based Sentiment Classifier”）")
    principle: Optional[str] = Field(default=None, description="核心原理")
    novelty: Optional[str] = Field(default=None, description="创新点（如“首次引入领域自适应预训练”）")


class ExtractedPaperData(BaseModel):
    # paper_id: str = Field(default=None, description="论文ID")
    core_problem: str = Field(default=None, description="核心问题")
    key_methodology: KeyMethodology = Field(default=None, description="关键方法")
    datasets_used: List[str] = Field(default=[], description="使用的数据集")
    evaluation_metrics: List[str] = Field(default=[], description="评估指标")
    main_results: str = Field(default="", description="主要结果")
    limitations: str = Field(default="", description="局限性")
    contributions: List[str] = Field(default=[], description="贡献")
    # author_institutions: Optional[str]  # 如“Stanford University, Department of CS”

# 创建一个新的Pydantic模型来包装列表
class ExtractedPapersData(BaseModel):
    papers: List[ExtractedPaperData] = Field(default=[], description="提取的论文数据列表")

model_client = create_reading_model_client()

read_agent = AssistantAgent(
    name="read_agent",
    model_client=model_client,
    system_message=reading_agent_prompt,
    output_content_type=ExtractedPaperData,
    model_client_stream=True
)


async def add_papers_to_kb(papers:Optional[List[Dict[str, Any]]], extracted_papers: ExtractedPapersData):
    """将提取的论文数据添加到知识库"""
    embedding_dic = config.get("embedding-model")
    embedding_provider = embedding_dic.get("model-provider")
    provider_dic = config.get(embedding_provider)
    
    embed_info = {
        "name": embedding_dic.get("model"),
        "dimension": embedding_dic.get("dimension"),
        "base_url": provider_dic.get("base_url"),
        "api_key": provider_dic.get("api_key"),
    }
    kb_type = config.get("KB_TYPE")
    database_info = await knowledge_base.create_database(
        "临时知识库", "用于存储临时提取的论文数据，仅用于本次报告的生成，用完即删", kb_type=kb_type, embed_info=embed_info, llm_info=None,
    )
    db_id = database_info["db_id"]
    config.set("tmp_db_id", db_id) # 记录临时知识库的db_id，后面retrieval_agent中使用
    
    documents=[json.dumps(paper.model_dump(),ensure_ascii=False) for paper in extracted_papers.papers],
    metadatas=[paper for paper in papers],
    ids = [i for i in range(len(papers))]
    data = {
        "documents": documents,
        "metadatas": metadatas,
        "ids": ids,
    }

    await knowledge_base.add_processed_content(db_id, data)


async def reading_node(state: State) -> State:
    """搜索论文节点"""
    state_queue = state["state_queue"]
    current_state = state["value"]
    current_state.current_step = ExecutionState.READING
    await state_queue.put(BackToFrontData(step=ExecutionState.READING,state="initializing",data=None))

    papers = current_state.search_results

    # 将papers合理分割成多个任务，交给多个read_agent并行执行，最后合并结果
    # 并行执行任务，使用asyncio.gather
    results = await asyncio.gather(*[read_agent.run(task=str(paper)) for paper in papers])

    # 合并结果
    extracted_papers = ExtractedPapersData()
    for result in results:
        parsed_paper = result.messages[-1].content
        extracted_papers.papers.append(parsed_paper)     

     # 还得存入向量数据库中
    await add_papers_to_kb(papers,extracted_papers)
        
    current_state.extracted_data = extracted_papers
    await state_queue.put(BackToFrontData(step=ExecutionState.READING,state="completed",data=f"论文阅读完成，共阅读 {len(extracted_papers.papers)} 篇论文"))
    return {"value": current_state}


if __name__ == "__main__":
    paper = {
        'core_problem': 'Despite the rapid introduction of autonomous vehicles, public misunderstanding and mistrust are prominent issues hindering their acceptance.'
    }
    chroma_client = ChromaClient()
    chroma_client.add_documents(
        documents=[paper],
        metadatas=[paper],
    )   