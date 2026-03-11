import re

class SimpleChunker:
    """
    一个增强的分块器，基于语义结构（标题、段落、代码块）分割文本。
    专门针对 CTF Writeup 的 Markdown 和代码格式进行了优化。
    """
    
    def __init__(self, chunk_size=800, chunk_overlap=150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        """
        将文本分割成块。
        采用分层分割策略：
        1. 按一级标题 (# )
        2. 按二级标题 (## )
        3. 按三级标题 (### )
        4. 按换行符 (\n\n)
        5. 按代码块边界
        """
        chunks = []
        
        # 预处理：统一换行符，移除多余空行
        text = text.replace('\r\n', '\n')
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 1. 尝试按 Markdown 标题分割（保留标题）
        # 正则捕获：(#+ Title)
        # 使用非贪婪匹配尽量保持上下文
        header_pattern = r'(^#{1,3}\s+.+$)'
        parts = re.split(header_pattern, text, flags=re.MULTILINE)
        
        # 合并部分以形成初始逻辑块
        logical_blocks = []
        current_block = ""
        
        for part in parts:
            if not part.strip():
                continue
            
            # 如果是标题，且当前块已有内容，说明是新章节的开始
            is_header = re.match(header_pattern, part, flags=re.MULTILINE)
            
            if is_header:
                if current_block:
                    logical_blocks.append(current_block)
                current_block = part
            else:
                # 将内容附加到当前标题下
                current_block += "\n" + part
        
        if current_block:
            logical_blocks.append(current_block)
            
        # 2. 对每个逻辑块进行大小检查和进一步分割
        for block in logical_blocks:
            if len(block) <= self.chunk_size:
                chunks.append(block.strip())
            else:
                # 块过大，需要递归分割
                chunks.extend(self._recursive_split(block))
                
        # 3. 后处理：合并过小的碎片块（可选）
        return self._merge_small_chunks(chunks)

    def _recursive_split(self, text: str) -> list[str]:
        """
        递归分割大块文本。
        优先级：代码块 -> 段落 -> 句子 -> 字符
        """
        if len(text) <= self.chunk_size:
            return [text.strip()]
            
        # 1. 尝试按代码块分割（保护代码完整性）
        if "```" in text:
            code_pattern = r'(```[\s\S]*?```)'
            parts = re.split(code_pattern, text)
            chunks = []
            for part in parts:
                if not part.strip(): continue
                # 如果代码块本身过大，也没办法，只能按行强切或保留
                if len(part) > self.chunk_size and part.startswith("```"):
                     # 代码块过大，不做处理直接放入，或者按行切
                     chunks.append(part) 
                else:
                    chunks.extend(self._recursive_split(part))
            return chunks

        # 2. 尝试按双换行（段落）分割
        if "\n\n" in text:
            parts = text.split("\n\n")
            return self._combine_parts(parts, delimiter="\n\n")

        # 3. 尝试按单换行分割
        if "\n" in text:
            parts = text.split("\n")
            return self._combine_parts(parts, delimiter="\n")
            
        # 4. 强制按字符分割（带重叠）
        return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]

    def _combine_parts(self, parts: list[str], delimiter: str) -> list[str]:
        """
        将分割后的部分重新组合，尽量填满 chunk_size
        """
        chunks = []
        current_chunk = ""
        
        for part in parts:
            if not part.strip(): continue
            
            new_chunk = current_chunk + delimiter + part if current_chunk else part
            
            if len(new_chunk) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = part
                else:
                    # 单个部分依然过大
                    chunks.extend(self._recursive_split(part))
                    current_chunk = ""
            else:
                current_chunk = new_chunk
                
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    def _merge_small_chunks(self, chunks: list[str]) -> list[str]:
        """
        合并过小的块，避免碎片化上下文
        """
        if not chunks: return []
        
        merged = []
        current = chunks[0]
        
        for i in range(1, len(chunks)):
            next_chunk = chunks[i]
            if len(current) + len(next_chunk) < self.chunk_size * 0.5: # 阈值可调
                current += "\n\n" + next_chunk
            else:
                merged.append(current)
                current = next_chunk
        
        merged.append(current)
        return merged
