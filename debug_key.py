import os
from dotenv import load_dotenv
from openai import OpenAI

# Force reload
load_dotenv(override=True)

api_key = os.getenv("DASHSCOPE_API_KEY")
print(f"已加载 API Key: {api_key!r}") 

if not api_key:
    print("错误: API Key 为空！请检查 .env 文件。")
    exit(1)

try:
    print("正在测试连接到 ModelScope Inference (OpenAI 兼容接口)...")
    
    client = OpenAI(
        base_url='https://api-inference.modelscope.cn/v1',
        api_key=api_key
    )

    response = client.chat.completions.create(
        model='ZhipuAI/GLM-4.7-Flash',
        messages=[
            {'role': 'user', 'content': '你好，请回复“API连接成功”'}
        ],
        stream=False
    )
    
    print("成功！API Key 有效。")
    print("模型回复:", response.choices[0].message.content)

except Exception as e:
    print(f"连接失败！")
    print(f"发生异常: {e}")
