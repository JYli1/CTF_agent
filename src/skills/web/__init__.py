"""
Web安全技能
"""

from .sqli import SQLInjectionSkill
from .php_analysis import PHPSourceAnalysisSkill
from .ssrf import SSRFSkill

__all__ = ['SQLInjectionSkill', 'PHPSourceAnalysisSkill', 'SSRFSkill']
