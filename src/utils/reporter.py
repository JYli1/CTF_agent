import os
import datetime

class Reporter:
    """
    处理日志记录和报告生成（纯文本格式）
    """
    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 会话数据
        self.session_id = None
        self.target_url = None
        self.start_time = None
        self.steps = []
        self.current_step = 0

    def start_session(self, target_url: str = None):
        """开始新会话"""
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.target_url = target_url or "未指定"
        self.start_time = datetime.datetime.now()
        self.steps = []
        self.current_step = 0

    def log_event(self, event_type: str, **kwargs):
        """记录事件"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        event = {
            "type": event_type,
            "timestamp": timestamp,
            **kwargs
        }

        # 如果是新步骤，增加步骤计数
        if event_type in ["user_to_strategist", "strategist_to_expert"]:
            self.current_step += 1
            event["step_number"] = self.current_step

        self.steps.append(event)

    def create_report(self, task_name: str, content: list):
        """生成纯文本格式报告"""
        if not self.session_id:
            self.start_session()

        end_time = datetime.datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        filename = f"{self.log_dir}/{task_name}_{self.session_id}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            # 头部
            f.write("=" * 80 + "\n")
            f.write("CTF Agent 会话日志\n")
            f.write("=" * 80 + "\n")
            f.write(f"会话ID: {self.session_id}\n")
            f.write(f"目标URL: {self.target_url}\n")
            f.write(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总耗时: {int(duration)}秒\n")
            f.write("=" * 80 + "\n\n")

            # 处理步骤
            self._write_steps(f)

            # 尾部
            f.write("\n" + "=" * 80 + "\n")
            f.write("会话结束\n")
            f.write("=" * 80 + "\n")

        return filename

    def _write_steps(self, f):
        """写入步骤详情"""
        current_step_num = 0

        for event in self.steps:
            event_type = event["type"]
            timestamp = event["timestamp"]

            if event_type == "user_to_strategist":
                current_step_num = event.get("step_number", current_step_num + 1)
                f.write(f"[步骤 {current_step_num}] 初始分析 - {timestamp}\n")
                f.write("-" * 80 + "\n\n")

                f.write("[用户] ---> [战略专家]\n")
                f.write(f"  提示词:\n")
                self._write_indented(f, event.get("prompt", ""), 4)

                if event.get("rag_context"):
                    f.write(f"\n  RAG上下文:\n")
                    self._write_indented(f, event.get("rag_context", ""), 4)
                f.write("\n")

            elif event_type == "strategist_response":
                f.write("[战略专家] 响应:\n")
                self._write_indented(f, event.get("response", ""), 2)
                f.write("\n\n")

            elif event_type == "strategist_to_expert":
                current_step_num = event.get("step_number", current_step_num + 1)
                f.write("-" * 80 + "\n\n")
                f.write(f"[步骤 {current_step_num}] {event.get('expert_name', '专家')}执行 - {timestamp}\n")
                f.write("-" * 80 + "\n\n")

                f.write(f"[战略专家] ---> [{event.get('expert_name', '专家')}]\n")
                f.write(f"  任务指派:\n")
                self._write_indented(f, event.get("task", ""), 4)
                f.write("\n\n")

            elif event_type == "expert_analysis":
                f.write(f"[{event.get('expert_name', '专家')}] 分析:\n")
                self._write_indented(f, event.get("analysis", ""), 2)
                f.write("\n\n")

            elif event_type == "tool_call":
                f.write(f"[{event.get('expert_name', '专家')}] ---> [工具: {event.get('tool_name', 'unknown')}]\n")
                f.write(f"  {event.get('action_type', '命令')}:\n")
                self._write_indented(f, event.get("content", ""), 4)
                f.write("\n\n")

            elif event_type == "tool_result":
                f.write(f"[工具: {event.get('tool_name', 'unknown')}] ---> [{event.get('expert_name', '专家')}]\n")
                f.write(f"  执行结果:\n")
                self._write_indented(f, event.get("result", ""), 4)
                f.write("\n\n")

            elif event_type == "code_detected":
                f.write(f"[系统] 源码检测:\n")
                f.write(f"  检测状态: 检测到源码\n")
                f.write(f"  源码类型: {event.get('code_type', 'Unknown')}\n")
                f.write(f"  源码长度: {event.get('code_length', 0)}字符\n\n")
                f.write(f"  提取的{event.get('code_type', '')}源码:\n")
                self._write_indented(f, event.get("code", ""), 4)
                f.write("\n\n")

            elif event_type == "code_analysis":
                f.write(f"[{event.get('expert_name', '专家')}] 源码分析:\n")
                self._write_indented(f, event.get("analysis", ""), 2)
                f.write("\n\n")

            elif event_type == "expert_to_strategist":
                f.write(f"[{event.get('expert_name', '专家')}] ---> [战略专家]\n")
                f.write(f"  汇报:\n")
                self._write_indented(f, event.get("report", ""), 4)
                f.write("\n\n")

            elif event_type == "flag_found":
                f.write("\n" + "=" * 80 + "\n")
                f.write("最终结果\n")
                f.write("=" * 80 + "\n")
                f.write(f"Flag状态: [✓] 已找到\n")
                flags = event.get("flags", [])
                for flag in flags:
                    f.write(f"Flag内容: {flag}\n")
                f.write(f"检测方法: {event.get('method', 'unknown')}\n")
                f.write(f"总步骤数: {current_step_num}\n")
                f.write("=" * 80 + "\n")

            elif event_type == "phase_achieved":
                f.write(f"[系统] 阶段达成:\n")
                f.write(f"  阶段名称: {event.get('phase_name', 'Unknown')}\n")
                f.write(f"  触发工具: {event.get('tool', 'Unknown')}\n")
                f.write(f"  触发命令: {event.get('command', 'Unknown')}\n")
                f.write("\n")

    def _write_indented(self, f, text: str, indent: int):
        """写入缩进文本"""
        if not text:
            return

        lines = text.split('\n')
        prefix = ' ' * indent
        for line in lines:
            f.write(f"{prefix}{line}\n")
