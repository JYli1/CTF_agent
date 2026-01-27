
import requests

def check_target():
    url = "http://49.232.142.230:17894/"
    try:
        response = requests.get(url)
        # 输出状态码和部分响应文本（仅用于初步检查，避免输出过量内容）
        print(f"Status Code: {response.status_code}")
        print("Response Content Preview:")
        # 限制输出长度，避免信息过多
        content_preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
        print(content_preview)
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    check_target()