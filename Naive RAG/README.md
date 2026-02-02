# Naive RAG (检索增强生成) 系统

这是一个简单但完整的 RAG (Retrieval Augmented Generation) 系统实现，用于从学术论文中检索信息并使用大语言模型生成答案。

## 系统概述

Naive RAG 系统将文档检索与大语言模型推理相结合，实现基于知识库的智能问答。系统通过以下四个步骤处理学术论文并提供智能问答服务：

```
论文下载 → 文本提取 → 向量化存储 → 查询问答
```

## 文件说明

### Step 1: 获取论文 (`step1_get_papers.ipynb`)
- **功能**: 从 arXiv 下载研究论文
- **主要操作**:
  - 使用 arXiv API 查询特定研究主题的论文
  - 批量下载论文 PDF 文件
  - 将 PDF 保存到本地文件夹
- **依赖库**: `arxiv`
- **输出**: 研究论文的 PDF 文件

### Step 2: 读取数据 (`step2_read_data.ipynb`)
- **功能**: 从 PDF 文件中提取文本内容
- **主要操作**:
  - 解析 PDF 文档
  - 逐页提取文本内容
  - 清理和结构化提取的文本
  - 按文档组织文本数据
- **依赖库**: PDF 处理库（如 PyPDF2 或 pdfplumber）
- **输出**: 结构化的论文文本数据

### Step 3: 构建向量数据库 (`step3_build_vectordb.ipynb`)
- **功能**: 生成文本嵌入并构建向量数据库用于语义搜索
- **主要操作**:
  - 使用 Sentence Transformers 生成文本嵌入向量
  - 初始化 ChromaDB 向量存储
  - 将文档及其嵌入向量添加到数据库
  - 持久化保存向量数据库
- **依赖库**: `chromadb`, `sentence-transformers`
- **输出**: 包含文档嵌入的持久化向量数据库

### Step 4: 查询与回答 (`step4_query_and_answer.ipynb`)
- **功能**: 查询向量数据库并使用大语言模型生成答案
- **主要操作**:
  - 基于相似度搜索从 ChromaDB 检索相关文档
  - 将检索到的上下文发送到 OpenAI API
  - 使用 ChatGPT 生成答案
  - 显示带有来源引用的结果
- **依赖库**: `chromadb`, `openai`
- **输出**: AI 生成的答案及相关文档上下文

## 技术栈

- **数据收集**: arXiv API
- **PDF 处理**: PyPDF2 / pdfplumber
- **文本嵌入**: Sentence Transformers
- **向量数据库**: ChromaDB
- **大语言模型**: OpenAI ChatGPT API
- **开发环境**: Jupyter Notebook / Google Colab

## 使用流程

1. **准备工作**: 安装所需的依赖库
   ```bash
   pip install arxiv chromadb sentence-transformers openai pypdf2
   ```

2. **运行 Step 1**: 从 arXiv 下载感兴趣的研究论文
   - 打开 `step1_get_papers.ipynb`
   - 修改查询参数以获取特定主题的论文
   - 运行 notebook 下载 PDF 文件

3. **运行 Step 2**: 提取论文文本内容
   - 打开 `step2_read_data.ipynb`
   - 运行 notebook 从 PDF 中提取并处理文本

4. **运行 Step 3**: 构建向量数据库
   - 打开 `step3_build_vectordb.ipynb`
   - 运行 notebook 生成嵌入并构建向量数据库

5. **运行 Step 4**: 开始问答
   - 打开 `step4_query_and_answer.ipynb`
   - 配置 OpenAI API 密钥
   - 输入问题，获取基于论文内容的智能答案

## 系统特点

- ✅ **端到端流程**: 从数据收集到智能问答的完整流程
- ✅ **模块化设计**: 每个步骤独立运行，便于调试和修改
- ✅ **语义检索**: 使用向量相似度进行智能文档检索
- ✅ **上下文感知**: LLM 基于检索到的相关文档生成答案
- ✅ **可扩展性**: 易于添加新的数据源或更换模型

## 注意事项

1. **API 密钥**: 使用 OpenAI API 需要有效的 API 密钥
2. **数据存储**: 确保有足够的磁盘空间存储 PDF 文件和向量数据库
3. **网络连接**: 下载论文和调用 API 需要稳定的网络连接
4. **成本**: OpenAI API 调用会产生费用，请注意使用量

## RAG 系统原理

RAG (Retrieval Augmented Generation) 结合了检索系统和生成式 AI 的优势：

1. **检索阶段**: 将用户查询转换为向量，在向量数据库中搜索最相关的文档片段
2. **增强阶段**: 将检索到的文档作为上下文提供给大语言模型
3. **生成阶段**: 大语言模型基于检索到的上下文和用户问题生成准确的答案

这种方法相比直接使用 LLM 的优势：
- 答案更准确，基于实际文档内容
- 可以引用信息来源
- 不受 LLM 训练数据时效性限制
- 减少 AI 幻觉（hallucination）

## 后续改进方向

- [ ] 支持更多文档格式（Word, HTML 等）
- [ ] 实现更复杂的文本分块策略
- [ ] 添加多轮对话支持
- [ ] 优化检索算法（混合检索、重排序等）
- [ ] 添加评估指标和测试集
- [ ] 构建 Web 界面

## 许可证

请参考项目根目录的 LICENSE 文件。
