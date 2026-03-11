"""
技能自动加载器
自动扫描并导入所有技能模块
"""

import os
import importlib
import pkgutil
from pathlib import Path

def auto_load_skills():
    """
    自动加载所有技能
    扫描skills目录下的所有Python文件并导入
    """
    print("[技能系统] 开始自动加载技能...")

    # 获取skills目录路径
    skills_dir = Path(__file__).parent

    # 扫描所有子目录
    categories = ['web', 'crypto', 'reverse', 'pwn', 'misc']

    for category in categories:
        category_path = skills_dir / category
        if not category_path.exists():
            continue

        # 扫描该分类下的所有.py文件
        for file_path in category_path.glob('*.py'):
            if file_path.name.startswith('_'):
                continue

            # 构建模块名
            module_name = f"src.skills.{category}.{file_path.stem}"

            try:
                # 导入模块（装饰器会自动注册）
                importlib.import_module(module_name)
            except Exception as e:
                print(f"[技能系统] 加载模块失败 {module_name}: {e}")

    from .registry import skill_registry
    print(f"[技能系统] 自动加载完成，共加载 {len(skill_registry.list_all())} 个技能")
