# CLI-Anything OpenClaw / Codex 定制版发布公告（2026-03-21）

各位开发者好，

`canxia-hub/cli-anything-openclaw-codex` 的当前已测试版本现已整理完成并推送至 GitHub：

- Repository: `https://github.com/canxia-hub/cli-anything-openclaw-codex`
- Published branch target: `main`

本次发布聚焦于 **托管版一致性收口、Windows 主机验证、以及高风险 harness 的定向回归**，重点完成了以下工作：

## 本次发布内容

### 1. 仓库级一致性与技能打包验证
- 完成仓库级 harness conformance audit：**17/17 PASS**
- 完成 SKILL 路径 / `package_data` / banner skill 展示回归：**51 passed**
- 完成 Codex Windows 安装脚本真实冒烟：**PASS**

### 2. Mermaid 主链路与主体功能闭环
- 修复 Mermaid renderer 外部依赖的超时脆弱性，增加短超时、重试与明确报错
- 修复 Windows 非交互控制台下默认 REPL 进入时的兼容性问题
- 补齐 Mermaid subprocess 测试对 `CLI_ANYTHING_FORCE_INSTALLED=1` 的支持
- 完成 Mermaid 主体功能闭环：
  - 已安装命令可调用
  - `--json` 输出稳定
  - SVG / PNG 真正导出成功
  - Mermaid Live 分享链接生成成功
  - `skill_generator.py` 可生成 `SKILL.md`

### 3. 高风险 harness 定向扩测
- **AdGuardHome**：31 passed / 5 skipped
  - 修复 CLI 模块入口顺序问题
  - Docker 缺失时改为优雅 skip，而非直接报错
- **ComfyUI**：70 passed
  - 修复 `--json` 模式输出混入人类提示的问题
- **NotebookLM**：21 passed
  - 修复测试路径依赖当前工作目录的问题

## 本次发布结论
当前版本已经达到：

- 可作为托管版阶段性发布结果对外展示
- 可作为后续继续扩测与继续发布的稳定基线
- 可供其他开发者接手剩余环境边界测试

## 本次明确未完成的测试
为了避免对外造成“全部环境全覆盖验证完成”的误解，本次也明确保留以下未完成项：

1. **AdGuardHome Docker-backed E2E 未完成**
   - 原因：当前测试主机未安装 Docker
   - 当前状态：相关测试已改为环境不足时 `skip`

2. **`cli-anything-plugin/scripts/setup-cli-anything.sh` 未完成真实 Bash 环境端到端实跑**
   - 原因：当前主机缺少可直接用于该脚本的 Bash / Git Bash / WSL 测试环境

3. **并未在当前这台 Windows 主机上重新全量执行每一个 harness 的完整 pytest 套件**
   - 本次采取的是：
     - 仓库级 conformance audit
     - 技能打包与安装链路验证
     - Mermaid 主体功能闭环
     - 对高风险 harness（AdGuardHome / ComfyUI / NotebookLM）做定向回归

## 测试报告索引
本次发布相关测试文档见：

- `docs/testing/harness-audit-2026-03-21.md`
- `docs/testing/smoke-report-2026-03-21.md`
- `docs/testing/expansion-report-2026-03-21.md`
- `docs/testing/plugin-mermaid-e2e-report-2026-03-21.md`
- `docs/testing/final-test-report-2026-03-21.md`

## 致谢
感谢参与本轮验证、修复与收口的开发者。剩余环境边界测试（Docker / Bash / 更广覆盖的全量主机复测）欢迎后续开发者继续接力完成。

在继续发布、复测或二次开发前，建议优先阅读：

- `README.md`
- `docs/testing/final-test-report-2026-03-21.md`
- `DISCLAIMER.md`
- `NOTICE.md`
