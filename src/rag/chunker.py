import re

class SimpleChunker:
    """
    一个简单的分块器，基于标题或逻辑块分割文本。
    专门针对 CTF Writeup 的 Markdown 和代码格式进行了优化。
    """
    
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        """
        将文本分割成块。
        优先级：
        1. 按 Markdown 标题分割 (#, ##, ###)
        2. 如果块仍然太大，按代码块分割 (```)
        3. 如果仍然太大，按段落分割 (\\n\\n)
        """
        # 首先，尝试按主标题分割，以保持逻辑章节的完整性
        # 正则表达式查找像 # Title, ## Subtitle 这样的标题
        headers_pattern = r'(^#{1,3}\s+.+$)'
        
        # 分割但保留分隔符（标题）
        parts = re.split(headers_pattern, text, flags=re.MULTILINE)
        
        chunks = []
        current_chunk = ""
        
        for part in parts:
            if not part.strip():
                continue
                
            # 如果添加此部分超过块大小，验证是否应该开始新块
            if len(current_chunk) + len(part) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # 带重叠开始新块（简单实现：直接开始新的）
                    # 对于简单实现，我们暂时跳过复杂的重叠逻辑
                    current_chunk = part
                else:
                    # 部分本身很大。我们需要进一步分割它。
                    sub_chunks = self._split_large_block(part)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
            else:
                current_chunk += part
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    def _split_large_block(self, text: str) -> list[str]:
        """
        分割没有标题的大块文本。
        尝试按代码块或换行符分割。
        """
        # 尝试按代码块分隔符分割
        code_block_pattern = r'(```[\s\S]*?```)'
        parts = re.split(code_block_pattern, text)
        
        chunks = []
        current_chunk = ""
        
        for part in parts:
            if len(current_chunk) + len(part) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # 如果部分本身（例如巨大的代码块）仍然太大，
                # 作为最后手段，按字符限制强制分割
                if len(part) > self.chunk_size:
                    chunks.extend(self._hard_split(part))
                    current_chunk = ""
                else:
                    current_chunk = part
            else:
                current_chunk += part
                
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    def _hard_split(self, text: str) -> list[str]:
        """按字符数强制分割。"""
        return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]
