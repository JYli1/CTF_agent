"""
测试漏洞检测器
"""

import sys
sys.path.insert(0, 'd:/ctf_agent')

from src.utils.vuln_detector import VulnerabilityDetector

detector = VulnerabilityDetector()

print("=== 漏洞检测器测试 ===\n")

# 测试用例
test_cases = [
    {
        "name": "SQL注入 - 数字参数",
        "url": "http://example.com/index.php?id=1",
        "response": None
    },
    {
        "name": "SQL注入 - 多个参数",
        "url": "http://example.com/user.php?id=1&name=admin&page=2",
        "response": None
    },
    {
        "name": "SSRF - URL参数",
        "url": "http://example.com/fetch.php?url=http://internal.com",
        "response": None
    },
    {
        "name": "文件包含 - file参数",
        "url": "http://example.com/view.php?file=../../../etc/passwd",
        "response": None
    },
    {
        "name": "命令注入 - cmd参数",
        "url": "http://example.com/ping.php?cmd=whoami",
        "response": None
    },
    {
        "name": "SQL错误 - 响应检测",
        "url": "http://example.com/test.php",
        "response": "MySQL Error: You have an error in your SQL syntax near 'SELECT'"
    },
    {
        "name": "PHP源码 - 响应检测",
        "url": "http://example.com/test.php",
        "response": "<?php $id = $_GET['id']; echo $id; ?>"
    },
    {
        "name": "综合测试",
        "url": "http://example.com/article.php?id=1&category=news",
        "response": "<?php\n$id = $_GET['id'];\n$sql = \"SELECT * FROM articles WHERE id = $id\";\n?>"
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*60}")
    print(f"测试 {i}: {test['name']}")
    print(f"URL: {test['url']}")
    if test['response']:
        print(f"响应: {test['response'][:50]}...")
    print(f"{'='*60}")

    result = detector.get_skill_recommendation(test['url'], test['response'])

    print(f"\n{result['summary']}\n")

    if result['recommendations']:
        for rec in result['recommendations']:
            print(f"漏洞类型: {rec['vuln_type']}")
            print(f"置信度: {rec['confidence']:.0%}")
            print(f"推荐技能: {rec['skill_id']}")
            print(f"原因: {rec['reason']}")
            print(f"来源: {rec['source']}")
            print(f"指标: {', '.join(rec['indicators'][:3])}")
            print()

print("\n=== 测试完成 ===")
