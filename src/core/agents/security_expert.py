from src.core.agents.base import BaseAgent
from src.core.prompts import SECURITY_EXPERT_PROMPT

class SecurityExpert(BaseAgent):
    def __init__(self):
        super().__init__(role='security', system_prompt=SECURITY_EXPERT_PROMPT)
