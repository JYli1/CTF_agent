"""
CTF Agent 配置向导
帮助用户快速配置 .env 文件
"""
import os
import shutil


def setup_wizard():
    print("=" * 60)
    print("CTF Agent 配置向导")
    print("=" * 60)

    # 检查是否已有 .env 文件
    if os.path.exists(".env"):
        print("\n检测到已存在 .env 文件")
        choice = input("是否覆盖现有配置? (y/N): ").strip().lower()
        if choice != 'y':
            print("配置取消")
            return

        # 备份现有配置
        backup_path = ".env.backup"
        shutil.copy(".env", backup_path)
        print(f"已备份现有配置到: {backup_path}")

    print("\n开始配置...")

    # 1. API Key
    print("\n" + "=" * 60)
    print("步骤 1: API Key 配置")
    print("=" * 60)
    print("请访问 https://siliconflow.cn 获取 API Key")
    api_key = input("请输入硅基流动 API Key: ").strip()

    if not api_key:
        print("错误: API Key 不能为空")
        return

    # 2. 模型选择
    print("\n" + "=" * 60)
    print("步骤 2: 模型选择")
    print("=" * 60)
    print("推荐配置:")
    print("  1. 均衡配置 (推荐)")
    print("     - CTF 战略专家: GLM-5")
    print("     - Python 专家: Kimi-K2.5")
    print("     - 安全专家: GLM-5")
    print("  2. 高性能配置")
    print("     - 全部使用: Claude-Sonnet-4.5")
    print("  3. 经济配置")
    print("     - 全部使用: DeepSeek-V3.2")
    print("  4. 自定义")

    choice = input("\n请选择配置方案 (1-4) [1]: ").strip() or "1"

    if choice == "1":
        ctf_model = "Pro/zai-org/GLM-5"
        python_model = "Pro/moonshotai/Kimi-K2.5"
        security_model = "Pro/zai-org/GLM-5"
    elif choice == "2":
        ctf_model = python_model = security_model = "Pro/anthropic/claude-sonnet-4.5"
    elif choice == "3":
        ctf_model = python_model = security_model = "deepseek-ai/DeepSeek-V3.2"
    else:
        print("\n自定义模型配置:")
        ctf_model = input("  CTF 战略专家模型 [Pro/zai-org/GLM-5]: ").strip() or "Pro/zai-org/GLM-5"
        python_model = input("  Python 专家模型 [Pro/moonshotai/Kimi-K2.5]: ").strip() or "Pro/moonshotai/Kimi-K2.5"
        security_model = input("  安全专家模型 [Pro/zai-org/GLM-5]: ").strip() or "Pro/zai-org/GLM-5"

    # 3. SSH 配置
    print("\n" + "=" * 60)
    print("步骤 3: SSH 配置 (可选)")
    print("=" * 60)
    print("如果你有远程 Kali Linux 机器，可以配置 SSH 连接")
    print("安全专家将使用远程机器执行 nmap, sqlmap 等工具")

    use_ssh = input("\n是否配置 SSH? (y/N): ").strip().lower() == 'y'

    if use_ssh:
        ssh_host = input("  SSH 主机地址: ").strip()
        ssh_port = input("  SSH 端口 [22]: ").strip() or "22"
        ssh_user = input("  SSH 用户名 [kali]: ").strip() or "kali"
        ssh_password = input("  SSH 密码: ").strip()
    else:
        ssh_host = ""
        ssh_port = "22"
        ssh_user = "kali"
        ssh_password = ""

    # 4. 生成 .env 文件
    print("\n" + "=" * 60)
    print("步骤 4: 生成配置文件")
    print("=" * 60)

    env_content = f"""# ============================================================
# CTF Agent 配置文件
# 由配置向导自动生成
# ============================================================

# ============================================================
# 1. API 密钥配置
# ============================================================
SILICONFLOW_API_KEY={api_key}

# ============================================================
# 2. LLM 基础配置
# ============================================================
LLM_PROVIDER=openai
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
MODEL_NAME={ctf_model}

# ============================================================
# 3. 三大专家模型配置
# ============================================================

# CTF 战略专家
CTF_API_KEY={api_key}
CTF_BASE_URL=https://api.siliconflow.cn/v1
CTF_MODEL={ctf_model}

# Python 编程专家
PYTHON_API_KEY={api_key}
PYTHON_BASE_URL=https://api.siliconflow.cn/v1
PYTHON_MODEL={python_model}

# 安全渗透专家
SECURITY_API_KEY={api_key}
SECURITY_BASE_URL=https://api.siliconflow.cn/v1
SECURITY_MODEL={security_model}

# ============================================================
# 4. RAG 知识库配置
# ============================================================
EMBEDDING_API_KEY={api_key}
EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5

CHROMA_DB_DIR=data/chroma_db
KNOWLEDGE_BASE_DIR=data/knowledge_base

# ============================================================
# 5. SSH 远程执行配置
# ============================================================
"""

    if use_ssh:
        env_content += f"""SSH_HOST={ssh_host}
SSH_PORT={ssh_port}
SSH_USER={ssh_user}
SSH_PASSWORD={ssh_password}
"""
    else:
        env_content += """# SSH_HOST=
# SSH_PORT=22
# SSH_USER=kali
# SSH_PASSWORD=
"""

    env_content += """
# ============================================================
# 6. 高级配置（可选）
# ============================================================
# MAX_SUB_STEPS=5
# RAG_DISTANCE_THRESHOLD=1.5
# LOG_LEVEL=INFO
"""

    # 写入文件
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)

    print("\n配置文件已生成: .env")

    # 5. 验证配置
    print("\n" + "=" * 60)
    print("步骤 5: 验证配置")
    print("=" * 60)

    try:
        from src.utils.config import Config
        Config.print_config()
        if Config.validate():
            print("\n配置成功！")
            print("\n下一步:")
            print("  1. 运行测试: python test_llm.py")
            print("  2. 导入知识: python import_knowledge.py")
            print("  3. 启动 Agent: python main.py")
        else:
            print("\n配置验证失败，请检查 .env 文件")
    except Exception as e:
        print(f"\n配置验证出错: {e}")


if __name__ == "__main__":
    try:
        setup_wizard()
    except KeyboardInterrupt:
        print("\n\n配置已取消")
    except Exception as e:
        print(f"\n配置出错: {e}")
        import traceback
        traceback.print_exc()
