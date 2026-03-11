# RAG 知识库使用指南

## 丰富知识库的方法

### 1. 使用导入工具
```bash
python import_knowledge.py
```

功能：
- 从单个文件导入
- 从目录批量导入
- 从 URL 导入 Writeup

### 2. 手动添加知识文档

在 `data/knowledge_base/` 目录创建 Markdown 文件：

```markdown
# 标题（会自动提取）

## 题目类型
Web/Pwn/Reverse/Crypto/Misc

## 漏洞类型
SQL注入/XSS/命令注入/反序列化等

## 内容
详细的解题思路、Payload、工具使用等
```

### 3. 自动学习

在 `main.py` 解题后，选择保存到知识库：
- 系统会自动生成 Writeup
- 保存为 `auto_learned_YYYYMMDD_HHMMSS.md`
- 自动导入到 RAG 系统

## 知识来源推荐

### 1. CTF Writeup 网站
- CTFtime.org
- GitHub CTF Writeups
- 各大战队博客

### 2. 漏洞知识库
- OWASP Top 10
- CWE 常见漏洞
- CVE 漏洞详情

### 3. 工具文档
- sqlmap 使用手册
- Burp Suite 技巧
- Metasploit 模块

### 4. 个人经验
- 解题笔记
- 踩坑记录
- 技巧总结

## 知识文档模板

### Web 题目模板
```markdown
# [题目名称] - [漏洞类型]

## 题目类型
Web

## 漏洞类型
SQL注入/XSS/命令注入/反序列化/文件上传/SSRF/XXE

## 题目描述
简要描述题目场景

## 解题思路
1. 信息收集
2. 漏洞发现
3. 漏洞利用
4. Flag 获取

## 关键 Payload
\`\`\`
具体的 Payload 代码
\`\`\`

## 工具使用
\`\`\`bash
具体的命令
\`\`\`

## 注意事项
- 关键点1
- 关键点2

## 相关知识
- 相关漏洞原理
- 绕过技巧
```

### Pwn 题目模板
```markdown
# [题目名称] - [漏洞类型]

## 题目类型
Pwn

## 漏洞类型
栈溢出/堆溢出/格式化字符串/UAF/整数溢出

## 保护机制
- NX: Enabled/Disabled
- PIE: Enabled/Disabled
- Canary: Enabled/Disabled
- RELRO: Full/Partial/None

## 漏洞分析
详细的漏洞分析过程

## Exploit 脚本
\`\`\`python
from pwn import *

# Exploit 代码
\`\`\`

## 调试技巧
- GDB 命令
- 调试过程
```

## 管理知识库

### 查看知识库
```bash
python manage_rag.py
```

### 删除低质量内容
1. 查看所有来源
2. 删除 `auto_learned_*` 中质量差的
3. 删除重复或过时的内容

### 定期维护
- 每周检查自动学习的内容
- 删除无用的记录
- 补充新的漏洞知识
- 更新工具使用方法

## 最佳实践

### 1. 内容质量
- 包含完整的解题流程
- 提供可复用的 Payload
- 注明适用场景和限制
- 添加相关标签

### 2. 文档结构
- 使用清晰的标题层级
- 代码块使用正确的语言标记
- 关键信息使用列表或表格
- 添加示例和注释

### 3. 标签规范
- 题目类型：Web/Pwn/Reverse/Crypto/Misc
- 漏洞类型：具体的漏洞名称
- 工具：使用的工具名称
- 难度：Easy/Medium/Hard

### 4. 更新频率
- 每次解题后及时保存
- 每周整理一次知识库
- 每月清理过时内容
- 持续补充新知识

## 已创建的知识文档

1. `web_sqli_bypass.md` - SQL注入绕过技巧
2. `web_php_unserialize.md` - PHP反序列化漏洞
3. `web_command_injection.md` - 命令注入绕过技巧

可以继续添加：
- XSS 绕过技巧
- 文件上传绕过
- SSRF 利用方法
- XXE 漏洞利用
- SSTI 模板注入
- 等等...

## 使用 RAG 的技巧

### 1. 精确查询
使用具体的漏洞类型和关键词：
- "SQL注入 布尔盲注"
- "PHP反序列化 POP链"
- "命令注入 空格绕过"

### 2. 场景查询
描述具体的场景：
- "过滤了空格的命令注入"
- "绕过 WAF 的 SQL 注入"
- "无回显的命令执行"

### 3. 工具查询
查询工具使用方法：
- "sqlmap 使用方法"
- "Burp Suite 抓包"
- "nmap 端口扫描"
