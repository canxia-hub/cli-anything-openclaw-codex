# CLI-Anything 扩测记录（2026-03-21）

## 测试范围
在当前 Windows 主机上继续对以下高风险 harness 做扩展测试：

- `adguardhome`
- `comfyui`
- `notebooklm`

测试环境：
- Host: Windows Server 2022
- Repo: `C:\Users\Administrator\Projects\cli-anything-lt001`
- Python: repo-local `.venv`

---

## 1. AdGuardHome

### 初始现象
首轮扩测结果：
- Core 单元测试大量通过
- CLI subprocess / Docker E2E 存在明显问题

### 根因定位
1. `cli_anything/adguardhome/adguardhome_cli.py`
   - `python -m cli_anything.adguardhome.adguardhome_cli` 最初无入口执行
   - 修第一次时又将 `if __name__ == "__main__": main()` 放得过早，导致命令组尚未注册就提前启动，只能看到 root help，看不到 `config/filter/rewrite/blocking`
2. `tests/test_full_e2e.py`
   - Docker fixture 直接执行 `docker ...`，在当前主机无 Docker 时抛 `FileNotFoundError`
   - 应当 skip，而不是报错

### 修复内容
- 将 AdGuardHome CLI 的 `__main__` 入口挪到文件底部，确保所有 Click 命令组注册后再执行
- 为 Docker E2E 增加 `_require_docker()`：Docker 不存在时 `pytest.skip(...)`
- 将 fixture 中所有 docker 调用改为使用解析出的 docker 路径变量

### 回归结果
命令：

```powershell
.\.venv\Scripts\python -m pytest .\adguardhome\agent-harness\cli_anything\adguardhome\tests -v
```

结果：
- **31 passed**
- **5 skipped**（当前主机未安装 Docker，符合预期）
- **0 failed / 0 error**

---

## 2. ComfyUI

### 初始现象
首轮扩测结果：
- 69 passed
- 1 failed

失败用例：
- `TestCLIWorkflow::test_workflow_validate_json_output`

### 根因定位
`workflow validate --json` 虽然已经输出 JSON，但在 JSON 后又额外打印了人类提示：

```text
Workflow is valid.
```

导致 JSON 被污染，`json.loads()` 抛 `Extra data`。

### 修复内容
在 `cli_anything/comfyui/comfyui_cli.py` 的 `workflow_validate()` 中：
- 当 `_json_output == True` 时，输出 JSON 后直接返回
- 仅在非 JSON 模式输出人类提示语

### 回归结果
命令：

```powershell
.\.venv\Scripts\python -m pytest .\comfyui\agent-harness\cli_anything\comfyui\tests -v
```

结果：
- **70 passed**
- **0 failed**

---

## 3. NotebookLM

### 初始现象
首轮扩测结果：
- CLI smoke 基本通过
- 4 个 packaging fixture 测试失败

失败原因表现为：
- `README.md` / `skills/SKILL.md` 路径找不到

### 根因定位
`tests/test_core.py` 中直接使用：

```python
Path("cli_anything/notebooklm/README.md")
Path("cli_anything/notebooklm/skills/SKILL.md")
```

这隐式依赖 pytest 从 `agent-harness` 目录启动；但从仓库根目录运行时，当前工作目录不同，导致路径失效。

### 修复内容
在 `tests/test_core.py` 中改为：
- 基于 `Path(__file__).resolve().parents[1]` 计算 `PACKAGE_ROOT`
- 所有 README / SKILL 路径都改为基于 `PACKAGE_ROOT` 解析

### 回归结果
命令：

```powershell
.\.venv\Scripts\python -m pytest .\notebooklm\agent-harness\cli_anything\notebooklm\tests\test_core.py .\notebooklm\agent-harness\cli_anything\notebooklm\tests\test_cli_smoke.py -v
```

结果：
- **21 passed**
- **0 failed**

---

## 本轮改动摘要

### 修改文件
- `adguardhome/agent-harness/cli_anything/adguardhome/adguardhome_cli.py`
- `adguardhome/agent-harness/cli_anything/adguardhome/tests/test_full_e2e.py`
- `comfyui/agent-harness/cli_anything/comfyui/comfyui_cli.py`
- `notebooklm/agent-harness/cli_anything/notebooklm/tests/test_core.py`
- `docs/testing/expansion-report-2026-03-21.md`

### 测试结论
当前主机扩测完成后：
- `adguardhome`：**PASS（Docker E2E 环境受限 skip）**
- `comfyui`：**PASS**
- `notebooklm`：**PASS**

## 后续建议
1. 如需把 `adguardhome` 的 Docker E2E 也打绿，需要补一台带 Docker 的 Windows/Linux 测试环境
2. 可继续扩测下一批 harness，优先考虑：
   - 依赖外部二进制/服务的 harness
   - 最近发生过结构修复的 harness
3. 在全部目标 harness 扩测收口后，再统一 push 远端
