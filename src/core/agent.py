from src.core.llm import LLMProvider
from src.rag.engine import RAGSystem
import json
import re

class CTFAgent:
    def __init__(self):
        self.llm = LLMProvider()
        self.rag = RAGSystem()
        self.history = []
        
        # System Prompt definition
        self.system_prompt = """
你是一个专注于 Web 安全的自动化 CTF (Capture The Flag) Agent。
你的目标是通过分析问题、制定计划并执行 Python 代码来解决 CTF 挑战。

你的回答除专业名词外全部用中文回答

你可以访问一个 RAG (检索增强生成) 系统，其中包含过去 CTF Writeup 和 Payload 的知识。

工作流程:
1.  **分析**: 理解用户输入或题目描述。
2.  **检索**: 如果你需要知识（例如，“如何利用 php 反序列化”），系统会自动检索相关信息。
3.  **计划**: 将解决方案分解为步骤。
4.  **执行**: 
    - 你可以编写 Python 代码与目标 URL 进行交互。
    - 你也可以编写 Bash/Shell 命令在 Kali Linux 终端中执行（如 nmap, curl, nc 等）。
    - 重要: 请将代码输出在代码块 ```python ... ``` 或 ```bash ... ``` 中。
    - 系统将执行此代码并将输出返回给你。
5.  **反思**: 根据执行结果，调整你的计划。

响应格式:
你的回答应该是有结构的。如果你想执行代码，只提供代码块和简短的说明。
如果你找到了 Flag，请明确输出 "FLAG: ctf{...}"。

处理 HTTP 响应时：

- 不要简单用 response.text[:500] 截断查看。
- 如果响应较长，请至少同时输出头部和尾部预览，并在代码中搜索 flag{ 、 ctf{ 等关键字，打印关键字附近的上下文。
- 注意flag不只是flag{xxx/}这种形式，只要是xxx{xxx/}这种形式都要注意。
- 需要检查源码时，可以将完整响应保存到文件，再基于文件内容继续分析。

当前挑战上下文:
目标 URL: {target_url}
"""
        self.target_url = ""

    def set_target(self, url: str):
        self.target_url = url
        # 更新包含目标 URL 的系统提示
        # 注意：如果提示包含其他大括号，我们需要处理潜在的大括号冲突
        # 但目前提示只有 {target_url} 作为占位符。
        # 然而，为了安全起见，防止未来的提示更改包含字面大括号（如 JSON 示例），
        # 直接替换比使用 format() 更安全。
        
        final_prompt = self.system_prompt.replace("{target_url}", url)
        
        self.history = [
            {'role': 'system', 'content': final_prompt}
        ]

    def run_step(self, user_input: str):
        """
        执行 Agent 循环的一个步骤。
        """
        # 1. RAG 检索（简单的关键词提取或仅使用完整查询）
        # 为简单起见，我们直接使用用户输入作为查询
        relevant_docs = self.rag.query(user_input)
        context_str = "\n---\n".join(relevant_docs)
        
        rag_message = f"用户输入: {user_input}\n\n数据库相关知识:\n{context_str}"
        
        # 添加到历史记录
        self.history.append({'role': 'user', 'content': rag_message})
        
        # 2. LLM 调用
        response = self.llm.chat(self.history)
        
        # 将响应添加到历史记录
        self.history.append({'role': 'assistant', 'content': response})
        
        return response

    def extract_code(self, response: str) -> tuple[str, str]:
        """
        从响应中提取代码。
        返回 (code_type, code_content)。
        code_type: 'python' | 'bash' | None
        """
        # 尝试提取 bash/shell
        match = re.search(r'```(bash|shell)(.*?)```', response, re.DOTALL)
        if match:
            return 'bash', match.group(2).strip()
            
        # 尝试提取 python
        match = re.search(r'```python(.*?)```', response, re.DOTALL)
        if match:
            return 'python', match.group(1).strip()
            
        return None, None

    def summarize_session(self) -> str:
        """
        使用 LLM 总结当前会话，生成一份 Writeup。
        """
        if not self.history:
            return None
            
        print("[Agent] 正在总结本次会话经验...")
        
        # 构建总结的 Prompt
        summary_prompt = """
请回顾上述对话历史，针对这次 CTF 挑战生成一份简洁的 Writeup（解题报告）。
这份报告将作为未来的知识库条目。

要求：
1. 包含题目目标或漏洞类型。
2. 简述关键解题步骤。
3. 包含关键的 Payload 或利用代码片段。
4. 格式使用 Markdown。
5. 去除无关的对话闲聊。
"""
        # 创建一个新的消息列表用于总结，包含历史记录
        summary_messages = self.history.copy()
        summary_messages.append({'role': 'user', 'content': summary_prompt})
        
        # 调用 LLM
        summary = self.llm.chat(summary_messages)
        return summary
