# 主体架构
## 启动类
main.py是整个项目的启动类，使用fastapi定义api接口（知识库接口和报告生成接口）
## 报告生成接口
1.后端返回 EventSourceResponse ，建立 SSE 连接。
2.event_generator 从队列读取状态并实时推送到前端。event_generator 从队列读取状态并实时推送到前端。
3.通过langgraph构建生成报告业务流程图，并启动流程的执行。
```python
async def event_generator():
        while True:
            state = await state_queue.get()
            yield {"data": f"{state.model_dump_json()}"
                   
# 启动事件生成器（此时已开始监听队列）
event_source = EventSourceResponse(event_generator(), media_type="text/event-stream")

# 初始化业务流程控制器
orchestrator = PaperAgentOrchestrator(state_queue = state_queue)
# 启动异步任务
    asyncio.create_task(orchestrator.run(user_request=query))

return event_source
```
# 生成报告业务流程图
由search_agent_node、reading_agent_node、analyse_agent_node、writing_agent_node、report_agent_node组成。
1.search_agent_node：根据用户需求，生成检索条件（这部分会触发用户审查检索条件），并从arxiv中搜索相关论文，返回搜索结果。
2.reading_agent_node：根据搜索结果，阅读每篇论文，提取每一篇论文的主要内容特点，将每一篇论文整理成结构化的数据。
3.analyse_agent_node：根据结构化的论文数据，汇总成一篇概论。
4.writing_agent_node：根据这篇概论生成论文报告的总体写作大纲，再拆分并行完成各个部分的写作任务。
5.report_agent_node：汇总每个部分的写作任务形成完整的报告，展示到前端。

下面介绍每个节点的具体实现细节

# search_agent_node（论文搜索节点）
search_agent_node 负责根据用户需求，从 arxiv 中搜索相关论文。该节点首先使用 LLM 将用户的自然语言需求转换为结构化的查询条件（SearchQuery），然后通过用户代理（userProxyAgent）进行人工审核，审核通过后调用 PaperSearcher 进行论文检索。

核心实现流程：
```python
async def search_node(state: State) -> State:
    state_queue = state["state_queue"]
    current_state = state["value"]
    
    # 1. 使用 search_agent 生成查询条件
    response = await search_agent.run(task=f"用户查询需求：{current_state.user_request}")
    search_query = response.messages[-1].content
    
    # 2. 通过 userProxyAgent 进行人工审核（等待前端输入）
    result = await userProxyAgent.on_messages(
        [TextMessage(content="请人工审核：查询条件是否符合？", source="AI")],
        cancellation_token=CancellationToken()
    )
    search_query = parse_search_query(result.content)
    
    # 3. 调用检索服务搜索论文
    paper_searcher = PaperSearcher()
    results = await paper_searcher.search_papers(
        querys=search_query.querys,
        start_date=search_query.start_date,
        end_date=search_query.end_date,
    )
    
    current_state.search_results = results
    return {"value": current_state}
```

关键步骤：
- **查询生成**：LLM 将自然语言转为结构化查询条件（querys、start_date、end_date）
- **人工审核**：通过 Future 机制等待前端传入审核结果
- **论文检索**：调用 PaperSearcher 从 arxiv 获取论文列表

**从arxiv中爬取的格式**
```json
[{
    'arxiv_id': '1909.03818v2',
    'title': 'Large-Scale Local Causal Inference of Gene Regulatory Relationships',
    'abstract': "Gene regulatory networks play a crucial role in controlling an organism's\nbiological processes, which is why there is significant interest in ...",
    'authors': ['Ioan Gabriel Bucur', 'Tom Claassen', 'Tom Heskes'],
    'published': '2019-09-03T17:54:33+00:00',
    'categories': ['stat.ML', 'cs.LG', 'q-bio.GN', 'q-bio.MN', 'q-bio.QM'],
    'link': 'http://arxiv.org/abs/1909.03818v2'
}, {...},...]
```
下面介绍用户审查如何实现
## userproxy_agent（用户审查代理）
userproxy_agent_node 是一个用户代理节点，用于在关键步骤中引入人工审核。该节点继承自 AutoGen 的 UserProxyAgent，通过异步 Future 机制实现与前端的交互。这里继承了AutoGen的UserProxyAgent类，并重写on_messages方法，实现与前端的交互。

核心实现机制：
```python
class WebUserProxyAgent(UserProxyAgent):
    def __init__(self, name):
        super().__init__(name)
        self.waiting_future = None
    
    async def on_messages(self, messages, cancellation_token: CancellationToken):
        # 创建 Future 并等待前端输入
        self.waiting_future = asyncio.get_event_loop().create_future()
        user_input = await self.waiting_future
        return TextMessage(content=user_input, source="human")

    def set_user_input(self, user_input: str):
        # 前端调用此方法唤醒等待
        if self.waiting_future and not self.waiting_future.done():
            self.waiting_future.set_result(user_input)
```

工作流程：
1. create_future()创建 Future对象，代表一个尚未完成的计算结果
2. await waiting_future会挂起当前协程，直到Future有结果,这是典型的生产者-消费者模式的异步实现
3. 前端通过 "/send_input" 接口 后端调用 `set_user_input` 传入审核结果
4. set_result() 完成Future 并设置结果。这会唤醒所有正在await这个Future的协程
5. 流程继续执行

# reading_agent_node（论文阅读节点）
reading_agent_node 负责阅读搜索到的论文，提取每篇论文的核心信息，并将其整理为结构化数据。该节点使用多个 read_agent 并行处理论文，提高处理效率，同时将提取的数据存入向量数据库供后续写作时检索使用。

核心数据结构：
```python
class ExtractedPaperData(BaseModel):
    core_problem: str              # 核心问题
    key_methodology: KeyMethodology # 关键方法（名称、原理、创新点）
    datasets_used: List[str]       # 使用的数据集
    evaluation_metrics: List[str]  # 评估指标
    main_results: str              # 主要结果
    limitations: str               # 局限性
    contributions: List[str]       # 贡献
```

核心实现流程：
```python
async def reading_node(state: State) -> State:
    papers = state["value"].search_results
    
    # 并行处理每篇论文
    results = await asyncio.gather(
        *[read_agent.run(task=str(paper)) for paper in papers]
    )
    
    # 合并结果
    extracted_papers = ExtractedPapersData()
    for result in results:
        extracted_papers.papers.append(result.messages[-1].content)
    
    # 存入向量数据库
    await add_papers_to_kb(papers, extracted_papers)
    
    state["value"].extracted_data = extracted_papers
    return {"value": state["value"]}
```

关键特点：
- **并行处理**：使用 `asyncio.gather` 并行阅读多篇论文
- **结构化提取**：LLM 按照预定义模型提取论文关键信息
- **向量存储**：提取结果存入向量数据库，支持后续检索增强（注：将提取后的论文信息extracted_papers转为json字符串存储为document，将原始检索结果papers存储为metadata，这样后续检索时，通过向量检索document，返回信息更详细的metadata数据）

# analyse_agent_node（论文分析节点）
analyse_agent_node 负责对结构化的论文数据进行深度分析，生成全局分析报告。该节点内部包含三个子智能体：聚类智能体（PaperClusterAgent）、深度分析智能体（DeepAnalyseAgent）和全局分析智能体（GlobalanalyseAgent），通过三阶段分析流程生成综合分析结果。

核心实现流程：
```python
async def on_messages_stream(self, message: ExtractedPapersData, cancellation_token):
    # 1. 聚类分析：按主题对论文进行分组
    cluster_results = await self.cluster_agent.run(message)
    
    # 2. 深度分析：对每个聚类进行深入分析（并行）
    deep_analysis_results = await asyncio.gather(
        *[self.deep_analyse_agent.run(cluster) for cluster in cluster_results]
    )
    
    # 3. 全局分析：汇总所有聚类分析结果
    async for chunk in self.global_analyse_agent.run(deep_analysis_results):
        if isinstance(chunk, Dict):
            global_analysis = chunk
            break
    
    return Response(
        chat_message=TextMessage(
            content=json.dumps(global_analysis, ensure_ascii=False),
            source=self.name
        )
    )
```

分析流程：
- **聚类分析**：将论文按主题分组，识别研究主题和方向
- **深度分析**：并行对每个聚类进行技术路线、方法对比、应用领域等深入分析
- **全局分析**：汇总所有聚类结果，生成包含研究热点、局限性、未来趋势的全局报告

## PaperClusterAgent（论文聚类分析智能体）
PaperClusterAgent 负责将结构化的论文数据按照主题进行聚类分组，识别研究主题和方向。该智能体结合了嵌入向量生成、KMeans 聚类算法和 LLM 主题描述生成，实现智能化的论文分类。

核心实现流程：
```python
class PaperClusterAgent:
    def cluster_papers(self, papers: List[Dict]) -> List[PaperCluster]:
        # 1. 生成嵌入向量
        embeddings = self.generate_embeddings(papers)
        
        # 2. 确定最佳聚类数量（肘部法则）
        n_clusters = self.determine_optimal_clusters(embeddings)
        
        # 3. 执行KMeans聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(embeddings)
        
        # 4. 构建聚类结果
        clusters = []
        for cluster_id in range(n_clusters):
            cluster_papers = [
                papers[i] for i, label in enumerate(cluster_labels) 
                if label == cluster_id
            ]
            clusters.append(PaperCluster(
                cluster_id=cluster_id,
                papers=cluster_papers,
                theme_description="",
                keywords=[]
            ))
        
        return clusters
    
    async def generate_cluster_theme(self, cluster: PaperCluster):
        # 使用LLM生成主题描述和关键词
        prompt = f"""
        基于以下论文信息，生成主题描述和3-5个关键词：
        {json.dumps(cluster.papers[:3], ensure_ascii=False)}
        
        格式：
        主题描述：[主题描述]
        关键词：[关键词1, 关键词2, 关键词3]
        """
        response = await self.clustering_agent.run(task=prompt)
        return self.parse_llm_response(response.messages[-1].content)
```

聚类流程：
- **嵌入生成**：将论文的核心问题、方法、结果等信息转换为向量表示
- **聚类数量确定**：使用肘部法则自动确定最佳聚类数量
- **KMeans聚类**：基于向量相似度将论文分组
- **主题生成**：使用 LLM 为每个聚类生成主题描述和关键词

## DeepAnalyseAgent（论文深度分析智能体）
DeepAnalyseAgent 负责对单个聚类进行深入分析，包括技术路线、方法对比、应用领域等方面的详细分析。该智能体基于聚类主题和论文内容，生成结构化的深度分析报告。

核心实现流程：
```python
async def deep_analyze_cluster(self, cluster: PaperCluster) -> DeepAnalyseResult:
    prompt = f"""
    基于以下聚类信息进行深入学术分析：

    ## 基本信息
    - 聚类主题：{cluster.theme_description}
    - 核心关键词：{', '.join(cluster.keywords)}
    - 论文数量：{len(cluster.papers)}

    ## 详细论文数据
    {json.dumps(cluster.papers, ensure_ascii=False, indent=2)}

    请以结构化的方式组织你的分析结果。
    """
    
    response = await self.deep_analyse_agent.run(task=prompt)
    analyse_content = response.messages[-1].content
    
    return DeepAnalyseResult(
        cluster_id=cluster.cluster_id,
        theme=cluster.theme_description,
        keywords=cluster.keywords,
        paper_count=len(cluster.papers),
        deep_analyse=analyse_content,
        papers=cluster.papers
    )
```

分析内容：
- **技术路线分析**：梳理该主题下的核心技术发展脉络
- **方法对比**：从效率、成本、适用场景等维度对比不同方法
- **应用领域分析**：归类各主题的应用案例，分析需求差异
- **研究热点识别**：提炼当前关注的技术方向，预测未来趋势

## GlobalanalyseAgent（全局分析智能体）
GlobalanalyseAgent 负责汇总所有聚类的深度分析结果，生成包含技术趋势、方法对比、应用领域、研究热点、局限性、建议与展望等六大模块的全局分析报告。

核心实现流程：
```python
async def generate_global_analyse(self, analyse_results: List[DeepAnalyseResult]):
    # 准备所有聚类的分析内容
    cluster_summaries = []
    for result in analyse_results:
        cluster_summaries.append({
            "cluster_id": result.cluster_id,
            "theme": result.theme,
            "keywords": result.keywords,
            "paper_count": result.paper_count,
            "analyse_summary": result.deep_analyse
        })
    
    prompt = f"""
    基于以下多主题聚类分析结果，生成全局分析草稿：
    {json.dumps(cluster_summaries, ensure_ascii=False)}
    
    # 全局分析核心模块要求
    ## 1. 技术趋势总结
    ## 2. 方法对比
    ## 3. 应用领域分析
    ## 4. 研究热点识别
    ## 5. 局限性总结
    ## 6. 建议与展望
    """
    
    # 流式生成全局分析
    async for chunk in self.global_analyse_agent.run_stream(task=prompt):
        if chunk.type == "TextMessage":
            global_analyse = {
                "isSuccess": True,
                "total_clusters": len(analyse_results),
                "total_papers": sum(r.paper_count for r in analyse_results),
                "cluster_themes": [r.theme for r in analyse_results],
                "global_analyse": chunk.content,
                "cluster_summaries": cluster_summaries
            }
            yield global_analyse
```

全局分析模块：
- **技术趋势总结**：明确各主题间的技术交叉点，梳理发展脉络
- **方法对比**：横向对比不同方法的技术优势与适用边界
- **应用领域分析**：按行业/场景维度归类应用案例，标注高潜力领域
- **研究热点识别**：提炼当前关注的技术方向，预测未来1-3年的潜在热点
- **局限性总结**：归纳共性局限性，分析根本原因及影响
- **建议与展望**：提出具体研究建议，展望技术成熟后的应用前景

# writing_agent_node（写作节点）
writing_agent_node 负责根据全局分析结果生成论文报告的总体写作大纲，并拆分并行完成各个部分的写作任务。该节点内部使用 LangGraph 构建工作流，包含两个主要节点：writing_director_node（写作主管节点）和 parallel_writing_node（并行写作节点）。

核心工作流构建：
```python
class WritingWorkflow:
    def build_workflow(self):
        builder = StateGraph(WritingState)
        
        # 添加节点
        builder.add_node("writing_director_node", writing_director_node)
        builder.add_node("parallel_writing_node", parallel_writing_node)
        
        # 设置流程：主管 → 并行写作 → 结束
        builder.set_entry_point("writing_director_node")
        builder.add_edge("writing_director_node", "parallel_writing_node")
        builder.add_edge("parallel_writing_node", END)
        
        return builder.compile()
```

核心实现流程：
```python
async def writing_node(state: State) -> State:
    # 初始化写作状态
    writing_state = WritingState()
    writing_state["state_queue"] = state["state_queue"]
    writing_state["user_request"] = state["value"].user_request
    writing_state["global_analysis"] = state["value"].analyse_results
    writing_state["sections"] = []
    writing_state["writted_sections"] = []
    
    # 执行写作工作流
    workflow = WritingWorkflow()
    writing_state = await workflow.workflow.ainvoke(writing_state)
    
    # 提取写作结果
    state["value"].writted_sections = [
        section.content for section in writing_state["writted_sections"]
    ]
    return {"value": state["value"]}
```

写作流程：
- **写作主管节点**：根据用户需求和全局分析，生成报告大纲并拆分为多个写作子任务
- **并行写作节点**：使用多智能体协作（writing_agent、retrieval_agent、review_agent）并行完成各章节写作，支持检索增强和质量审查

## writing_director_node（写作主管节点）
writing_director_node 负责根据用户需求和全局分析结果，生成报告大纲并将其拆分为多个写作子任务。该节点使用 LLM 分析用户需求，生成结构化的写作大纲，然后解析大纲为可执行的子任务列表。

核心实现流程：
```python
async def writing_director_node(state: WritingState) -> Dict[str, Any]:
    user_request = state["user_request"]
    global_analysis = state["global_analysis"]
    
    prompt = f"""
    用户的需求: {user_request}
    该领域的分析: {global_analysis}
    
    请根据用户提供的需求和关于该领域的分析，生成结构清晰、逻辑连贯的写作子任务。
    """
    
    # 流式生成大纲
    async for chunk in writing_director_agent.run_stream(task=prompt):
        if chunk.type == "TextMessage":
            outline = chunk.content
            break
    
    # 解析大纲为子任务列表
    sections = parse_outline(outline)
    
    return {"sections": sections}
```
关键功能：
- **大纲生成**：基于用户需求和全局分析，生成结构化的报告大纲
- **任务拆分**：将大纲解析为可并行执行的写作子任务
- **流式输出**：实时推送生成进度到前端

## parallel_writing_node（并行写作节点）
parallel_writing_node 负责并行执行所有写作子任务，使用多智能体协作完成各章节的写作。该节点为每个子任务创建一个写作组（包含 writing_agent、retrieval_agent、review_agent），通过异步并发提高写作效率。

核心实现流程：
```python
async def parallel_writing_node(state: WritingState) -> Dict[str, Any]:
    # 准备所有子任务
    subtasks = []
    for i, section in enumerate(state["sections"]):
        subtasks.append({
            "user_request": state["user_request"],
            "global_analyse": state["global_analysis"],
            "section": section,
            "index": i + 1
        })
    
    # 并行执行所有子任务
    tasks = [run_single_subtask(task) for task in subtasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    return state

async def run_single_subtask(task: Dict):
    # 执行单个子任务
    task_prompt = f"""
    请根据以下内容完成写作任务：
    用户的请求是：{task['user_request']}
    当前写作子任务: {task['section']}
    论文全局分析: {task['global_analyse']}
    """
    
    # 创建写作组（writing_agent + retrieval_agent + review_agent）
    task_group = create_writing_group()
    
    # 执行写作流程
    async for chunk in task_group.run_stream(task=task_prompt):
        if chunk.type == "TextMessage" and chunk.source == "writing_agent":
            state["sections"][task["index"]] = chunk.content
```

写作组架构：
```python
def create_writing_group():
    # 创建三个智能体
    writing_agent = writing_agent(state_queue)      # 写作智能体
    retrieval_agent = retrieval_agent(state_queue)    # 检索智能体
    review_agent = review_agent(state_queue)          # 审查智能体
    
    # 使用 SelectorGroupChat 协作
    task_group = SelectorGroupChat(
        [writing_agent, retrieval_agent, review_agent],
        model_client=model_client,
        termination_condition=TextMentionTermination("APPROVE"),
        selector_prompt=selector_prompt
    )
    return task_group
```

协作流程：
- **writing_agent**：负责根据子任务撰写章节内容
- **retrieval_agent**：当写作智能体需要补充资料时，从向量数据库检索相关内容（从两个来源检索内容，1.用户创建的知识库，2.系统在reading_agent_node节点中嵌入的从arxiv中检索到的论文）
- **review_agent**：审查写作内容质量，通过后输出 "APPROVE" 终止该子任务
- **并行执行**：所有子任务并发执行，互不干扰


# report_agent_node（报告生成节点）
report_agent_node 负责汇总所有写作章节，生成完整的调研报告，并以 Markdown 格式输出。该节点使用流式输出，实时将生成进度推送到前端。

核心实现流程：
```python
async def report_node(state: State) -> State:
    sections = state["value"].writted_sections
    sections_text = "\n".join(sections) if sections else "无章节内容提供"
    
    prompt = f"""
    请将以下章节内容组装成完整的调研报告，以Markdown格式输出。
    
    【章节内容】
    {sections_text}
    
    【要求】
    1. 使用Markdown格式排版
    2. 自动补充过渡语句使报告连贯
    3. 保持专业学术风格
    """
    
    # 流式生成报告
    async for chunk in report_agent.run_stream(task=prompt):
        if chunk.type == "TextMessage":
            state["value"].report_markdown = chunk.content
            break
    
    return {"value": state["value"]}
```

报告生成特点：
- **流式输出**：实时推送生成进度到前端
- **自动过渡**：补充过渡语句确保报告连贯性
- **专业风格**：保持学术报告的专业性
- **Markdown格式**：生成结构化的 Markdown 报告


