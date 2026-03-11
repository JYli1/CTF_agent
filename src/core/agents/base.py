from src.core.llm import LLMProvider
from src.utils.config import Config

class BaseAgent:
    def __init__(self, role: str, system_prompt: str):
        self.role = role
        self.config = Config

        # Get agent-specific config
        api_key, base_url, model = self.config.get_agent_config(role)
        
        self.llm = LLMProvider(api_key=api_key, base_url=base_url, model_name=model)
        self.system_prompt = system_prompt
        self.history = [{'role': 'system', 'content': system_prompt}]

    def chat(self, message: str, tools: list = None) -> str:
        self.history.append({'role': 'user', 'content': message})
        response_message = self.llm.chat(self.history, tools=tools)
        
        # 将回复添加到历史记录（OpenAI 要求 tool_calls 必须跟在 assistant 消息中）
        msg_dict = {'role': 'assistant', 'content': response_message.content}
        if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
            msg_dict['tool_calls'] = response_message.tool_calls
        
        self.history.append(msg_dict)
        return response_message
    
    def reset(self):
        self.history = [{'role': 'system', 'content': self.system_prompt}]
