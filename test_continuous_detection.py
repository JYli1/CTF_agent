"""
测试改进后的漏洞检测器 - 持续检测
"""

import sys
sys.path.insert(0, 'd:/ctf_agent')

from src.utils.vuln_detector import VulnerabilityDetector

detector = VulnerabilityDetector()

print("=== 漏洞检测器 - 持续检测演示 ===\n")

# 场景1：初始URL分析
print("【场景1】初始URL分析")
print("-" * 60)
url = "http://ctf.com/index.php?id=1"
print(f"输入URL: {url}\n")

result = detector.get_skill_recommendation(url)
print(f"检测结果: {result['summary']}")
for rec in result['recommendations']:
    print(f"  • {rec['vuln_type']} ({rec['confidence']:.0%}) → {rec['skill_id']}")
print()

# 场景2：curl命令执行后的响应分析
print("\n【场景2】curl命令执行后 - 发现SQL错误")
print("-" * 60)
print("命令: curl 'http://ctf.com/index.php?id=1'")
print()

response = """
HTTP/1.1 200 OK
Content-Type: text/html

<html>
<body>
<h1>Error</h1>
<p>MySQL Error: You have an error in your SQL syntax near 'SELECT * FROM users WHERE id = 1'' at line 1</p>
</body>
</html>
"""

print("响应内容:")
print(response[:200] + "...")
print()

vuln_in_response = detector.analyze_response(response)
if vuln_in_response:
    print("🔍 在响应中检测到漏洞特征：")
    for vuln_type, confidence, skill_id, indicators in vuln_in_response:
        print(f"  • {vuln_type} (置信度: {confidence:.0%}) → {skill_id}")
        print(f"    指标: {', '.join(indicators)}")
print()

# 场景3：发现PHP源码
print("\n【场景3】curl命令执行后 - 发现PHP源码")
print("-" * 60)
print("命令: curl 'http://ctf.com/index.php?file=index.php'")
print()

response2 = """
<?php
error_reporting(0);
$file = $_GET['file'];
if(isset($file)) {
    include($file);
}
$flag = "flag{php_source_leak}";
?>
"""

print("响应内容:")
print(response2)
print()

vuln_in_response2 = detector.analyze_response(response2)
if vuln_in_response2:
    print("🔍 在响应中检测到漏洞特征：")
    for vuln_type, confidence, skill_id, indicators in vuln_in_response2:
        print(f"  • {vuln_type} (置信度: {confidence:.0%}) → {skill_id}")
        print(f"    指标: {', '.join(indicators)}")
print()

# 场景4：综合分析
print("\n【场景4】综合分析 - URL + 响应")
print("-" * 60)
url3 = "http://ctf.com/view.php?page=home"
response3 = """
<?php
$page = $_GET['page'];
include($page . '.php');
?>
"""

print(f"URL: {url3}")
print(f"响应: {response3[:50]}...")
print()

result3 = detector.get_skill_recommendation(url3, response3)
print(f"综合检测: {result3['summary']}")
for rec in result3['recommendations']:
    print(f"  • {rec['vuln_type']} ({rec['confidence']:.0%}) → {rec['skill_id']}")
    print(f"    来源: {rec['source']}")
    print(f"    原因: {rec['reason']}")
print()

print("\n=== 总结 ===")
print("改进后的检测器可以：")
print("✓ 1. 分析初始URL")
print("✓ 2. 分析命令执行后的响应")
print("✓ 3. 检测SQL错误信息")
print("✓ 4. 检测PHP源码泄露")
print("✓ 5. 综合URL和响应进行分析")
print("\n持续检测，不遗漏任何漏洞特征！")
