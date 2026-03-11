#!/bin/bash
# 项目清理脚本

echo "=== CTF Agent 项目清理 ==="
echo ""

# 1. 删除备份文件
echo "[1/7] 删除备份文件..."
rm -f src/core/prompts.py.backup
echo "✓ 已删除 prompts.py.backup"

# 2. 删除测试文件（保留重要的）
echo ""
echo "[2/7] 删除测试文件..."
rm -f test.py
rm -f test_embedding.py
rm -f test_llm.py
rm -f test_qwen_embedding.py
rm -f test_retrieval.py
rm -f test_ssh.py
echo "✓ 已删除旧测试文件（保留 test_skills.py 和 test_vuln_detector.py）"

# 3. 删除调试文件
echo ""
echo "[3/7] 删除调试文件..."
rm -f debug_key.py
rm -f ingest_docs.py
echo "✓ 已删除调试文件"

# 4. 归档过时文档
echo ""
echo "[4/7] 归档过时文档..."
mkdir -p .archive
mv rework.md .archive/ 2>/dev/null
mv IMPROVEMENT_PLAN.md .archive/ 2>/dev/null
mv SKILLS_DESIGN.md .archive/ 2>/dev/null
echo "✓ 已归档过时文档到 .archive/"

# 5. 清理旧日志（保留最近10个）
echo ""
echo "[5/7] 清理旧日志..."
cd data/logs
# 保留最新的10个.md文件
ls -t *.md 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null
# 删除所有.txt文件
rm -f *.txt 2>/dev/null
cd ../..
echo "✓ 已清理旧日志（保留最近10个）"

# 6. 清理旧的自动学习文件（保留最新的）
echo ""
echo "[6/7] 清理旧的自动学习文件..."
cd data/knowledge_base
ls -t auto_learned_*.md 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null
cd ../..
echo "✓ 已清理旧的自动学习文件（保留最新3个）"

# 7. 删除未实现的示例技能
echo ""
echo "[7/7] 删除未实现的示例技能..."
rm -f src/skills/web/xss.py
echo "✓ 已删除示例技能"

echo ""
echo "=== 清理完成 ==="
echo ""
echo "已删除的文件类型："
echo "  - 备份文件"
echo "  - 旧测试文件"
echo "  - 调试文件"
echo "  - 过时文档（已归档）"
echo "  - 旧日志文件"
echo "  - 旧的自动学习文件"
echo "  - 未实现的示例技能"
echo ""
echo "保留的文件："
echo "  - test_skills.py（技能测试示例）"
echo "  - test_vuln_detector.py（漏洞检测测试示例）"
echo "  - 最近10个会话日志"
echo "  - 最新3个自动学习文件"
echo ""
