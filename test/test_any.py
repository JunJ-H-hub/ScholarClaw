from langchain_community.utilities import SerpAPIWrapper

# 初始化SerpAPI
search = SerpAPIWrapper(serpapi_api_key="4a0d7556aaa9bdf806083661d38e205c838fdae709e38a714b84e22315d3f1fa")

# 执行搜索查询
result = search.run("最近的时事新闻")
print(result)  # 输出结果


    