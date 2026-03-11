# CTF Agent 技能系统设计方案

## 1. 架构设计

### 1.1 技能分类
按CTF题目类型组织技能：
- **Web** - Web安全相关技能
- **Crypto** - 密码学相关技能
- **Reverse** - 逆向工程相关技能
- **Pwn** - 二进制漏洞利用相关技能
- **Misc** - 杂项技能

### 1.2 技能结构
每个技能包含：
```python
{
    "id": "web_sqli_detect",
    "name": "SQL注入检测",
    "category": "web",
    "description": "检测目标是否存在SQL注入漏洞",
    "prerequisites": ["target_url"],  # 前置条件
    "tools_required": ["execute_shell"],  # 需要的工具
    "difficulty": "medium",
    "execute": function  # 执行函数
}
```

### 1.3 集成方式
```
用户输入
    ↓
战略专家分析
    ↓
识别题目类型 → 加载对应技能库
    ↓
选择合适技能 → 指派给专家
    ↓
专家执行技能 → 返回结果
    ↓
战略专家综合分析
```

## 2. 技能示例

### 2.1 Web技能
1. **信息收集**
   - `web_info_gather` - 基础信息收集（响应头、robots.txt、sitemap）
   - `web_dir_scan` - 目录扫描
   - `web_subdomain_enum` - 子域名枚举

2. **漏洞检测**
   - `web_sqli_detect` - SQL注入检测
   - `web_xss_detect` - XSS检测
   - `web_lfi_detect` - 本地文件包含检测
   - `web_rfi_detect` - 远程文件包含检测
   - `web_ssrf_detect` - SSRF检测

3. **漏洞利用**
   - `web_sqli_exploit` - SQL注入利用
   - `web_file_upload` - 文件上传绕过
   - `web_deserialize` - 反序列化利用

### 2.2 Crypto技能
1. **编码识别**
   - `crypto_detect_encoding` - 识别编码类型（Base64/Hex/URL等）
   - `crypto_decode_multi` - 多层解码

2. **密码分析**
   - `crypto_caesar` - 凯撒密码破解
   - `crypto_rsa_weak` - 弱RSA攻击
   - `crypto_hash_crack` - 哈希碰撞

### 2.3 Reverse技能
1. **静态分析**
   - `reverse_strings` - 提取字符串
   - `reverse_decompile` - 反编译

2. **动态分析**
   - `reverse_debug` - 动态调试
   - `reverse_trace` - 函数追踪

### 2.4 Pwn技能
1. **漏洞检测**
   - `pwn_checksec` - 安全检查
   - `pwn_find_gadgets` - 查找ROP gadgets

2. **漏洞利用**
   - `pwn_buffer_overflow` - 缓冲区溢出
   - `pwn_format_string` - 格式化字符串

### 2.5 Misc技能
1. **通用工具**
   - `misc_file_analysis` - 文件分析
   - `misc_steganography` - 隐写术检测
   - `misc_forensics` - 取证分析

## 3. 实现文件结构

```
src/skills/
├── __init__.py
├── base.py              # 技能基类
├── registry.py          # 技能注册中心
├── web/
│   ├── __init__.py
│   ├── info_gather.py
│   ├── sqli.py
│   ├── xss.py
│   └── file_inclusion.py
├── crypto/
│   ├── __init__.py
│   ├── encoding.py
│   ├── classical.py
│   └── modern.py
├── reverse/
│   ├── __init__.py
│   ├── static.py
│   └── dynamic.py
├── pwn/
│   ├── __init__.py
│   ├── detection.py
│   └── exploitation.py
└── misc/
    ├── __init__.py
    ├── file_analysis.py
    └── steganography.py
```

## 4. 使用流程

### 4.1 战略专家提示词增强
```
你现在可以使用技能系统。可用技能分类：
- Web: SQL注入、XSS、文件包含等
- Crypto: 编码识别、密码破解等
- Reverse: 静态分析、动态调试等
- Pwn: 缓冲区溢出、ROP等
- Misc: 文件分析、隐写术等

当你需要执行特定任务时，可以：
1. 使用技能：[USE_SKILL] skill_id [/USE_SKILL]
2. 或指派给专家执行自定义任务
```

### 4.2 执行示例
```python
# 战略专家识别需要SQL注入检测
response = """
分析：目标是Web应用，需要检测SQL注入
决策：使用SQL注入检测技能

[USE_SKILL]
web_sqli_detect
[/USE_SKILL]
"""

# Agent解析并执行技能
skill = skill_registry.get("web_sqli_detect")
result = skill.execute(target_url="http://example.com")
```

## 5. 优势

1. **模块化** - 每个技能独立，易于维护和扩展
2. **复用性** - 常用攻击手法封装为技能，避免重复编写
3. **可扩展** - 轻松添加新技能
4. **智能选择** - 战略专家根据场景自动选择合适技能
5. **知识积累** - 技能可以从历史经验中学习和优化

## 6. 实施步骤

### 阶段1：基础框架（高优先级）
1. 创建技能基类和注册中心
2. 实现技能加载和执行机制
3. 修改战略专家提示词，支持技能调用

### 阶段2：Web技能库（高优先级）
1. 实现5-10个常用Web技能
2. 测试技能执行效果
3. 优化技能参数和输出

### 阶段3：其他分类（中优先级）
1. 实现Crypto技能库
2. 实现Misc技能库
3. 实现Reverse和Pwn技能库

### 阶段4：智能增强（低优先级）
1. 技能推荐系统
2. 技能链组合
3. 自动学习新技能

## 7. 与现有系统集成

### 7.1 与专家系统集成
- 战略专家：负责选择技能
- 安全专家：执行Web/Pwn技能
- Python专家：执行Crypto/编码技能

### 7.2 与RAG系统集成
- 技能执行结果可以存入知识库
- 从历史技能执行中学习最佳实践

### 7.3 与阶段追踪集成
- 技能执行可以触发阶段达成
- 某些技能需要特定阶段才能使用

## 8. 配置示例

```yaml
# skills_config.yaml
skills:
  web_sqli_detect:
    enabled: true
    timeout: 30
    tools:
      - sqlmap
      - custom_script

  web_dir_scan:
    enabled: true
    timeout: 60
    wordlist: /path/to/wordlist.txt
```
