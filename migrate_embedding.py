"""
迁移现有知识库到新的 Embedding 模型
"""
import chromadb
import os
from src.utils.config import Config
from src.rag.siliconflow_embedding import SiliconFlowEmbeddingFunction

def migrate_knowledge_base():
    print("=" * 60)
    print("知识库迁移工具")
    print("=" * 60)

    db_path = Config.CHROMA_DB_DIR

    if not os.path.exists(db_path):
        print(f"\n[提示] 知识库目录不存在: {db_path}")
        print("无需迁移，可以直接使用新的 Embedding 模型")
        return

    # 1. 连接到旧数据库
    print(f"\n[步骤1] 读取旧知识库...")
    old_client = chromadb.PersistentClient(path=db_path)

    try:
        old_collection = old_client.get_collection(name="ctf_knowledge_base")
        doc_count = old_collection.count()
        print(f"发现 {doc_count} 个文档")

        if doc_count == 0:
            print("\n[提示] 知识库为空，无需迁移")
            old_client.delete_collection(name="ctf_knowledge_base")
            print("已删除空集合")
            return

    except Exception as e:
        print(f"[提示] 无法读取旧集合: {e}")
        print("可能是新数据库，无需迁移")
        return

    # 2. 导出所有数据
    print(f"\n[步骤2] 导出数据...")
    result = old_collection.get(include=['documents', 'metadatas'])

    documents = result['documents']
    metadatas = result['metadatas']

    print(f"导出 {len(documents)} 个文档")

    # 3. 删除旧集合
    print(f"\n[步骤3] 删除旧集合...")
    old_client.delete_collection(name="ctf_knowledge_base")
    print("旧集合已删除")

    # 4. 创建新集合（使用新 Embedding）
    print(f"\n[步骤4] 创建新集合（使用 {Config.EMBEDDING_MODEL}）...")

    embedding_function = SiliconFlowEmbeddingFunction(
        api_key=Config.EMBEDDING_API_KEY,
        base_url=Config.EMBEDDING_BASE_URL,
        model=Config.EMBEDDING_MODEL
    )

    new_collection = old_client.get_or_create_collection(
        name="ctf_knowledge_base",
        embedding_function=embedding_function
    )

    # 5. 重新导入数据
    print(f"\n[步骤5] 重新导入数据...")
    print("这可能需要一些时间，请耐心等待...")

    # 分批导入（每批3个文档，避免请求过大）
    batch_size = 3
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]

        # 生成新的 ID
        import uuid
        batch_ids = [str(uuid.uuid4()) for _ in batch_docs]

        new_collection.add(
            documents=batch_docs,
            metadatas=batch_metas,
            ids=batch_ids
        )

        print(f"  已导入 {min(i+batch_size, len(documents))}/{len(documents)} 个文档")

    print(f"\n[完成] 迁移成功!")
    print(f"新知识库文档数量: {new_collection.count()}")
    print(f"Embedding 模型: {Config.EMBEDDING_MODEL}")
    print(f"向量维度: 1024")

if __name__ == "__main__":
    if not Config.EMBEDDING_API_KEY:
        print("[错误] 未配置 EMBEDDING_API_KEY")
        print("请在 .env 文件中配置:")
        print("  EMBEDDING_API_KEY=your-api-key")
        print("  EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1")
        print("  EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5")
    else:
        migrate_knowledge_base()
