import os
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

class Config:
    """
    CTF Agent 配置类
    所有配置从 .env 文件读取
    """

    # ============================================================
    # 1. API 密钥
    # ============================================================
    SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

    # ============================================================
    # 2. LLM 基础配置
    # ============================================================
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
    MODEL_NAME = os.getenv("MODEL_NAME", "Pro/zai-org/GLM-5")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
    MODELSCOPE_BASE_URL = "https://api-inference.modelscope.cn/v1"

    # ============================================================
    # 3. 三大专家配置
    # ============================================================
    # CTF 战略专家
    CTF_API_KEY = os.getenv("CTF_API_KEY") or SILICONFLOW_API_KEY
    CTF_BASE_URL = os.getenv("CTF_BASE_URL", "https://api.siliconflow.cn/v1")
    CTF_MODEL = os.getenv("CTF_MODEL", "Pro/zai-org/GLM-5")

    # Python 编程专家
    PYTHON_API_KEY = os.getenv("PYTHON_API_KEY") or SILICONFLOW_API_KEY
    PYTHON_BASE_URL = os.getenv("PYTHON_BASE_URL", "https://api.siliconflow.cn/v1")
    PYTHON_MODEL = os.getenv("PYTHON_MODEL", "Pro/moonshotai/Kimi-K2.5")

    # 安全渗透专家
    SECURITY_API_KEY = os.getenv("SECURITY_API_KEY") or SILICONFLOW_API_KEY
    SECURITY_BASE_URL = os.getenv("SECURITY_BASE_URL", "https://api.siliconflow.cn/v1")
    SECURITY_MODEL = os.getenv("SECURITY_MODEL", "Pro/zai-org/GLM-5")

    # ============================================================
    # 4. RAG 知识库配置
    # ============================================================
    # Embedding 模型
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY") or SILICONFLOW_API_KEY
    EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "https://api.siliconflow.cn/v1")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-8B")

    # 存储路径
    CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "data/chroma_db")
    KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", "data/knowledge_base")

    # ============================================================
    # 5. SSH 配置
    # ============================================================
    SSH_HOST = os.getenv("SSH_HOST")
    SSH_PORT = int(os.getenv("SSH_PORT", "22"))
    SSH_USER = os.getenv("SSH_USER", "kali")
    SSH_PASSWORD = os.getenv("SSH_PASSWORD")
    SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")

    # ============================================================
    # 6. 高级配置
    # ============================================================
    MAX_SUB_STEPS = int(os.getenv("MAX_SUB_STEPS", "5"))
    RAG_DISTANCE_THRESHOLD = float(os.getenv("RAG_DISTANCE_THRESHOLD", "1.5"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/ctf_agent.log")

    # ============================================================
    # 辅助方法
    # ============================================================

    @property
    def LLM_API_KEY(self):
        """获取全局 LLM API Key"""
        if self.LLM_PROVIDER == "openai":
            return self.OPENAI_API_KEY or self.SILICONFLOW_API_KEY
        return self.DASHSCOPE_API_KEY

    @property
    def LLM_BASE_URL(self):
        """获取全局 LLM Base URL"""
        if self.LLM_PROVIDER == "openai":
            return self.OPENAI_BASE_URL
        return self.MODELSCOPE_BASE_URL

    def get_agent_config(self, role: str):
        """
        获取指定专家的配置

        Args:
            role: 'ctf', 'python', 'security'

        Returns:
            (api_key, base_url, model)
        """
        role = role.lower()

        if role == 'ctf':
            return (self.CTF_API_KEY, self.CTF_BASE_URL, self.CTF_MODEL)
        elif role == 'python':
            return (self.PYTHON_API_KEY, self.PYTHON_BASE_URL, self.PYTHON_MODEL)
        elif role == 'security':
            return (self.SECURITY_API_KEY, self.SECURITY_BASE_URL, self.SECURITY_MODEL)

        # 默认返回全局配置
        return (self.LLM_API_KEY, self.LLM_BASE_URL, self.MODEL_NAME)

    @staticmethod
    def validate():
        """验证配置完整性"""
        errors = []
        warnings = []

        # 检查必需的 API Key
        if not Config.SILICONFLOW_API_KEY and not Config.OPENAI_API_KEY:
            errors.append("未配置 API Key (SILICONFLOW_API_KEY 或 OPENAI_API_KEY)")

        # 检查专家配置
        if not Config.CTF_API_KEY:
            warnings.append("CTF 战略专家未配置 API Key，将使用全局配置")
        if not Config.PYTHON_API_KEY:
            warnings.append("Python 专家未配置 API Key，将使用全局配置")
        if not Config.SECURITY_API_KEY:
            warnings.append("安全专家未配置 API Key，将使用全局配置")

        # 检查 Embedding 配置
        if not Config.EMBEDDING_API_KEY:
            warnings.append("Embedding 未配置 API Key，将使用全局配置")

        # 检查 SSH 配置
        if not Config.SSH_HOST:
            warnings.append("未配置 SSH_HOST，安全专家将无法使用远程工具")

        # 输出结果
        if errors:
            print("\n[错误] 配置验证失败:")
            for error in errors:
                print(f"  ❌ {error}")
            return False

        if warnings:
            print("\n[提示] 配置建议:")
            for warning in warnings:
                print(f"  ⚠️  {warning}")

        print("\n[成功] 配置验证通过")
        return True

    @staticmethod
    def print_config():
        """打印当前配置（隐藏敏感信息）"""
        def mask_key(key):
            if not key:
                return "未配置"
            return f"{key[:10]}...{key[-4:]}" if len(key) > 14 else "***"

        print("\n" + "="*60)
        print("CTF Agent 当前配置")
        print("="*60)

        print("\n[LLM 配置]")
        print(f"  提供商: {Config.LLM_PROVIDER}")
        print(f"  Base URL: {Config.OPENAI_BASE_URL}")
        print(f"  默认模型: {Config.MODEL_NAME}")

        print("\n[专家配置]")
        print(f"  CTF 战略专家: {Config.CTF_MODEL}")
        print(f"  Python 专家: {Config.PYTHON_MODEL}")
        print(f"  安全专家: {Config.SECURITY_MODEL}")

        print("\n[RAG 配置]")
        print(f"  Embedding 模型: {Config.EMBEDDING_MODEL}")
        print(f"  知识库路径: {Config.CHROMA_DB_DIR}")

        print("\n[SSH 配置]")
        print(f"  主机: {Config.SSH_HOST or '未配置'}")
        print(f"  用户: {Config.SSH_USER}")

        print("\n[API Key 状态]")
        print(f"  硅基流动: {mask_key(Config.SILICONFLOW_API_KEY)}")
        print(f"  CTF 专家: {mask_key(Config.CTF_API_KEY)}")
        print(f"  Python 专家: {mask_key(Config.PYTHON_API_KEY)}")
        print(f"  安全专家: {mask_key(Config.SECURITY_API_KEY)}")
        print(f"  Embedding: {mask_key(Config.EMBEDDING_API_KEY)}")

        print("\n" + "="*60 + "\n")


# 创建全局配置实例
Config = Config()


if __name__ == "__main__":
    # 测试配置
    Config.print_config()
    Config.validate()
