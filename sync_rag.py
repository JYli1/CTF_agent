"""
RAG 知识库同步工具

功能：
- 自动同步 data/knowledge_base/ 文件夹和向量数据库
- 新增文件 → 添加到数据库
- 删除文件 → 从数据库删除
- 修改文件 → 更新数据库

使用方法：
    python sync_rag.py                    # 同步默认文件夹
    python sync_rag.py --folder <path>    # 同步指定文件夹
    python sync_rag.py --clear            # 清空数据库后重新同步
"""

from src.rag.engine import RAGSystem
from rich.console import Console
import argparse
import sys

console = Console()


def main():
    parser = argparse.ArgumentParser(description="RAG 知识库同步工具")
    parser.add_argument(
        "--folder",
        default="data/knowledge_base",
        help="知识库文件夹路径（默认: data/knowledge_base）"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="清空数据库后重新同步"
    )
    args = parser.parse_args()

    try:
        console.print("[bold cyan]RAG 知识库同步工具[/bold cyan]\n")

        # 初始化 RAG 系统
        rag = RAGSystem()

        # 如果需要清空数据库
        if args.clear:
            console.print("[yellow]警告: 清空模式：将删除所有现有数据[/yellow]")
            confirm = console.input("[red]确认清空数据库? (yes/no):[/red] ").strip().lower()
            if confirm == 'yes':
                rag.clear_all()
                console.print("[green][OK] 数据库已清空[/green]\n")
            else:
                console.print("[yellow]已取消[/yellow]")
                sys.exit(0)

        # 执行同步
        report = rag.sync_folder(args.folder)

        # 显示最终统计
        total_docs = rag.count()
        console.print(f"[bold green]当前知识库总数: {total_docs} 条[/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]同步已取消[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]错误: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
