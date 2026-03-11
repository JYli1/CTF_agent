from src.core.agents.base import BaseAgent
from src.core.prompts import CTF_STRATEGIST_PROMPT

class CTFStrategist(BaseAgent):
    def __init__(self):
        # We start with a placeholder or empty prompt, it will be updated when target is set
        super().__init__(role='ctf', system_prompt=CTF_STRATEGIST_PROMPT.replace("{target_url}", "Not Set"))
        self.raw_prompt_template = CTF_STRATEGIST_PROMPT

    def chat(self, message: str, tools: list = None) -> str:
        # 兼容旧的调用方式，战略专家通常返回 content
        resp = super().chat(message, tools=tools)
        return resp.content if hasattr(resp, 'content') else str(resp)

    def set_target(self, url: str):
        final_prompt = self.raw_prompt_template.replace("{target_url}", url)
        self.system_prompt = final_prompt
        # Update the system message in history
        if self.history and self.history[0]['role'] == 'system':
            self.history[0]['content'] = final_prompt
        else:
            self.history = [{'role': 'system', 'content': final_prompt}] + self.history
