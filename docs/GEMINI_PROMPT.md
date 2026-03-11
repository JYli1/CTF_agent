# CTF Agent Web UI 前端开发提示词

## 项目概述

你需要为 CTF Agent（一个自动化 CTF 解题系统）开发 Web 前端界面。后端已经完成，提供了完整的 RESTful API 和 WebSocket 实时通信接口。

**项目特点**:
- 多专家协作架构（CTF战略专家、Python编程专家、安全渗透专家）
- RAG 知识库增强
- 实时执行过程展示
- 配置管理

---

## 技术栈要求

### 必需
- **前端框架**: React 或 Vue.js（你选择）
- **UI 库**: Ant Design（React）或 Element Plus（Vue）
- **WebSocket**: socket.io-client
- **HTTP 客户端**: axios
- **状态管理**: Redux（React）或 Vuex（Vue）

### 部署方式
- **重要**: 使用 CDN 方式引入库，不需要 npm 构建
- 所有文件放在 `webui/static/` 目录
- 直接由 Flask 提供服务

---

## 页面设计

### 1. 主界面布局

```
┌─────────────────────────────────────────────────────────┐
│  CTF Agent - 自动解题系统                    [配置] [帮助] │
├──────────────────┬──────────────────────────────────────┤
│  会话信息         │  执行过程（实时滚动）                  │
│  ─────────────   │  ─────────────────────────────────   │
│  目标: xxx.com   │  [2024-03-11 10:00:00]               │
│  状态: 分析中    │  [战略专家] 正在分析目标...           │
│  进度: ████░ 40% │                                      │
│  阶段: 漏洞检测  │  [2024-03-11 10:00:05]               │
│                  │  [Python专家] 执行代码:              │
│  已发现 Flag: 0  │  ```python                           │
│                  │  import requests                     │
│  [重置会话]      │  response = requests.get(...)        │
│  [导出报告]      │  ```                                 │
│                  │                                      │
│                  │  [2024-03-11 10:00:10]               │
│                  │  [执行结果] 200 OK                   │
│                  │  响应内容: ...                       │
│                  │                                      │
│                  │  [2024-03-11 10:00:15]               │
│                  │  [漏洞检测] 发现 SQL 注入漏洞 ⚠️      │
│                  │                                      │
├──────────────────┴──────────────────────────────────────┤
│  对话框                                                  │
│  ─────────────────────────────────────────────────────  │
│  [用户] 请开始分析目标 URL                               │
│  [战略专家] 好的，我将开始全面分析...                    │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 输入指令...                                         │ │
│  └────────────────────────────────────────────────────┘ │
│  [发送] [自动模式: ⚪ OFF]                               │
└─────────────────────────────────────────────────────────┘
```

### 2. 配置页面

```
┌─────────────────────────────────────────┐
│  配置管理                    [保存] [取消] │
├─────────────────────────────────────────┤
│  📡 LLM 配置                             │
│  ├─ 提供商: [OpenAI ▼]                  │
│  ├─ API Key: [sk-xxx...] [👁️ 显示]      │
│  ├─ Base URL: [https://...]             │
│  └─ 模型: [Pro/zai-org/GLM-5]           │
│                                          │
│  👥 专家配置                             │
│  ├─ CTF 战略专家                         │
│  │   ├─ API Key: [继承全局 ▼]           │
│  │   └─ 模型: [Pro/zai-org/GLM-5]       │
│  ├─ Python 编程专家 ...                 │
│  └─ 安全渗透专家 ...                     │
│                                          │
│  📚 RAG 配置                             │
│  ├─ Embedding API Key: [...]            │
│  ├─ Embedding 模型: [Qwen/...]          │
│  └─ 距离阈值: [1.5] ━━━━━━━━━━━━━━━━━   │
│                                          │
│  🔐 SSH 配置                             │
│  ├─ 主机: [192.168.1.100]               │
│  ├─ 端口: [22]                          │
│  ├─ 用户: [kali]                        │
│  └─ 密码: [***] [👁️ 显示]               │
│                                          │
│  ⚙️ 高级配置                             │
│  ├─ 最大子步骤: [5]                     │
│  └─ 日志级别: [INFO ▼]                  │
│                                          │
│  [测试连接] [恢复默认] [导入] [导出]     │
└─────────────────────────────────────────┘
```

---

## 核心功能需求

### 1. 会话管理
- 页面加载时自动初始化会话（调用 `/api/agent/init`）
- 保存 `session_id` 到状态管理
- 页面关闭时销毁会话（调用 `/api/agent/destroy`）

### 2. WebSocket 实时通信
- 连接到 WebSocket 服务器
- 加入会话房间（`socket.emit('join', {session_id})`）
- 监听以下事件：
  - `agent_thinking` - 显示"正在思考..."
  - `tool_call` - 显示工具调用（代码高亮）
  - `tool_result` - 显示执行结果
  - `phase_achieved` - 显示阶段达成提示
  - `flag_found` - 高亮显示 Flag
  - `error` - 显示错误提示

### 3. 对话功能
- 用户输入框
- 发送按钮（调用 `/api/agent/step`）
- 对话历史显示（用户消息 vs Agent 响应）
- 自动滚动到最新消息

### 4. 执行过程展示
- 实时滚动的日志窗口
- 时间戳显示
- 不同类型消息的颜色区分：
  - 战略专家：蓝色
  - Python专家：绿色
  - 安全专家：橙色
  - 执行结果：灰色
  - 错误：红色
  - Flag：金色高亮
- 代码块语法高亮（使用 Prism.js 或 highlight.js）

### 5. 状态显示
- 目标 URL
- 当前状态（INFO_GATHERING, VULN_DETECTION 等）
- 进度条（0-100%）
- 当前阶段
- 已发现的 Flag 数量

### 6. 配置管理
- 获取当前配置（`/api/config/get`）
- 表单验证
- 保存配置（`/api/config/update`）
- 测试连接功能
- 配置导入/导出（JSON 格式）

### 7. 自动/半自动模式切换
- 切换按钮
- 自动模式：连续执行直到发现 Flag
- 半自动模式：每步需要用户确认

---

## API 对接指南

### 初始化流程

```javascript
// 1. 初始化会话
const response = await axios.post('/api/agent/init');
const sessionId = response.data.session_id;

// 2. 连接 WebSocket
const socket = io('http://localhost:5000');
socket.emit('join', {session_id: sessionId});

// 3. 监听事件
socket.on('tool_result', (data) => {
  // 更新执行过程显示
  addLog({
    time: new Date(),
    type: 'result',
    content: data.output
  });
});

socket.on('flag_found', (data) => {
  // 显示 Flag 发现提示
  showNotification('发现 Flag: ' + data.flag);
});
```

### 发送消息

```javascript
async function sendMessage(userInput) {
  const response = await axios.post('/api/agent/step', {
    session_id: sessionId,
    user_input: userInput,
    auto_mode: isAutoMode
  });

  // 更新对话历史
  addMessage({
    role: 'user',
    content: userInput
  });

  addMessage({
    role: 'assistant',
    content: response.data.response
  });

  // 更新状态
  updateStatus({
    state: response.data.state,
    progress: response.data.progress,
    flags: response.data.flags
  });
}
```

### 获取状态

```javascript
async function fetchStatus() {
  const response = await axios.get('/api/agent/status', {
    params: {session_id: sessionId}
  });

  updateStatus(response.data);
}

// 每 5 秒轮询一次状态
setInterval(fetchStatus, 5000);
```

---

## UI/UX 设计要求

### 1. 颜色方案
- 主色调：深蓝色（#1890ff）
- 成功：绿色（#52c41a）
- 警告：橙色（#faad14）
- 错误：红色（#f5222d）
- Flag：金色（#fadb14）
- 背景：浅灰色（#f0f2f5）

### 2. 交互反馈
- 按钮点击有加载状态
- 长时间操作显示进度条
- 操作成功/失败有提示消息
- WebSocket 断开显示重连提示

### 3. 响应式设计
- 支持桌面端（1920x1080）
- 支持平板端（768x1024）
- 移动端可选

### 4. 代码高亮
- Python 代码使用 Prism.js 或 highlight.js
- 支持深色主题
- 显示行号

### 5. 动画效果
- 消息淡入效果
- 进度条平滑过渡
- Flag 发现时的闪烁效果

---

## 文件结构

```
webui/static/
├── index.html          # 主页面
├── css/
│   └── style.css       # 自定义样式
├── js/
│   ├── app.js          # 主应用逻辑
│   ├── api.js          # API 封装
│   ├── websocket.js    # WebSocket 处理
│   └── config.js       # 配置页面逻辑
└── assets/
    └── logo.png        # Logo 图片
```

---

## 示例代码（React + CDN）

### index.html

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>CTF Agent Web UI</title>
  <!-- React -->
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <!-- Babel (用于 JSX) -->
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <!-- Ant Design -->
  <link rel="stylesheet" href="https://unpkg.com/antd@5/dist/reset.css">
  <script src="https://unpkg.com/antd@5/dist/antd.min.js"></script>
  <!-- Socket.IO -->
  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
  <!-- Axios -->
  <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
  <!-- Prism.js (代码高亮) -->
  <link rel="stylesheet" href="https://unpkg.com/prismjs@1/themes/prism-tomorrow.css">
  <script src="https://unpkg.com/prismjs@1/prism.js"></script>
  <script src="https://unpkg.com/prismjs@1/components/prism-python.min.js"></script>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel" src="js/app.js"></script>
</body>
</html>
```

### js/app.js (React 示例)

```javascript
const { useState, useEffect } = React;
const { Layout, Input, Button, Progress, Card, message } = antd;
const { Header, Sider, Content } = Layout;

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState({
    state: 'INIT',
    progress: 0,
    flags: []
  });
  const [userInput, setUserInput] = useState('');

  // 初始化
  useEffect(() => {
    initSession();
  }, []);

  async function initSession() {
    try {
      const res = await axios.post('/api/agent/init');
      const sid = res.data.session_id;
      setSessionId(sid);

      // 连接 WebSocket
      const ws = io('http://localhost:5000');
      ws.emit('join', {session_id: sid});

      ws.on('tool_result', (data) => {
        addLog({type: 'result', content: data.output});
      });

      ws.on('flag_found', (data) => {
        message.success('发现 Flag: ' + data.flag);
      });

      setSocket(ws);
    } catch (error) {
      message.error('初始化失败: ' + error.message);
    }
  }

  function addLog(log) {
    setLogs(prev => [...prev, {time: new Date(), ...log}]);
  }

  async function sendMessage() {
    if (!userInput.trim()) return;

    try {
      const res = await axios.post('/api/agent/step', {
        session_id: sessionId,
        user_input: userInput,
        auto_mode: false
      });

      setMessages(prev => [
        ...prev,
        {role: 'user', content: userInput},
        {role: 'assistant', content: res.data.response}
      ]);

      setStatus({
        state: res.data.state,
        progress: res.data.progress,
        flags: res.data.flags
      });

      setUserInput('');
    } catch (error) {
      message.error('发送失败: ' + error.message);
    }
  }

  return (
    <Layout style={{height: '100vh'}}>
      <Header style={{color: 'white', fontSize: '20px'}}>
        CTF Agent - 自动解题系统
      </Header>
      <Layout>
        <Sider width={300} style={{background: '#fff', padding: '16px'}}>
          <Card title="会话信息" size="small">
            <p>状态: {status.state}</p>
            <Progress percent={status.progress} />
            <p>已发现 Flag: {status.flags.length}</p>
          </Card>
        </Sider>
        <Content style={{padding: '16px'}}>
          <div style={{height: '60%', overflow: 'auto', background: '#fff', padding: '16px', marginBottom: '16px'}}>
            {logs.map((log, i) => (
              <div key={i}>
                <span style={{color: '#999'}}>[{log.time.toLocaleTimeString()}]</span>
                <span> {log.content}</span>
              </div>
            ))}
          </div>
          <div style={{height: '35%', background: '#fff', padding: '16px'}}>
            {messages.map((msg, i) => (
              <div key={i} style={{marginBottom: '8px'}}>
                <strong>{msg.role === 'user' ? '用户' : 'Agent'}:</strong> {msg.content}
              </div>
            ))}
            <Input.TextArea
              value={userInput}
              onChange={e => setUserInput(e.target.value)}
              placeholder="输入指令..."
              rows={2}
            />
            <Button type="primary" onClick={sendMessage} style={{marginTop: '8px'}}>
              发送
            </Button>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
```

---

## 测试要点

1. **会话管理**: 测试会话创建、销毁、超时
2. **WebSocket**: 测试断线重连、事件接收
3. **API 调用**: 测试所有 API 端点
4. **错误处理**: 测试网络错误、API 错误
5. **UI 响应**: 测试加载状态、进度更新
6. **代码高亮**: 测试 Python 代码显示
7. **Flag 检测**: 测试 Flag 高亮显示

---

## 交付要求

1. 所有文件放在 `webui/static/` 目录
2. 使用 CDN 引入库，不需要 npm
3. 代码注释清晰
4. 实现所有核心功能
5. UI 美观、交互流畅
6. 错误处理完善

---

## 参考资料

- API 文档: `docs/API_SPEC.md`
- 后端代码: `webui/app.py`, `webui/api/*.py`
- Ant Design: https://ant.design/
- Socket.IO: https://socket.io/docs/v4/client-api/
- Prism.js: https://prismjs.com/

---

## 开始开发

请根据以上要求开发前端界面。如有疑问，请参考 API 文档或询问。祝开发顺利！
