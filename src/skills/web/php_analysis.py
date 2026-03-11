from typing import Dict, Any
from ..base import Skill, SkillCategory, SkillResult
from ..decorators import register_skill

@register_skill
class PHPSourceAnalysisSkill(Skill):
    """
    PHP源码分析技能
    """

    def __init__(self):
        super().__init__()
        self.id = "web_php_analysis"
        self.name = "PHP源码分析"
        self.category = SkillCategory.WEB
        self.description = "分析PHP源码，识别漏洞点和利用思路"
        self.prerequisites = ["php_code"]
        self.tools_required = ["execute_python"]
        self.difficulty = "medium"

    def execute(self, context: Dict[str, Any], executor: Any) -> SkillResult:
        """
        执行PHP源码分析

        分析重点：
        1. 危险函数识别
        2. 变量追踪
        3. 过滤绕过
        4. 逻辑漏洞
        5. 反序列化漏洞
        """
        # 检查前置条件
        ok, msg = self.check_prerequisites(context)
        if not ok:
            return SkillResult(success=False, message=msg)

        php_code = context["php_code"]
        findings = []
        commands = []

        # 分析脚本
        analysis_script = f'''
import re

php_code = """
{php_code}
"""

findings = []

# 1. 危险函数检测
dangerous_functions = [
    'eval', 'assert', 'system', 'exec', 'shell_exec', 'passthru',
    'popen', 'proc_open', 'pcntl_exec', 'create_function',
    'unserialize', 'file_get_contents', 'file_put_contents',
    'include', 'require', 'include_once', 'require_once',
    'preg_replace', 'call_user_func', 'call_user_func_array'
]

for func in dangerous_functions:
    pattern = rf'\\b{{func}}\\s*\\('
    if re.search(pattern, php_code, re.IGNORECASE):
        findings.append(f"[危险函数] 发现 {{{{func}}}}() 函数")

# 2. 变量追踪 - $_GET, $_POST, $_REQUEST, $_COOKIE
user_inputs = ['$_GET', '$_POST', '$_REQUEST', '$_COOKIE', '$_SERVER']
for inp in user_inputs:
    if inp in php_code:
        findings.append(f"[用户输入] 发现 {{{{inp}}}} 变量")

# 3. SQL查询检测
sql_patterns = [
    r'mysql_query\\s*\\(',
    r'mysqli_query\\s*\\(',
    r'->query\\s*\\(',
    r'SELECT\\s+.*\\s+FROM',
    r'INSERT\\s+INTO',
    r'UPDATE\\s+.*\\s+SET',
    r'DELETE\\s+FROM'
]

for pattern in sql_patterns:
    if re.search(pattern, php_code, re.IGNORECASE):
        findings.append(f"[SQL查询] 发现SQL操作")
        break

# 4. 文件操作检测
file_ops = ['fopen', 'fread', 'fwrite', 'file', 'readfile', 'file_get_contents', 'file_put_contents']
for op in file_ops:
    if re.search(rf'\\b{{op}}\\s*\\(', php_code, re.IGNORECASE):
        findings.append(f"[文件操作] 发现 {{{{op}}}}() 函数")

# 5. 反序列化检测
if 'unserialize' in php_code:
    findings.append("[反序列化] 发现unserialize()函数，可能存在反序列化漏洞")
    # 查找魔术方法
    magic_methods = ['__wakeup', '__destruct', '__toString', '__call']
    for method in magic_methods:
        if method in php_code:
            findings.append(f"[魔术方法] 发现 {{{{method}}}} 方法")

# 6. 命令执行检测
cmd_funcs = ['system', 'exec', 'shell_exec', 'passthru', '`']
for func in cmd_funcs:
    if func in php_code:
        findings.append(f"[命令执行] 发现命令执行函数/操作符")
        break

# 7. 文件包含检测
include_funcs = ['include', 'require', 'include_once', 'require_once']
for func in include_funcs:
    if re.search(rf'\\b{{func}}\\s*\\(', php_code, re.IGNORECASE):
        findings.append(f"[文件包含] 发现 {{{{func}}}} 语句")

# 8. 过滤函数检测
filter_funcs = ['htmlspecialchars', 'addslashes', 'mysql_real_escape_string',
                'strip_tags', 'preg_replace', 'str_replace', 'filter_var']
filters_found = []
for func in filter_funcs:
    if re.search(rf'\\b{{func}}\\s*\\(', php_code, re.IGNORECASE):
        filters_found.append(func)

if filters_found:
    findings.append(f"[过滤函数] 发现过滤: {{{{', '.join(filters_found)}}}}")
else:
    findings.append("[无过滤] 未发现明显的输入过滤")

# 9. 弱比较检测
if '==' in php_code:
    findings.append("[弱比较] 发现==比较，可能存在类型混淆漏洞")

# 10. extract()函数检测
if 'extract(' in php_code:
    findings.append("[变量覆盖] 发现extract()函数，可能存在变量覆盖漏洞")

print("\\n".join(findings))
'''

        commands.append(analysis_script)

        # 构建分析报告
        message = f"""PHP源码分析技能已启动

源码长度: {len(php_code)} 字符

分析维度：
1. 危险函数识别（eval, system, exec等）
2. 用户输入追踪（$_GET, $_POST等）
3. SQL注入风险点
4. 文件操作函数
5. 反序列化漏洞
6. 命令执行风险
7. 文件包含漏洞
8. 输入过滤机制
9. 弱类型比较
10. 变量覆盖风险

常见PHP漏洞类型：
- SQL注入: 未过滤的SQL查询
- 命令注入: system/exec等函数
- 文件包含: include/require动态参数
- 反序列化: unserialize()处理用户输入
- 变量覆盖: extract()/${{}}等
- 弱类型比较: ==导致的绕过
- XXE: simplexml_load_string处理XML
- SSRF: file_get_contents/curl处理URL

请Python专家执行分析脚本，识别所有潜在漏洞点。
"""

        findings.extend([
            "分析PHP源码中的危险函数",
            "追踪用户输入变量",
            "检测SQL注入风险",
            "识别命令执行点",
            "查找反序列化漏洞",
            "检查输入过滤机制"
        ])

        return SkillResult(
            success=True,
            message=message,
            data={
                "code_length": len(php_code),
                "analysis_points": [
                    "dangerous_functions",
                    "user_inputs",
                    "sql_injection",
                    "command_execution",
                    "file_inclusion",
                    "deserialization",
                    "weak_comparison",
                    "variable_override"
                ]
            },
            commands=commands,
            findings=findings
        )
