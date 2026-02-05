# Streamlit RAG 应用部署指南

这是一个基于 LangChain + DashScope + Milvus 的 RAG（检索增强生成）问答系统，已配置为 Streamlit 应用。

## 📋 功能特性

- ✅ 支持 PDF 和 TXT 文档上传
- ✅ 自动构建向量索引（使用 DashScope Embeddings）
- ✅ 基于文档内容的智能问答（使用 DashScope LLM）
- ✅ 向量存储使用 Milvus（支持云端部署）
- ✅ 所有密钥通过 Streamlit Secrets 管理，安全可靠

## 🚀 部署到 Streamlit Cloud

### 1. 准备 GitHub 仓库

1. 将代码推送到 GitHub 仓库
2. 确保以下文件在仓库根目录：
   - `app.py` - 主应用文件
   - `requirements.txt` - Python 依赖

### 2. 在 Streamlit Cloud 部署

1. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
2. 使用 GitHub 账号登录
3. 点击 "New app"
4. 选择你的 GitHub 仓库
5. 设置：
   - **Main file path**: `app.py`
   - **Python version**: 3.10（推荐）

### 3. 配置 Secrets（重要！）

在 Streamlit Cloud 的 **Settings > Secrets** 中添加以下配置：

```toml
DASHSCOPE_API_KEY = "your_dashscope_api_key"
DASHSCOPE_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MILVUS_URI = "https://your-milvus-instance.serverless.gcp-us-west1.cloud.zilliz.com"
MILVUS_USER = "your_milvus_user"
MILVUS_PASSWORD = "your_milvus_password"
```

**获取密钥：**

- **DashScope API Key**: 
  - 访问 https://dashscope.console.aliyun.com
  - 创建 API Key
  - 确保账户有足够余额

- **Milvus 配置**:
  - 访问 https://zilliz.com/cloud
  - 创建免费实例或使用现有实例
  - 获取 URI、用户名和密码

### 4. 部署完成

点击 "Deploy" 后，Streamlit Cloud 会自动：
- 安装依赖
- 运行应用
- 提供公开访问链接

## 🏃 本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（或使用 Streamlit Secrets）：

```bash
DASHSCOPE_API_KEY=your_dashscope_api_key
DASHSCOPE_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
MILVUS_URI=https://your-milvus-instance.serverless.gcp-us-west1.cloud.zilliz.com
MILVUS_USER=your_milvus_user
MILVUS_PASSWORD=your_milvus_password
```

### 3. 运行应用

```bash
streamlit run app.py
```

## 📖 使用说明

1. **首次使用**：
   - 进入「文档管理」标签页
   - 上传 PDF 或 TXT 文档
   - 点击「构建向量索引」
   - 等待索引构建完成

2. **提问**：
   - 进入「问答」标签页
   - 输入问题
   - 调整检索参数（可选）
   - 点击「提交问题」
   - 查看答案和检索到的文档片段

## 🔒 安全注意事项

- ⚠️ **不要**将包含真实密钥的文件提交到 Git
- ✅ 使用 Streamlit Secrets 管理所有敏感信息
- ✅ `.streamlit/secrets.toml.example` 仅作为示例，不要包含真实密钥
- ✅ 确保 `.gitignore` 包含 `.env` 和 `.streamlit/secrets.toml`

## 🐛 故障排除

### 问题：无法连接到 Milvus

- 检查 MILVUS_URI、MILVUS_USER、MILVUS_PASSWORD 是否正确
- 确认 Milvus 实例是否正常运行
- 检查网络连接

### 问题：DashScope API 调用失败

- 检查 DASHSCOPE_API_KEY 是否正确
- 确认账户余额是否充足
- 查看 DashScope 控制台是否有错误信息

### 问题：向量索引构建失败

- 检查文档格式是否正确
- 确认 Milvus 连接正常
- 查看错误日志获取详细信息

## 📝 文件结构

```
.
├── app.py                      # Streamlit 主应用
├── requirements.txt            # Python 依赖
├── .streamlit/
│   └── secrets.toml.example   # Secrets 配置示例
├── README_STREAMLIT.md        # 本文件
└── .gitignore                 # Git 忽略文件（应包含 .env 和 secrets.toml）
```

## 🔗 相关链接

- [Streamlit 文档](https://docs.streamlit.io/)
- [LangChain 文档](https://python.langchain.com/)
- [DashScope 文档](https://help.aliyun.com/zh/model-studio/)
- [Milvus 文档](https://milvus.io/docs)
