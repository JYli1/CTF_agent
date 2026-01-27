import os
import sys
import glob
from src.rag.engine import RAGSystem
from src.utils.config import Config

def ingest_documents():
    # 验证
    Config.validate()
    
    # 支持命令行传入笔记目录，否则使用配置默认目录
    kb_dir = sys.argv[1] if len(sys.argv) > 1 else Config.KNOWLEDGE_BASE_DIR
    if not os.path.exists(kb_dir):
        print(f"目录 {kb_dir} 不存在。正在创建...")
        os.makedirs(kb_dir)
        # 新建目录后目前没有文件可导入

    print(f"正在扫描 {kb_dir} 下的笔记文件（.md/.txt）...")
    md_files = glob.glob(os.path.join(kb_dir, "**/*.md"), recursive=True)
    txt_files = glob.glob(os.path.join(kb_dir, "**/*.txt"), recursive=True)
    files = md_files + txt_files
    
    if not files:
        print("未找到可导入的笔记文件。")
        return

    rag = RAGSystem()
    
    for file_path in files:
        print(f"正在处理 {file_path}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 添加到 RAG
            # 元数据使用文件名
            metadata = {"source": os.path.basename(file_path)}
            rag.add_document(content, metadata)
            print(f"成功添加 {file_path}")
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")

    print(f"\n导入完成。知识库文档总数: {rag.count()}")

if __name__ == "__main__":
    ingest_documents()
