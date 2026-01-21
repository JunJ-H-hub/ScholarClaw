"""
测试 ChromaKB 的 _get_embedding_function 方法
"""
import sys
from pathlib import Path
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import config
import asyncio


def test_get_embedding_function():
    """测试 _get_embedding_function 方法"""
    print("===== 测试 _get_embedding_function 方法 =====\n")

    # 准备测试用的 embed_info
    # 从配置中获取嵌入模型信息
    print("--- 1. 准备嵌入配置 ---")
    embeding_dic = config.get("embedding-model")
    embedding_provider = embeding_dic.get("model-provider")
    provider_dic = config.get(embedding_provider)
    
    embed_info = {
        "name": embeding_dic.get("model"),
        "dimension": embeding_dic.get("dimension"),
        "base_url": provider_dic.get("base_url"),
        "api_key": provider_dic.get("api_key"),
    }
    
    print(f"嵌入模型: {embed_info['name']}")
    print(f"维度: {embed_info['dimension']}")
    print(f"Base URL: {embed_info['base_url']}")
    print(f"API Key: {embed_info['api_key'][:10]}..." if embed_info['api_key'] else "API Key: None")
    print()

    # 测试 _get_embedding_function 方法
    print("--- 2. 调用 _get_embedding_function 方法 ---")
    try:               
        embedding_function = OpenAIEmbeddingFunction(
                                model_name="text-embedding-v4",
                                api_key=embed_info["api_key"],
                                api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                            )
        print("✓ 成功获取 embedding 函数") 
        print(f"  函数类型: {type(embedding_function)}")
        print()
    except Exception as e:
        print(f"✗ 获取 embedding 函数失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试嵌入函数调用
    print("--- 3. 测试嵌入函数调用 ---")
    test_texts = [
        "这是一个测试文本。",
        "机器学习是人工智能的一个重要分支。",
        "深度学习使用神经网络来模拟人脑的工作方式。"
    ]
    
    try:
        print(f"  输入文本数量: {len(test_texts)}")
        embeddings = embedding_function(test_texts)
        print(f"✓ 成功生成嵌入向量")
        print(f"  嵌入向量数量: {len(embeddings)}")
        print(f"  第一个嵌入向量维度: {len(embeddings[0])}")
        print(f"  第一个嵌入向量前5个值: {embeddings[0][:5]}")
        print()
    except Exception as e:
        print(f"✗ 生成嵌入向量失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 验证嵌入向量维度
    print("--- 4. 验证嵌入向量维度 ---")
    expected_dimension = embed_info.get("dimension", 1024)
    actual_dimension = len(embeddings[0])
    
    if actual_dimension == expected_dimension:
        print(f"✓ 嵌入向量维度正确: {actual_dimension}")
    else:
        print(f"✗ 嵌入向量维度不匹配: 期望 {expected_dimension}, 实际 {actual_dimension}")
    print()


    print("===== 测试完成 =====")
    return True

def test_openai_embedding_function():
    """测试 OpenAIEmbeddingFunction 类"""
    print("===== 测试 OpenAIEmbeddingFunction 类 =====\n")
    import openai
    from typing import Dict, Any
    client_params: Dict[str, Any] = {"api_key": self.api_key}
    client_params["base_url"] = "https://ark.cn-beijing.volces.com/api/v3"

    client = openai.OpenAI(**client_params)
    print(client)
    test_texts = [
        "这是一个测试文本。",
        "机器学习是人工智能的一个重要分支。",
        "深度学习使用神经网络来模拟人脑的工作方式。"
    ]
    print(f"输入文本数量: {len(test_texts)}")
    embedding_params: Dict[str, Any] = {
                "model": "doubao-embedding-text-240715",
                "input": test_texts,
            }
    response = client.embeddings.create(**embedding_params)

    print(response)


def test_ark_embedding_function():
    """测试 ArkEmbeddingFunction 类"""
    print("===== 测试 ArkEmbeddingFunction 类 =====\n")
    import os
    from volcenginesdkarkruntime import Ark
    # 初始化客户端
    client = Ark(
        # 从环境变量中读取您的方舟API Key
        api_key=self.api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )
    response = client.multimodal_embeddings.create(
    # doubao-embedding-text-240715
        model="doubao-embedding-vision-250615",
        input=[{"type":"text","text":"天很蓝"},{"type":"text","text":"水很深"}],
        encoding_format="float"  
    )
    # 打印结果
    print(response)
    print(f"向量维度: {len(response.data.embedding)}")
    # print(f"向量维度: {len(response.data[0].embedding)}")
    # print(f"前10维向量: {response.data[0].embedding[:10]}")


async def test_ark_chat_model():
    """测试 ArkChatModel 类"""
    import asyncio
    import os
    # Install SDK:  pip install 'volcengine-python-sdk[ark]'
    from volcenginesdkarkruntime import AsyncArk

    # 初始化Ark客户端
    client = AsyncArk(
        # The base URL for model invocation
        base_url="https://ark.cn-beijing.volces.com/api/v3", 
        # Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey 
        api_key=self.api_key, 
    )
    stream = await client.chat.completions.create(  
        # Replace with Model ID
        model = "doubao-seed-1-6-thinking-250715",
        messages=[
            {"role": "system", "content": "你是 AI 人工智能助手"},
            {"role": "user", "content": "常见的十字花科植物有哪些？"},
        ],
        stream=True
    )
    async for completion in stream:
        print(completion.choices[0].delta.content, end="")
    print()


    

if __name__ == "__main__":
    # 测试 1: 基本功能测试
    success1 = test_get_embedding_function()
    # asyncio.run(test_ark_chat_model())
    
    # 总结
    print("\n===== 测试总结 =====")
    print(f"基本功能测试: {'✓ 通过' if success1 else '✗ 失败'}")
