"""
技能加载器
使用自动加载机制
"""

from .auto_loader import auto_load_skills

def load_all_skills():
    """加载所有技能（使用自动加载）"""
    auto_load_skills()

# 自动加载
load_all_skills()
