import os
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

class Config:
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "data/chroma_db")
    KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", "data/knowledge_base")
    
    
    # --- LLM 配置 ---
    # 提供商: "openai" 或 "modelscope"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "modelscope").lower()
    
    # 模型名称
    MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3.2")
    
    # ModelScope 推理 API 基础 URL
    MODELSCOPE_BASE_URL = "https://api-inference.modelscope.cn/v1"
    
    # --- SSH 配置 (Kali Linux) ---
    SSH_HOST = os.getenv("SSH_HOST")
    SSH_PORT = int(os.getenv("SSH_PORT", "22"))
    SSH_USER = os.getenv("SSH_USER")
    SSH_PASSWORD = os.getenv("SSH_PASSWORD")
    SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")

    @property
    def LLM_API_KEY(self):
        if self.LLM_PROVIDER == "openai":
            return self.OPENAI_API_KEY
        return self.DASHSCOPE_API_KEY
        
    @property
    def LLM_BASE_URL(self):
        if self.LLM_PROVIDER == "openai":
            return os.getenv("OPENAI_BASE_URL", None) 
        return self.MODELSCOPE_BASE_URL

    @staticmethod
    def validate():
        if Config.LLM_PROVIDER == "modelscope" and not Config.DASHSCOPE_API_KEY:
             print("警告: 未找到 DASHSCOPE_API_KEY，但 LLM_PROVIDER 设置为 modelscope")
        if Config.LLM_PROVIDER == "openai" and not Config.OPENAI_API_KEY:
             print("警告: 未找到 OPENAI_API_KEY，但 LLM_PROVIDER 设置为 openai")
