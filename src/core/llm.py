import time
from openai import OpenAI
from src.utils.config import Config

class LLMProvider:
    def __init__(self):
        # 实例化 Config 对象以访问属性
        self.config = Config()
        
        self.api_key = self.config.LLM_API_KEY
        if not self.api_key:
            raise ValueError(f"未找到 API Key。请检查 .env 文件配置 (当前提供商: {Config.LLM_PROVIDER})")
            
        # 使用 OpenAI 客户端 (兼容 ModelScope 和 OpenAI)
        self.client = OpenAI(
            base_url=self.config.LLM_BASE_URL,
            api_key=self.api_key
        )
        self.model = Config.MODEL_NAME

    def chat(self, messages: list, retries: int = 3) -> str:
        """
        使用具有重试逻辑的 OpenAI 兼容 API 进行多轮对话。
        messages: 字典列表 {'role': '...', 'content': '...'}
        """
        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=False # Agent 逻辑在非流式传输下更容易
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                error_str = str(e)
                # 检查速率限制或服务器错误
                if "429" in error_str or "500" in error_str or "502" in error_str or "503" in error_str:
                    if attempt < retries - 1:
                        wait_time = (attempt + 1) * 2  # 简单退避：2s, 4s, 6s
                        print(f"[警告] LLM 调用失败 ({error_str})。正在进行第 {attempt + 1} 次重试，等待 {wait_time} 秒...")
                        time.sleep(wait_time)
                        continue
                
                return f"LLM 调用异常 (已重试 {attempt} 次): {error_str}"
        
        return "LLM 调用失败：超过最大重试次数。"
            
    # 如果需要兼容性的别名，但 chat() 现在是主要的
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        return self.chat(messages)
