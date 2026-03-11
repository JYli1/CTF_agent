import time
from openai import OpenAI
from src.utils.config import Config

class LLMProvider:
    def __init__(self, api_key: str = None, base_url: str = None, model_name: str = None):
        # 使用全局 Config 实例
        self.config = Config

        self.api_key = api_key or self.config.LLM_API_KEY
        base_url = base_url or self.config.LLM_BASE_URL
        self.model = model_name or Config.MODEL_NAME

        if not self.api_key:
            raise ValueError(f"未找到 API Key。请检查 .env 文件配置 (当前提供商: {Config.LLM_PROVIDER})")
            
        # 使用 OpenAI 客户端 (兼容 ModelScope 和 OpenAI)
        self.client = OpenAI(
            base_url=base_url,
            api_key=self.api_key
        )

    def chat(self, messages: list, tools: list = None, tool_choice: str = "auto", retries: int = 3) -> str:
        """
        使用具有重试逻辑的 OpenAI 兼容 API 进行多轮对话。
        messages: 字典列表 {'role': '...', 'content': '...'}
        tools: 可选的工具列表
        """
        for attempt in range(retries):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = tool_choice

                response = self.client.chat.completions.create(**kwargs)

                # 返回完整的消息对象，以便处理 tool_calls
                return response.choices[0].message

            except Exception as e:
                error_str = str(e)
                error_type = type(e).__name__

                # 打印详细错误信息
                print(f"[DEBUG] {error_type}: {error_str[:300]}")

                # 如果是 JSON 解析错误，打印更多信息
                if "json" in error_str.lower() or "JSONDecodeError" in error_type:
                    print(f"[DEBUG] JSON 解析失败，可能是 API 返回了非 JSON 内容")
                    print(f"[DEBUG] 完整错误: {error_str}")

                # 检查速率限制或服务器错误
                if "429" in error_str or "500" in error_str or "502" in error_str or "503" in error_str:
                    if attempt < retries - 1:
                        wait_time = (attempt + 1) * 2  # 简单退避：2s, 4s, 6s
                        print(f"[警告] LLM 调用失败 ({error_str})。正在进行第 {attempt + 1} 次重试，等待 {wait_time} 秒...")
                        time.sleep(wait_time)
                        continue
                
                # 如果是最后一次尝试且失败，返回一个模拟的消息对象
                class MockMessage:
                    def __init__(self, content):
                        self.content = content
                        self.tool_calls = None
                return MockMessage(f"LLM 调用异常 (已重试 {attempt} 次): {error_str}")
        
        class MockMessage:
            def __init__(self, content):
                self.content = content
                self.tool_calls = None
        return MockMessage("LLM 调用失败：超过最大重试次数。")
            
    # 如果需要兼容性的别名，但 chat() 现在是主要的
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        return self.chat(messages).content
