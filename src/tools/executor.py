import sys
import io
import contextlib
import paramiko
from src.utils.config import Config

class CodeExecutor:
    """
    安全地执行 Agent 生成的 python 代码。
    """
    def __init__(self):
        self.globals = {
            "requests": __import__("requests"),
            "bs4": __import__("bs4"),
            "re": __import__("re"),
            "json": __import__("json"),
            "base64": __import__("base64")
        }

    def execute(self, code: str) -> str:
        """
        执行代码并捕获 stdout/stderr。
        """
        # 创建字符串缓冲区以捕获输出
        f = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                # 在受限的全局变量中执行代码
                exec(code, self.globals)
            
            output = f.getvalue()
            return output if output else "(代码执行无输出)"
            
        except Exception as e:
            return f"代码执行错误: {str(e)}"

class SSHExecutor:
    """
    通过 SSH 在远程服务器（如 Kali）上执行 Shell 命令。
    """
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connected = False
        
    def connect(self) -> str:
        if self.connected:
            return "已连接。"
            
        try:
            host = Config.SSH_HOST
            if not host:
                return "错误: 未在 .env 或配置中设置 SSH_HOST。"
                
            print(f"[SSH] 正在连接到 {host}...")
            
            kwargs = {
                "hostname": host,
                "port": Config.SSH_PORT,
                "username": Config.SSH_USER,
                "timeout": 10
            }
            
            if Config.SSH_PASSWORD:
                kwargs["password"] = Config.SSH_PASSWORD
            
            if Config.SSH_KEY_PATH:
                kwargs["key_filename"] = Config.SSH_KEY_PATH
                
            self.client.connect(**kwargs)
            self.connected = True
            return f"成功连接到 {host}"
        except Exception as e:
            return f"SSH 连接失败: {str(e)}"

    def execute(self, command: str) -> str:
        """
        执行 Shell 命令。
        """
        if not self.connected:
            res = self.connect()
            if "Failed" in res or "not configured" in res or "错误" in res or "失败" in res:
                return f"[系统错误] SSH 连接失败: {res}"
        
        try:
            # 执行命令
            stdin, stdout, stderr = self.client.exec_command(command)
            
            # 读取输出 (阻塞直到命令结束)
            out = stdout.read().decode('utf-8', errors='replace')
            err = stderr.read().decode('utf-8', errors='replace')
            
            result = ""
            if out:
                result += out
            if err:
                if result:
                    result += "\n"
                result += f"[标准错误]\n{err}"
                
            if not result:
                result = "(命令执行无输出)"
                
            return result.strip()
        except Exception as e:
            # 如果连接断开，尝试重连一次
            if not self.client.get_transport() or not self.client.get_transport().is_active():
                self.connected = False
                print("[SSH] 连接断开，正在重试...")
                self.connect()
                try:
                    stdin, stdout, stderr = self.client.exec_command(command)
                    out = stdout.read().decode('utf-8', errors='replace')
                    err = stderr.read().decode('utf-8', errors='replace')
                    return (out + err).strip()
                except Exception as retry_e:
                    return f"SSH 命令执行错误 (重试后): {str(retry_e)}"
            return f"SSH 命令执行错误: {str(e)}"

    def close(self):
        if self.connected:
            self.client.close()
            self.connected = False
