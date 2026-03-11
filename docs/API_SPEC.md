# CTF Agent Web API 对接文档

## 概述

CTF Agent Web API 提供完整的 RESTful API 和 WebSocket 实时通信接口，用于前后端交互。

**基础信息**:
- Base URL: `http://localhost:5000`
- API 前缀: `/api`
- WebSocket: `ws://localhost:5000`
- 数据格式: JSON
- 字符编码: UTF-8

---

## 1. Agent 管理 API

### 1.1 初始化会话

**接口**: `POST /api/agent/init`

**请求体**:
```json
{}
```

**响应**:
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "会话创建成功"
}
```

### 1.2 设置目标 URL

**接口**: `POST /api/agent/set-target`

**请求体**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "target_url": "http://example.com/challenge"
}
```

**响应**:
```json
{
  "success": true,
  "message": "目标已设置为: http://example.com/challenge"
}
```

### 1.3 执行一步分析

**接口**: `POST /api/agent/step`

**请求体**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_input": "请开始分析目标 URL",
  "auto_mode": false
}
```

**响应**:
```json
{
  "success": true,
  "response": "好的，我将开始分析目标...",
  "state": "INFO_GATHERING",
  "progress": 20,
  "flags": [],
  "phases": ["信息收集"],
  "flag_found": false
}
```

### 1.4 获取会话状态

**接口**: `GET /api/agent/status?session_id=xxx`

**响应**:
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": 1710123456.789,
  "last_activity": 1710123500.123,
  "target_url": "http://example.com/challenge",
  "state": "INFO_GATHERING",
  "progress": 20,
  "flags_found": 0
}
```

### 1.5 获取对话历史

**接口**: `GET /api/agent/history?session_id=xxx`

**响应**:
```json
{
  "success": true,
  "messages": [
    {
      "role": "user",
      "content": "请开始分析"
    },
    {
      "role": "assistant",
      "content": "好的，我将开始..."
    }
  ]
}
```

### 1.6 重置会话

**接口**: `POST /api/agent/reset`

**请求体**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**响应**:
```json
{
  "success": true,
  "session_id": "新的会话ID",
  "message": "会话已重置"
}
```

### 1.7 销毁会话

**接口**: `DELETE /api/agent/destroy`

**请求体**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**响应**:
```json
{
  "success": true,
  "message": "会话已销毁"
}
```

---

## 2. 配置管理 API

### 2.1 获取当前配置

**接口**: `GET /api/config/get`

**响应**:
```json
{
  "success": true,
  "config": {
    "llm": {
      "provider": "openai",
      "api_key": "sk-xxxxxx...xxxx",
      "base_url": "https://api.siliconflow.cn/v1",
      "model": "Pro/zai-org/GLM-5"
    },
    "experts": {
      "ctf": {
        "api_key": "sk-xxxxxx...xxxx",
        "base_url": "https://api.siliconflow.cn/v1",
        "model": "Pro/zai-org/GLM-5"
      },
      "python": {...},
      "security": {...}
    },
    "rag": {
      "embedding_api_key": "sk-xxxxxx...xxxx",
      "embedding_model": "Qwen/Qwen3-Embedding-8B",
      "distance_threshold": 1.5
    },
    "ssh": {
      "host": "192.168.1.100",
      "port": 22,
      "user": "kali",
      "password": "***"
    },
    "advanced": {
      "max_sub_steps": 5,
      "log_level": "INFO"
    }
  }
}
```

### 2.2 获取配置模板

**接口**: `GET /api/config/schema`

**响应**: 返回配置字段的类型定义和默认值

### 2.3 验证配置

**接口**: `POST /api/config/validate`

**请求体**:
```json
{
  "config": {
    "llm": {
      "api_key": "sk-xxx",
      "model": "Pro/zai-org/GLM-5"
    }
  }
}
```

**响应**:
```json
{
  "success": true,
  "valid": true,
  "errors": [],
  "warnings": ["SSH 已配置主机但未配置密码"]
}
```

---

## 3. RAG 知识库 API

### 3.1 查询知识库

**接口**: `POST /api/rag/query`

**请求体**:
```json
{
  "query": "SQL 注入绕过方法",
  "n_results": 5,
  "challenge_type": "Web"
}
```

**响应**:
```json
{
  "success": true,
  "documents": [
    "SQL 注入绕过技巧：1. 使用注释符...",
    "常见 WAF 绕过方法..."
  ],
  "count": 2
}
```

### 3.2 同步知识库

**接口**: `POST /api/rag/sync`

**请求体**:
```json
{
  "folder_path": "data/knowledge_base"
}
```

**响应**:
```json
{
  "success": true,
  "report": {
    "added": 3,
    "deleted": 1,
    "updated": 2,
    "skipped": 5
  },
  "message": "同步完成: 新增 3, 删除 1, 更新 2, 跳过 5"
}
```

### 3.3 获取统计信息

**接口**: `GET /api/rag/stats`

**响应**:
```json
{
  "success": true,
  "count": 150,
  "sources": ["web_sqli_bypass.md", "web_php_unserialize.md"],
  "source_count": 2
}
```

### 3.4 列出文档

**接口**: `GET /api/rag/list?limit=50`

**响应**:
```json
{
  "success": true,
  "items": [
    {
      "id": "doc-id-1",
      "content": "文档内容预览...",
      "metadata": {
        "source": "web_sqli_bypass.md",
        "challenge_type": "Web"
      }
    }
  ],
  "count": 50
}
```

---

## 4. 技能系统 API

### 4.1 列出所有技能

**接口**: `GET /api/skills/list?category=WEB`

**响应**:
```json
{
  "success": true,
  "skills": [
    {
      "id": "sqli_detection",
      "name": "SQL 注入检测",
      "category": "WEB",
      "description": "自动检测 SQL 注入漏洞",
      "difficulty": "medium",
      "prerequisites": ["target_url"],
      "tools_required": ["execute_shell"]
    }
  ],
  "count": 1
}
```

### 4.2 获取技能详情

**接口**: `GET /api/skills/info?skill_id=sqli_detection`

**响应**:
```json
{
  "success": true,
  "skill": {
    "id": "sqli_detection",
    "name": "SQL 注入检测",
    "category": "WEB",
    "description": "自动检测 SQL 注入漏洞",
    "difficulty": "medium",
    "prerequisites": ["target_url"],
    "tools_required": ["execute_shell"]
  }
}
```

### 4.3 执行技能

**接口**: `POST /api/skills/execute`

**请求体**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "skill_id": "sqli_detection",
  "context": {
    "target_url": "http://example.com/login"
  }
}
```

**响应**:
```json
{
  "success": true,
  "result": {
    "success": true,
    "message": "检测完成",
    "data": {},
    "commands": ["sqlmap -u http://example.com/login"],
    "findings": ["发现 SQL 注入漏洞"]
  }
}
```

---

## 5. WebSocket 实时通信

### 5.1 连接

```javascript
const socket = io('http://localhost:5000');

// 加入会话房间
socket.emit('join', {session_id: 'xxx'});

// 监听连接成功
socket.on('connected', (data) => {
  console.log(data.message);
});
```

### 5.2 事件类型

| 事件类型 | 说明 | 数据格式 |
|---------|------|---------|
| `agent_thinking` | Agent 正在思考 | `{message: "正在分析..."}` |
| `tool_call` | 工具调用开始 | `{tool: "execute_python", code: "..."}` |
| `tool_result` | 工具执行结果 | `{output: "执行结果"}` |
| `phase_achieved` | 达成新阶段 | `{phase: "漏洞检测", phases: [...]}` |
| `flag_found` | 发现 Flag | `{flag: "flag{xxx}", flags: [...]}` |
| `error` | 错误信息 | `{message: "错误描述"}` |
| `state_change` | 状态变更 | `{state: "EXPLOITATION", progress: 80}` |

### 5.3 监听事件

```javascript
socket.on('agent_thinking', (data) => {
  console.log('Agent 正在思考:', data.message);
});

socket.on('tool_call', (data) => {
  console.log('工具调用:', data.tool);
  console.log('代码:', data.code);
});

socket.on('tool_result', (data) => {
  console.log('执行结果:', data.output);
});

socket.on('flag_found', (data) => {
  console.log('发现 Flag:', data.flag);
});
```

---

## 6. 错误处理

### 6.1 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": "详细信息（可选）"
  }
}
```

### 6.2 错误码

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|------------|
| `INVALID_PARAMS` | 参数无效 | 400 |
| `SESSION_NOT_FOUND` | 会话不存在 | 404 |
| `AGENT_ERROR` | Agent 执行错误 | 500 |
| `CONFIG_INVALID` | 配置无效 | 400 |
| `RAG_ERROR` | RAG 系统错误 | 500 |
| `SKILL_NOT_FOUND` | 技能不存在 | 404 |

---

## 7. 完整使用流程示例

```javascript
// 1. 初始化会话
const initRes = await fetch('http://localhost:5000/api/agent/init', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({})
});
const {session_id} = await initRes.json();

// 2. 连接 WebSocket
const socket = io('http://localhost:5000');
socket.emit('join', {session_id});

// 3. 监听事件
socket.on('tool_result', (data) => {
  console.log('执行结果:', data.output);
});

// 4. 设置目标
await fetch('http://localhost:5000/api/agent/set-target', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id,
    target_url: 'http://example.com/challenge'
  })
});

// 5. 执行分析
const stepRes = await fetch('http://localhost:5000/api/agent/step', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id,
    user_input: '请开始分析目标 URL',
    auto_mode: false
  })
});
const result = await stepRes.json();
console.log('响应:', result.response);

// 6. 获取状态
const statusRes = await fetch(`http://localhost:5000/api/agent/status?session_id=${session_id}`);
const status = await statusRes.json();
console.log('进度:', status.progress);
```

---

## 8. 注意事项

1. **会话管理**: 会话会在 30 分钟无活动后自动清理
2. **并发限制**: 建议每个用户只维护一个活跃会话
3. **长时间任务**: Agent 执行可能需要几分钟，前端需要显示加载状态
4. **WebSocket 重连**: 网络断开后需要重新连接并 join 房间
5. **API Key 安全**: 配置中的 API Key 已脱敏，不会返回完整值
6. **CORS**: API 已启用 CORS，允许跨域访问

---

## 9. 开发建议

1. 使用 `axios` 或 `fetch` 进行 HTTP 请求
2. 使用 `socket.io-client` 进行 WebSocket 通信
3. 实现请求拦截器统一处理错误
4. 使用状态管理（Redux/Vuex）管理会话状态
5. 实现自动重连机制
6. 添加请求超时处理
7. 显示友好的错误提示
