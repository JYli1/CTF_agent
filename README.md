# CTF Agent - 智能 CTF 解题助手

<div align="center">

**基于大语言模型的 CTF 自动化解题系统**

多专家协作 · RAG 知识增强 · Web UI · 智能解题

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用指南](#使用指南) • [配置说明](#配置说明)

</div>

---

## 📖 项目简介

CTF Agent 是一个智能的 CTF（Capture The Flag）解题助手，采用多专家协作架构，集成 RAG 知识库和技能系统，支持命令行和 Web 界面两种使用方式。

### 核心特性

- 🤖 **多专家协作** - CTF 战略专家、Python 编程专家、安全渗透专家分工协作
- 📚 **RAG 知识增强** - 内置知识库检索系统，支持自动学习和经验积累
- 🌐 **双模式支持** - 命令行模式（CLI）和 Web 界面（Web UI）
- 🔧 **技能系统** - 预定义的 SQL 注入、SSRF、文件上传等常见漏洞检测技能
- 🔗 **SSH 集成** - 支持连接远程 Kali Linux，使用专业渗透工具
- 🎯 **智能检测** - 自动检测漏洞特征、Flag 格式、解题阶段
- 🇨🇳 **中文优化** - 全中文交互界面，友好的使用体验

---

## 🚀 快速开始

### 系统要求

- **Python**: 3.9 或更高版本
- **操作系统**: Windows / Linux / macOS
- **网络**: 需要访问 LLM API（如 OpenAI、通义千问等）

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/JYli1/CTF_agent.git
cd CTF_agent
```

#### 2. 创建虚拟环境

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

复制模板文件并编辑：

```bash
cp .env.template .env
```

编辑 `.env` 文件，填入你的 API Key：

```ini
# 必填：LLM API 配置
DASHSCOPE_API_KEY=sk-你的API密钥
MODEL_NAME=deepseek-ai/DeepSeek-V3.2

# 可选：SSH 配置（用于远程工具）
SSH_HOST=192.168.1.100
SSH_USER=kali
SSH_PASSWORD=你的密码
```

> 💡 **提示**: 如果没有 API Key，可以在 硅基流动（等） 注册获取
   
#### 5. 初始化知识库

```bash
python sync_rag.py --clear
```

#### 6. 启动程序

**Web 模式（推荐）:**
```bash
python main.py --web --port 5000
```
然后打开浏览器访问 `http://localhost:5000`

**命令行模式:**
```bash
python main.py
```

---

## 💻 使用指南

### Web 界面使用

1. **启动 Web 服务器**
   ```bash
   python main.py --web
   ```

2. **打开浏览器**
   访问 `http://localhost:5000`

3. **设置目标**
   - 在 "TARGET_URL" 输入框输入题目 URL
   - 点击 "SET TARGET" 按钮

4. **开始分析**
   - 在底部输入框输入指令，如 "请开始分析目标 URL"
   - 点击 "SEND" 发送
   - 实时查看执行过程和结果

5. **查看配置**
   - 点击右上角 "CONFIG" 按钮查看当前配置
   - 可以查看模型、API Key 等信息

### 命令行使用

1. **启动程序**
   ```bash
   python main.py
   ```

2. **选择模式**
   - 选项 1: 自动模式（全程无需干预）
   - 选项 2: 交互模式（每步需要确认）

3. **输入目标**
   - 输入题目 URL 或直接回车跳过

4. **开始解题**
   - 自动模式：Agent 会自动分析直到找到 Flag
   - 交互模式：每步输入指令，Agent 执行后等待下一步指令

5. **查看结果**
   - Flag 会自动高亮显示
   - 会话结束后可选择保存到知识库

### 知识库管理

**同步知识库**（推荐方式）:
```bash
python sync_rag.py
```

**清空并重新同步**:
```bash
python sync_rag.py --clear
```

**添加新知识**:
1. 在 `data/knowledge_base/` 目录下添加 `.md` 文件
2. 运行 `python sync_rag.py` 同步

---

## ⚙️ 配置说明

### 环境变量配置 (`.env`)

#### 必需配置

```ini
# LLM API 配置
DASHSCOPE_API_KEY=sk-你的密钥        # 通义千问 API Key
MODEL_NAME=deepseek-ai/DeepSeek-V3.2  # 模型名称
```

#### 可选配置

**专家专属模型**（可为不同专家配置不同模型）:
```ini
# CTF 战略专家
CTF_MODEL=deepseek-reasoner

# Python 编程专家
PYTHON_MODEL=gpt-4o

# 安全渗透专家
SECURITY_MODEL=claude-3-5-sonnet
```

**SSH 远程连接**（用于使用 Kali 工具）:
```ini
SSH_HOST=192.168.1.100
SSH_PORT=22
SSH_USER=kali
SSH_PASSWORD=你的密码
# 或使用密钥
SSH_KEY_PATH=/path/to/your/key
```

**RAG 配置**:
```ini
EMBEDDING_API_KEY=sk-你的密钥
EMBEDDING_MODEL=Qwen/Qwen3-Embedding-8B
RAG_DISTANCE_THRESHOLD=1.5
```

### 配置验证

运行以下命令检查配置是否正确：

```bash
python -c "from src.utils.config import Config; Config.validate()"
```

---

## 📁 项目结构

```
CTF_agent/
├── data/
│   ├── chroma_db/              # 向量数据库（自动生成）
│   └── knowledge_base/         # 知识库文档（.md 格式）
│       ├── web_sqli_bypass.md
│       ├── web_php_unserialize.md
│       └── ...
├── src/
│   ├── core/
│   │   ├── agents/             # 专家 Agent
│   │   │   ├── ctf_strategist.py
│   │   │   ├── python_coder.py
│   │   │   └── security_expert.py
│   │   ├── agent.py            # 主协调器
│   │   ├── llm.py              # LLM 接口
│   │   ├── prompts.py          # 提示词
│   │   └── phase_tracker.py    # 阶段追踪
│   ├── rag/
│   │   ├── engine.py           # RAG 引擎
│   │   └── chunker.py          # 文本分块
│   ├── tools/
│   │   └── executor.py         # 代码/命令执行器
│   ├── skills/                 # 技能系统
│   │   ├── web/                # Web 漏洞技能
│   │   └── registry.py         # 技能注册表
│   └── utils/
│       ├── config.py           # 配置管理
│       ├── reporter.py         # 报告生成
│       └── flag_detector.py    # Flag 检测
├── webui/                      # Web UI
│   ├── app.py                  # Flask 应用
│   ├── api/                    # API 路由
│   └── static/                 # 前端文件
├── docs/
│   ├── API_SPEC.md             # API 文档
│   └── GEMINI_PROMPT.md        # 前端开发指南
├── main.py                     # 主入口
├── sync_rag.py                 # 知识库同步工具
├── requirements.txt            # 依赖列表
├── .env.template               # 配置模板
└── README.md                   # 本文件
```

---

## 🎯 使用示例

### 示例 1: Web SQL 注入题目

```
用户: 请分析这个 URL: http://example.com/login.php?id=1

Agent:
[战略专家] 正在分析目标...
[安全专家] 使用 curl 获取源码...
[战略专家] 发现可能存在 SQL 注入，使用技能检测...
[技能: web_sqli] 检测到 SQL 注入漏洞！
[Python专家] 编写盲注脚本提取数据...
[阶段突破] 文件读取
[发现 Flag] flag{sql_injection_master}
```

### 示例 2: PHP 反序列化题目

```
用户: 分析这段 PHP 代码

Agent:
[战略专家] 收到 PHP 源码，交给 Python 专家分析...
[Python专家] 发现 unserialize() 函数，存在反序列化漏洞
[战略专家] 构造 POP 链...
[Python专家] 生成 payload 并发送...
[阶段突破] 代码执行
[发现 Flag] flag{php_unserialize_pwn}
```

---

## 🔧 高级功能

### 技能系统

Agent 内置了常见漏洞的检测技能：

- `web_sqli` - SQL 注入检测与利用
- `web_ssrf` - SSRF 检测与利用
- `web_php_analysis` - PHP 源码分析
- `web_upload` - 文件上传漏洞检测

### 阶段追踪

系统会自动追踪解题进度：

- **文件读取** - 成功读取目标服务器文件
- **代码执行** - 成功在目标服务器执行代码
- **命令执行** - 成功在目标服务器执行系统命令

### 自动学习

解题完成后，可以将经验保存到知识库：

```bash
# 会话结束时选择 "y" 保存
是否将本次会话总结并存入知识库？(y/n): y
```

---

## 🐛 常见问题

### Q: 提示 "No module named 'chromadb'"

**A**: 请确保已激活虚拟环境并安装了依赖：
```bash
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Q: Web 界面无法访问

**A**: 检查端口是否被占用，尝试更换端口：
```bash
python main.py --web --port 8080
```

### Q: SSH 连接失败

**A**: 检查 `.env` 中的 SSH 配置是否正确，确保：
- SSH_HOST 可以 ping 通
- SSH_USER 和 SSH_PASSWORD 正确
- 防火墙允许 SSH 连接

### Q: API 调用失败

**A**: 检查：
- API Key 是否正确
- 网络是否可以访问 API 服务
- API 额度是否充足

---

## 📝 更新日志

### v2.0.0 (2026-03-11)
- ✨ 新增 Web UI 界面
- ✨ 新增知识库文件夹同步功能
- ✨ 改进阶段检测逻辑
- 🐛 修复 Windows 编码问题
- 📚 完善文档和使用指南

### v1.0.0 (2026-01-24)
- 🎉 初始版本发布
- ✨ 多专家协作架构
- ✨ RAG 知识库系统
- ✨ SSH 远程执行支持

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [OpenAI](https://openai.com/) - GPT 模型
- [Anthropic](https://anthropic.com/) - Claude 模型
- [DeepSeek](https://deepseek.com/) - DeepSeek 模型
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [Flask](https://flask.palletsprojects.com/) - Web 框架

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

Made with ❤️ by CTF Enthusiasts

</div>
