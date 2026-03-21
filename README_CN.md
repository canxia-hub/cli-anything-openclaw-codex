<h1 align="center"><img src="assets/icon.png" alt="" width="64" style="vertical-align: middle;">&nbsp; CLI-Anything：让软件真正变成 Agent 可用的 CLI</h1>

<p align="center">
  <strong>把 GUI 软件、云服务或本地后端整理成 Agent 能稳定调用的 CLI。<br>
  本仓库为 OpenClaw / Codex 定制托管版。</strong>
</p>

<p align="center">
  <a href="README.md">English README</a> ·
  <a href="docs/testing/final-test-report-2026-03-21.md">总测试报告</a> ·
  <a href="docs/openclaw-agent-install-cn.md">OpenClaw Agent 安装说明</a>
</p>

---

## 仓库说明

本仓库是基于上游 [`HKUDS/CLI-Anything`](https://github.com/HKUDS/CLI-Anything) 维护的托管分支：

- 上游仓库：`HKUDS/CLI-Anything`
- 当前托管仓库：`canxia-hub/cli-anything-openclaw-codex`
- 维护方式：**OpenClaw 编排 + Codex 执行**

本仓库保留上游许可证和归属说明，请在使用前同时阅读：

- [`LICENSE`](LICENSE)
- [`NOTICE.md`](NOTICE.md)
- [`DISCLAIMER.md`](DISCLAIMER.md)

---

## 这是什么

CLI-Anything 的目标很直接：

> **把原本给人类操作的软件，转成 Agent 可发现、可组合、可测试、可脚本化的 CLI。**

它适合做这些事：

- 为有源码的软件自动生成结构化 CLI
- 把零散 API 组织成可组合的命令组
- 让 Agent 用 `--help` / `--json` / REPL 直接接管真实软件
- 为后续自动化测试、Benchmark、任务编排提供统一接口

生成的 harness 通常具备这些特征：

- Click 命令行结构
- 默认 REPL 模式
- `--json` 机器可读输出
- `cli_anything.<software>` 命名空间包结构
- `SKILL.md` 自动生成与随包分发
- `test_core.py` + `test_full_e2e.py` 双层测试

---

## 当前托管版验证状态（2026-03-21）

这次托管版发布前，已经在 **Windows 主机** 上做过一轮集中验证。

### 已完成验证

- 仓库级 harness conformance audit：**17/17 PASS**
- SKILL 路径 / `package_data` / banner skill 展示回归：**51 passed**
- Mermaid force-installed 测试：**13 passed**
- AdGuardHome 定向扩测：**31 passed / 5 skipped**
- ComfyUI 定向扩测：**70 passed**
- NotebookLM 定向扩测：**21 passed**
- Codex Windows 安装脚本真实冒烟：**PASS**
- Mermaid 主体功能闭环（已安装命令 + JSON + 导出 + SKILL 生成）：**PASS**

### 尚未完成的测试

以下项目已经明确标注为**未完成**，方便后续开发者继续接力：

1. **AdGuardHome Docker-backed E2E 未完成**
   - 原因：当前测试主机没有 Docker
   - 当前状态：已改成环境不足时 `skip`，不会误报为代码错误

2. **`cli-anything-plugin/scripts/setup-cli-anything.sh` 未完成真实 Bash / Git Bash / WSL 端到端实跑**
   - 原因：当前主机没有合适的 Bash 环境

3. **未在当前这台 Windows 主机上重新全量执行每一个 harness 的完整 pytest 套件**
   - 本次采用的是：
     - 仓库级 conformance audit
     - 打包与安装链路验证
     - Mermaid 主体功能闭环
     - 高风险 harness 定向回归（AdGuardHome / ComfyUI / NotebookLM）

完整说明请看：

- [`docs/testing/final-test-report-2026-03-21.md`](docs/testing/final-test-report-2026-03-21.md)

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/canxia-hub/cli-anything-openclaw-codex.git
cd cli-anything-openclaw-codex
```

### 2. 选择你的平台

CLI-Anything 当前主要提供这些接入方式：

- Claude Code 插件：`cli-anything-plugin/`
- OpenCode 命令：`opencode-commands/`
- OpenClaw Skill：`openclaw-skill/`
- Codex Skill：`codex-skill/`
- Qodercli 插件：`qoder-plugin/`

如果你是 **OpenClaw Agent** 用户，建议直接看这份说明：

- [`docs/openclaw-agent-install-cn.md`](docs/openclaw-agent-install-cn.md)

### 3. 生成一个 CLI harness

典型使用方式：

```text
@cli-anything build a CLI for ./gimp
@cli-anything refine ./shotcut for picture-in-picture workflows
@cli-anything validate ./libreoffice
```

或在其它平台使用对应命令：

```bash
/cli-anything ./gimp
/cli-anything:refine ./gimp "batch processing and filters"
/cli-anything:test ./inkscape
/cli-anything:validate ./audacity
```

---

## OpenClaw 使用说明（简版）

### 最简安装

```bash
# 1) 克隆仓库
git clone https://github.com/canxia-hub/cli-anything-openclaw-codex.git

# 2) 安装 OpenClaw skill
mkdir -p ~/.openclaw/skills/cli-anything
cp cli-anything-openclaw-codex/openclaw-skill/SKILL.md ~/.openclaw/skills/cli-anything/SKILL.md
```

### 推荐安装方式

除了复制 `SKILL.md`，**最好把整个仓库保留在本地**，因为：

- Skill 会参考仓库中的方法论文档 `cli-anything-plugin/HARNESS.md`
- 需要生成、测试、修复 harness 时，完整仓库更方便复用脚本与模板
- 后续如果要做 Codex / OpenCode / README / 发布收尾，也都在同一仓库里

### 推荐给 Agent 的使用提示

```text
使用 CLI-Anything 为 ./gimp 生成完整 harness
使用 CLI-Anything 为 ./drawio 做 validate
使用 CLI-Anything 为 ./shotcut 做 refine，重点补强 picture-in-picture
```

更完整步骤见：

- [`docs/openclaw-agent-install-cn.md`](docs/openclaw-agent-install-cn.md)

---

## 这次托管版重点修复了什么

本轮测试与收口里，比较关键的修复有：

### 1. Mermaid 渲染链路稳健性
- 从“单次请求 + 长超时”改成了更合理的短超时、重试和明确报错
- 避免外部 renderer 抽风时把整个流程卡死

### 2. Windows 非交互 REPL 兼容
- 修复 `prompt_toolkit` 在非交互控制台 / 管道环境下崩溃的问题
- 现在会优先降级回退，不让默认 REPL 直接炸掉

### 3. 高风险 harness 定向回归
- **AdGuardHome**：修正模块入口与 Docker 缺失时的测试行为
- **ComfyUI**：修复 `--json` 输出被人类提示污染的问题
- **NotebookLM**：修复测试路径依赖当前工作目录的问题

---

## 已生成的测试与发布文档

本仓库当前已经补齐这些测试/发布文档：

- [`docs/testing/harness-audit-2026-03-21.md`](docs/testing/harness-audit-2026-03-21.md)
- [`docs/testing/smoke-report-2026-03-21.md`](docs/testing/smoke-report-2026-03-21.md)
- [`docs/testing/expansion-report-2026-03-21.md`](docs/testing/expansion-report-2026-03-21.md)
- [`docs/testing/plugin-mermaid-e2e-report-2026-03-21.md`](docs/testing/plugin-mermaid-e2e-report-2026-03-21.md)
- [`docs/testing/final-test-report-2026-03-21.md`](docs/testing/final-test-report-2026-03-21.md)
- [`docs/release-announcement-2026-03-21.md`](docs/release-announcement-2026-03-21.md)

---

## 适合谁用

CLI-Anything 特别适合以下场景：

- 你要让 Agent 稳定操控一个原本只有 GUI 的软件
- 你想把某个开源软件的后端能力包装成结构化 CLI
- 你需要一个带 `--json` 输出、可测试、可持续扩展的代理接口
- 你想为 OpenClaw / Codex / Claude Code 等平台统一提供软件操作能力

---

## 后续建议

如果你准备继续接力这个仓库，建议优先做：

1. 在有 Docker 的环境上补完 AdGuardHome Docker E2E
2. 在 Git Bash / WSL / Linux 环境里补跑 `setup-cli-anything.sh`
3. 选择更多高风险 harness 做主机级全量复测
4. 如有需要，再更新 `README_JA.md` 与其它对外材料

---

## 相关入口

- 英文 README：[`README.md`](README.md)
- OpenClaw 安装说明：[`docs/openclaw-agent-install-cn.md`](docs/openclaw-agent-install-cn.md)
- 总测试报告：[`docs/testing/final-test-report-2026-03-21.md`](docs/testing/final-test-report-2026-03-21.md)
- 发布公告：[`docs/release-announcement-2026-03-21.md`](docs/release-announcement-2026-03-21.md)

---

## 许可证

MIT License。

本托管分支在保留上游许可证的前提下维护，请在再分发或商用前同时审阅：

- [`LICENSE`](LICENSE)
- [`NOTICE.md`](NOTICE.md)
- [`DISCLAIMER.md`](DISCLAIMER.md)
