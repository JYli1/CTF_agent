# CTF Agent 项目技术文档

## 📋 项目概述

**项目名称**: CTF Agent - 智能 CTF 解题助手
**GitHub**: https://github.com/JYli1/CTF_agent
**语言**: Python 3.9+
**架构**: 多专家协作 + RAG 知识增强 + Web UI

### 核心功能
- 🤖 多专家协作解题（战略专家、Python专家、安全专家）
- 📚 RAG 知识库系统（向量检索增强）
- 🌐 双模式：CLI 命令行 + Web UI 界面
- 🔧 技能系统（SQL注入、SSRF、文件上传等）
- 🔗 SSH 远程执行（连接 Kali Linux）
- 🎯 智能检测（漏洞特征、Flag、解题阶段）

---

## 🏗️ 项目架构

### 目录结构
```
CTF_agent/
├── main.py                    # 主入口（支持 --web 参数）
├── sync_rag.py                # 知识库同步工具
├── requirements.txt           # Python 依赖
├── .env.template              # 环境变量模板
├── .env                       # 环境变量（不提交）
│
├── src/                       # 源代码
│   ├── core/                  # 核心模块
│   │   ├── agent.py           # 主协调器 CTFAgent
│   │   ├── llm.py             # LLM 接口封装
│   │   ├── prompts.py         # 提示词定义
│   │   ├── state_machine.py   # 状态机
│   │   ├── phase_tracker.py   # 阶段追踪器
│   │   └── agents/            # 专家实现
│   │       ├── base.py        # 基础专家类
│   │       ├── ctf_strategist.py    # CTF 战略专家
│   │       ├── python_coder.py      # Python 编程专家
│   │       └── security_expert.py   # 安全渗透专家
│   │
│   ├── rag/                   # RAG 系统
│   │   ├── engine.py          # RAG 核心引擎
│   │   ├── chunker.py         # 文本分块器
│   │   └── siliconflow_embedding.py  # 硅基流动 Embedding
│   │
│   ├── tools/                 # 工具执行器
│   │   └── executor.py        # CodeExecutor, SSHExecutor
│   │
│   ├── skills/                # 技能系统
│   │   ├── base.py            # 技能基类
│   │   ├── registry.py        # 技能注册表
│   │   └── web/               # Web 漏洞技能
│   │       ├── sqli.py        # SQL 注入
│   │       ├── ssrf.py        # SSRF
│   │       └── upload.py      # 文件上传
│   │
│   └── utils/                 # 工具函数
│       ├── config.py          # 配置管理
│       ├── reporter.py        # 报告生成
│       ├── flag_detector.py   # Flag 检测
│       └── vuln_detector.py   # 漏洞检测
│
├── webui/                     # Web UI（Flask）
│   ├── app.py                 # Flask 应用主入口
│   ├── session_manager.py     # 会话管理
│   ├── websocket_handler.py   # WebSocket 处理
│   ├── api/                   # RESTful API
│   │   ├── agent.py           # Agent API
│   │   ├── config.py          # 配置 API
│   │   ├── rag.py             # RAG API
│   │   └── skills.py          # 技能 API
│   └── static/                # 前端静态文件
│       ├── index.html         # 主页面
│       ├── style.css          # 样式
│       └── js/
│           ├── app.js         # Vue.js 应用
│           └── api.js         # API 客户端
│
├── data/                      # 数据目录
│   ├── knowledge_base/        # 知识库文档（.md）
│   ├── chroma_db/             # 向量数据库（不提交）
│   └── logs/                  # 日志（不提交）
│
└── docs/                      # 文档
    ├── API_SPEC.md            # API 接口文档
    └── GEMINI_PROMPT.md       # 前端开发指南
```

---

## 🔧 核心模块详解

### 1. CTFAgent (src/core/agent.py)

**主协调器**，负责调度专家和工具执行。

**关键方法**:
```python
class CTFAgent:
    def __init__(self, reporter=None, event_callback=None):
        # 初始化三个专家
        self.strategist = CTFStrategist()
        self.python_coder = PythonCoder()
        self.security_expert = SecurityExpert()

        # 初始化执行器
        self.code_executor = CodeExecutor()
        self.ssh_executor = SSHExecutor()

        # RAG 系统
        self.rag = RAGSystem()

        # 事件回调（用于 WebSocket）
        self.event_callback = event_callback

    def run_step(self, user_input: str) -> str:
        """执行一步分析"""
        # 1. RAG 检索相关知识
        # 2. 战略专家制定计划
        # 3. 分配任务给专家
        # 4. 执行工具调用
        # 5. 检测阶段和 Flag
        # 6. 返回结果

    def set_target(self, url: str):
        """设置目标 URL"""

    def use_skill(self, skill_id: str, context: dict = None):
        """使用技能"""
```

**工作流程**:
1. 用户输入 → RAG 检索 → 战略专家分析
2. 战略专家返回 JSON：`{action: {type, agent, task}, phase_achieved, flag}`
3. 根据 `action.agent` 分配给 Python 专家或安全专家
4. 专家返回工具调用（`execute_python` 或 `execute_shell`）
5. 执行工具 → 检测阶段/Flag → 返回结果

---

### 2. 专家系统 (src/core/agents/)

#### CTFStrategist (战略专家)
- **职责**: 分析题目、制定计划、调度团队
- **输出**: JSON 格式的任务分配
- **提示词**: `src/core/prompts.py` 中的 `CTF_STRATEGIST_PROMPT`

#### PythonCoder (Python 专家)
- **职责**: 编写 Python 脚本、数据处理、加解密
- **工具**: `execute_python`

#### SecurityExpert (安全专家)
- **职责**: 使用渗透工具（nmap、curl、sqlmap 等）
- **工具**: `execute_shell`（本地或 SSH）

---

### 3. RAG 系统 (src/rag/)

#### RAGSystem (engine.py)
```python
class RAGSystem:
    def __init__(self, persist_path: str = None):
        # 强制使用硅基流动 Embedding（不下载本地模型）
        if not Config.EMBEDDING_API_KEY:
            raise ValueError("未配置 EMBEDDING_API_KEY")

        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name="ctf_knowledge_base",
            embedding_function=SiliconFlowEmbeddingFunction(...)
        )

    def add_document(self, content: str, metadata: Dict, file_path: str):
        """添加文档（带文件哈希追踪）"""

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """查询知识库"""

    def sync_folder(self, folder_path: str) -> Dict:
        """同步文件夹（增量更新）"""
        # 1. 扫描文件夹中的 .md 文件
        # 2. 计算文件哈希
        # 3. 对比数据库记录
        # 4. 新增/更新/删除文档
```

**重要**: 必须配置 `EMBEDDING_API_KEY`，否则会报错（不使用默认本地模型）。

---

### 4. 阶段追踪 (src/core/phase_tracker.py)

**CTF 解题阶段**:
- `UNSOLVED` - 未解题
- `FILE_READING` - 在目标网站实现文件读取
- `CODE_EXECUTION` - 在目标服务器实现代码执行
- `COMMAND_EXECUTION` - 在目标服务器实现命令执行

**检测逻辑**:
```python
def _detect_file_reading(self, tool_name, command, result) -> bool:
    # 检测是否在利用文件读取漏洞（LFI/XXE/SSRF）
    # 检测结果中是否有文件内容特征
    # 排除本地操作和错误
```

**战略专家主动报告**:
```json
{
  "phase_achieved": "文件读取"  // 或 "代码执行" 或 "命令执行"
}
```

---

### 5. Web UI (webui/)

#### 技术栈
- **后端**: Flask + Flask-SocketIO
- **前端**: Vue.js 3 (CDN) + Tailwind CSS
- **通信**: RESTful API + WebSocket

#### 核心 API
```python
# Agent API
POST /api/agent/init          # 初始化会话
POST /api/agent/set-target    # 设置目标
POST /api/agent/step          # 执行一步
GET  /api/agent/status        # 获取状态
GET  /api/agent/history       # 获取历史

# Config API
GET  /api/config/get          # 获取配置
POST /api/config/validate     # 验证配置

# RAG API
POST /api/rag/query           # 查询知识库
POST /api/rag/sync            # 同步知识库

# Skills API
GET  /api/skills/list         # 列出技能
POST /api/skills/execute      # 执行技能
```

#### WebSocket 事件
```javascript
// 客户端监听
socket.on('agent_thinking', (data) => {})
socket.on('tool_call', (data) => {})
socket.on('tool_result', (data) => {})
socket.on('phase_achieved', (data) => {})
socket.on('flag_found', (data) => {})
socket.on('state_change', (data) => {})
```

---

## ⚙️ 配置说明

### .env 文件（必需）
```bash
# LLM 配置
LLM_PROVIDER=modelscope
SILICONFLOW_API_KEY=sk-xxx
MODEL_NAME=deepseek-ai/DeepSeek-V3.2

# Embedding 配置（必需！）
EMBEDDING_API_KEY=sk-xxx
EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5

# SSH 配置（可选）
SSH_HOST=192.168.1.100
SSH_USER=kali
SSH_PASSWORD=xxx

# 存储路径
CHROMA_DB_DIR=data/chroma_db
KNOWLEDGE_BASE_DIR=data/knowledge_base
```

---

## 🚀 使用方式

### CLI 模式
```bash
python main.py
```

### Web 模式
```bash
python main.py --web --port 5000
# 访问 http://localhost:5000
```

### 知识库同步
```bash
python sync_rag.py --clear  # 清空后重新同步
python sync_rag.py          # 增量同步
```

---

## 🔑 关键设计决策

### 1. 为什么强制使用 API Embedding？
- 避免下载 79MB 的本地模型
- 网络慢的服务器无法使用
- API 调用更快、更稳定

### 2. 为什么使用文件哈希追踪？
- 增量同步，只更新变化的文件
- 避免重复添加相同内容
- 提高同步效率

### 3. 为什么阶段检测改为主动报告？
- 自动检测不准确（误判本地操作）
- 大模型更理解上下文
- 战略专家在 JSON 中报告 `phase_achieved`

### 4. 为什么前后端分离？
- 前端可以独立开发（交给 Gemini）
- API 可以被其他客户端使用
- WebSocket 实现实时通信

---

## 🐛 常见问题

### 1. ChromaDB 下载模型很慢
**原因**: 未配置 `EMBEDDING_API_KEY`
**解决**: 在 `.env` 中配置硅基流动 API Key

### 2. SSH 连接失败
**原因**: SSH 配置错误或防火墙
**解决**: 检查 `SSH_HOST`、`SSH_USER`、`SSH_PASSWORD`

### 3. Web UI 无法访问
**原因**: 端口被占用或防火墙
**解决**: 更换端口 `python main.py --web --port 8080`

### 4. 知识库同步失败
**原因**: 缺少 Embedding API Key
**解决**: 配置 `.env` 中的 `EMBEDDING_API_KEY`

---

## 📝 开发指南

### 添加新技能
1. 在 `src/skills/web/` 创建新文件
2. 继承 `BaseSkill` 类
3. 实现 `execute()` 方法
4. 使用 `@skill()` 装饰器注册

### 修改提示词
- 编辑 `src/core/prompts.py`
- 重启程序生效

### 添加新 API
1. 在 `webui/api/` 创建新文件
2. 创建 Blueprint
3. 在 `webui/app.py` 中注册

### 修改前端
- 编辑 `webui/static/` 下的文件
- 刷新浏览器即可（无需构建）

---

## 📚 重要文件清单

### 必读文件
- `main.py` - 主入口
- `src/core/agent.py` - 核心逻辑
- `src/core/prompts.py` - 提示词
- `src/rag/engine.py` - RAG 系统
- `webui/app.py` - Web 服务器

### 配置文件
- `.env.template` - 环境变量模板
- `requirements.txt` - Python 依赖
- `.gitignore` - Git 忽略规则

### 文档
- `README.md` - 用户文档
- `docs/API_SPEC.md` - API 文档
- `docs/GEMINI_PROMPT.md` - 前端开发指南

---

## 🔄 Git 工作流

### 提交规范
```bash
feat: 新功能
fix: 修复 bug
docs: 文档更新
chore: 构建/工具更新
refactor: 重构
```

### 忽略规则
- `.env` - 环境变量（敏感信息）
- `data/chroma_db/*` - 向量数据库（太大）
- `data/logs/*` - 日志文件
- `venv/` - 虚拟环境
- `__pycache__/` - Python 缓存

---

## 🎯 快速上手检查清单

- [ ] 克隆项目
- [ ] 创建虚拟环境
- [ ] 安装依赖 `pip install -r requirements.txt`
- [ ] 复制 `.env.template` 为 `.env`
- [ ] 配置 API Key（LLM + Embedding）
- [ ] 运行 `python sync_rag.py --clear`
- [ ] 启动 `python main.py` 或 `python main.py --web`

---

## 📞 联系方式

- **GitHub**: https://github.com/JYli1/CTF_agent
- **Issues**: https://github.com/JYli1/CTF_agent/issues

---

**最后更新**: 2026-03-12
**版本**: v2.0.0
