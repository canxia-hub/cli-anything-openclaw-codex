# OpenClaw Agent 安装与使用 CLI-Anything（中文说明）

本文面向 **其它 OpenClaw Agent 的维护者 / 操作员**，目的是让你能尽量低成本地把 CLI-Anything 安装到自己的 OpenClaw 环境中，并开始使用。

---

## 一、你会得到什么

安装完成后，你的 OpenClaw Agent 可以理解并执行类似下面的任务：

```text
@cli-anything build a CLI for ./gimp
@cli-anything refine ./shotcut for picture-in-picture workflows
@cli-anything test ./drawio
@cli-anything validate ./libreoffice
```

它会按照 CLI-Anything 的方法论去：

- 分析代码库
- 设计命令组与状态模型
- 生成 `agent-harness/` 结构
- 编写测试
- 生成 `SKILL.md`
- 验证打包与命令入口

---

## 二、前置条件

建议具备以下条件：

- OpenClaw 已正常运行
- Agent 具备基本文件读写能力
- 主机已安装：
  - Python 3.10+
  - Git
- 如果要跑某个目标软件的真实 E2E，还需要那个软件本体或对应后端已经安装

可选但推荐：

- 有可用的 Bash / Git Bash / WSL（方便脚本测试）
- 有 Docker（如果你要补 AdGuardHome 这类依赖 Docker 的 E2E）

---

## 三、最简安装方式

### 步骤 1：克隆仓库

```bash
git clone https://github.com/canxia-hub/cli-anything-openclaw-codex.git
```

建议放在稳定路径，例如：

```bash
~/projects/cli-anything-openclaw-codex
```

或 Windows：

```powershell
C:\Projects\cli-anything-openclaw-codex
```

### 步骤 2：安装 OpenClaw Skill

将 `openclaw-skill/SKILL.md` 复制到你的 OpenClaw 技能目录。

常见示例：

```bash
mkdir -p ~/.openclaw/skills/cli-anything
cp cli-anything-openclaw-codex/openclaw-skill/SKILL.md ~/.openclaw/skills/cli-anything/SKILL.md
```

如果你的 OpenClaw 实例使用的是工作区内 skills 目录，也可以按你的实例习惯放到对应目录，只要最终能被 Agent 发现即可。

---

## 四、推荐安装方式（更稳）

只复制 `SKILL.md` 可以让 Agent“知道有这个技能”，但**更推荐保留整个仓库**，原因是：

1. Skill 会参考完整仓库中的方法论文档
2. 生成 harness 后，经常还要继续测试、修复、更新 README、打包、发布
3. 仓库中有现成的：
   - `cli-anything-plugin/HARNESS.md`
   - `skill_generator.py`
   - 各种已完成的 harness 样例
   - 测试与发布报告

所以推荐做法是：

- **保留完整仓库在本地**
- **安装 `openclaw-skill/SKILL.md` 到 OpenClaw 技能目录**
- 在实际使用时，告诉 Agent 去这个仓库里参考方法论或直接复用脚本/样板

---

## 五、推荐给 OpenClaw Agent 的提示词

### 新建 harness

```text
使用 CLI-Anything 为 ./gimp 生成完整 harness
```

### 定向 refine

```text
使用 CLI-Anything 为 ./shotcut 做 refine，重点补强 picture-in-picture workflows
```

### 运行测试

```text
使用 CLI-Anything 测试 ./drawio 的 harness，并更新测试结果文档
```

### 验证结构

```text
使用 CLI-Anything 验证 ./libreoffice 的 harness 是否符合 HARNESS.md 规范
```

---

## 六、OpenClaw 环境下的实际建议

### 1. 尽量给 Agent 一个明确的源码路径

比起只说“帮我搞 GIMP”，更推荐直接给路径：

```text
使用 CLI-Anything 为 C:\Projects\gimp 生成 harness
```

或：

```text
使用 CLI-Anything 为 /home/agent/gimp 生成 harness
```

### 2. 最好告诉 Agent 当前仓库位置

例如：

```text
CLI-Anything 仓库在 C:\Projects\cli-anything-openclaw-codex
请优先参考其中的 HARNESS.md 和已有 harness 样板
```

### 3. 让 Agent 优先走真实后端，而不是玩具重写

CLI-Anything 的核心哲学是：

> 生成合法中间格式 → 调用真实软件后端 → 验证真实输出

所以像 LibreOffice、Blender、Shotcut、Mermaid 这类目标，都应优先使用真实后端，而不是自己手搓一个“看起来像”的替代实现。

---

## 七、如果你是别的 OpenClaw Agent 的维护者

建议把这几条一起交给维护中的 Agent：

1. **优先读取** `cli-anything-plugin/HARNESS.md`
2. 生成的 harness 要遵守：
   - `cli_anything.<software>` 命名空间结构
   - `--json` 输出
   - 默认 REPL 模式
   - `test_core.py` + `test_full_e2e.py`
   - `SKILL.md` 自动生成
3. 完成后要补：
   - `README.md`
   - `tests/TEST.md`
   - 必要时的 `<SOFTWARE>.md`
4. 在推送前最好至少跑：
   - 打包验证
   - 已安装命令 subprocess 测试
   - 真实后端导出测试

---

## 八、已知未完成测试边界（当前托管版）

为避免误判当前托管版状态，这里把尚未完成的部分再重复一遍：

1. **AdGuardHome Docker-backed E2E 未完成**
   - 需要有 Docker 的环境补测

2. **`cli-anything-plugin/scripts/setup-cli-anything.sh` 未完成真实 Bash / Git Bash / WSL 端到端实跑**
   - 需要在具备 Bash 的环境中补测

3. **尚未在当前 Windows 主机上重跑全部 harness 的完整 pytest 套件**
   - 当前是 conformance audit + 高风险定向回归 + 主体功能闭环验证

如果你接手的是“发布前最终验收”，建议优先把这三项补齐。

---

## 九、推荐你先读的文档

按优先级建议顺序：

1. [`README_CN.md`](../README_CN.md)
2. [`README.md`](../README.md)
3. [`cli-anything-plugin/HARNESS.md`](../cli-anything-plugin/HARNESS.md)
4. [`docs/testing/final-test-report-2026-03-21.md`](testing/final-test-report-2026-03-21.md)
5. [`docs/release-announcement-2026-03-21.md`](release-announcement-2026-03-21.md)

---

## 十、最短可复制安装指令

### Linux / macOS

```bash
git clone https://github.com/canxia-hub/cli-anything-openclaw-codex.git
mkdir -p ~/.openclaw/skills/cli-anything
cp cli-anything-openclaw-codex/openclaw-skill/SKILL.md ~/.openclaw/skills/cli-anything/SKILL.md
```

### Windows PowerShell

```powershell
git clone https://github.com/canxia-hub/cli-anything-openclaw-codex.git
New-Item -ItemType Directory -Force -Path $HOME\.openclaw\skills\cli-anything | Out-Null
Copy-Item .\cli-anything-openclaw-codex\openclaw-skill\SKILL.md $HOME\.openclaw\skills\cli-anything\SKILL.md -Force
```

然后在 OpenClaw 里对 Agent 说：

```text
使用 CLI-Anything 为 ./gimp 生成完整 harness
```

就可以开始用了。
