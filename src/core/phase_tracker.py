from enum import Enum
from typing import Set, Optional

class CTFPhase(Enum):
    """CTF解题阶段"""
    UNSOLVED = "未解题"
    FILE_READING = "文件读取"
    CODE_EXECUTION = "代码执行"
    COMMAND_EXECUTION = "命令执行"

class PhaseTracker:
    """
    CTF解题阶段追踪器
    追踪解题过程中达成的各个阶段
    """

    def __init__(self):
        self.achieved_phases: Set[CTFPhase] = set()
        self.phase_details = {}  # 存储每个阶段的详细信息

    def detect_phase(self, tool_name: str, command: str, result: str) -> Optional[CTFPhase]:
        """
        根据工具调用和结果检测是否达成新阶段

        Args:
            tool_name: 工具名称 (execute_shell, execute_python)
            command: 执行的命令或代码
            result: 执行结果

        Returns:
            如果检测到新阶段，返回该阶段；否则返回None
        """
        detected_phase = None

        # 检测文件读取
        if not self.is_achieved(CTFPhase.FILE_READING):
            if self._detect_file_reading(tool_name, command, result):
                detected_phase = CTFPhase.FILE_READING
                self.achieved_phases.add(CTFPhase.FILE_READING)
                self.phase_details[CTFPhase.FILE_READING] = {
                    "tool": tool_name,
                    "command": command[:100],
                    "evidence": result[:200]
                }

        # 检测代码执行
        if not self.is_achieved(CTFPhase.CODE_EXECUTION):
            if self._detect_code_execution(tool_name, command, result):
                detected_phase = CTFPhase.CODE_EXECUTION
                self.achieved_phases.add(CTFPhase.CODE_EXECUTION)
                self.phase_details[CTFPhase.CODE_EXECUTION] = {
                    "tool": tool_name,
                    "command": command[:100],
                    "evidence": result[:200]
                }

        # 检测命令执行
        if not self.is_achieved(CTFPhase.COMMAND_EXECUTION):
            if self._detect_command_execution(tool_name, command, result):
                detected_phase = CTFPhase.COMMAND_EXECUTION
                self.achieved_phases.add(CTFPhase.COMMAND_EXECUTION)
                self.phase_details[CTFPhase.COMMAND_EXECUTION] = {
                    "tool": tool_name,
                    "command": command[:100],
                    "evidence": result[:200]
                }

        return detected_phase

    def _detect_file_reading(self, tool_name: str, command: str, result: str) -> bool:
        """检测是否成功读取文件"""
        # 命令特征
        file_read_commands = [
            'cat ', 'head ', 'tail ', 'less ', 'more ',
            'file_get_contents', 'readfile', 'fopen',
            'open(', 'read()', '.read(', 'with open',
            'curl', 'wget'
        ]

        command_lower = command.lower()
        has_read_command = any(cmd in command_lower for cmd in file_read_commands)

        # 结果特征：不是错误信息
        result_lower = result.lower()
        is_error = any(err in result_lower for err in [
            'error', 'failed', 'permission denied', 'no such file',
            'cannot open', 'not found', '404', '403', '500'
        ])

        # 结果有实质内容（长度>50且不全是错误）
        has_content = len(result.strip()) > 50 and not is_error

        return has_read_command and has_content

    def _detect_code_execution(self, tool_name: str, command: str, result: str) -> bool:
        """检测是否成功执行代码"""
        # Python代码执行
        if tool_name == "execute_python":
            # 检查是否有输出或成功执行的迹象
            result_lower = result.lower()
            is_error = any(err in result_lower for err in [
                'traceback', 'error:', 'exception:', 'syntaxerror',
                'nameerror', 'typeerror', 'valueerror'
            ])
            # 有输出或没有错误
            return len(result.strip()) > 0 and not is_error

        # Shell中执行脚本
        if tool_name == "execute_shell":
            script_indicators = [
                'python ', 'python3 ', 'php ', 'node ', 'ruby ',
                'perl ', 'bash ', 'sh ', '.py', '.php', '.js'
            ]
            command_lower = command.lower()
            has_script = any(ind in command_lower for ind in script_indicators)

            result_lower = result.lower()
            is_error = any(err in result_lower for err in [
                'error', 'failed', 'not found', 'cannot execute',
                'permission denied', 'syntax error'
            ])

            return has_script and not is_error

        return False

    def _detect_command_execution(self, tool_name: str, command: str, result: str) -> bool:
        """检测是否成功执行系统命令"""
        if tool_name != "execute_shell":
            return False

        # 系统命令特征
        system_commands = [
            'ls', 'pwd', 'whoami', 'id', 'uname', 'hostname',
            'ps', 'netstat', 'ifconfig', 'ip addr', 'env',
            'echo', 'cat /etc/', 'find /', 'grep'
        ]

        command_lower = command.lower()
        has_system_cmd = any(cmd in command_lower for cmd in system_commands)

        # 结果特征
        result_lower = result.lower()
        is_error = any(err in result_lower for err in [
            'command not found', 'permission denied', 'cannot access',
            'no such file', 'failed'
        ])

        has_output = len(result.strip()) > 0

        return has_system_cmd and has_output and not is_error

    def is_achieved(self, phase: CTFPhase) -> bool:
        """检查某个阶段是否已达成"""
        return phase in self.achieved_phases

    def get_achieved_phases(self) -> list:
        """获取所有已达成的阶段"""
        return list(self.achieved_phases)

    def get_phase_summary(self) -> str:
        """获取阶段达成情况摘要"""
        if not self.achieved_phases:
            return "当前阶段：未解题"

        phases = []
        for phase in [CTFPhase.FILE_READING, CTFPhase.CODE_EXECUTION, CTFPhase.COMMAND_EXECUTION]:
            if phase in self.achieved_phases:
                phases.append(f"✓ {phase.value}")
            else:
                phases.append(f"✗ {phase.value}")

        return " | ".join(phases)

    def reset(self):
        """重置追踪器"""
        self.achieved_phases.clear()
        self.phase_details.clear()
