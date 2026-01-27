import chromadb
from chromadb.config import Settings
import os
import uuid
from typing import List, Dict, Optional
from src.utils.config import Config
from src.rag.chunker import SimpleChunker

class RAGSystem:
    def __init__(self, persist_path: str = None):
        self.persist_path = persist_path or Config.CHROMA_DB_DIR
        
        # 初始化 ChromaDB 客户端
        self.client = chromadb.PersistentClient(path=self.persist_path)
        
        # 创建或获取集合
        # 我们将使用 Chroma 提供的默认嵌入函数 (sentence-transformers/all-MiniLM-L6-v2)
        # 这在本地运行且免费。
        self.collection = self.client.get_or_create_collection(name="ctf_knowledge_base")
        
        self.chunker = SimpleChunker()

    def add_document(self, content: str, metadata: Dict = None):
        """
        向知识库添加文档。
        """
        if metadata is None:
            metadata = {}
            
        # 1. 分割内容
        chunks = self.chunker.split_text(content)
        
        if not chunks:
            return
            
        # 2. 准备 Chroma 数据
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [metadata for _ in chunks] # 为每个块复制元数据
        
        # 3. 添加到集合
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        print(f"已向知识库添加 {len(chunks)} 个数据块。")

    def query(self, query_text: str, n_results: int = 3) -> List[str]:
        """
        查询知识库。
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # 展平结果
        documents = results['documents'][0]
        return documents

    def count(self):
        return self.collection.count()
