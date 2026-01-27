# CTF Agent 项目计划

## 核心架构 (Python原生实现)
为了满足你的学习需求，我已经移除了复杂的 LangChain 框架，全部采用 Python 原生实现，让你能清晰看到 Agent 的每一个工作细节。

### 1. 基础模块 (已完成)
- **Chunking (切分器)**: `src/rag/chunker.py`
    - 针对 CTF Writeup 特性，实现了 `SimpleChunker`。
    - 优先按 Markdown 标题 (`#`, `##`) 切分，其次按代码块 (` ``` `) 切分。
    - 保证代码块的完整性，不会把一段 Python 脚本切成两半。
- **Vector DB (向量库)**: `src/rag/engine.py`
    - 封装 `chromadb` 原生接口。
    - 自动使用 Chroma 内置的轻量级 Embedding 模型 (运行在本地，无需 API Key)。
    - 提供 `add_document` (存) 和 `query` (取) 接口。

### 2. LLM 与 Agent (已完成)
- **LLM 封装**: `src/core/llm.py`
    - 直接对接 **ModelScope (DashScope)** API。
    - 默认使用 `qwen-turbo` (通义千问)，通常有免费额度。
- **Agent 核心**: `src/core/agent.py`
    - 实现了 "思考 (Thinking) -> 检索 (Retrieval) -> 计划 (Planning)" 的循环。
    - 能够解析 LLM 输出中的 Python 代码块。

### 3. 工具与执行 (已完成)
- **代码执行器**: `src/tools/executor.py`
    - 一个安全的 Python 解释器环境。
    - 预置了 `requests`, `bs4`, `base64` 等常用 CTF 库。
    - 捕获 `stdout` 输出，将执行结果反馈给 Agent。
- **报告生成**: `src/utils/reporter.py`
    - 会话结束后，自动将所有思考过程和结果保存为 Markdown 文件到 `data/logs/`。

### 4. 入口 (已完成)
- **CLI**: `main.py`
    - 启动后输入 Target URL。
    - 交互式对话。
    - 自动检测 Agent 生成的代码并执行，然后将结果喂回给 Agent 进行下一步判断。

---

## 下一步行动 (需要你配合)
1.  **安装依赖**: 运行 `pip install -r requirements.txt`。
2.  **配置 API Key**:
    - 复制 `.env.example` 为 `.env`。
    - 填入你的 ModelScope API Key (`DASHSCOPE_API_KEY`).
3.  **运行测试**: 运行 `python main.py` 开始尝试。

你现在可以去获取 API Key 并配置环境了，代码已经就绪！