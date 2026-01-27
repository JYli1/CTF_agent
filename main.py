import sys
import os
from src.core.agent import CTFAgent
from src.tools.executor import CodeExecutor, SSHExecutor
from src.utils.config import Config
from src.utils.reporter import Reporter

def main():
    # 1. 验证
    Config.validate()
    
    print("=== CTF Agent 命令行工具 ===")
    print("输入 'exit' 或 'quit' 退出程序。")
    
    # 2. 初始化
    agent = CTFAgent()
    code_executor = CodeExecutor()
    ssh_executor = SSHExecutor()
    reporter = Reporter()
    
    # 模式选择
    print("\n请选择运行模式:")
    print("1. 辅助做题 (交互式，每步等待用户指令)")
    print("2. 自动做题 (自动循环，直到找到 Flag)")
    mode_choice = input("请输入选项 (1/2) [默认: 2]: ").strip()
    
    auto_mode = True
    if mode_choice == '1':
        auto_mode = False
        print("已切换至 [辅助做题] 模式。")
    else:
        print("已切换至 [自动做题] 模式。")
    
    target_url = input("\n请输入目标题目 URL (如果没有请直接回车): ").strip()
    if target_url:
        agent.set_target(target_url)
        print(f"目标已设置为: {target_url}")
        
    # 如果是自动模式且设置了 URL，开始自动循环的初始输入
    current_input = ""
    no_code_counter = 0 # 连续未生成代码的计数器
    
    if auto_mode and target_url:
        current_input = "请开始分析目标并寻找 Flag。"
        
    while True:
        try:
            # 如果是辅助模式，或者自动模式下当前没有待处理的输入（初始状态或需要人工干预）
            if not auto_mode or not current_input:
                user_input = input("\n[用户]> ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    break
                if not user_input:
                    continue
                current_input = user_input
                no_code_counter = 0 # 用户介入后重置计数器

            print("\n[AGENT] 正在思考...")
            
            # Agent 步骤
            response = agent.run_step(current_input)
            print(f"\n[AGENT]> {response}")
            
            # 检查是否有代码执行
            code_type, code = agent.extract_code(response)
            if code:
                no_code_counter = 0 # 有代码，重置计数器
                print(f"\n[系统] 检测到 {code_type} 代码。正在执行...")
                print("-" * 20)
                print(code)
                print("-" * 20)
                
                execution_result = ""
                if code_type == 'python':
                    execution_result = code_executor.execute(code)
                elif code_type == 'bash':
                    execution_result = ssh_executor.execute(code)
                else:
                    execution_result = f"错误: 未知的代码类型 {code_type}"

                print(f"[执行结果]\n{execution_result}")
                
                # 将结果反馈给 Agent
                follow_up_msg = f"代码执行输出:\n{execution_result}\n\n你找到 Flag 了吗？如果没有，下一步该怎么做？"
                
                if auto_mode:
                    # 自动模式下，直接将反馈作为下一轮的输入
                    # 检查是否找到 Flag
                    if "FLAG:" in response or "ctf{" in response.lower() or "flag{" in response.lower():
                        print("\n[系统] 似乎找到了 Flag，停止自动循环。")
                        current_input = "" # 停止自动循环，等待用户
                    else:
                        current_input = follow_up_msg
                        print("\n[系统] (自动模式) 继续分析执行结果...")
                        # 添加简单的延迟以避免刷屏过快
                        import time
                        time.sleep(1)
                else:
                    # 辅助模式下，执行一次反馈步骤（之前的逻辑是执行一次反馈，现在我们可以保持这个逻辑）
                    response_2 = agent.run_step(follow_up_msg)
                    print(f"\n[AGENT]> {response_2}")
                    current_input = "" # 清空，等待用户输入
            else:
                # 没有代码执行
                if auto_mode:
                    # 如果没有代码，Agent 只是在说话。
                    # 检查是否包含 Flag
                    if "FLAG:" in response or "ctf{" in response.lower() or "flag{" in response.lower():
                        print("\n[系统] 似乎找到了 Flag，停止自动循环。")
                        current_input = ""
                    else:
                        no_code_counter += 1
                        if no_code_counter >= 3:
                            print(f"\n[系统] Agent 连续 {no_code_counter} 次未生成代码，暂停自动循环，等待人工干预。")
                            current_input = ""
                            no_code_counter = 0
                        else:
                            # 鼓励 Agent 继续尝试
                            print(f"\n[系统] Agent 未生成代码 (连续 {no_code_counter} 次)。要求其继续尝试...")
                            current_input = "请继续分析，如果你需要验证想法，请务必编写并执行 Python 代码。"
                            import time
                            time.sleep(1)
                else:
                    current_input = ""

        except KeyboardInterrupt:
            print("\n正在退出...")
            break
        except Exception as e:
            print(f"发生错误: {e}")
            current_input = "" # 出错时重置输入，等待用户干预

    # 保存会话
    print("\n正在保存会话报告...")
    report_path = reporter.create_report("session_log", agent.history)
    print(f"报告已保存至 {report_path}")
    
    # 关闭 SSH 连接
    ssh_executor.close()

    # 3. 学习与经验回存
    save_to_kb = input("\n是否将本次会话总结并存入知识库以供未来学习？(y/n): ").strip().lower()
    if save_to_kb == 'y':
        # 1. 生成总结
        summary = agent.summarize_session()
        print("\n=== 生成的 Writeup 摘要 ===")
        print(summary)
        print("===========================")
        
        confirm = input("\n确认存入数据库吗？(y/n): ").strip().lower()
        if confirm == 'y':
            # 2. 存入 RAG
            # 使用当前时间戳作为源标识
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            source_name = f"auto_learned_{timestamp}.md"
            
            # 同时保存一份 md 文件到知识库目录（作为备份和持久化）
            kb_dir = "data/knowledge_base"
            if not os.path.exists(kb_dir):
                os.makedirs(kb_dir)
            
            kb_file_path = os.path.join(kb_dir, source_name)
            with open(kb_file_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            # 添加到向量数据库
            agent.rag.add_document(summary, metadata={"source": source_name, "type": "auto_learned"})
            print(f"\n[成功] 经验已存入知识库！文件备份于: {kb_file_path}")
        else:
            print("已取消存入。")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[提示] 程序已由用户中断退出。再见！")
        sys.exit(0)
