# 漏洞自动识别系统

## 概述

漏洞自动识别系统能够分析URL和HTTP响应，自动识别潜在的漏洞特征，并推荐对应的技能进行测试。

## 核心功能

### 1. URL参数分析

自动识别URL中的可疑参数：

#### SQL注入特征
- **参数名识别**：`id`, `uid`, `user_id`, `page`, `cat`, `search`等
- **数字参数**：`?id=1` → 高概率SQL注入点
- **置信度**：80%

示例：
```
http://example.com/index.php?id=1
→ 检测到：SQL注入 (80%) → 推荐技能: web_sqli
```

#### SSRF特征
- **参数名识别**：`url`, `link`, `redirect`, `target`, `callback`等
- **URL值检测**：参数值包含`http://`、`https://`
- **置信度**：80%

示例：
```
http://example.com/fetch.php?url=http://internal.com
→ 检测到：SSRF (80%) → 推荐技能: web_ssrf
```

#### 文件包含特征
- **参数名识别**：`file`, `page`, `include`, `template`, `path`等
- **路径特征**：包含`/`、`\`、`..`
- **文件扩展名**：`.php`, `.html`, `.txt`
- **置信度**：70%

示例：
```
http://example.com/view.php?file=../../../etc/passwd
→ 检测到：文件包含 (70%) → 推荐技能: web_lfi
```

#### 命令注入特征
- **参数名识别**：`cmd`, `command`, `exec`, `ping`, `ip`等
- **置信度**：70%

示例：
```
http://example.com/ping.php?cmd=whoami
→ 检测到：命令注入 (70%) → 推荐技能: web_cmdi
```

### 2. HTTP响应分析

自动识别响应中的漏洞特征：

#### SQL错误信息
检测模式：
- `SQL syntax error`
- `mysql_fetch`
- `PostgreSQL ERROR`
- `SQLSTATE[...]`
- `ORA-xxxxx`

置信度：90%

#### PHP源码泄露
检测模式：
- `<?php` 标签
- PHP函数：`echo`, `print`, `var_dump`
- PHP变量：`$_GET`, `$_POST`

置信度：95%

示例：
```
响应包含：<?php $id = $_GET['id']; ?>
→ 检测到：PHP源码 (95%) → 推荐技能: web_php_analysis
```

#### 技术栈识别
检测：
- PHP版本
- Apache/Nginx
- MySQL/MariaDB
- ASP.NET

用于辅助判断可能的漏洞类型。

## 工作流程

```
用户设置目标URL
    ↓
Agent自动调用漏洞检测器
    ↓
分析URL参数特征
    ↓
（如有响应）分析响应内容
    ↓
识别潜在漏洞类型
    ↓
推荐对应技能
    ↓
显示给用户和战略专家
    ↓
战略专家根据建议决策
    ↓
使用推荐的技能测试
```

## 使用示例

### 自动模式（Agent集成）

当你设置目标URL后，Agent会自动检测：

```python
agent = CTFAgent()
agent.set_target("http://example.com/index.php?id=1")

# Agent会自动显示：
# 🔍 正在分析目标URL的漏洞特征...
# 🎯 漏洞特征识别
# 检测到1个潜在漏洞点
#   • SQL注入 (置信度: 80%) → 推荐技能: web_sqli
#     原因: URL参数特征: 参数名: id, 数字参数: id=1
```

### 手动调用

```python
from src.utils.vuln_detector import VulnerabilityDetector

detector = VulnerabilityDetector()

# 分析URL
result = detector.get_skill_recommendation(
    url="http://example.com/index.php?id=1",
    response=None  # 可选
)

print(result['summary'])
for rec in result['recommendations']:
    print(f"{rec['vuln_type']}: {rec['skill_id']}")
```

## 检测规则

### 参数名匹配规则

| 漏洞类型 | 参数名关键字 | 示例 |
|---------|------------|------|
| SQL注入 | id, uid, user, page, cat, search | ?id=1 |
| SSRF | url, link, redirect, target, callback | ?url=http:// |
| 文件包含 | file, page, include, template, path | ?file=index.php |
| 命令注入 | cmd, command, exec, ping, ip | ?cmd=ls |

### 参数值特征

| 特征 | 说明 | 示例 |
|-----|------|------|
| 纯数字 | 可能是数据库ID | id=123 |
| URL格式 | 可能是SSRF | url=http://example.com |
| 路径格式 | 可能是文件包含 | file=../etc/passwd |
| 文件扩展名 | 可能是文件操作 | page=index.php |

### 响应特征

| 特征 | 正则模式 | 漏洞类型 |
|-----|---------|---------|
| SQL错误 | `SQL syntax.*error` | SQL注入 |
| PHP标签 | `<?php` | PHP源码泄露 |
| MySQL函数 | `mysql_fetch` | SQL注入 |
| PostgreSQL错误 | `PostgreSQL.*ERROR` | SQL注入 |

## 置信度说明

- **90-100%**：非常确定，强烈建议测试
  - 例：响应中包含SQL错误信息
  - 例：响应中包含PHP源码

- **70-89%**：较为确定，建议测试
  - 例：URL包含`?id=1`这样的数字参数
  - 例：URL包含`?url=`这样的SSRF参数

- **50-69%**：可能存在，可以尝试
  - 例：参数名模糊匹配
  - 例：技术栈推测

## 与技能系统集成

检测到漏洞后，自动推荐对应技能：

| 检测到的漏洞 | 推荐技能 | 技能功能 |
|------------|---------|---------|
| SQL注入 | web_sqli | 系统化SQL注入测试 |
| SSRF | web_ssrf | SSRF检测与利用 |
| PHP源码 | web_php_analysis | PHP源码漏洞分析 |
| 文件包含 | web_lfi | 文件包含测试（待实现） |
| 命令注入 | web_cmdi | 命令注入测试（待实现） |

## 优势

1. **自动化**：无需手动判断，自动识别漏洞特征
2. **智能推荐**：根据特征推荐最合适的技能
3. **提高效率**：快速定位测试方向
4. **降低遗漏**：系统化检测，不会遗漏常见漏洞
5. **可扩展**：轻松添加新的检测规则

## 实际效果

### 场景1：发现SQL注入点

```
用户输入：http://ctf.example.com/article.php?id=1

系统输出：
🔍 正在分析目标URL的漏洞特征...
🎯 漏洞特征识别: 检测到1个潜在漏洞点
  • SQL注入 (置信度: 80%) → 推荐技能: web_sqli
    原因: URL参数特征: 参数名: id, 数字参数: id=1

战略专家决策：
{
  "reasoning": "系统检测到SQL注入特征，使用web_sqli技能系统化测试",
  "action": {
    "type": "use_skill",
    "skill_id": "web_sqli",
    "agent": "安全专家"
  }
}
```

### 场景2：发现PHP源码

```
用户输入：http://ctf.example.com/index.php

响应包含：<?php $flag = "flag{...}"; ?>

系统输出：
🔍 正在分析目标URL的漏洞特征...
🎯 漏洞特征识别: 检测到1个潜在漏洞点
  • PHP源码 (置信度: 95%) → 推荐技能: web_php_analysis
    原因: 响应特征: 发现PHP开始标签, 发现PHP函数/变量: $_GET

战略专家决策：
{
  "reasoning": "响应中包含PHP源码，使用web_php_analysis技能分析漏洞",
  "action": {
    "type": "use_skill",
    "skill_id": "web_php_analysis",
    "agent": "Python专家"
  }
}
```

## 未来扩展

### 计划添加的检测规则

1. **XSS检测**
   - 输入框参数
   - 搜索参数
   - 反射型XSS特征

2. **XXE检测**
   - XML内容类型
   - XML解析错误

3. **反序列化检测**
   - Base64编码的序列化数据
   - 特定序列化格式

4. **目录遍历检测**
   - 路径参数
   - 目录列表响应

5. **认证绕过检测**
   - 登录页面
   - 认证参数

## 配置

未来可以通过配置文件自定义检测规则：

```yaml
# vuln_detection_config.yaml
sql_injection:
  enabled: true
  confidence: 0.8
  param_names:
    - id
    - uid
    - custom_param  # 自定义参数名

ssrf:
  enabled: true
  confidence: 0.8
  param_names:
    - url
    - custom_url  # 自定义参数名
```

## 测试

运行测试脚本：

```bash
python test_vuln_detector.py
```

测试覆盖：
- SQL注入检测
- SSRF检测
- 文件包含检测
- 命令注入检测
- PHP源码检测
- SQL错误检测
- 综合场景测试
