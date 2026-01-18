# 前端功能模块开发计划

## 一、项目依赖安装

1. 安装 `vue-router` - 用于页面路由管理
2. 安装 `axios` - 用于HTTP请求封装

## 二、项目结构调整

1. 创建 `src/router/index.js` - 路由配置文件
2. 创建 `src/api/knowledge.js` - 知识库相关API封装
3. 创建 `src/components/` 目录 - 存放组件
4. 创建 `src/views/` 目录 - 存放页面视图
5. 更新 `src/main.js` - 集成路由

## 三、API封装层开发 (`src/api/knowledge.js`)

封装以下接口：

* `getDatabases()` - 获取所有知识库

* `createDatabase(data)` - 创建知识库

* `deleteDatabase(dbId)` - 删除知识库

* `selectDatabase(dbId)` - 选择知识库

* `getDatabaseInfo(dbId)` - 获取知识库详情

* `uploadFile(file, dbId)` - 上传文件

* `addDocuments(dbId, items, params)` - 添加文档到知识库

* `queryDatabase(dbId, query, meta)` - 查询知识库

* `getSupportedTypes()` - 获取支持的文件类型

## 四、RAG知识库管理界面开发

### 4.1 创建 `src/views/KnowledgeBase.vue` 页面

包含以下功能模块：

* **知识库列表展示**：卡片式布局展示所有知识库

* **创建知识库**：模态框表单（名称、描述）

* **删除知识库**：带确认对话框

* **选择知识库**：点击卡片选择当前知识库

* **文件上传**：拖拽上传区域，支持多文件，显示上传进度

* **知识库查询测试**：查询输入框 + 结果展示区域

### 4.2 创建组件

* `src/components/DatabaseCard.vue` - 知识库卡片组件

* `src/components/CreateDatabaseModal.vue` - 创建知识库模态框

* `src/components/FileUpload.vue` - 文件上传组件

* `src/components/QueryTest.vue` - 查询测试组件

## 五、智能调研报告生成功能增强

### 5.1 修改 `src/App.vue`

* 在输入区域添加"选择知识库"按钮

* 添加知识库选择模态框

* 添加当前选中知识库显示

### 5.2 创建 `src/components/SelectKnowledgeModal.vue`

* 展示所有可用知识库列表

* 支持选择和取消选择（仅支持同时选择一个知识库）

* 显示当前已选中的知识库

## 六、样式与交互优化

* 统一的设计风格（与现有App.vue保持一致）

* 加载状态提示（骨架屏、加载动画）

* 错误处理与友好提示

* 响应式布局适配

## 七、路由配置

* `/` - 主页（调研报告生成）

* `/knowledge` - 知识库管理页面

## 八、更新 vite.config.js

* 添加 `/knowledge` 路径的代理配置

