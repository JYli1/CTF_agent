from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

class SkillCategory(Enum):
    """技能分类"""
    WEB = "web"
    CRYPTO = "crypto"
    REVERSE = "reverse"
    PWN = "pwn"
    MISC = "misc"

@dataclass
class SkillResult:
    """技能执行结果"""
    success: bool
    message: str
    data: Dict[str, Any] = None
    commands: List[str] = None  # 执行的命令列表
    findings: List[str] = None  # 发现的漏洞或信息

    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.commands is None:
            self.commands = []
        if self.findings is None:
            self.findings = []

class Skill:
    """
    技能基类
    每个具体技能继承此类并实现execute方法
    """

    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.category: SkillCategory = SkillCategory.WEB
        self.description: str = ""
        self.prerequisites: List[str] = []  # 前置条件（如target_url）
        self.tools_required: List[str] = []  # 需要的工具（execute_shell, execute_python）
        self.difficulty: str = "medium"  # easy, medium, hard

    def check_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, str]:
        """
        检查前置条件是否满足

        Args:
            context: 执行上下文，包含target_url等信息

        Returns:
            (是否满足, 错误信息)
        """
        for prereq in self.prerequisites:
            if prereq not in context or not context[prereq]:
                return False, f"缺少前置条件: {prereq}"
        return True, ""

    def execute(self, context: Dict[str, Any], executor: Any) -> SkillResult:
        """
        执行技能

        Args:
            context: 执行上下文
            executor: 工具执行器（包含execute_shell, execute_python等方法）

        Returns:
            SkillResult: 执行结果
        """
        raise NotImplementedError("子类必须实现execute方法")

    def get_info(self) -> Dict[str, Any]:
        """获取技能信息"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "prerequisites": self.prerequisites,
            "tools_required": self.tools_required,
            "difficulty": self.difficulty
        }
