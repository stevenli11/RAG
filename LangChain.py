import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_milvus import Milvus
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END

# 加载环境变量
load_dotenv()

key = os.getenv("DASHSCOPE_API_KEY")
base_url = os.getenv("DASHSCOPE_API_BASE")

# 初始化 LLM
graph_llm = ChatOpenAI(temperature=0, model_name="qwen-plus-2025-12-01", api_key=key, base_url=base_url)
llm = ChatOpenAI(temperature=0, model_name="qwen-plus", api_key=key, base_url=base_url)

# 3.4 创建传统 RAG Agent

# Step 1: 加载文档并分割
with open('../doc/company.txt', 'r', encoding="utf-8") as file:
    content = file.read()

documents = [Document(page_content=content)]

# Step 2: 文本分割
chunk_size = 250
chunk_overlap = 30
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap
)

splits = text_splitter.split_documents(documents)

# Step 3: 初始化 Embeddings
embeddings = DashScopeEmbeddings(
    model="text-embedding-v4",
    dashscope_api_key=key
)

# Step 4: 构建向量索引并存储到 Milvus
vectorstore = Milvus.from_documents(
    documents=splits,
    collection_name="company_milvus",
    embedding=embeddings,
    connection_args={
        "uri": "https://xxxxxxxxxxxxxxx.serverless.gcp-us-west1.cloud.zilliz.com",
        "user": "xxxxxxxxx",  # 替换为自己的
        "password": "xxxxxx",
    }
)

# Step 5: 创建 RAG Chain
prompt = PromptTemplate(
    template="""You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. 
    Use three sentences maximum and keep the answer concise:
    Question: {question} 
    Context: {context} 
    Answer: 
    """,
    input_variables=["question", "context"],
)

rag_chain = prompt | graph_llm | StrOutputParser()

# Step 6: 测试 RAG Chain
question = "我的知识库中都有哪些公司信息"
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
docs = retriever.invoke(question)
generation = rag_chain.invoke({"context": docs, "question": question})
print(f"生成的答案: {generation}")

# Step 7: 定义 AgentState
class AgentState(MessagesState):
    next: str

# Step 8: 创建传统 RAG 的 Agent 节点
def vec_kg(state: AgentState):
    messages = state["messages"][-1]
    question = messages.content
    
    prompt = PromptTemplate(
        template="""You are an assistant for question-answering tasks. 
        Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. 
        Use three sentences maximum and keep the answer concise:
        Question: {question} 
        Context: {context} 
        Answer: 
        """,
        input_variables=["question", "context"],
    )

    # 构建传统的RAG Chain
    rag_chain = prompt | graph_llm | StrOutputParser()
   
    # 构建检索器
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
    
    # 执行检索
    docs = retriever.invoke(question)
    generation = rag_chain.invoke({"context": docs, "question": question})
    
    final_response = [HumanMessage(content=generation, name="vec_kg")]
    
    return {"messages": final_response}

# Step 9: 测试 vec_kg 节点
if __name__ == "__main__":
    test_state = AgentState(
        messages=[HumanMessage(content="我的知识库中都有哪些公司信息")]
    )
    result = vec_kg(test_state)
    print(f"RAG Agent 响应: {result}")
