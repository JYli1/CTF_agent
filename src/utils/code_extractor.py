import re

def extract_php_code(content: str) -> list[str]:
    """
    从HTML内容中提取PHP代码块

    返回:
        PHP代码块列表
    """
    # 匹配 <?php ... ?> 和 <? ... ?>
    patterns = [
        r'<\?php(.*?)\?>',
        r'<\?(.*?)\?>'
    ]

    php_blocks = []
    for pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        php_blocks.extend(matches)

    return [block.strip() for block in php_blocks if block.strip()]
