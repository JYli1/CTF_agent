import os
import datetime

class Reporter:
    """
    处理日志记录和报告生成。
    """
    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
    def create_report(self, task_name: str, content: list):
        """
        为任务生成 markdown 报告。
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join([c if c.isalnum() else "_" for c in task_name])
        filename = f"{self.log_dir}/{safe_name}_{timestamp}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# CTF Agent Report: {task_name}\n")
            f.write(f"Date: {timestamp}\n\n")
            
            for item in content:
                role = item.get('role', 'unknown')
                text = item.get('content', '')
                f.write(f"## {role.upper()}\n\n")
                f.write(f"{text}\n\n")
                
        return filename
