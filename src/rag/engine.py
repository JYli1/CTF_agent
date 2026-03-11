import chromadb
from chromadb.config import Settings
import os
import re
import uuid
import hashlib
import glob
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from src.utils.config import Config
from src.rag.chunker import SimpleChunker
from src.rag.siliconflow_embedding import SiliconFlowEmbeddingFunction

class RAGSystem:
    def __init__(self, persist_path: str = None):
        self.persist_path = persist_path or Config.CHROMA_DB_DIR

        # 初始化 ChromaDB 客户端
        self.client = chromadb.PersistentClient(path=self.persist_path)

        # 初始化硅基流动 Embedding Function
        self.embedding_function = None
        embedding_function = None
        if Config.EMBEDDING_API_KEY:
            try:
                embedding_function = SiliconFlowEmbeddingFunction(
                    api_key=Config.EMBEDDING_API_KEY,
                    base_url=Config.EMBEDDING_BASE_URL,
                    model=Config.EMBEDDING_MODEL
                )
                self.embedding_function = embedding_function
                print(f"[RAG] 使用硅基流动 Embedding: {Config.EMBEDDING_MODEL}")
            except Exception as e:
                print(f"[警告] 硅基流动 Embedding 初始化失败: {e}")
                print("[RAG] 回退到默认 Embedding (all-MiniLM-L6-v2)")
        else:
            print("[RAG] 未配置 EMBEDDING_API_KEY，使用默认 Embedding (all-MiniLM-L6-v2)")

        # 创建或获取集合
        try:
            self.collection = self.client.get_or_create_collection(
                name="ctf_knowledge_base",
                embedding_function=embedding_function
            )
        except ValueError as e:
            if "Embedding function conflict" in str(e):
                print("[警告] 检测到 Embedding 函数冲突，正在重建集合...")
                self.client.delete_collection(name="ctf_knowledge_base")
                self.collection = self.client.get_or_create_collection(
                    name="ctf_knowledge_base",
                    embedding_function=embedding_function
                )
                print("[OK] 集合已重建")
            else:
                raise

        self.chunker = SimpleChunker()

    def calculate_file_hash(self, file_path: str) -> str:
        """计算文件的 SHA256 哈希"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def add_document(self, content: str, metadata: Dict = None, file_path: str = None):
        """
        向知识库添加文档，自动提取元数据

        参数:
            content: 文档内容
            metadata: 手动指定的元数据（可选）
            file_path: 文件路径（用于同步追踪）
        """
        if metadata is None:
            metadata = {}

        # 如果提供了文件路径，添加追踪信息
        if file_path:
            metadata['file_path'] = file_path
            metadata['file_hash'] = self.calculate_file_hash(file_path)
            if 'source' not in metadata:
                metadata['source'] = os.path.basename(file_path)

        # 自动提取题目类型
        content_lower = content.lower()

        if 'challenge_type' not in metadata:
            if any(kw in content_lower for kw in ['web', 'http', 'url', 'sql', 'xss']):
                metadata['challenge_type'] = 'Web'
            elif any(kw in content_lower for kw in ['pwn', '溢出', 'overflow', 'rop']):
                metadata['challenge_type'] = 'Pwn'
            elif any(kw in content_lower for kw in ['reverse', '逆向', 'ida', 'ghidra']):
                metadata['challenge_type'] = 'Reverse'
            elif any(kw in content_lower for kw in ['crypto', '密码', 'rsa', 'aes']):
                metadata['challenge_type'] = 'Crypto'

        # 提取漏洞标签
        tags = []
        if 'sql注入' in content_lower or 'sql injection' in content_lower:
            tags.append('SQL注入')
        if 'xss' in content_lower or '跨站' in content_lower:
            tags.append('XSS')
        if '反序列化' in content_lower or 'unserialize' in content_lower:
            tags.append('反序列化')
        if '命令注入' in content_lower or 'command injection' in content_lower:
            tags.append('命令注入')
        if '文件上传' in content_lower or 'upload' in content_lower:
            tags.append('文件上传')

        if tags:
            metadata['tags'] = ', '.join(tags)

        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()

        # 添加时间戳
        metadata['added_time'] = datetime.now().isoformat()

        # 分割并添加
        chunks = self.chunker.split_text(content)
        if not chunks:
            print("[警告] 文档为空，跳过添加")
            return

        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [metadata.copy() for _ in chunks]

        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

        print(f"[OK] 已添加 {len(chunks)} 个数据块")
        if metadata.get('challenge_type'):
            print(f"   类型: {metadata['challenge_type']}")
        if metadata.get('tags'):
            print(f"   标签: {metadata['tags']}")

    def query(self, query_text: str, n_results: int = 5, distance_threshold: float = 1.5,
              challenge_type: str = None) -> List[str]:
        """
        查询知识库，添加相关性过滤

        参数:
            query_text: 查询文本
            n_results: 最大返回数量
            distance_threshold: 距离阈值，超过此值的结果将被过滤（越小越相关）
            challenge_type: 题目类型过滤（Web/Pwn/Reverse/Crypto）

        返回:
            过滤后的相关文档列表
        """
        where_filter = None
        if challenge_type:
            where_filter = {"challenge_type": challenge_type}

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_filter
        )

        documents = results['documents'][0]
        distances = results['distances'][0] if 'distances' in results else []

        # 过滤：只保留距离小于阈值的结果
        filtered_docs = []
        for i, doc in enumerate(documents):
            if i < len(distances):
                if distances[i] < distance_threshold:
                    filtered_docs.append(doc)
                    print(f"  [OK] 相关度: {1 - distances[i]:.2%} - {doc[:50]}...")
            else:
                filtered_docs.append(doc)

        # 如果过滤后为空，返回最相关的1条
        if not filtered_docs and documents:
            print("  [警告] 未找到高相关度结果，返回最接近的1条")
            filtered_docs = [documents[0]]

        return filtered_docs

    def count(self):
        return self.collection.count()

    def list_all(self, limit: int = 100) -> List[Dict]:
        """列出所有文档"""
        result = self.collection.get(limit=limit, include=['documents', 'metadatas'])
        items = []
        for i, doc_id in enumerate(result['ids']):
            items.append({
                'id': doc_id,
                'content': result['documents'][i][:100] + '...',
                'metadata': result['metadatas'][i]
            })
        return items

    def list_sources(self) -> List[str]:
        """列出所有来源"""
        result = self.collection.get(include=['metadatas'])
        sources = set()
        for metadata in result['metadatas']:
            if 'source' in metadata:
                sources.add(metadata['source'])
        return sorted(list(sources))

    def delete_by_id(self, doc_id: str):
        """根据ID删除文档"""
        self.collection.delete(ids=[doc_id])
        print(f"[OK] 已删除文档: {doc_id}")

    def delete_by_source(self, source_pattern: str, exact_match: bool = False):
        """
        根据来源删除文档（支持模糊匹配）

        Args:
            source_pattern: 来源名称或模式
            exact_match: 是否精确匹配（默认False，支持模糊匹配）
        """
        # 获取所有文档
        result = self.collection.get(include=['metadatas'])

        # 找到匹配的文档ID
        ids_to_delete = []
        for i, metadata in enumerate(result['metadatas']):
            source = metadata.get('source', '')
            if exact_match:
                if source == source_pattern:
                    ids_to_delete.append(result['ids'][i])
            else:
                if source_pattern.lower() in source.lower():
                    ids_to_delete.append(result['ids'][i])

        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            print(f"[OK] 已删除 {len(ids_to_delete)} 个文档（来源匹配 '{source_pattern}'）")
        else:
            print(f"[警告] 未找到匹配 '{source_pattern}' 的文档")

    def delete_by_type(self, challenge_type: str):
        """根据题目类型删除"""
        result = self.collection.get(include=['metadatas'])
        ids_to_delete = []
        for i, metadata in enumerate(result['metadatas']):
            if metadata.get('challenge_type', '').lower() == challenge_type.lower():
                ids_to_delete.append(result['ids'][i])

        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            print(f"[OK] 已删除 {len(ids_to_delete)} 个 {challenge_type} 类型的文档")
        else:
            print(f"[警告] 未找到 {challenge_type} 类型的文档")

    def clear_all(self):
        """清空整个知识库"""
        self.client.delete_collection(name="ctf_knowledge_base")
        self.collection = self.client.get_or_create_collection(
            name="ctf_knowledge_base",
            embedding_function=self.embedding_function
        )
        print("[OK] 知识库已清空")

    def get_all_file_records(self) -> Dict[str, Dict]:
        """
        获取数据库中所有文件记录

        返回:
            {file_path: {ids: [...], hash: "..."}}
        """
        result = self.collection.get(include=['metadatas'])
        file_records = {}

        for i, doc_id in enumerate(result['ids']):
            metadata = result['metadatas'][i]
            file_path = metadata.get('file_path')
            file_hash = metadata.get('file_hash')

            if file_path:
                if file_path not in file_records:
                    file_records[file_path] = {'ids': [], 'hash': file_hash}
                file_records[file_path]['ids'].append(doc_id)

        return file_records

    def delete_by_file_path(self, file_path: str):
        """根据文件路径删除所有相关的文档块"""
        result = self.collection.get(include=['metadatas'])
        ids_to_delete = []

        for i, metadata in enumerate(result['metadatas']):
            if metadata.get('file_path') == file_path:
                ids_to_delete.append(result['ids'][i])

        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            return len(ids_to_delete)
        return 0

    def sync_folder(self, folder_path: str = "data/knowledge_base") -> Dict:
        """
        同步文件夹和向量数据库

        参数:
            folder_path: 知识库文件夹路径

        返回:
            同步报告 {added: int, deleted: int, updated: int, skipped: int}
        """
        print(f"\n[同步] 开始同步文件夹: {folder_path}")

        # 1. 扫描文件夹中的所有 .md 文件
        md_files = glob.glob(os.path.join(folder_path, "*.md"))
        folder_files = {}

        for file_path in md_files:
            abs_path = os.path.abspath(file_path)
            file_hash = self.calculate_file_hash(abs_path)
            folder_files[abs_path] = file_hash

        print(f"[扫描] 文件夹中找到 {len(folder_files)} 个 .md 文件")

        # 2. 获取数据库中的文件记录
        db_records = self.get_all_file_records()
        print(f"[扫描] 数据库中有 {len(db_records)} 个文件记录")

        # 3. 对比并同步
        report = {'added': 0, 'deleted': 0, 'updated': 0, 'skipped': 0}

        # 3.1 处理文件夹中的文件（新增或更新）
        for file_path, file_hash in folder_files.items():
            if file_path not in db_records:
                # 新文件 - 添加
                print(f"\n[新增] {os.path.basename(file_path)}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.add_document(content, file_path=file_path)
                report['added'] += 1

            elif db_records[file_path]['hash'] != file_hash:
                # 文件已修改 - 更新
                print(f"\n[更新] {os.path.basename(file_path)}")
                # 删除旧记录
                deleted_count = self.delete_by_file_path(file_path)
                print(f"  删除旧记录: {deleted_count} 个块")
                # 添加新记录
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.add_document(content, file_path=file_path)
                report['updated'] += 1

            else:
                # 文件未变化 - 跳过
                report['skipped'] += 1

        # 3.2 处理数据库中但文件夹中不存在的文件（删除）
        for file_path in db_records:
            if file_path not in folder_files:
                print(f"\n[删除] {os.path.basename(file_path)}")
                deleted_count = self.delete_by_file_path(file_path)
                print(f"  删除 {deleted_count} 个块")
                report['deleted'] += 1

        # 4. 输出报告
        print(f"\n{'='*50}")
        print(f"[同步完成]")
        print(f"  [OK] 新增: {report['added']} 个文件")
        print(f"  [OK] 删除: {report['deleted']} 个文件")
        print(f"  [OK] 更新: {report['updated']} 个文件")
        print(f"  [OK] 跳过: {report['skipped']} 个文件（未变化）")
        print(f"{'='*50}\n")

        return report

