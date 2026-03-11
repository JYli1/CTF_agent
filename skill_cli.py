"""
技能管理CLI工具
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.skills.skill_generator import create_skill
from src.skills.registry import skill_registry
from src.skills.loader import load_all_skills

def list_skills():
    """列出所有已加载的技能"""
    skills = skill_registry.list_all()

    if not skills:
        print("未找到任何技能")
        return

    print(f"\n共有 {len(skills)} 个技能:\n")
    print(f"{'ID':<20} {'名称':<20} {'分类':<10} {'难度':<10}")
    print("=" * 70)

    for skill in skills:
        info = skill.get_info()
        print(f"{info['id']:<20} {info['name']:<20} {info['category']:<10} {info['difficulty']:<10}")

def show_skill(skill_id: str):
    """显示技能详情"""
    skill = skill_registry.get(skill_id)

    if not skill:
        print(f"未找到技能: {skill_id}")
        return

    info = skill.get_info()
    print(f"\n技能详情:")
    print(f"  ID: {info['id']}")
    print(f"  名称: {info['name']}")
    print(f"  分类: {info['category']}")
    print(f"  描述: {info['description']}")
    print(f"  前置条件: {', '.join(info['prerequisites'])}")
    print(f"  需要工具: {', '.join(info['tools_required'])}")
    print(f"  难度: {info['difficulty']}")

def new_skill():
    """交互式创建新技能"""
    print("\n=== 创建新技能 ===\n")

    skill_id = input("技能ID (如 web_xss): ").strip()
    if not skill_id:
        print("技能ID不能为空")
        return

    skill_name = input("技能名称 (如 XSS检测与利用): ").strip()
    if not skill_name:
        print("技能名称不能为空")
        return

    category = input("技能分类 (WEB/CRYPTO/REVERSE/PWN/MISC) [默认: WEB]: ").strip().upper() or "WEB"

    description = input(f"技能描述 [默认: {skill_name}]: ").strip() or skill_name

    print("\n前置条件 (逗号分隔，如 target_url,php_code) [默认: target_url]:")
    prereq_input = input("> ").strip()
    prerequisites = [p.strip() for p in prereq_input.split(',')] if prereq_input else ["target_url"]

    print("\n需要工具 (逗号分隔，如 execute_shell,execute_python) [默认: execute_shell]:")
    tools_input = input("> ").strip()
    tools_required = [t.strip() for t in tools_input.split(',')] if tools_input else ["execute_shell"]

    difficulty = input("难度 (easy/medium/hard) [默认: medium]: ").strip() or "medium"

    print("\n即将创建技能:")
    print(f"  ID: {skill_id}")
    print(f"  名称: {skill_name}")
    print(f"  分类: {category}")
    print(f"  描述: {description}")
    print(f"  前置条件: {prerequisites}")
    print(f"  需要工具: {tools_required}")
    print(f"  难度: {difficulty}")

    confirm = input("\n确认创建? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return

    success = create_skill(
        skill_id=skill_id,
        skill_name=skill_name,
        category=category,
        description=description,
        prerequisites=prerequisites,
        tools_required=tools_required,
        difficulty=difficulty
    )

    if success:
        print("\n✓ 技能创建成功！")
        print("下一步:")
        print(f"  1. 编辑文件实现execute()方法")
        print(f"  2. 重启程序，技能将自动加载")

def main():
    if len(sys.argv) < 2:
        print("CTF Agent 技能管理工具")
        print("\n用法:")
        print("  python skill_cli.py list              - 列出所有技能")
        print("  python skill_cli.py show <skill_id>   - 显示技能详情")
        print("  python skill_cli.py new               - 创建新技能")
        print("\n示例:")
        print("  python skill_cli.py list")
        print("  python skill_cli.py show web_sqli")
        print("  python skill_cli.py new")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_skills()
    elif command == "show":
        if len(sys.argv) < 3:
            print("用法: python skill_cli.py show <skill_id>")
            sys.exit(1)
        show_skill(sys.argv[2])
    elif command == "new":
        new_skill()
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
