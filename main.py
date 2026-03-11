import sys
import os
import datetime
import time
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.core.agent import CTFAgent
from src.utils.config import Config
from src.utils.reporter import Reporter

console = Console()

def run_cli_mode():
    # 1. 显示欢迎界面
    console.print(Panel.fit(
        "[bold cyan]CTF Agent 自动解题系统[/bold cyan]\n"
        "[dim]多专家协作 · RAG知识增强 · 智能解题[/dim]",
        border_style="cyan"
    ))

    # 2. 验证配置
    with console.status("[bold green]正在验证配置..."):
        Config.validate()
    console.print("[green]✓[/green] 配置验证通过")

    # 3. 初始化
    with console.status("[bold green]正在初始化Agent..."):
        reporter = Reporter()
        agent = CTFAgent(reporter=reporter)
    console.print("[green]✓[/green] Agent初始化完成")

    # 4. 模式选择
    table = Table(show_header=True, header_style="bold magenta", border_style="blue")
    table.add_column("选项", style="cyan", width=6, justify="center")
    table.add_column("模式", style="green", width=12)
    table.add_column("说明", style="yellow")

    table.add_row("1", "自动模式", "全程无需干预，自动分析直到获取 Flag")
    table.add_row("2", "交互模式", "每一步由用户下达指令，可控性强")

    console.print(table)

    mode_choice = console.input("\n[bold cyan]请选择模式 (1/2) [默认: 1]:[/bold cyan] ").strip()

    auto_mode = True
    if mode_choice == '2':
        auto_mode = False
        console.print("[yellow]已切换至交互模式[/yellow]")
    else:
        console.print("[green]已切换至自动模式[/green]")

    target_url = console.input("\n[bold cyan]请输入目标题目 URL (没有请直接回车):[/bold cyan] ").strip()
    if target_url:
        agent.set_target(target_url)
        reporter.start_session(target_url)
        console.print(f"[green]✓[/green] 目标已设置为: [bold]{target_url}[/bold]")
    else:
        reporter.start_session()

    console.print(Panel("[bold green]Agent 已就绪，开始解题！[/bold green]", border_style="green", expand=False))

    # 初始输入
    current_input = ""
    if auto_mode and target_url:
        current_input = "请开始对目标 URL 进行全面分析，并寻找 Flag。"
    elif not auto_mode:
        console.print("[dim]您可以直接下达指令，例如 '开始分析' 或 '帮我扫描端口'。[/dim]")

    while True:
        try:
            # 获取输入
            if not current_input:
                user_input = console.input("\n[bold cyan][用户]>[/bold cyan] ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    break
                if not user_input:
                    continue
                current_input = user_input

            console.print("\n[bold yellow]正在调度专家团队...[/bold yellow]")

            # Agent 运行
            response = agent.run_step(current_input)

            console.print(Panel(
                response,
                title="[bold]CTF 战略专家",
                border_style="cyan"
            ))

            # 显示阶段达成情况
            phase_summary = agent.phase_tracker.get_phase_summary()
            console.print(f"\n[bold cyan]解题进度：[/bold cyan]{phase_summary}")

            # 检查是否达成新阶段
            if agent.new_phase_achieved:
                console.print(Panel(
                    f"[bold green]🎯 新阶段达成：{agent.new_phase_achieved.value}[/bold green]\n\n"
                    f"当前已达成的阶段：\n" + "\n".join([f"  ✓ {p.value}" for p in agent.phase_tracker.get_achieved_phases()]),
                    border_style="green",
                    title="[bold green]阶段进展"
                ))

                # 半自动模式：暂停并等待用户建议
                if not auto_mode:
                    console.print("\n[yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/yellow]")
                    console.print("[bold yellow]⏸️  半自动模式：达成新阶段，暂停等待用户建议[/bold yellow]")
                    console.print("[yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/yellow]")
                    user_suggestion = console.input("\n[bold cyan]请输入下一步建议 (直接回车继续当前策略):[/bold cyan] ").strip()
                    if user_suggestion:
                        current_input = user_suggestion
                        continue

            # 自动模式逻辑处理
            if auto_mode:
                # 检查Agent的flag_found状态
                if agent.flag_found:
                    console.print(Panel(
                        f"[bold green]✓ 检测到Flag，自动任务结束！[/bold green]\n\n"
                        f"发现的Flag:\n" + "\n".join([f"  • {flag}" for flag in agent.found_flags]),
                        border_style="green",
                        title="[bold green]任务完成"
                    ))
                    break
                else:
                    console.print("[dim](自动模式) 未检测到Flag，继续分析...[/dim]")
                    current_input = "请根据当前结果，继续制定下一步计划并执行。如果卡住了，请尝试其他思路。"
                    time.sleep(2)
            else:
                current_input = ""

        except KeyboardInterrupt:
            console.print("\n[yellow]正在退出...[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]发生错误: {e}[/red]")
            import traceback
            traceback.print_exc()
            current_input = ""

    # 保存会话
    console.print("\n[dim]正在保存会话报告...[/dim]")
    report_path = reporter.create_report("session_log", agent.history)
    console.print(f"[green]✓[/green] 报告已保存至 {report_path}")

    # 关闭资源
    agent.close()

    # 学习与经验回存
    save_to_kb = console.input("\n[bold cyan]是否将本次会话总结并存入知识库？(y/n):[/bold cyan] ").strip().lower()
    if save_to_kb == 'y':
        summary = agent.summarize_session()
        if summary:
            console.print(Panel(summary, title="[bold]生成的 Writeup 摘要", border_style="green"))

            confirm = console.input("[bold cyan]确认存入数据库吗？(y/n):[/bold cyan] ").strip().lower()
            if confirm == 'y':
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                source_name = f"auto_learned_{timestamp}.md"

                kb_dir = Config.KNOWLEDGE_BASE_DIR
                if not os.path.exists(kb_dir):
                    os.makedirs(kb_dir)

                kb_file_path = os.path.join(kb_dir, source_name)
                with open(kb_file_path, 'w', encoding='utf-8') as f:
                    f.write(summary)

                agent.rag.add_document(summary, metadata={"source": source_name, "type": "auto_learned"})
                console.print(f"[green]✓[/green] 经验已存入知识库！文件备份于: {kb_file_path}")
            else:
                console.print("[dim]已取消存入。[/dim]")
        else:
            console.print("[yellow]没有足够的历史记录生成总结。[/yellow]")
    else:
        console.print("[dim]已取消存入。[/dim]")

def main():
    """主入口"""
    parser = argparse.ArgumentParser(description='CTF Agent - 自动解题系统')
    parser.add_argument('--web', action='store_true', help='启动 Web 模式')
    parser.add_argument('--port', type=int, default=5000, help='Web 端口（默认: 5000）')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Web 监听地址（默认: 0.0.0.0）')

    args = parser.parse_args()

    if args.web:
        # Web 模式
        from webui.app import run_web_server
        run_web_server(host=args.host, port=args.port)
    else:
        # CLI 模式
        run_cli_mode()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]程序已由用户中断退出。再见！[/yellow]")
        sys.exit(0)
