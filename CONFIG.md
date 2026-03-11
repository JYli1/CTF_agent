# CTF Agent 配置指南

## 快速开始

### 方法 1: 使用配置向导（推荐）

```bash
python setup_config.py
```

配置向导会引导你完成：
1. 输入 API Key
2. 选择模型配置方案
3. 配置 SSH（可选）
4. 自动生成 .env 文件
5. 验证配置

### 方法 2: 手动配置

1. 复制模板文件：
```bash
cp .env.template .env
```

2. 编辑 `.env` 文件，填入你的配置：
```bash
# 最少只需要修改这一项
SILICONFLOW_API_KEY=your-api-key-here
```

3. 验证配置：
```bash
python src/utils/config.py
```

## 配置说明

### 必需配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `SILICONFLOW_API_KEY` | 硅基流动 API Key | `sk-xxx` |

### 可选配置

#### 1. 专家模型配置

如果不配置，所有专家将使用默认模型 `Pro/zai-org/GLM-5`

```env
CTF_MODEL=Pro/zai-org/GLM-5          # CTF 战略专家
PYTHON_MODEL=Pro/moonshotai/Kimi-K2.5  # Python 编程专家
SECURITY_MODEL=Pro/zai-org/GLM-5     # 安全渗透专家
```

**推荐模型组合：**

| 方案 | CTF 专家 | Python 专家 | 安全专家 | 特点 |
|------|----------|-------------|----------|------|
| 均衡 | GLM-5 | Kimi-K2.5 | GLM-5 | 性价比高 |
| 高性能 | Claude-Sonnet-4.5 | Claude-Sonnet-4.5 | Claude-Sonnet-4.5 | 效果最好 |
| 经济 | DeepSeek-V3.2 | DeepSeek-V3.2 | DeepSeek-V3.2 | 成本最低 |

#### 2. Embedding 模型配置

```env
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5  # 中文优化（推荐）
# EMBEDDING_MODEL=BAAI/bge-m3           # 多语言
# EMBEDDING_MODEL=BAAI/bge-large-en-v1.5  # 英文优化
```

**注意：** 切换 Embedding 模型后需要运行迁移脚本：
```bash
python migrate_embedding.py
```

#### 3. SSH 配置（远程 Kali）

```env
SSH_HOST=192.168.1.100
SSH_PORT=22
SSH_USER=kali
SSH_PASSWORD=kali
```

如果不配置 SSH，安全专家将无法使用 nmap、sqlmap 等工具。

## 配置验证

### 1. 查看当前配置

```bash
python src/utils/config.py
```

输出示例：
```
============================================================
CTF Agent 当前配置
============================================================

[LLM 配置]
  提供商: openai
  Base URL: https://api.siliconflow.cn/v1
  默认模型: Pro/zai-org/GLM-5

[专家配置]
  CTF 战略专家: Pro/zai-org/GLM-5
  Python 专家: Pro/moonshotai/Kimi-K2.5
  安全专家: Pro/zai-org/GLM-5

[RAG 配置]
  Embedding 模型: BAAI/bge-large-zh-v1.5
  知识库路径: data/chroma_db

[SSH 配置]
  主机: 192.168.75.128
  用户: kali

[API Key 状态]
  硅基流动: sk-lqezhku...umie
  CTF 专家: sk-lqezhku...umie
  Python 专家: sk-lqezhku...umie
  安全专家: sk-lqezhku...umie
  Embedding: sk-lqezhku...umie

============================================================

[成功] 配置验证通过
```

### 2. 测试 LLM 连接

```bash
python test_llm.py
```

### 3. 测试 Embedding

```bash
python test_embedding.py
```

### 4. 测试 RAG 检索

```bash
python test_retrieval.py
```

## 高级配置

在 `.env` 文件中添加：

```env
# Agent 行为配置
MAX_SUB_STEPS=5                # 最大子任务步骤数
RAG_DISTANCE_THRESHOLD=1.5     # RAG 检索相关度阈值

# 日志配置
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/ctf_agent.log    # 日志文件路径
```

## 常见问题

### Q1: 如何获取硅基流动 API Key？

访问 [https://siliconflow.cn](https://siliconflow.cn)，注册并在控制台获取 API Key。

### Q2: 可以使用 OpenAI 官方 API 吗？

可以，修改配置：
```env
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Q3: 如何切换 Embedding 模型？

1. 修改 `.env` 中的 `EMBEDDING_MODEL`
2. 运行迁移脚本：`python migrate_embedding.py`

### Q4: SSH 连接失败怎么办？

检查：
1. SSH 主机是否可达：`ping <SSH_HOST>`
2. SSH 端口是否正确：`telnet <SSH_HOST> 22`
3. 用户名密码是否正确

### Q5: 如何备份配置？

```bash
cp .env .env.backup
```

## 配置文件结构

```
.env                    # 当前配置（不要提交到 Git）
.env.template           # 配置模板
.env.backup             # 配置备份（setup_config.py 自动生成）
src/utils/config.py     # 配置类
setup_config.py         # 配置向导
```

## 下一步

配置完成后：

1. **导入知识库**
   ```bash
   python import_knowledge.py
   ```

2. **启动 Agent**
   ```bash
   python main.py
   ```

3. **查看使用文档**
   ```bash
   cat README.md
   ```
