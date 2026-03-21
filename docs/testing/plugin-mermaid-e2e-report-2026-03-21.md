# CLI-Anything 主体功能闭环测试（Mermaid 对象）

## 测试目的
使用 **Mermaid Live Editor** 作为简单对象，对 CLI-Anything 插件的主体承诺做一次真实闭环验证：

1. 插件元数据与命令定义存在且可解析
2. 生成出的 harness 可以被安装为 `cli-anything-<software>` 命令
3. 已安装命令可以完成项目创建、修改、导出、分享等主流程
4. `--json` 输出可被程序稳定解析
5. `skill_generator.py` 能从 harness 自动生成 `SKILL.md`
6. 子进程测试可在 **force-installed** 模式下跑过
7. Windows 非交互/管道场景下，默认 REPL 不应崩溃

## 测试对象
- Plugin source: `cli-anything-plugin/`
- Harness object: `mermaid/agent-harness/`
- Installed command: `C:\Users\Administrator\Projects\cli-anything-lt001\.venv\Scripts\cli-anything-mermaid.exe`

## 本轮发现与修复

### 1) REPL 在 Windows 非交互控制台崩溃
**现象：**
- 在 PowerShell 管道/非控制台环境调用 `cli-anything-mermaid` 时，`prompt_toolkit` 创建会话触发 `NoConsoleScreenBufferError`
- 这会让“无参数默认进入 REPL”在自动化环境下直接炸掉

**修复：**
- 在 `create_prompt_session()` 中增加非交互控制台兜底
- `prompt_toolkit` 初始化失败时回退到普通 `input()`

**修改文件：**
- `cli-anything-plugin/repl_skin.py`
- `mermaid/agent-harness/cli_anything/mermaid/utils/repl_skin.py`

### 2) Mermaid subprocess 测试未完全符合 HARNESS 要求
**现象：**
- `_resolve_cli()` 不支持 `CLI_ANYTHING_FORCE_INSTALLED=1`
- 不打印实际 backend 选择结果
- 未覆盖“管道退出 REPL”路径

**修复：**
- `_resolve_cli()` 增加 force-installed 模式与日志输出
- 新增 `test_repl_quit_with_piped_stdin`
- `_run()` 支持传入 `input=` 等额外参数

**修改文件：**
- `mermaid/agent-harness/cli_anything/mermaid/tests/test_full_e2e.py`

## 验证步骤

### A. 插件元数据与命令定义
验证项：
- `.claude-plugin/plugin.json` 可被 JSON 正常解析
- 4 个核心命令定义存在：
  - `commands/cli-anything.md`
  - `commands/refine.md`
  - `commands/test.md`
  - `commands/validate.md`

结果：PASS

### B. Mermaid harness force-installed 测试
命令：

```powershell
$env:CLI_ANYTHING_FORCE_INSTALLED='1'
$env:PATH='C:\Users\Administrator\Projects\cli-anything-lt001\.venv\Scripts;' + $env:PATH
C:\Users\Administrator\Projects\cli-anything-lt001\.venv\Scripts\python.exe -m pytest .\mermaid\agent-harness\cli_anything\mermaid\tests -v -s
```

结果摘要：

```text
[_resolve_cli] Using installed command: C:\Users\Administrator\Projects\cli-anything-lt001\.venv\Scripts\cli-anything-mermaid.EXE
13 passed in 3.32s
```

说明：
- 已确认 subprocess 测试实际走的是 **已安装命令**，不是模块回退
- 新增 REPL 管道退出测试通过

### C. Mermaid 主流程手工闭环
执行内容：
1. `--help`
2. `project new --sample flowchart`
3. `diagram set --text ...`
4. `diagram show`
5. `export render demo.svg -f svg`
6. `export render demo.png -f png`
7. `export share --mode view/edit`
8. `session status`
9. `skill_generator.py` 生成临时 `SKILL.md`

产物目录：
- `C:\Users\Administrator\AppData\Local\Temp\cli-anything-mermaid-e2e`

关键产物：
- `demo.mermaid.json`
- `demo.svg`（12119 bytes）
- `demo.png`（10536 bytes, magic bytes: `89-50-4E-47`）
- `GENERATED_SKILL.md`

分享链接验证：
- `https://mermaid.live/view#pako:...`
- `https://mermaid.live/edit#pako:...`

结果：PASS

## 当前结论

以 Mermaid 作为简单对象的主体功能闭环结果：

- **插件基础结构：PASS**
- **命令定义存在且可解析：PASS**
- **Mermaid harness 可安装为 PATH 命令：PASS**
- **force-installed subprocess 测试：PASS**
- **JSON 输出链路：PASS**
- **真实 SVG/PNG 导出：PASS**
- **分享 URL 生成：PASS**
- **SKILL 自动生成：PASS**
- **Windows 非交互 REPL 兼容：PASS（已修复）**

## 建议下一步
1. 如果继续做主体功能样本扩展，可再补 1 个“本地后端型”对象（如 AdGuardHome/ComfyUI）与 1 个“文档型”对象（如 NotebookLM）形成三角验证
2. 后续可考虑把 `repl_skin.py` 的非交互控制台兜底同步推广到更多已生成 harness
3. 等全部主体测试结束后，再统一 push 远端
