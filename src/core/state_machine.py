from enum import Enum
from typing import List
from datetime import datetime


class CTFState(Enum):
    """CTF解题状态枚举"""
    INIT = "初始化"
    INFO_GATHERING = "信息收集"
    VULN_DETECTION = "漏洞识别"
    VULN_VERIFICATION = "漏洞验证"
    EXPLOITATION = "漏洞利用"
    FLAG_EXTRACTION = "Flag提取"
    COMPLETED = "完成"
    STUCK = "卡住"


class StateManager:
    """状态管理器"""

    def __init__(self):
        self.current_state = CTFState.INIT
        self.state_history = [(CTFState.INIT, datetime.now())]
        self.attempts_in_state = 0
        self.max_attempts_per_state = 3

    def transition(self, new_state: CTFState, reason: str = ""):
        """
        状态转换

        参数:
            new_state: 新状态
            reason: 转换原因
        """
        if new_state != self.current_state:
            print(f"[状态转换] {self.current_state.value} → {new_state.value}")
            if reason:
                print(f"  原因: {reason}")

            self.current_state = new_state
            self.state_history.append((new_state, datetime.now()))
            self.attempts_in_state = 0
        else:
            self.attempts_in_state += 1

    def is_stuck(self) -> bool:
        """判断是否卡住（同一状态重复太多次）"""
        return self.attempts_in_state >= self.max_attempts_per_state

    def get_progress(self) -> float:
        """
        获取解题进度（0.0-1.0）
        """
        state_progress = {
            CTFState.INIT: 0.0,
            CTFState.INFO_GATHERING: 0.2,
            CTFState.VULN_DETECTION: 0.4,
            CTFState.VULN_VERIFICATION: 0.6,
            CTFState.EXPLOITATION: 0.8,
            CTFState.FLAG_EXTRACTION: 0.9,
            CTFState.COMPLETED: 1.0,
        }
        return state_progress.get(self.current_state, 0.0)

    def get_allowed_actions(self) -> List[str]:
        """获取当前状态允许的操作"""
        actions_map = {
            CTFState.INFO_GATHERING: [
                "curl获取网页",
                "nmap端口扫描",
                "查看源码",
                "目录爆破"
            ],
            CTFState.VULN_DETECTION: [
                "分析源码",
                "测试注入",
                "查找危险函数",
                "分析逻辑漏洞"
            ],
            CTFState.VULN_VERIFICATION: [
                "手动测试注入",
                "构造Payload",
                "验证漏洞存在"
            ],
            CTFState.EXPLOITATION: [
                "使用sqlmap",
                "编写利用脚本",
                "执行命令",
                "提取数据"
            ],
            CTFState.FLAG_EXTRACTION: [
                "查找flag表",
                "读取flag文件",
                "搜索flag格式"
            ],
        }
        return actions_map.get(self.current_state, [])
