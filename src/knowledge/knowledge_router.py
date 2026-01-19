import asyncio
import os
import traceback
from urllib.parse import quote, unquote
from pathlib import Path

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse

from src.knowledge.knowledge import config, knowledge_base
from src.knowledge.knowledge.indexing import SUPPORTED_FILE_EXTENSIONS, is_supported_file_extension, process_file_to_markdown
from src.knowledge.knowledge.utils import calculate_content_hash
from src.utils import hashstr
from src.utils.log_utils import setup_logger

logger = setup_logger(__name__)

knowledge = APIRouter(prefix="/knowledge", tags=["knowledge"])

# =============================================================================
# === 数据库管理分组 ===
# =============================================================================

# 获取所有知识库
@knowledge.get("/databases")
async def get_databases():
    """获取所有知识库"""
    try:
        database = knowledge_base.get_databases()
        return database
    except Exception as e:
        logger.error(f"获取数据库列表失败 {e}, {traceback.format_exc()}")
        return {"message": f"获取数据库列表失败 {e}", "databases": []}

# 创建知识库
@knowledge.post("/databases")
async def create_database(
    database_name: str = Body(...),
    description: str = Body(...),
    additional_params: dict = Body({}),
): 
    """创建知识库"""
    try:
        embeding_dic = config.get("embedding-model")
        embedding_provider = embeding_dic.get("model-provider")
        provider_dic = config.get(embedding_provider)
        
        embed_info = {
            "name":embeding_dic.get("model"),
            "dimension": embeding_dic.get("dimension"),
            "base_url": provider_dic.get("base_url"),
            "api_key": provider_dic.get("api_key"), 
        }
        kb_type = config.get("KB_TYPE")
        database_info = await knowledge_base.create_database(
            database_name, description, kb_type=kb_type, embed_info=embed_info, llm_info=None, **additional_params
        )

        return database_info
    except Exception as e:
        logger.error(f"创建数据库失败 {e}, {traceback.format_exc()}")
        return {"message": f"创建数据库失败 {e}", "status": "failed"}

# 选择知识库
@knowledge.get("/databases/select/{db_id}")
async def select_database(db_id: str):
    """选择知识库"""
    database = knowledge_base.get_database_info(db_id)
    config.set("current_db_id", db_id)
    if database is None:
        raise HTTPException(status_code=404, detail="Database not found")
    return database



# 获取知识库详细信息
@knowledge.get("/databases/{db_id}")
async def get_database_info(db_id: str):
    """获取知识库详细信息"""
    database = knowledge_base.get_database_info(db_id)
    if database is None:
        raise HTTPException(status_code=404, detail="Database not found")
    return database

# 更新知识库信息
@knowledge.put("/databases/{db_id}")
async def update_database_info(
    db_id: str, name: str = Body(...), description: str = Body(...)
):
    """更新知识库信息"""
    logger.debug(f"Update database {db_id} info: {name}, {description}")
    try:
        database = await knowledge_base.update_database(db_id, name, description)
        return {"message": "更新成功", "database": database}
    except Exception as e:
        logger.error(f"更新数据库失败 {e}, {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"更新数据库失败: {e}")

# 删除知识库
@knowledge.delete("/databases/{db_id}")
async def delete_database(db_id: str):
    """删除知识库"""
    logger.debug(f"Delete database {db_id}")
    try:
        await knowledge_base.delete_database(db_id)

        # 需要重新加载所有智能体，因为工具刷新了
        from src.agents import agent_manager

        await agent_manager.reload_all()

        return {"message": "删除成功"}
    except Exception as e:
        logger.error(f"删除数据库失败 {e}, {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"删除数据库失败: {e}")



# =============================================================================
# === 文档管理分组 ===
# =============================================================================

# 添加文档到知识库
@knowledge.post("/databases/{db_id}/documents")
async def add_documents(
    db_id: str, items: list[str] = Body(...), params: dict = Body(...)
):
    """添加文档到知识库"""
    logger.debug(f"Add documents for db_id {db_id}: {items} {params=}")

    content_type = params.get("content_type", "file")

    # 安全检查：验证文件路径
    if content_type == "file":
        from src.knowledge.knowledge.utils.kb_utils import validate_file_path

        for item in items:
            try:
                validate_file_path(item, db_id)
            except ValueError as e:
                raise HTTPException(status_code=403, detail=str(e))

        processed_items = []

            # 逐个处理文档并更新进度
        for idx, item in enumerate(items, 1):
                # 处理单个文档
            result = await knowledge_base.add_content(db_id, [item], params=params)
            processed_items.extend(result)

        item_type = "URL" if content_type == "url" else "文件"
        failed_count = len([_p for _p in processed_items if _p.get("status") == "failed"])
        summary = {
            "db_id": db_id,
            "item_type": item_type,
            "submitted": len(processed_items),
            "failed": failed_count,
        }
        return summary | {"items": processed_items}

    try:
        task = await tasker.enqueue(
            name=f"知识库文档处理({db_id})",
            task_type="knowledge_ingest",
            payload={
                "db_id": db_id,
                "items": items,
                "params": params,
                "content_type": content_type,
            },
            coroutine=run_ingest,
        )
        return {
            "message": "任务已提交，请在任务中心查看进度",
            "status": "queued",
            "task_id": task.id,
        }
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to enqueue {content_type}s: {e}, {traceback.format_exc()}")
        return {"message": f"Failed to enqueue task: {e}", "status": "failed"}


# 获取文档详细信息
@knowledge.get("/databases/{db_id}/documents/{doc_id}")
async def get_document_info(db_id: str, doc_id: str):
    """获取文档详细信息（包含基本信息和内容信息）"""
    logger.debug(f"GET document {doc_id} info in {db_id}")

    try:
        info = await knowledge_base.get_file_info(db_id, doc_id)
        return info
    except Exception as e:
        logger.error(f"Failed to get file info, {e}, {db_id=}, {doc_id=}, {traceback.format_exc()}")
        return {"message": "Failed to get file info", "status": "failed"}

# 获取文档基本信息
@knowledge.get("/databases/{db_id}/documents/{doc_id}/basic")
async def get_document_basic_info(db_id: str, doc_id: str):
    """获取文档基本信息（仅元数据）"""
    logger.debug(f"GET document {doc_id} basic info in {db_id}")

    try:
        info = await knowledge_base.get_file_basic_info(db_id, doc_id)
        return info
    except Exception as e:
        logger.error(f"Failed to get file basic info, {e}, {db_id=}, {doc_id=}, {traceback.format_exc()}")
        return {"message": "Failed to get file basic info", "status": "failed"}


# 获取文档内容
@knowledge.get("/databases/{db_id}/documents/{doc_id}/content")
async def get_document_content(db_id: str, doc_id: str):
    """获取文档内容信息（chunks和lines）"""
    logger.debug(f"GET document {doc_id} content in {db_id}")

    try:
        info = await knowledge_base.get_file_content(db_id, doc_id)
        return info
    except Exception as e:
        logger.error(f"Failed to get file content, {e}, {db_id=}, {doc_id=}, {traceback.format_exc()}")
        return {"message": "Failed to get file content", "status": "failed"}


# 删除文档
@knowledge.delete("/databases/{db_id}/documents/{doc_id}")
async def delete_document(db_id: str, doc_id: str):
    """删除文档"""
    logger.debug(f"DELETE document {doc_id} info in {db_id}")
    try:
        await knowledge_base.delete_file(db_id, doc_id)
        return {"message": "删除成功"}
    except Exception as e:
        logger.error(f"删除文档失败 {e}, {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"删除文档失败: {e}")



# =============================================================================
# === 查询分组 ===
# =============================================================================


# 测试查询知识库
@knowledge.post("/databases/{db_id}/query-test")
async def query_knowledge_base(
    db_id: str, query: str = Body(...), meta: dict = Body(...)
):
    """查询知识库"""
    logger.debug(f"Query knowledge base {db_id}: {query}")
    try:
        result = await knowledge_base.aquery(query, db_id=db_id, **meta)
        return {"result": result, "status": "success"}
    except Exception as e:
        logger.error(f"知识库查询失败 {e}, {traceback.format_exc()}")
        return {"message": f"知识库查询失败: {e}", "status": "failed"}




# =============================================================================
# === 文件管理分组 ===
# =============================================================================

# 将用户上传的文件保存到服务器磁盘
@knowledge.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    db_id: str | None = Query(None),         
    allow_jsonl: bool = Query(False),
):
    """上传文件"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No selected file")

    logger.debug(f"Received upload file with filename: {file.filename}")

    ext = os.path.splitext(file.filename)[1].lower()

    if ext == ".jsonl":
        if allow_jsonl is not True or db_id is not None:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
    elif not is_supported_file_extension(file.filename):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # 根据db_id获取上传路径，如果db_id为None则使用默认路径
    if db_id:
        upload_dir = knowledge_base.get_db_upload_path(db_id)
    else:
        upload_dir = os.path.join(config.get("SAVE_DIR"), "database", "uploads")

    basename, ext = os.path.splitext(file.filename)
    filename = f"{basename}_{hashstr(basename, 4, with_salt=True)}{ext}".lower()
    file_path = os.path.join(upload_dir, filename)
    os.makedirs(upload_dir, exist_ok=True)

    file_bytes = await file.read()

    content_hash = calculate_content_hash(file_bytes)
    if knowledge_base.file_existed_in_db(db_id, content_hash):
        raise HTTPException(
            status_code=409,
            detail="数据库中已经存在了相同文件，File with the same content already exists in this database",
        )

    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)

    return {
        "message": "File successfully uploaded",
        "file_path": file_path,
        "db_id": db_id,
        "content_hash": content_hash,
    }


# 获取支持的文件类型
@knowledge.get("/files/supported-types")
async def get_supported_file_types():
    """获取当前支持的文件类型"""
    return {"message": "success", "file_types": sorted(SUPPORTED_FILE_EXTENSIONS)}




