# CTF Agent

这是一个基于 LLM 的 CTF 辅助 Agent，集成了 RAG（检索增强生成）和 SSH 远程执行功能。它可以协助分析代码、执行 Python 脚本，并通过 SSH 连接到 Kali Linux 执行渗透测试工具命令。

## 功能特性

- **双模式执行**: 自动识别并分流执行本地 Python 代码和远程 SSH Shell 命令。
- **RAG 知识库**: 内置知识库检索系统，支持加载 Markdown 格式的 CTF 技巧和 Writeup，辅助模型生成更准确的方案。
- **SSH 集成**: 支持通过 SSH 连接到远程 Linux (如 Kali) 环境，允许 Agent 调用 `nmap`, `netcat`, `metasploit` 等原生安全工具。
- **中文优化**: 核心交互流程、错误处理及异常提示信息已全面本地化，提供更友好的使用体验。

## 安装指南

### 1. 克隆项目

```bash
git clone <repository_url>
cd ctf_agent
```

### 2. 环境准备

建议使用 Python 3.9+。

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate

# 激活虚拟环境 (Linux/macOS)
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

> **注意**：由于 `.env` 文件包含敏感配置信息（如 API Key），本项目**未将其上传**至仓库。您需要手动在项目根目录下创建该文件，并参考以下模板填入您的配置：

在项目根目录下创建一个 `.env` 文件，参考以下模板进行配置：

```ini
# --- LLM 模型配置 ---
# 提供商选择: "modelscope" (默认) 或 "openai"
LLM_PROVIDER=modelscope

# DashScope (通义千问) API Key
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# OpenAI API Key (如果使用 OpenAI)
# OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
# OPENAI_BASE_URL=https://api.openai.com/v1

# 模型名称指定
MODEL_NAME=deepseek-ai/DeepSeek-V3.2

# --- 存储路径配置 ---
CHROMA_DB_DIR=data/chroma_db
KNOWLEDGE_BASE_DIR=data/knowledge_base

# --- SSH 远程连接配置 (Kali Linux) ---
SSH_HOST=192.168.1.100
SSH_PORT=22
SSH_USER=kali
SSH_PASSWORD=your_password
# 可选: 使用密钥登录
# SSH_KEY_PATH=C:/Users/You/.ssh/id_rsa
```

## 使用方法

### 1. 初始化知识库

首次使用或添加新文档后，需运行以下命令将 `data/knowledge_base` 目录下的文档导入向量数据库：

```bash
python ingest_docs.py
```

### 2. 启动 Agent

```bash
python main.py
```

启动后，您可以直接与 Agent 对话。例如：
- "帮我写一个 Python 脚本来爆破这个 zip 文件"
- "连接 SSH 扫描目标主机 192.168.1.5 的开放端口"

## 目录结构

```
ctf_agent/
├── data/
│   ├── chroma_db/       # 向量数据库存储
│   └── knowledge_base/  # RAG 知识库文档 (.md)
├── src/
│   ├── core/            # 核心逻辑 (Agent, LLM)
│   ├── rag/             # 检索增强生成模块
│   ├── tools/           # 执行工具 (PythonExecutor, SSHExecutor)
│   └── utils/           # 配置与辅助函数
├── ingest_docs.py       # 知识库导入脚本
├── main.py              # 主程序入口
└── requirements.txt     # 项目依赖
```
