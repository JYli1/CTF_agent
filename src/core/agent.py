from src.core.agents.ctf_strategist import CTFStrategist
from src.core.agents.python_coder import PythonCoder
from src.core.agents.security_expert import SecurityExpert
from src.tools.executor import CodeExecutor, SSHExecutor
from src.rag.engine import RAGSystem
from src.core.prompts import RAG_QUERY_PROMPT
from src.core.state_machine import StateManager, CTFState
from src.core.phase_tracker import PhaseTracker, CTFPhase
from src.utils.config import Config
from src.utils.code_extractor import extract_php_code
from src.utils.flag_detector import FlagDetector
from src.utils.vuln_detector import VulnerabilityDetector
from src.skills.registry import skill_registry
from src.skills.loader import load_all_skills
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import re
import json

console = Console()

class CTFAgent:
    def __init__(self, reporter=None, event_callback=None):
        # Initialize Experts
        self.strategist = CTFStrategist()
        self.python_coder = PythonCoder()
        self.security_expert = SecurityExpert()

        # Initialize Executors
        self.code_executor = CodeExecutor()
        self.ssh_executor = SSHExecutor()

        # Reporter
        self.reporter = reporter

        # Event callback (for WebSocket)
        self.event_callback = event_callback

        # Phase Tracker
        self.phase_tracker = PhaseTracker()
        self.new_phase_achieved = None  # 存储本轮新达成的阶段

        # Skill System
        self.skill_registry = skill_registry
        self.target_url = None  # 存储目标URL，供技能使用

        # Vulnerability Detector
        self.vuln_detector = VulnerabilityDetector()
        
        # 定义工具列表
        self.python_tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_python",
                    "description": "执行 Python 代码。适用于复杂的逻辑计算、特定的利用脚本编写、数据加解密等。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "要执行的 Python 代码"
                            }
                        },
                        "required": ["code"]
                    }
                }
            }
        ]
        
        self.security_tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_shell",
                    "description": "在远程 Kali 机器上执行 Shell 命令。适用于使用 nmap, sqlmap, curl, gobuster 等标准安全工具。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "要执行的 Shell 命令"
                            }
                        },
                        "required": ["command"]
                    }
                }
            }
        ]
        
        # 预先建立 SSH 连接
        if Config.SSH_HOST:
            print(f"[系统] 正在建立 SSH 连接 ({Config.SSH_HOST})...")
            ssh_status = self.ssh_executor.connect()
            print(f"[SSH] {ssh_status}")
        else:
            print("[系统] 未配置 SSH_HOST，跳过 SSH 连接。")
        
        # Initialize RAG
        self.rag = RAGSystem()

        # 状态管理
        self.state_manager = StateManager()

        # 临时记忆：存储提取的源代码
        self.extracted_code = {}

        # Flag检测器
        self.flag_detector = FlagDetector()
        self.flag_found = False
        self.found_flags = []

        # Configuration
        self.max_sub_steps = 5

    def _emit_event(self, event_type: str, data: dict):
        """发射事件（用于 WebSocket 推送）"""
        if self.event_callback:
            try:
                self.event_callback(event_type, data)
            except Exception as e:
                print(f"[警告] 事件回调失败: {e}")

    def set_target(self, url: str):
        self.strategist.set_target(url)
        self.target_url = url  # 保存供技能使用

    def use_skill(self, skill_id: str, context: dict = None) -> dict:
        """
        使用技能

        Args:
            skill_id: 技能ID
            context: 执行上下文

        Returns:
            技能执行结果
        """
        skill = self.skill_registry.get(skill_id)
        if not skill:
            return {
                "success": False,
                "message": f"技能不存在: {skill_id}"
            }

        # 准备上下文
        if context is None:
            context = {}

        # 自动添加target_url
        if self.target_url and "target_url" not in context:
            context["target_url"] = self.target_url

        # 创建执行器包装
        class ExecutorWrapper:
            def __init__(self, code_executor, ssh_executor):
                self.code_executor = code_executor
                self.ssh_executor = ssh_executor

            def execute_python(self, code):
                return self.code_executor.execute(code)

            def execute_shell(self, command):
                return self.ssh_executor.execute(command)

        executor = ExecutorWrapper(self.code_executor, self.ssh_executor)

        # 执行技能
        result = skill.execute(context, executor)

        return {
            "success": result.success,
            "message": result.message,
            "data": result.data,
            "commands": result.commands,
            "findings": result.findings
        }

    def run_step(self, user_input: str):
        """
        主循环:
        1. 检索上下文 (RAG)
        2. 咨询CTF战略专家
        3. 如果指派任务 -> 执行 -> 汇报 -> 重复
        4. 返回最终响应
        """
        # 重置本轮阶段检测
        self.new_phase_achieved = None

        console.print(Panel("[bold yellow]分析阶段[/bold yellow]", border_style="yellow", expand=False))

        # 显示当前状态和进度
        progress = self.state_manager.get_progress()
        console.print(
            f"[bold]当前状态：[/bold][cyan]{self.state_manager.current_state.value}[/cyan] "
            f"[dim]({progress:.0%})[/dim]"
        )

        # 检查是否卡住
        if self.state_manager.is_stuck():
            console.print("[red]⚠️  检测到重复尝试，可能需要调整策略[/red]")

        # 自动漏洞检测
        vuln_suggestions = ""
        if self.target_url:
            console.print(f"\n[cyan]🔍 正在分析目标URL的漏洞特征...[/cyan]")
            vuln_analysis = self.vuln_detector.get_skill_recommendation(self.target_url)

            if vuln_analysis["recommendations"]:
                console.print(Panel(
                    vuln_analysis["summary"],
                    title="[bold magenta]🎯 漏洞特征识别",
                    border_style="magenta"
                ))

                # 显示推荐
                for rec in vuln_analysis["recommendations"]:
                    console.print(
                        f"  [magenta]•[/magenta] {rec['vuln_type']} "
                        f"[dim](置信度: {rec['confidence']:.0%})[/dim] "
                        f"→ 推荐技能: [cyan]{rec['skill_id']}[/cyan]"
                    )
                    console.print(f"    原因: {rec['reason']}")

                # 构建建议文本，传递给战略专家
                vuln_suggestions = "\n\n<vulnerability_analysis>\n"
                vuln_suggestions += f"系统自动检测到以下潜在漏洞特征：\n\n"
                for rec in vuln_analysis["recommendations"]:
                    vuln_suggestions += f"- {rec['vuln_type']} (置信度{rec['confidence']:.0%})\n"
                    vuln_suggestions += f"  原因: {rec['reason']}\n"
                    vuln_suggestions += f"  推荐技能: {rec['skill_id']}\n\n"
                vuln_suggestions += "建议优先测试上述漏洞类型。\n</vulnerability_analysis>"
            else:
                console.print(f"[dim]未检测到明显漏洞特征，继续常规分析[/dim]")

        # 判断是否需要RAG检索
        need_rag = self._should_retrieve(user_input)

        relevant_docs = []
        context_str = ""
        rag_queries = []

        if need_rag:
            # 1. Pre-analysis for RAG Query (RAG 前置分析)
            pre_analysis_msg = f"{user_input}\n\n{RAG_QUERY_PROMPT}"

            console.print(f"\n[cyan]正在进行检索前置分析...[/cyan]")
            analysis_response = self.strategist.chat(pre_analysis_msg)
            rag_queries = self._extract_rag_query(analysis_response)

            console.print(Panel(analysis_response, title="[bold]RAG 需求分析", border_style="dim"))

            # 2. RAG Retrieval
            if len(self.history) <= 1 or not rag_queries:
                rag_queries = ["CTF Web 渗透测试 信息收集 流程"]
                console.print(f"[dim]使用默认检索词[/dim]")

        # 执行多查询检索
        all_docs = []
        for query in rag_queries[:2]:  # 最多使用前2个查询
            console.print(f"[cyan]检索:[/cyan] {query}")
            docs = self.rag.query(query, n_results=3, distance_threshold=1.5)
            all_docs.extend(docs)

        # 去重并限制数量
        seen = set()
        relevant_docs = []
        for doc in all_docs:
            if doc not in seen:
                seen.add(doc)
                relevant_docs.append(doc)
                if len(relevant_docs) >= 5:
                    break
        
            context_str = "\n---\n".join(relevant_docs)
            
            if relevant_docs:
                console.print(f"\n[green]✓[/green] 检索到 [bold]{len(relevant_docs)}[/bold] 条相关知识")
                for i, doc in enumerate(relevant_docs, 1):
                    console.print(f"  [cyan]{i}.[/cyan] {doc[:80]}...", style="dim")
            else:
                console.print("[yellow]⚠[/yellow] 未检索到相关知识")
        else:
            console.print("[dim]⏭️  跳过RAG检索（使用已有上下文）[/dim]")

        # 3. Initial Prompt to Strategist
        full_message = f"""
<user_input>
{user_input}
</user_input>

<rag_context_reference>
注意：以下内容是根据关键字从知识库检索的历史经验，**仅供参考**。
请不要将其误认为是当前题目的条件或环境！
如果上下文与题目无关，请忽略。

{context_str}
</rag_context_reference>

{vuln_suggestions}
"""

        console.print(f"\n[cyan]正在请求 CTF 战略专家分析...[/cyan]")

        # 记录：用户 -> 战略专家
        if self.reporter:
            self.reporter.log_event("user_to_strategist",
                                   prompt=user_input,
                                   rag_context=context_str if context_str else None)

        current_response = self.strategist.chat(full_message)

        # 打印战略专家的完整分析
        console.print(Panel(
            current_response,
            title="[bold cyan]💭 CTF 战略专家初步分析",
            border_style="cyan"
        ))

        # 记录：战略专家响应
        if self.reporter:
            self.reporter.log_event("strategist_response", response=current_response)
        
        # 4. Sub-task Loop
        for i in range(self.max_sub_steps):
            # Check for assignments
            assignment = self._parse_assignment(current_response)

            if not assignment:
                break

            target_agent_name, task_content = assignment

            # 记录：战略专家 -> 专家
            if self.reporter:
                self.reporter.log_event("strategist_to_expert",
                                       expert_name=target_agent_name,
                                       task=task_content)

            console.print(f"\n[yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/yellow]")
            console.print(Panel(
                f"[bold cyan]目标专家：[/bold cyan][green]{target_agent_name}[/green]\n\n"
                f"[bold cyan]任务内容：[/bold cyan]\n{task_content}",
                title=f"[bold yellow]📋 任务指派 (步骤 {i+1}/{self.max_sub_steps})",
                border_style="yellow"
            ))
            console.print(f"[yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/yellow]\n")

            # Execute sub-task
            try:
                result = self._execute_subtask(target_agent_name, task_content)
            except Exception as e:
                result = f"执行出错: {str(e)}"

            # Report back to Strategist
            console.print(f"\n[yellow]━━━ 专家执行完成，汇报给战略专家 ━━━[/yellow]")

            # 让战略专家智能识别代码
            console.print(f"[dim]正在让战略专家分析是否包含代码...[/dim]")
            code_detection_prompt = f"""
请分析以下专家执行结果，判断是否包含编程语言代码（如Python、PHP、JavaScript、Java、C等）。

专家执行结果：
{result[:3000]}

如果包含代码，请按以下格式输出：
[CODE_DETECTED]
language: 语言名称（如Python、PHP、JavaScript等）
[/CODE_DETECTED]

[CODE_CONTENT]
提取的完整代码
[/CODE_CONTENT]

如果不包含代码，只输出：
[NO_CODE]
"""
            code_analysis_response = self.strategist.chat(code_detection_prompt)

            # 解析战略专家的代码识别结果
            code_info = self._parse_code_detection(code_analysis_response)

            if code_info.get("has_code"):
                code_type = code_info.get("language", "Unknown")
                code_content = code_info.get("code", "")

                console.print(f"[bold green]✓ 战略专家识别到{code_type}代码[/bold green]")

                # 保存到临时记忆
                self.extracted_code[code_type] = code_content

                # 显示代码
                display_code = code_content if len(code_content) <= 1500 else code_content[:1500] + "\n... (已截断)"
                syntax_type = code_type.lower().replace("javascript", "js")

                console.print(Panel(
                    Syntax(display_code, syntax_type, theme="monokai", line_numbers=True),
                    title=f"[bold green]📝 {code_type}源代码",
                    border_style="green"
                ))

                # 记录：源码检测
                if self.reporter:
                    self.reporter.log_event("code_detected",
                                           code_type=code_type,
                                           code=code_content,
                                           code_length=len(code_content))

                # 要求专家分析源码
                console.print(f"[cyan]📋 要求{target_agent_name}分析源码...[/cyan]")
                analysis_prompt = f"""
检测到{code_type}源码，请立即分析：

```{syntax_type}
{code_content[:2000]}
```

请分析：
1. 关键函数和变量
2. 可能的漏洞点
3. 下一步利用思路
"""
                if "Python" in target_agent_name:
                    analysis_response = self.python_coder.chat(analysis_prompt)
                else:
                    analysis_response = self.security_expert.chat(analysis_prompt)

                console.print(Panel(
                    analysis_response.content or "无分析内容",
                    title=f"[bold magenta]🔬 {code_type}源码分析",
                    border_style="magenta"
                ))

                # 记录：源码分析
                if self.reporter:
                    self.reporter.log_event("code_analysis",
                                           expert_name=target_agent_name,
                                           analysis=analysis_response.content or "")

                # 构建源码上下文
                code_context = f"\n\n[已提取{code_type}源代码 - 请仔细分析]\n```{syntax_type}\n{code_content}\n```\n\n[源码分析]\n{analysis_response.content}\n"
                result += code_context
            else:
                console.print(f"[dim]未检测到代码[/dim]")

            # 构建汇报消息
            report_msg = f"[{target_agent_name}] 执行完成。\n详细结果:\n{result}\n\n请根据结果继续分析，是继续指派任务还是输出最终 Flag？"

            console.print(f"[cyan]🤔 战略专家正在分析执行结果...[/cyan]")
            current_response = self.strategist.chat(report_msg)

            console.print(Panel(
                current_response,
                title="[bold cyan]💭 战略专家思考结果",
                border_style="cyan"
            ))

        # 根据结果自动更新状态
        self._update_state_from_response(current_response)

        # 统一Flag检测
        console.print(f"\n[dim]正在检测Flag...[/dim]")
        flag_result = self.flag_detector.detect(current_response)

        if flag_result["found"]:
            self.flag_found = True
            self.found_flags = flag_result["flags"]

            console.print(Panel(
                f"[bold green]🎉 检测到Flag！[/bold green]\n\n"
                f"检测方法: {flag_result['method']}\n"
                f"Flag内容:\n" + "\n".join([f"  • {flag}" for flag in flag_result["flags"]]),
                title="[bold green]Flag发现",
                border_style="green"
            ))

            # 记录：Flag发现
            if self.reporter:
                self.reporter.log_event("flag_found",
                                       flags=flag_result["flags"],
                                       method=flag_result["method"])

            self.state_manager.transition(CTFState.COMPLETED, "发现Flag")

        return current_response

    def _should_retrieve(self, user_input: str) -> bool:
        """
        判断是否需要进行RAG检索

        返回:
            True表示需要检索，False表示跳过
        """
        # 1. 初始阶段必须检索
        if len(self.history) <= 2:
            return True

        # 2. 用户明确要求时检索
        trigger_keywords = ['搜索', '查找', '参考', '知识库', '类似', '经验']
        if any(kw in user_input for kw in trigger_keywords):
            return True

        # 3. 遇到新类型问题时检索
        new_challenge_keywords = ['新发现', '不熟悉', '不确定', '没见过', '奇怪']
        if any(kw in user_input for kw in new_challenge_keywords):
            return True

        # 4. 连续执行阶段不检索（避免重复）
        if len(self.history) > 2:
            last_messages = [msg.get('content', '') for msg in self.history[-3:] if isinstance(msg.get('content'), str)]
            if all('执行' in msg or 'task' in msg.lower() for msg in last_messages if msg):
                return False

        # 5. 默认不检索（节省时间）
        return False

    def _update_state_from_response(self, response: str):
        """根据响应自动更新状态"""
        response_lower = response.lower()

        # 尝试从JSON响应中获取信息
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                if data.get('flag'):
                    self.state_manager.transition(CTFState.COMPLETED, "发现Flag")
                    return
        except:
            pass

        if 'flag{' in response_lower or 'ctf{' in response_lower:
            self.state_manager.transition(CTFState.COMPLETED, "发现Flag")
        elif any(kw in response_lower for kw in ['注入', 'injection', 'xss', '反序列化', '漏洞']):
            if self.state_manager.current_state == CTFState.INFO_GATHERING:
                self.state_manager.transition(CTFState.VULN_DETECTION, "发现潜在漏洞")
            elif self.state_manager.current_state == CTFState.VULN_DETECTION:
                self.state_manager.transition(CTFState.VULN_VERIFICATION, "开始验证漏洞")
        elif any(kw in response_lower for kw in ['sqlmap', 'exploit', '利用', 'payload']):
            if self.state_manager.current_state in (CTFState.VULN_DETECTION, CTFState.VULN_VERIFICATION):
                self.state_manager.transition(CTFState.EXPLOITATION, "开始漏洞利用")
        elif any(kw in response_lower for kw in ['curl', 'nmap', '扫描', '源码', '信息收集']):
            if self.state_manager.current_state == CTFState.INIT:
                self.state_manager.transition(CTFState.INFO_GATHERING, "开始信息收集")

    def _extract_rag_query(self, response: str) -> list:
        """
        从响应中提取检索查询列表

        返回:
            检索词列表
        """
        try:
            # 尝试提取JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                queries = data.get('search_queries', [])

                if queries:
                    print(f"[RAG] 生成的检索词: {queries}")
                    return queries
        except Exception as e:
            print(f"[RAG] JSON解析失败: {e}")

        # 回退到原有逻辑
        match = re.search(r"\*\*检索查询\*\*：(.*?)(?=\n|$)", response)
        if match:
            return [match.group(1).strip()]

        return []

    def _parse_assignment(self, text):
        """
        解析JSON格式的响应

        返回:
            (agent_name, task_content) 或 None
        """
        try:
            # 尝试提取JSON（可能包含在markdown代码块中）
            json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析整个文本
                json_str = text.strip()

            data = json.loads(json_str)

            # 检查是否报告了新阶段
            if data.get('phase_achieved'):
                phase_name = data['phase_achieved']
                from src.core.phase_tracker import CTFPhase

                # 将字符串转换为枚举
                phase_map = {
                    "文件读取": CTFPhase.FILE_READING,
                    "代码执行": CTFPhase.CODE_EXECUTION,
                    "命令执行": CTFPhase.COMMAND_EXECUTION
                }

                if phase_name in phase_map:
                    phase = phase_map[phase_name]
                    if not self.phase_tracker.is_achieved(phase):
                        self.phase_tracker.achieved_phases.add(phase)
                        self.new_phase_achieved = phase
                        print(f"\n🎯 [阶段突破] {phase.value}")

                        # 发送事件
                        if self.event_callback:
                            self._emit_event('phase_achieved', {
                                'phase': phase.value,
                                'phases': [p.value for p in self.phase_tracker.get_achieved_phases()]
                            })

                        # 记录到 Reporter
                        if self.reporter:
                            self.reporter.log_event("phase_achieved",
                                phase=phase.value,
                                all_phases=[p.value for p in self.phase_tracker.get_achieved_phases()]
                            )

            # 检查是否找到flag
            if data.get('flag'):
                print(f"\n🎉 [发现Flag] {data['flag']}")
                return None

            # 检查action类型
            action = data.get('action', {})
            action_type = action.get('type')

            if action_type == 'assign_task':
                agent_name = action.get('agent')
                task_content = action.get('task')

                if agent_name and task_content:
                    return agent_name, task_content
                else:
                    print("[警告] JSON格式正确但缺少agent或task字段")
                    return None

            elif action_type == 'use_skill':
                # 使用技能
                skill_id = action.get('skill_id')
                if not skill_id:
                    print("[警告] use_skill类型但缺少skill_id")
                    return None

                console.print(f"\n[bold magenta]🎯 战略专家决定使用技能: {skill_id}[/bold magenta]")

                # 执行技能
                result = self.use_skill(skill_id)

                if result['success']:
                    console.print(Panel(
                        result['message'],
                        title=f"[bold magenta]💡 技能建议: {skill_id}",
                        border_style="magenta"
                    ))

                    # 将技能建议作为任务指派给专家
                    agent_name = action.get('agent', '安全专家')
                    task_with_skill = f"""[技能建议: {skill_id}]

{result['message']}

请根据以上技能建议，逐步执行测试。"""

                    return agent_name, task_with_skill
                else:
                    console.print(f"[red]技能执行失败: {result['message']}[/red]")
                    return None

            elif action_type == 'need_help':
                print("\n⚠️ [战略专家] 遇到困难，建议用户介入")
                return None

            elif action_type == 'report_flag':
                return None

            else:
                print(f"[警告] 未知的action类型: {action_type}")
                return None

        except json.JSONDecodeError as e:
            print(f"[警告] JSON解析失败: {e}")
            # 尝试清理控制字符后重新解析
            try:
                # 移除控制字符（保留换行符和制表符）
                cleaned_json = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', json_str)
                data = json.loads(cleaned_json)

                # 检查是否找到flag
                if data.get('flag'):
                    print(f"\n🎉 [发现Flag] {data['flag']}")
                    return None

                # 检查action类型
                action = data.get('action', {})
                action_type = action.get('type')

                if action_type == 'assign_task':
                    agent_name = action.get('agent')
                    task_content = action.get('task')

                    if agent_name and task_content:
                        return agent_name, task_content
                    else:
                        print("[警告] JSON格式正确但缺少agent或task字段")
                        return None

                elif action_type == 'need_help':
                    print("\n⚠️ [战略专家] 遇到困难，建议用户介入")
                    return None

                elif action_type == 'report_flag':
                    return None

                else:
                    print(f"[警告] 未知的action类型: {action_type}")
                    return None

            except Exception as e2:
                print(f"[警告] 清理后仍无法解析: {e2}")

            # 回退到正则解析
            return self._parse_assignment_regex(text)
        except Exception as e:
            print(f"[错误] 解析异常: {e}")
            return None

    def _parse_assignment_regex(self, text):
        """
        回退方案：使用正则表达式解析（兼容旧格式）
        """
        text = text.replace("**", "")
        agent_match = re.search(r"指派对象：\[(Python 专家|Python专家|安全专家)\]", text)

        if agent_match:
            agent_name = agent_match.group(1)
            content_match = re.search(r"任务内容：\s*(.*)", text, re.DOTALL)

            if content_match:
                task_content = content_match.group(1).strip()
                return agent_name, task_content

        return None

    def _execute_subtask(self, agent_name, content):
        if "Python" in agent_name:
            console.print(f"\n[green]┌─ Python 专家开始工作 ─┐[/green]")
            console.print(f"[dim]📝 正在分析任务需求...[/dim]")

            response_msg = self.python_coder.chat(content, tools=self.python_tools)

            console.print(f"[dim]✓ 任务分析完成[/dim]")

            # 记录：专家分析
            if self.reporter and response_msg.content:
                self.reporter.log_event("expert_analysis",
                                       expert_name=agent_name,
                                       analysis=response_msg.content)

            if response_msg.content:
                console.print(Panel(
                    response_msg.content,
                    title="[bold green]💬 Python 专家回复",
                    border_style="green"
                ))

            final_result = f"专家回复:\n{response_msg.content or ''}\n"

            # 处理工具调用
            if hasattr(response_msg, 'tool_calls') and response_msg.tool_calls:
                total_calls = len(response_msg.tool_calls)

                if total_calls > 1:
                    console.print(f"[yellow]⚠️  检测到 {total_calls} 个代码块，本次只执行第一个（单步执行模式）[/yellow]")

                # 只执行第一个tool_call
                tool_call = response_msg.tool_calls[0]
                if tool_call.function.name == "execute_python":
                    args = json.loads(tool_call.function.arguments)
                    code = args.get("code")

                    console.print(f"\n[bold yellow]━━━ 代码块 #1 ━━━[/bold yellow]")
                    # 显示代码
                    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
                    console.print(Panel(syntax, title="[bold green]📝 Python代码", border_style="green"))

                    # 记录：工具调用
                    if self.reporter:
                        self.reporter.log_event("tool_call",
                                               expert_name=agent_name,
                                               tool_name="execute_python",
                                               action_type="代码",
                                               content=code)

                    console.print(f"[cyan]▶️  开始执行...[/cyan]")
                    exec_output = self.code_executor.execute(code)
                    console.print(f"[dim]✓ 执行完成[/dim]")

                    # 阶段检测
                    detected_phase = self.phase_tracker.detect_phase("execute_python", code, exec_output)
                    if detected_phase:
                        self.new_phase_achieved = detected_phase
                        console.print(Panel(
                            f"[bold green]🎯 达成新阶段：{detected_phase.value}[/bold green]",
                            border_style="green"
                        ))
                        # 记录阶段达成
                        if self.reporter:
                            self.reporter.log_event("phase_achieved",
                                                   phase_name=detected_phase.value,
                                                   tool="execute_python",
                                                   command=code[:100])

                    # 响应漏洞检测
                    if len(exec_output) > 100:  # 只分析有实质内容的响应
                        vuln_in_response = self.vuln_detector.analyze_response(exec_output)
                        if vuln_in_response:
                            console.print(f"\n[magenta]🔍 在执行结果中检测到漏洞特征：[/magenta]")
                            for vuln_type, confidence, skill_id, indicators in vuln_in_response:
                                console.print(f"  • {vuln_type} (置信度: {confidence:.0%}) → {skill_id}")

                    # 记录：工具结果
                    if self.reporter:
                        self.reporter.log_event("tool_result",
                                               expert_name=agent_name,
                                               tool_name="execute_python",
                                               result=exec_output)

                    # 提取专家标记的PHP代码
                    php_code_blocks = self._extract_php_from_response(response_msg.content or "")
                    if php_code_blocks:
                        console.print(f"[magenta]🔍 专家提取了 {len(php_code_blocks)} 个PHP代码块[/magenta]")
                        for i, php_code in enumerate(php_code_blocks, 1):
                            syntax = Syntax(php_code, "php", theme="monokai", line_numbers=True)
                            console.print(Panel(
                                syntax,
                                title=f"[bold magenta]📄 PHP代码块 #{i}",
                                border_style="magenta"
                            ))

                    console.print(Panel(exec_output, title="[bold blue]📤 执行结果", border_style="blue"))

                    self.python_coder.history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "execute_python",
                        "content": exec_output
                    })
                    final_result += f"\n代码执行输出:\n{exec_output}"

            console.print(f"[green]└─ Python 专家工作完成 ─┘[/green]\n")
            return final_result

        elif "安全" in agent_name:
            console.print(f"\n[red]┌─ 安全专家开始工作 ─┐[/red]")
            console.print(f"[dim]📝 正在分析任务需求...[/dim]")

            response_msg = self.security_expert.chat(content, tools=self.security_tools)

            console.print(f"[dim]✓ 任务分析完成[/dim]")

            # 记录：专家分析
            if self.reporter and response_msg.content:
                self.reporter.log_event("expert_analysis",
                                       expert_name=agent_name,
                                       analysis=response_msg.content)

            if response_msg.content:
                console.print(Panel(
                    response_msg.content,
                    title="[bold red]💬 安全专家回复",
                    border_style="red"
                ))

            final_result = f"专家回复:\n{response_msg.content or ''}\n"

            # 处理工具调用
            if hasattr(response_msg, 'tool_calls') and response_msg.tool_calls:
                total_calls = len(response_msg.tool_calls)

                if total_calls > 1:
                    console.print(f"[yellow]⚠️  检测到 {total_calls} 个命令，本次只执行第一个（单步执行模式）[/yellow]")

                # 只执行第一个tool_call
                tool_call = response_msg.tool_calls[0]
                if tool_call.function.name == "execute_shell":
                    args = json.loads(tool_call.function.arguments)
                    command = args.get("command")

                    console.print(f"\n[bold yellow]━━━ 命令 #1 ━━━[/bold yellow]")
                    console.print(f"[bold green]$[/bold green] [cyan]{command}[/cyan]")

                    # 记录：工具调用
                    if self.reporter:
                        self.reporter.log_event("tool_call",
                                               expert_name=agent_name,
                                               tool_name="execute_shell",
                                               action_type="命令",
                                               content=command)

                    console.print(f"[cyan]▶️  开始执行...[/cyan]")
                    exec_output = self.ssh_executor.execute(command)
                    console.print(f"[dim]✓ 执行完成[/dim]")

                    # 阶段检测
                    detected_phase = self.phase_tracker.detect_phase("execute_shell", command, exec_output)
                    if detected_phase:
                        self.new_phase_achieved = detected_phase
                        console.print(Panel(
                            f"[bold green]🎯 达成新阶段：{detected_phase.value}[/bold green]",
                            border_style="green"
                        ))
                        # 记录阶段达成
                        if self.reporter:
                            self.reporter.log_event("phase_achieved",
                                                   phase_name=detected_phase.value,
                                                   tool="execute_shell",
                                                   command=command[:100])

                    # 响应漏洞检测
                    if len(exec_output) > 100:  # 只分析有实质内容的响应
                        vuln_in_response = self.vuln_detector.analyze_response(exec_output)
                        if vuln_in_response:
                            console.print(f"\n[magenta]🔍 在命令输出中检测到漏洞特征：[/magenta]")
                            for vuln_type, confidence, skill_id, indicators in vuln_in_response:
                                console.print(f"  • {vuln_type} (置信度: {confidence:.0%}) → {skill_id}")

                    # 记录：工具结果
                    if self.reporter:
                        self.reporter.log_event("tool_result",
                                               expert_name=agent_name,
                                               tool_name="execute_shell",
                                               result=exec_output)

                    # 提取专家标记的PHP代码
                    php_code_blocks = self._extract_php_from_response(response_msg.content or "")
                    if php_code_blocks:
                        console.print(f"[magenta]🔍 专家提取了 {len(php_code_blocks)} 个PHP代码块[/magenta]")
                        for i, php_code in enumerate(php_code_blocks, 1):
                            syntax = Syntax(php_code, "php", theme="monokai", line_numbers=True)
                            console.print(Panel(
                                syntax,
                                title=f"[bold magenta]📄 PHP代码块 #{i}",
                                border_style="magenta"
                            ))

                    console.print(Panel(exec_output, title="[bold blue]📤 命令输出", border_style="blue"))

                    self.security_expert.history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "execute_shell",
                        "content": exec_output
                    })
                    final_result += f"\n命令执行输出:\n{exec_output}"

            console.print(f"[red]└─ 安全专家工作完成 ─┘[/red]\n")
            return final_result

        return f"错误: 未知的专家类型 '{agent_name}'"

    def _parse_code_detection(self, response: str) -> dict:
        """
        解析战略专家的代码识别结果

        返回:
            {
                "has_code": bool,
                "language": str,
                "code": str
            }
        """
        # 检查是否明确表示没有代码
        if "[NO_CODE]" in response:
            return {"has_code": False}

        # 提取语言类型
        language_match = re.search(r'\[CODE_DETECTED\].*?language:\s*(\w+)', response, re.DOTALL | re.IGNORECASE)
        if not language_match:
            return {"has_code": False}

        language = language_match.group(1)

        # 提取代码内容
        code_match = re.search(r'\[CODE_CONTENT\](.*?)\[/CODE_CONTENT\]', response, re.DOTALL)
        if not code_match:
            return {"has_code": False}

        code = code_match.group(1).strip()

        if not code:
            return {"has_code": False}

        return {
            "has_code": True,
            "language": language,
            "code": code
        }

    def _extract_php_from_response(self, response: str) -> list[str]:
        """
        从专家回复中提取标记的PHP代码块

        格式: [PHP代码]...[/PHP代码]
        """
        php_blocks = []
        pattern = r'\[PHP代码\](.*?)\[/PHP代码\]'
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)

        for match in matches:
            code = match.strip()
            if code:
                php_blocks.append(code)

        return php_blocks

    def _extract_code(self, response: str) -> tuple[str, str]:
        """
        Extract code from markdown blocks.
        """
        # Try bash/shell
        match = re.search(r'```(bash|shell)(.*?)```', response, re.DOTALL)
        if match:
            return 'bash', match.group(2).strip()
            
        # Try python
        match = re.search(r'```python(.*?)```', response, re.DOTALL)
        if match:
            return 'python', match.group(1).strip()
            
        return None, None

    def close(self):
        if self.ssh_executor:
            self.ssh_executor.close()

    def summarize_session(self) -> str:
        """
        Use Strategist to summarize.
        """
        if not self.strategist.history:
            return None
            
        summary_prompt = "请回顾整个解题过程，生成一份 Markdown 格式的 Writeup，包含关键步骤和 Flag。"
        return self.strategist.chat(summary_prompt)

    @property
    def history(self):
        return self.strategist.history

    def _extract_code_from_response(self, result: str) -> dict:
        """
        从专家响应中提取源码检测结果
        解析格式：
        [源码检测]
        has_code: true/false
        code_type: PHP/Python/JavaScript/None
        [/源码检测]

        [源码内容]
        ...
        [/源码内容]
        """
        # 提取源码检测信息
        detection_match = re.search(r'\[源码检测\](.*?)\[/源码检测\]', result, re.DOTALL)
        if not detection_match:
            return {"has_code": False}

        detection_text = detection_match.group(1).strip()

        # 解析 has_code
        has_code_match = re.search(r'has_code:\s*(true|false)', detection_text, re.IGNORECASE)
        if not has_code_match:
            return {"has_code": False}

        has_code = has_code_match.group(1).lower() == 'true'

        if not has_code:
            return {"has_code": False}

        # 解析 code_type
        code_type_match = re.search(r'code_type:\s*(\w+)', detection_text)
        code_type = code_type_match.group(1) if code_type_match else "Unknown"

        # 提取源码内容
        content_match = re.search(r'\[源码内容\](.*?)\[/源码内容\]', result, re.DOTALL)
        if not content_match:
            return {"has_code": False}

        code_content = content_match.group(1).strip()

        return {
            "has_code": True,
            "code_type": code_type,
            "code": code_content
        }

    def _fallback_extract_code(self, result: str) -> dict:
        """
        备用代码提取方法：直接从响应中提取PHP/JavaScript代码
        """
        # 尝试提取PHP代码
        php_pattern = r'<\?php(.*?)\?>'
        php_matches = re.findall(php_pattern, result, re.DOTALL | re.IGNORECASE)

        if php_matches:
            # 合并所有PHP代码块
            php_code = '\n\n'.join([f'<?php{match}?>' for match in php_matches])
            console.print(f"[green]✓ 通过备用方法提取到PHP代码[/green]")
            return {
                "has_code": True,
                "code_type": "PHP",
                "code": php_code
            }

        # 尝试提取JavaScript代码
        js_pattern = r'<script[^>]*>(.*?)</script>'
        js_matches = re.findall(js_pattern, result, re.DOTALL | re.IGNORECASE)

        if js_matches:
            js_code = '\n\n'.join(js_matches)
            # 过滤掉太短的JS代码（可能只是简单的内联脚本）
            if len(js_code.strip()) > 50:
                console.print(f"[green]✓ 通过备用方法提取到JavaScript代码[/green]")
                return {
                    "has_code": True,
                    "code_type": "JavaScript",
                    "code": js_code
                }

        return {"has_code": False}

