# CTF Agent 技能系统使用指南

## 概述

技能系统将常见的CTF攻击手法封装为可复用的技能模块，让Agent能够快速、系统化地执行标准化攻击流程。

## 已实现的技能

### 1. SQL注入检测与利用 (web_sqli)

**功能**：
- 自动测试多种SQL注入类型
- 包含WAF绕过技巧
- 提供完整的注入测试流程

**使用场景**：
- 发现可疑的URL参数
- 需要系统化测试SQL注入
- 需要绕过WAF

**测试内容**：
1. 基础注入点检测（单引号、双引号）
2. 判断注入类型（数字型/字符型）
3. 判断数据库类型
4. 联合查询注入
5. 报错注入
6. 布尔盲注
7. 时间盲注

**绕过技巧**：
- WAF绕过：/**/注释、大小写混淆、编码
- 空格绕过：/**/、%09、%0a、+
- 引号绕过：十六进制、char()
- 关键字绕过：双写、内联注释

### 2. PHP源码分析 (web_php_analysis)

**功能**：
- 识别危险函数
- 追踪用户输入
- 检测过滤机制
- 发现潜在漏洞点

**使用场景**：
- 获取到PHP源码后
- 需要快速识别漏洞点
- 需要分析代码逻辑

**分析维度**：
1. 危险函数（eval, system, exec等）
2. 用户输入（$_GET, $_POST等）
3. SQL注入风险点
4. 文件操作函数
5. 反序列化漏洞
6. 命令执行风险
7. 文件包含漏洞
8. 输入过滤机制
9. 弱类型比较
10. 变量覆盖风险

### 3. SSRF检测与利用 (web_ssrf)

**功能**：
- 测试内网访问
- 测试协议支持
- IP编码绕过
- 内网服务探测

**使用场景**：
- 发现URL参数可控
- 需要访问内网资源
- 需要探测内网服务

**攻击流程**：
1. 识别SSRF参数
2. 测试外部访问
3. 测试内网访问
4. 测试协议支持（file, dict, gopher等）
5. 绕过过滤
6. 读取敏感文件
7. 探测内网服务
8. 攻击内网服务

**绕过技巧**：
- IP编码：十进制、十六进制、八进制
- 域名绕过：指向127.0.0.1的域名
- 302跳转
- DNS重绑定
- 协议绕过

## 使用方式

### 方式1：战略专家自动调用

战略专家会根据场景自动选择合适的技能：

```json
{
  "current_progress": "需要测试SQL注入",
  "reasoning": "目标URL可能存在SQL注入，使用技能快速检测",
  "action": {
    "url": "http://example.com/index.php?id=1",
    "type": "use_skill",
    "skill_id": "web_sqli",
    "agent": "安全专家",
    "task": null
  },
  "flag": null
}
```

### 方式2：代码直接调用

```python
from src.core.agent import CTFAgent

agent = CTFAgent()
agent.set_target("http://example.com/index.php?id=1")

# 使用SQL注入技能
result = agent.use_skill("web_sqli")

if result['success']:
    print(result['message'])
    print(f"建议命令数: {len(result['commands'])}")
```

### 方式3：Python脚本调用

```python
from src.skills.registry import skill_registry

# 获取技能
sqli_skill = skill_registry.get("web_sqli")

# 准备上下文
context = {"target_url": "http://example.com/index.php?id=1"}

# 执行技能
result = sqli_skill.execute(context, executor)

print(result.message)
```

## 技能执行流程

```
用户输入/战略专家决策
    ↓
识别需要使用的技能
    ↓
调用 agent.use_skill(skill_id)
    ↓
技能检查前置条件
    ↓
技能生成攻击建议和命令列表
    ↓
返回给战略专家
    ↓
战略专家将建议转化为任务
    ↓
指派给专家执行
    ↓
专家逐步执行命令
    ↓
返回结果
```

## 添加新技能

### 1. 创建技能类

```python
from src.skills.base import Skill, SkillCategory, SkillResult

class MyNewSkill(Skill):
    def __init__(self):
        super().__init__()
        self.id = "web_my_skill"
        self.name = "我的新技能"
        self.category = SkillCategory.WEB
        self.description = "技能描述"
        self.prerequisites = ["target_url"]
        self.tools_required = ["execute_shell"]
        self.difficulty = "medium"

    def execute(self, context, executor):
        # 检查前置条件
        ok, msg = self.check_prerequisites(context)
        if not ok:
            return SkillResult(success=False, message=msg)

        # 执行逻辑
        target_url = context["target_url"]
        commands = []
        findings = []

        # 生成命令和建议
        cmd1 = f"curl {target_url}"
        commands.append(cmd1)
        findings.append("测试基础访问")

        message = f"技能执行建议：\n..."

        return SkillResult(
            success=True,
            message=message,
            commands=commands,
            findings=findings
        )
```

### 2. 注册技能

在 `src/skills/loader.py` 中添加：

```python
from .web.my_skill import MyNewSkill

def load_all_skills():
    skill_registry.register(MyNewSkill())
    # ... 其他技能
```

### 3. 更新提示词

在 `src/core/prompts.py` 的技能列表中添加新技能说明。

## 技能vs专家

### 何时使用技能：
- ✅ 遇到常见漏洞类型（SQL注入、SSRF等）
- ✅ 需要系统化测试
- ✅ 想要快速获取攻击建议
- ✅ 需要标准化流程

### 何时使用专家：
- ✅ 需要自定义操作
- ✅ 技能不适用当前场景
- ✅ 需要精细控制
- ✅ 需要组合多个操作

## 技能优势

1. **标准化**：封装最佳实践，避免遗漏关键步骤
2. **高效**：一次调用获取完整攻击流程
3. **可复用**：相同漏洞类型可重复使用
4. **易扩展**：轻松添加新技能
5. **知识积累**：将经验固化为代码

## 未来扩展

### 计划添加的技能：

**Web类**：
- XSS检测与利用
- 文件包含（LFI/RFI）
- 文件上传绕过
- XXE注入
- 命令注入
- 反序列化利用

**Crypto类**：
- Base64/Hex多层解码
- 凯撒密码破解
- RSA弱密钥攻击
- 哈希碰撞

**Misc类**：
- 文件类型分析
- 隐写术检测
- 压缩包爆破

**Reverse类**：
- 字符串提取
- 反编译
- 动态调试

**Pwn类**：
- checksec分析
- ROP gadgets查找
- 缓冲区溢出

## 测试

运行测试脚本：

```bash
python test_skills.py
```

## 注意事项

1. 技能只提供建议，不直接执行命令
2. 专家会根据技能建议逐步执行
3. 技能需要满足前置条件才能使用
4. 技能可以与RAG系统结合，从历史经验中学习
