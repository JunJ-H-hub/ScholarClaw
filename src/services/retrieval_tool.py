from typing import List, Dict, Any
from src.services.chroma_client import ChromaClient
from src.knowledge.knowledge import knowledge_base
from src.utils.log_utils import setup_logger
import traceback
import json
from src.core.config import config

logger = setup_logger(__name__)

async def retrieval_tool(querys: List[str]) -> List[List[Dict[str, Any]]]:
    """
    检索工具，从向量数据库中查询相关文档
    
    :param querys: 查询文本列表
    :return: 包含文档的列表
    """
    retrieval_results = []

    try:
        # 从临时知识库中检索文档
        tmp_db_id = config.get("tmp_db_id")
        tmpdb_results = await knowledge_base.aquery(querys, db_id=tmp_db_id, top_k=config.get_int("tmpdb_top_k"),similarity_threshold=config.get_float("tmpdb_similarity_threshold"))
        # 提取documents列表
        if tmpdb_results and 'metadatas' in tmpdb_results:
            for result in tmpdb_results['metadatas']:
                retrieval_results.append(json.dumps(result, indent=4, ensure_ascii=False))

        # 从用户创建的知识库中检索文档
        db_id = config.get("current_db_id",default=None)
        if db_id is None:
            return retrieval_results
            
        db_results = await knowledge_base.aquery(querys, db_id=db_id, top_k=config.get_int("top_k"),similarity_threshold=config.get_float("similarity_threshold"))
        if db_results and 'documents' in db_results:
            for result, index in enumerate(db_results['documents']):
                result = result + " \n来源文件：" + db_results['metadatas'][index]['source']
                retrieval_results.append(result)

        return retrieval_results
    except Exception as e:
        logger.error(f"测试查询失败 {e}, {traceback.format_exc()}")
        return {"message": f"测试查询失败: {e}", "status": "failed"}
