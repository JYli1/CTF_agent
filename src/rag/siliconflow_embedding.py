"""
硅基流动 Embedding Function for ChromaDB
"""
import requests
from typing import List
from chromadb.api.types import EmbeddingFunction, Documents


class SiliconFlowEmbeddingFunction(EmbeddingFunction):
    """
    使用硅基流动 API 的 Embedding Function
    支持模型: BAAI/bge-large-zh-v1.5, BAAI/bge-large-en-v1.5 等
    """

    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn/v1",
                 model: str = "BAAI/bge-large-zh-v1.5"):
        """
        初始化硅基流动 Embedding Function

        Args:
            api_key: 硅基流动 API Key
            base_url: API 基础 URL
            model: Embedding 模型名称
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.endpoint = f"{self.base_url}/embeddings"

    def name(self) -> str:
        return f"siliconflow_{self.model.replace('/', '_')}"

    def __call__(self, input: Documents) -> List[List[float]]:
        """
        生成文本的 embedding 向量

        Args:
            input: 文本列表

        Returns:
            embedding 向量列表
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "input": input,
            "encoding_format": "float"
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()

            # 提取 embedding 向量
            embeddings = [item["embedding"] for item in result["data"]]

            return embeddings

        except requests.exceptions.RequestException as e:
            print(f"[错误] 硅基流动 Embedding API 调用失败: {e}")
            raise
        except (KeyError, ValueError) as e:
            print(f"[错误] 解析 Embedding 响应失败: {e}")
            raise
