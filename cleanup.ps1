# 项目清理脚本（Windows版本）

Write-Host "=== CTF Agent 项目清理 ===" -ForegroundColor Cyan
Write-Host ""

# 1. 删除备份文件
Write-Host "[1/7] 删除备份文件..." -ForegroundColor Yellow
Remove-Item -Path "src\core\prompts.py.backup" -ErrorAction SilentlyContinue
Write-Host "✓ 已删除 prompts.py.backup" -ForegroundColor Green

# 2. 删除测试文件（保留重要的）
Write-Host ""
Write-Host "[2/7] 删除测试文件..." -ForegroundColor Yellow
Remove-Item -Path "test.py" -ErrorAction SilentlyContinue
Remove-Item -Path "test_embedding.py" -ErrorAction SilentlyContinue
Remove-Item -Path "test_llm.py" -ErrorAction SilentlyContinue
Remove-Item -Path "test_qwen_embedding.py" -ErrorAction SilentlyContinue
Remove-Item -Path "test_retrieval.py" -ErrorAction SilentlyContinue
Remove-Item -Path "test_ssh.py" -ErrorAction SilentlyContinue
Write-Host "✓ 已删除旧测试文件（保留 test_skills.py 和 test_vuln_detector.py）" -ForegroundColor Green

# 3. 删除调试文件
Write-Host ""
Write-Host "[3/7] 删除调试文件..." -ForegroundColor Yellow
Remove-Item -Path "debug_key.py" -ErrorAction SilentlyContinue
Remove-Item -Path "ingest_docs.py" -ErrorAction SilentlyContinue
Write-Host "✓ 已删除调试文件" -ForegroundColor Green

# 4. 归档过时文档
Write-Host ""
Write-Host "[4/7] 归档过时文档..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path ".archive" -Force | Out-Null
Move-Item -Path "rework.md" -Destination ".archive\" -ErrorAction SilentlyContinue
Move-Item -Path "IMPROVEMENT_PLAN.md" -Destination ".archive\" -ErrorAction SilentlyContinue
Move-Item -Path "SKILLS_DESIGN.md" -Destination ".archive\" -ErrorAction SilentlyContinue
Write-Host "✓ 已归档过时文档到 .archive\" -ForegroundColor Green

# 5. 清理旧日志（保留最近10个）
Write-Host ""
Write-Host "[5/7] 清理旧日志..." -ForegroundColor Yellow
$logs = Get-ChildItem -Path "data\logs\*.md" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
if ($logs.Count -gt 10) {
    $logs | Select-Object -Skip 10 | Remove-Item
}
Remove-Item -Path "data\logs\*.txt" -ErrorAction SilentlyContinue
Write-Host "✓ 已清理旧日志（保留最近10个）" -ForegroundColor Green

# 6. 清理旧的自动学习文件（保留最新的）
Write-Host ""
Write-Host "[6/7] 清理旧的自动学习文件..." -ForegroundColor Yellow
$autoLearned = Get-ChildItem -Path "data\knowledge_base\auto_learned_*.md" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
if ($autoLearned.Count -gt 3) {
    $autoLearned | Select-Object -Skip 3 | Remove-Item
}
Write-Host "✓ 已清理旧的自动学习文件（保留最新3个）" -ForegroundColor Green

# 7. 删除未实现的示例技能
Write-Host ""
Write-Host "[7/7] 删除未实现的示例技能..." -ForegroundColor Yellow
Remove-Item -Path "src\skills\web\xss.py" -ErrorAction SilentlyContinue
Write-Host "✓ 已删除示例技能" -ForegroundColor Green

Write-Host ""
Write-Host "=== 清理完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "已删除的文件类型：" -ForegroundColor White
Write-Host "  - 备份文件"
Write-Host "  - 旧测试文件"
Write-Host "  - 调试文件"
Write-Host "  - 过时文档（已归档）"
Write-Host "  - 旧日志文件"
Write-Host "  - 旧的自动学习文件"
Write-Host "  - 未实现的示例技能"
Write-Host ""
Write-Host "保留的文件：" -ForegroundColor White
Write-Host "  - test_skills.py（技能测试示例）"
Write-Host "  - test_vuln_detector.py（漏洞检测测试示例）"
Write-Host "  - 最近10个会话日志"
Write-Host "  - 最新3个自动学习文件"
Write-Host ""
