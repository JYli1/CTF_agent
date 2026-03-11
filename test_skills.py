"""
测试技能系统
"""

import sys
sys.path.insert(0, 'd:/ctf_agent')

from src.skills.registry import skill_registry
from src.skills.loader import load_all_skills

# 测试技能注册
print("=== 技能系统测试 ===\n")

# 列出所有技能
all_skills = skill_registry.list_all()
print(f"已加载技能数量: {len(all_skills)}\n")

for skill in all_skills:
    info = skill.get_info()
    print(f"ID: {info['id']}")
    print(f"名称: {info['name']}")
    print(f"分类: {info['category']}")
    print(f"描述: {info['description']}")
    print(f"前置条件: {info['prerequisites']}")
    print(f"难度: {info['difficulty']}")
    print("-" * 50)

# 测试SQL注入技能
print("\n=== 测试SQL注入技能 ===\n")
sqli_skill = skill_registry.get("web_sqli")
if sqli_skill:
    # 模拟执行器
    class MockExecutor:
        def execute_shell(self, cmd):
            return f"[模拟执行] {cmd}"

    context = {"target_url": "http://example.com/index.php?id=1"}
    result = sqli_skill.execute(context, MockExecutor())

    print(f"执行成功: {result.success}")
    print(f"消息:\n{result.message}")
    print(f"\n发现数量: {len(result.findings)}")
    print(f"命令数量: {len(result.commands)}")

# 测试PHP分析技能
print("\n=== 测试PHP分析技能 ===\n")
php_skill = skill_registry.get("web_php_analysis")
if php_skill:
    php_code = '''<?php
$id = $_GET['id'];
$sql = "SELECT * FROM users WHERE id = $id";
$result = mysql_query($sql);
?>'''

    context = {"php_code": php_code}
    result = php_skill.execute(context, MockExecutor())

    print(f"执行成功: {result.success}")
    print(f"发现数量: {len(result.findings)}")

print("\n=== 测试完成 ===")
