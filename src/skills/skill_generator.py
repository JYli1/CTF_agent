"""
技能模板生成器
快速创建新技能的脚手架
"""

import os
from pathlib import Path

SKILL_TEMPLATE = '''from typing import Dict, Any
from ..base import Skill, SkillCategory, SkillResult
from ..decorators import register_skill

@register_skill
class {class_name}(Skill):
    """
    {description}
    """

    def __init__(self):
        super().__init__()
        self.id = "{skill_id}"
        self.name = "{skill_name}"
        self.category = SkillCategory.{category}
        self.description = "{description}"
        self.prerequisites = {prerequisites}
        self.tools_required = {tools_required}
        self.difficulty = "{difficulty}"

    def execute(self, context: Dict[str, Any], executor: Any) -> SkillResult:
        """
        执行{skill_name}

        Args:
            context: 执行上下文
            executor: 工具执行器

        Returns:
            SkillResult: 执行结果
        """
        # 检查前置条件
        ok, msg = self.check_prerequisites(context)
        if not ok:
            return SkillResult(success=False, message=msg)

        # TODO: 实现技能逻辑
        commands = []
        findings = []

        # 示例：添加命令
        # cmd1 = f"curl {{context['target_url']}}"
        # commands.append(cmd1)
        # findings.append("测试基础访问")

        message = f"""{{self.name}}技能已准备就绪

目标: {{context.get('target_url', 'N/A')}}

TODO: 添加技能执行建议和步骤说明
"""

        return SkillResult(
            success=True,
            message=message,
            data={{}},
            commands=commands,
            findings=findings
        )
'''

def create_skill(
    skill_id: str,
    skill_name: str,
    category: str = "WEB",
    description: str = "",
    prerequisites: list = None,
    tools_required: list = None,
    difficulty: str = "medium"
):
    """
    创建新技能

    Args:
        skill_id: 技能ID，如 "web_xss"
        skill_name: 技能名称，如 "XSS检测与利用"
        category: 技能分类，如 "WEB", "CRYPTO", "REVERSE", "PWN", "MISC"
        description: 技能描述
        prerequisites: 前置条件列表，如 ["target_url"]
        tools_required: 需要的工具列表，如 ["execute_shell"]
        difficulty: 难度，如 "easy", "medium", "hard"
    """
    if prerequisites is None:
        prerequisites = ["target_url"]
    if tools_required is None:
        tools_required = ["execute_shell"]

    # 生成类名
    class_name = ''.join(word.capitalize() for word in skill_id.split('_')) + 'Skill'

    # 生成文件名
    file_name = skill_id.replace(f"{category.lower()}_", "") + ".py"

    # 确定目录
    category_lower = category.lower()
    skills_dir = Path(__file__).parent
    category_dir = skills_dir / category_lower

    # 创建目录（如果不存在）
    category_dir.mkdir(exist_ok=True)

    # 生成文件路径
    file_path = category_dir / file_name

    # 检查文件是否已存在
    if file_path.exists():
        print(f"[错误] 文件已存在: {file_path}")
        return False

    # 生成代码
    code = SKILL_TEMPLATE.format(
        class_name=class_name,
        skill_id=skill_id,
        skill_name=skill_name,
        category=category.upper(),
        description=description or skill_name,
        prerequisites=prerequisites,
        tools_required=tools_required,
        difficulty=difficulty
    )

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"[成功] 技能已创建: {file_path}")
    print(f"[提示] 请编辑文件实现execute()方法")
    print(f"[提示] 重启程序后技能将自动加载")

    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("使用方法: python skill_generator.py <skill_id> <skill_name> [category] [description]")
        print("示例: python skill_generator.py web_xss 'XSS检测与利用' WEB 'XSS漏洞检测和利用'")
        sys.exit(1)

    skill_id = sys.argv[1]
    skill_name = sys.argv[2]
    category = sys.argv[3] if len(sys.argv) > 3 else "WEB"
    description = sys.argv[4] if len(sys.argv) > 4 else skill_name

    create_skill(skill_id, skill_name, category, description)
