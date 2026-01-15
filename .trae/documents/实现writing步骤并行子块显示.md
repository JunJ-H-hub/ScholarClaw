## 实现writing步骤并行子块显示功能

### 修改内容：

#### 1. 数据结构扩展
- 添加`activeSubSteps` ref（Map类型）来追踪多个活跃的子块
- 为writing步骤添加`subSteps`数组属性存储并行子块

#### 2. 模板结构调整
- 在step-card中添加条件渲染的子块区域（仅writing步骤显示）
- 使用grid布局实现多个子块的并行显示
- 每个子块包含：标题、加载动画、思考过程（可展开）、内容区域

#### 3. 处理函数优化
- **handleInitializing**：writing步骤创建包含`subSteps: []`的步骤
- **handleThinking/handleGenerating**：根据动态section_id查找或创建对应子块，更新thinking/content
- **handleComplete/handleError**：根据section_id更新对应子块的完成/错误状态

#### 4. 样式添加
- `.sub-steps-section`：子块容器样式
- `.sub-steps-grid`：网格布局（响应式，2列或3列）
- `.sub-step-card`：子块卡片样式（独立的状态指示、加载动画）
- 子块的thinking和content区域样式

### 技术要点：
- 使用Map以动态section_id为键存储活跃子块引用
- 子块首次出现时自动创建并添加到subSteps数组
- 每个子块独立管理状态（processing、error、completed）
- 保持向后兼容，非writing步骤不受影响