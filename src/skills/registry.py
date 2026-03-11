from typing import Dict, List, Optional
from .base import Skill, SkillCategory

class SkillRegistry:
    """
    技能注册中心
    管理所有可用技能
    """

    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._categories: Dict[SkillCategory, List[str]] = {
            category: [] for category in SkillCategory
        }

    def register(self, skill: Skill):
        """注册技能"""
        self._skills[skill.id] = skill
        if skill.category not in self._categories:
            self._categories[skill.category] = []
        self._categories[skill.category].append(skill.id)

    def get(self, skill_id: str) -> Optional[Skill]:
        """获取技能"""
        return self._skills.get(skill_id)

    def get_by_category(self, category: SkillCategory) -> List[Skill]:
        """获取某个分类的所有技能"""
        skill_ids = self._categories.get(category, [])
        return [self._skills[sid] for sid in skill_ids if sid in self._skills]

    def list_all(self) -> List[Skill]:
        """列出所有技能"""
        return list(self._skills.values())

    def search(self, keyword: str) -> List[Skill]:
        """搜索技能"""
        results = []
        keyword_lower = keyword.lower()
        for skill in self._skills.values():
            if (keyword_lower in skill.name.lower() or
                keyword_lower in skill.description.lower() or
                keyword_lower in skill.id.lower()):
                results.append(skill)
        return results

    def get_skill_list_text(self, category: Optional[SkillCategory] = None) -> str:
        """
        获取技能列表的文本描述（用于提示词）

        Args:
            category: 如果指定，只返回该分类的技能

        Returns:
            格式化的技能列表文本
        """
        if category:
            skills = self.get_by_category(category)
            text = f"## {category.value.upper()}技能\n\n"
        else:
            skills = self.list_all()
            text = "## 所有可用技能\n\n"

        for skill in skills:
            text += f"### {skill.id}\n"
            text += f"- 名称: {skill.name}\n"
            text += f"- 描述: {skill.description}\n"
            text += f"- 难度: {skill.difficulty}\n"
            text += f"- 前置条件: {', '.join(skill.prerequisites)}\n"
            text += "\n"

        return text


# 全局技能注册中心
skill_registry = SkillRegistry()
