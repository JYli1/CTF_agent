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
        """
        检测是否在目标网站上成功实现任意文件读取

        关键特征：
        - 读取了目标网站的敏感文件（如 /etc/passwd, flag.txt, config.php 等）
        - 通过漏洞（LFI, XXE, SSRF 等）读取到了文件内容
        """
        command_lower = command.lower()
        result_lower = result.lower()

        # 1. 检测是否在利用文件读取漏洞
        file_read_exploits = [
            'file=', 'path=', 'page=', 'include=',  # LFI 参数
            '../../', '../',  # 路径穿越
            'file://', 'php://filter',  # PHP 伪协议
            '/etc/passwd', '/etc/shadow', '/proc/self',  # Linux 敏感文件
            'flag.txt', 'flag.php', 'config.php', '.env',  # CTF 常见文件
            'xxe', 'xml', '<!entity'  # XXE
        ]

        has_exploit = any(exp in command_lower for exp in file_read_exploits)

        # 2. 检测结果中是否包含文件内容特征
        file_content_indicators = [
            'root:x:', 'root:0:0',  # /etc/passwd 内容
            '<?php', '<?=',  # PHP 代码
            'flag{', 'ctf{', 'flag:',  # Flag 格式
            'password', 'secret', 'api_key',  # 配置文件内容
            'database', 'db_host', 'db_user'  # 数据库配置
        ]

        has_file_content = any(ind in result_lower for ind in file_content_indicators)

        # 3. 排除错误情况
        is_error = any(err in result_lower for err in [
            'error', 'failed', 'permission denied', 'no such file',
            'cannot open', 'not found', '404', '403', '500',
            'invalid', 'forbidden'
        ])

        # 4. 结果有实质内容
        has_content = len(result.strip()) > 50

        return has_exploit and (has_file_content or (has_content and not is_error))

    def _detect_code_execution(self, tool_name: str, command: str, result: str) -> bool:
        """
        检测是否在目标网站上成功实现任意代码执行（RCE）

        关键特征：
        - 通过漏洞在目标服务器上执行了代码
        - 不是本地 Python 代码执行，而是远程代码执行
        """
        command_lower = command.lower()
        result_lower = result.lower()

        # 1. 检测是否在利用代码执行漏洞
        code_exec_exploits = [
            'eval(', 'exec(', 'system(',  # PHP/Python 代码执行函数
            'shell_exec', 'passthru', 'popen',  # PHP 命令执行
            'unserialize', 'pickle.loads',  # 反序列化
            '__import__', 'compile(',  # Python 动态执行
            'cmd=', 'command=', 'exec=',  # RCE 参数
            '<?php', '<?=',  # PHP 代码注入
            'payload', 'exploit', 'reverse_shell'  # 明确的利用
        ]

        has_exploit = any(exp in command_lower for exp in code_exec_exploits)

        # 2. 检测是否是针对目标网站的请求
        is_remote_target = any(indicator in command_lower for indicator in [
            'http://', 'https://',  # 网络请求
            'curl ', 'wget ', 'requests.',  # HTTP 客户端
            'post(', 'get(', '.request'  # HTTP 方法
        ])

        # 3. 检测结果中是否有代码执行成功的迹象
        exec_success_indicators = [
            'uid=', 'gid=',  # whoami/id 命令输出
            'www-data', 'apache', 'nginx',  # Web 服务器用户
            '/bin/', '/usr/bin/',  # 系统路径
            'flag{', 'ctf{',  # 直接获取 Flag
            'root', 'admin'  # 权限相关
        ]

        has_exec_result = any(ind in result_lower for ind in exec_success_indicators)

        # 4. 排除本地代码执行和错误
        is_local_only = tool_name == "execute_python" and not is_remote_target

        is_error = any(err in result_lower for err in [
            'traceback', 'error:', 'exception:', 'failed',
            'connection refused', 'timeout', '404', '403', '500'
        ])

        # 5. 有实质性输出
        has_output = len(result.strip()) > 20

        return (has_exploit and is_remote_target and (has_exec_result or (has_output and not is_error))) and not is_local_only

    def _detect_command_execution(self, tool_name: str, command: str, result: str) -> bool:
        """
        检测是否在目标网站上成功实现任意命令执行

        关键特征：
        - 通过漏洞在目标服务器上执行了系统命令
        - 获取到了目标服务器的系统信息
        """
        if tool_name != "execute_shell":
            return False

        command_lower = command.lower()
        result_lower = result.lower()

        # 1. 检测是否在利用命令执行漏洞
        cmd_exec_exploits = [
            'cmd=', 'command=', 'exec=', 'ping=',  # 命令注入参数
            ';', '|', '&&', '||', '`', '$(',  # 命令连接符
            'curl ', 'wget ', 'nc ', 'netcat',  # 常用命令
            'bash -c', 'sh -c', '/bin/sh',  # Shell 调用
        ]

        has_exploit = any(exp in command_lower for exp in cmd_exec_exploits)

        # 2. 检测是否针对远程目标
        is_remote_target = any(indicator in command_lower for indicator in [
            'http://', 'https://',
            'requests.', 'curl ', 'wget '
        ])

        # 3. 检测结果中是否有命令执行成功的特征
        cmd_success_indicators = [
            'uid=', 'gid=', 'groups=',  # id 命令
            'linux', 'ubuntu', 'debian', 'centos',  # uname 输出
            '/home/', '/var/', '/etc/', '/usr/',  # 文件系统路径
            'www-data', 'apache', 'nginx', 'root',  # 用户名
            'flag{', 'ctf{',  # Flag
            'total ', 'drwx', '-rw-',  # ls 输出
            'inet ', 'ether ',  # ifconfig 输出
        ]

        has_cmd_result = any(ind in result_lower for ind in cmd_success_indicators)

        # 4. 排除错误
        is_error = any(err in result_lower for err in [
            'command not found', 'permission denied', 'cannot access',
            'no such file', 'failed', 'error', '404', '403', '500',
            'connection refused', 'timeout'
        ])

        # 5. 有实质性输出
        has_output = len(result.strip()) > 20

        return has_exploit and is_remote_target and (has_cmd_result or (has_output and not is_error))

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
