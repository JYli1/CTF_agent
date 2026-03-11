from src.core.agents.base import BaseAgent
from src.core.prompts import PYTHON_CODER_PROMPT

class PythonCoder(BaseAgent):
    def __init__(self):
        super().__init__(role='python', system_prompt=PYTHON_CODER_PROMPT)
