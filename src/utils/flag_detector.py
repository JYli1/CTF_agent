import re
import base64
import binascii

class FlagDetector:
    """
    统一的Flag检测器，支持多种格式和编码
    """

    def __init__(self):
        # 标准flag格式的正则模式
        self.patterns = [
            # 通用格式：任意字母数字组合{内容}
            r'\b[a-zA-Z0-9_\-]+\{[^}]+\}',

            # 标签格式
            r'\[flag\]([^\[]+)\[/flag\]',

            # 键值对格式
            r'flag[:=]\s*([a-zA-Z0-9_\-\{\}]+)',
            r'flag\s+is\s+([a-zA-Z0-9_\-\{\}]+)',
        ]

    def detect(self, text: str) -> dict:
        """
        检测文本中的flag

        返回:
            {
                "found": bool,
                "flags": [flag1, flag2, ...],
                "method": "direct/base64/hex"
            }
        """
        if not text:
            return {"found": False, "flags": [], "method": None}

        # 1. 直接检测
        flags = self._direct_detect(text)
        if flags:
            return {"found": True, "flags": flags, "method": "direct"}

        # 2. Base64解码后检测
        flags = self._base64_detect(text)
        if flags:
            return {"found": True, "flags": flags, "method": "base64"}

        # 3. Hex解码后检测
        flags = self._hex_detect(text)
        if flags:
            return {"found": True, "flags": flags, "method": "hex"}

        return {"found": False, "flags": [], "method": None}

    def _direct_detect(self, text: str) -> list:
        """直接匹配flag格式"""
        flags = []
        text_lower = text.lower()

        for pattern in self.patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]

                # 过滤明显不是flag的内容
                if not match or len(match) < 5:  # 太短
                    continue

                # 如果是xxx{xxx}格式，检查是否是常见的非flag模式
                if '{' in match and '}' in match:
                    # 排除常见的代码模式
                    exclude_patterns = [
                        r'^(function|class|struct|interface|enum)\{',  # 代码关键字
                        r'^\$\{',  # 变量替换
                        r'^@\{',   # 注解
                        r'^\#\{',  # 注释
                    ]

                    is_excluded = False
                    for exclude in exclude_patterns:
                        if re.match(exclude, match, re.IGNORECASE):
                            is_excluded = True
                            break

                    if is_excluded:
                        continue

                    # 检查花括号内容是否合理（不能太短或全是特殊字符）
                    inner_content = re.search(r'\{([^}]+)\}', match)
                    if inner_content:
                        inner = inner_content.group(1)
                        # 内容至少3个字符，且包含字母或数字
                        if len(inner) < 3 or not re.search(r'[a-zA-Z0-9]', inner):
                            continue

                if match not in flags:
                    flags.append(match)

        return flags

    def _base64_detect(self, text: str) -> list:
        """尝试Base64解码后检测"""
        flags = []

        # 查找可能的base64字符串（长度>20的字母数字串）
        base64_candidates = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', text)

        for candidate in base64_candidates:
            try:
                decoded = base64.b64decode(candidate).decode('utf-8', errors='ignore')
                detected = self._direct_detect(decoded)
                if detected:
                    flags.extend(detected)
            except:
                continue

        return flags

    def _hex_detect(self, text: str) -> list:
        """尝试Hex解码后检测"""
        flags = []

        # 查找可能的hex字符串
        hex_candidates = re.findall(r'(?:0x)?([0-9a-fA-F]{40,})', text)

        for candidate in hex_candidates:
            try:
                decoded = bytes.fromhex(candidate).decode('utf-8', errors='ignore')
                detected = self._direct_detect(decoded)
                if detected:
                    flags.extend(detected)
            except:
                continue

        return flags
