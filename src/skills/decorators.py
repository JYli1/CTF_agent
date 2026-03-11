"""
技能装饰器和自动注册系统
"""

from typing import Type
from .base import Skill
from .registry import skill_registry

def register_skill(skill_class: Type[Skill]) -> Type[Skill]:
    """
    技能装饰器，自动注册技能到全局注册中心

    使用方法：
    @register_skill
    class MySkill(Skill):
        def __init__(self):
            super().__init__()
            self.id = "my_skill"
            ...
    """
    # 实例化并注册
    try:
        skill_instance = skill_class()
        skill_registry.register(skill_instance)
        print(f"[技能系统] 已注册技能: {skill_instance.id} - {skill_instance.name}")
    except Exception as e:
        print(f"[技能系统] 注册技能失败 {skill_class.__name__}: {e}")

    return skill_class
