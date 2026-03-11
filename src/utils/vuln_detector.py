from typing import Dict, List, Tuple, Optional
import re
from urllib.parse import urlparse, parse_qs

class VulnerabilityPattern:
    """漏洞特征模式"""
    def __init__(self, vuln_type: str, skill_id: str, confidence: float, indicators: List[str]):
        self.vuln_type = vuln_type  # 漏洞类型
        self.skill_id = skill_id    # 对应的技能ID
        self.confidence = confidence  # 置信度 0-1
        self.indicators = indicators  # 触发指标

class VulnerabilityDetector:
    """
    漏洞模式识别器
    自动识别URL、响应、代码中的漏洞特征，并推荐对应技能
    """

    def __init__(self):
        self.patterns = self._init_patterns()

    def _init_patterns(self) -> Dict[str, VulnerabilityPattern]:
        """初始化漏洞识别模式"""
        return {
            "sql_injection": VulnerabilityPattern(
                vuln_type="SQL注入",
                skill_id="web_sqli",
                confidence=0.8,
                indicators=[
                    "url_param_numeric",  # ?id=1
                    "url_param_string",   # ?name=admin
                    "sql_error",          # SQL错误信息
                    "database_keywords"   # 数据库关键字
                ]
            ),
            "ssrf": VulnerabilityPattern(
                vuln_type="SSRF",
                skill_id="web_ssrf",
                confidence=0.8,
                indicators=[
                    "url_param_url",      # ?url=http://
                    "url_param_redirect", # ?redirect=
                    "url_param_link"      # ?link=
                ]
            ),
            "php_code": VulnerabilityPattern(
                vuln_type="PHP源码",
                skill_id="web_php_analysis",
                confidence=0.9,
                indicators=[
                    "php_code_detected"   # 检测到PHP代码
                ]
            ),
            "file_inclusion": VulnerabilityPattern(
                vuln_type="文件包含",
                skill_id="web_lfi",  # 未来实现
                confidence=0.7,
                indicators=[
                    "url_param_file",     # ?file=
                    "url_param_page",     # ?page=
                    "url_param_include"   # ?include=
                ]
            ),
            "command_injection": VulnerabilityPattern(
                vuln_type="命令注入",
                skill_id="web_cmdi",  # 未来实现
                confidence=0.7,
                indicators=[
                    "url_param_cmd",      # ?cmd=
                    "url_param_exec",     # ?exec=
                    "url_param_ping"      # ?ping=
                ]
            )
        }

    def analyze_url(self, url: str) -> List[Tuple[str, float, str]]:
        """
        分析URL，识别潜在漏洞

        Args:
            url: 目标URL

        Returns:
            [(漏洞类型, 置信度, 推荐技能ID), ...]
        """
        findings = []

        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            if not params:
                return findings

            # 检查SQL注入特征
            sql_indicators = self._check_sql_injection_params(params)
            if sql_indicators:
                findings.append(("SQL注入", 0.8, "web_sqli", sql_indicators))

            # 检查SSRF特征
            ssrf_indicators = self._check_ssrf_params(params)
            if ssrf_indicators:
                findings.append(("SSRF", 0.8, "web_ssrf", ssrf_indicators))

            # 检查文件包含特征
            lfi_indicators = self._check_file_inclusion_params(params)
            if lfi_indicators:
                findings.append(("文件包含", 0.7, "web_lfi", lfi_indicators))

            # 检查命令注入特征
            cmdi_indicators = self._check_command_injection_params(params)
            if cmdi_indicators:
                findings.append(("命令注入", 0.7, "web_cmdi", cmdi_indicators))

        except Exception as e:
            print(f"[VulnerabilityDetector] URL分析错误: {e}")

        return findings

    def _check_sql_injection_params(self, params: Dict) -> List[str]:
        """检查SQL注入相关参数"""
        indicators = []

        # 常见SQL注入参数名
        sql_param_names = [
            'id', 'uid', 'user_id', 'userid', 'user',
            'page', 'pid', 'cat', 'category', 'item',
            'article', 'news', 'post', 'product',
            'search', 'query', 'keyword', 'name'
        ]

        for param_name, values in params.items():
            param_lower = param_name.lower()

            # 检查参数名
            if param_lower in sql_param_names:
                indicators.append(f"参数名: {param_name}")

            # 检查参数值是否为数字（常见SQL注入点）
            if values and values[0].isdigit():
                indicators.append(f"数字参数: {param_name}={values[0]}")

        return indicators

    def _check_ssrf_params(self, params: Dict) -> List[str]:
        """检查SSRF相关参数"""
        indicators = []

        ssrf_param_names = [
            'url', 'uri', 'link', 'src', 'source',
            'redirect', 'target', 'dest', 'destination',
            'next', 'callback', 'return', 'goto',
            'path', 'file', 'load', 'fetch'
        ]

        for param_name, values in params.items():
            param_lower = param_name.lower()

            if param_lower in ssrf_param_names:
                indicators.append(f"参数名: {param_name}")

            # 检查参数值是否包含URL
            if values and any(proto in values[0].lower() for proto in ['http://', 'https://', 'ftp://']):
                indicators.append(f"URL参数: {param_name}={values[0][:50]}")

        return indicators

    def _check_file_inclusion_params(self, params: Dict) -> List[str]:
        """检查文件包含相关参数"""
        indicators = []

        lfi_param_names = [
            'file', 'page', 'include', 'require',
            'path', 'template', 'view', 'doc',
            'document', 'folder', 'style', 'lang'
        ]

        for param_name, values in params.items():
            param_lower = param_name.lower()

            if param_lower in lfi_param_names:
                indicators.append(f"参数名: {param_name}")

            # 检查参数值是否包含文件路径特征
            if values:
                value = values[0]
                if any(char in value for char in ['/', '\\', '..']):
                    indicators.append(f"路径参数: {param_name}={value[:50]}")
                if value.endswith(('.php', '.html', '.txt', '.log')):
                    indicators.append(f"文件参数: {param_name}={value}")

        return indicators

    def _check_command_injection_params(self, params: Dict) -> List[str]:
        """检查命令注入相关参数"""
        indicators = []

        cmdi_param_names = [
            'cmd', 'command', 'exec', 'execute',
            'ping', 'ip', 'host', 'domain',
            'run', 'shell', 'bash', 'system'
        ]

        for param_name, values in params.items():
            param_lower = param_name.lower()

            if param_lower in cmdi_param_names:
                indicators.append(f"参数名: {param_name}")

        return indicators

    def analyze_response(self, response: str) -> List[Tuple[str, float, str, List[str]]]:
        """
        分析HTTP响应，识别潜在漏洞

        Args:
            response: HTTP响应内容

        Returns:
            [(漏洞类型, 置信度, 推荐技能ID, 指标列表), ...]
        """
        findings = []

        # 检查SQL错误信息
        sql_errors = self._check_sql_errors(response)
        if sql_errors:
            findings.append(("SQL注入", 0.9, "web_sqli", sql_errors))

        # 检查PHP代码
        php_code = self._check_php_code(response)
        if php_code:
            findings.append(("PHP源码", 0.95, "web_php_analysis", php_code))

        # 检查技术栈信息
        tech_stack = self._check_tech_stack(response)
        if tech_stack:
            # 根据技术栈推荐相应测试
            pass

        return findings

    def _check_sql_errors(self, response: str) -> List[str]:
        """检查SQL错误信息"""
        indicators = []

        sql_error_patterns = [
            r"SQL syntax.*?error",
            r"mysql_fetch",
            r"mysqli",
            r"PostgreSQL.*?ERROR",
            r"Warning.*?mysql",
            r"valid MySQL result",
            r"MySqlClient\.",
            r"com\.mysql\.jdbc",
            r"ORA-\d{5}",
            r"SQLite.*?error",
            r"SQLSTATE\[\w+\]",
            r"Syntax error.*?SQL"
        ]

        for pattern in sql_error_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                indicators.append(f"SQL错误: {pattern}")
                break

        return indicators

    def _check_php_code(self, response: str) -> List[str]:
        """检查PHP代码"""
        indicators = []

        # 检查PHP标签
        if '<?php' in response or '<?' in response:
            indicators.append("发现PHP开始标签")

        # 检查PHP函数
        php_functions = ['echo', 'print', 'var_dump', 'print_r', '$_GET', '$_POST', 'include', 'require']
        for func in php_functions:
            if func in response:
                indicators.append(f"发现PHP函数/变量: {func}")
                break

        return indicators

    def _check_tech_stack(self, response: str) -> List[str]:
        """检查技术栈信息"""
        indicators = []

        # 检查响应头中的技术信息（需要完整响应头）
        tech_patterns = {
            'PHP': [r'X-Powered-By:\s*PHP', r'\.php'],
            'Apache': [r'Server:\s*Apache'],
            'Nginx': [r'Server:\s*nginx'],
            'MySQL': [r'mysql', r'MariaDB'],
            'ASP.NET': [r'X-AspNet-Version', r'\.aspx'],
        }

        for tech, patterns in tech_patterns.items():
            for pattern in patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    indicators.append(f"技术栈: {tech}")
                    break

        return indicators

    def get_skill_recommendation(self, url: str, response: str = None) -> Dict:
        """
        综合分析URL和响应，给出技能推荐

        Args:
            url: 目标URL
            response: HTTP响应（可选）

        Returns:
            {
                "recommendations": [
                    {
                        "vuln_type": "SQL注入",
                        "confidence": 0.8,
                        "skill_id": "web_sqli",
                        "reason": "发现数字型参数id=1",
                        "indicators": [...]
                    }
                ],
                "summary": "检测到2个潜在漏洞点"
            }
        """
        recommendations = []

        # 分析URL
        url_findings = self.analyze_url(url)
        for vuln_type, confidence, skill_id, indicators in url_findings:
            recommendations.append({
                "vuln_type": vuln_type,
                "confidence": confidence,
                "skill_id": skill_id,
                "reason": f"URL参数特征: {', '.join(indicators[:2])}",
                "indicators": indicators,
                "source": "url"
            })

        # 分析响应
        if response:
            response_findings = self.analyze_response(response)
            for vuln_type, confidence, skill_id, indicators in response_findings:
                recommendations.append({
                    "vuln_type": vuln_type,
                    "confidence": confidence,
                    "skill_id": skill_id,
                    "reason": f"响应特征: {', '.join(indicators[:2])}",
                    "indicators": indicators,
                    "source": "response"
                })

        # 去重（同一漏洞类型只保留置信度最高的）
        unique_recommendations = {}
        for rec in recommendations:
            vuln_type = rec["vuln_type"]
            if vuln_type not in unique_recommendations or rec["confidence"] > unique_recommendations[vuln_type]["confidence"]:
                unique_recommendations[vuln_type] = rec

        final_recommendations = list(unique_recommendations.values())
        final_recommendations.sort(key=lambda x: x["confidence"], reverse=True)

        summary = f"检测到{len(final_recommendations)}个潜在漏洞点" if final_recommendations else "未检测到明显漏洞特征"

        return {
            "recommendations": final_recommendations,
            "summary": summary
        }
