# arcpy-scripting-skill

## 项目目标

`arcpy-scripting-skill` 是一个以文档为核心的项目，目标是提供一套可复用的 ArcPy 本地脚本技能说明。

该项目面向大模型阅读与调用，用于生成、完善或审阅 ArcPy 本地脚本。

## 适用范围

- 平台：Windows
- 前提：已安装 ArcGIS Pro
- 运行方式：使用 ArcPy 的本地 Python 脚本
- 包含内容：环境管理、模块选型、GIS 数据处理流程、脚本工程化
- 不包含内容：ArcGIS Pro 图形界面操作、ArcGIS Online、Portal、Web 发布、浏览器端流程

## 事实来源优先级

- 主技能文件：`skills/arcpy-scripting/SKILL.md`
- 本地 ArcPy 文档数据集：`arcpy_docs_markdown/`
- 文档抓取脚本：`scripts/crawl_arcpy_sidebar.py`

若内容出现冲突，以 `skills/arcpy-scripting/SKILL.md` 为准。

需要核对 ArcPy 官方工具、参数、返回值或边界行为时，可以读取 `arcpy_docs_markdown/` 作为本地事实来源；但 `skills/` 下的技能内容不得直接引用 `arcpy_docs_markdown/` 的路径、文件名或“参考来源”说明。

## 编写规则

- 内容必须强调可执行性与工程实践。
- 优先给出简洁、可操作的规则，避免纯概念描述。
- 保留稳定可用的命令示例（如 `propy.bat`、`proenv.bat`、conda 克隆流程）。
- ArcPy 调用优先使用现代模块形式（`arcpy.management.*`、`arcpy.analysis.*`、`arcpy.da.*`）。
- 除非用户明确要求，不要加入“代码润色/重构专用”章节。
- 不要加入“参考来源”标注块。
- 不要在 `skills/` 文档中写入对 `arcpy_docs_markdown/` 的显式引用；可吸收其事实内容，但技能本身应保持可独立分发。

## 更新检查清单

提交前确认：

1. 技能仍然只面向 ArcPy 本地脚本开发。
2. 未引入 Web / Portal / GUI 操作指导。
3. 示例仍可在 Windows + ArcGIS Pro 环境执行。
4. 命名与目录结构仍与项目约定一致。

## 测试约束

- 测试文档统一放在 `tests/README.md`，不在子目录重复放置 README。
- `skills/arcpy-scripting/modules/high-frequency/` 下每篇模块文档必须对应一个独立测试文件，路径为 `tests/high-frequency/test_arcpy_*.py`。
- 禁止将多个高频模块合并到单一测试文件中。
- 测试默认不依赖环境变量；在未设置任何 `ARCPY_*` 变量时必须可直接运行。
- 涉及扩展许可（如 `arcpy.sa`、`arcpy.ia`）时，默认采用免许可可运行校验，不得因许可缺失导致测试失败或阻塞。
- 涉及 `arcpy.mp` 时，优先自动创建临时 `.aprx`；无法创建时应回退到免依赖校验，不得直接跳过整套测试。
- 高频测试标准运行命令为：`"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\propy.bat" -m pytest tests/high-frequency -q`。

## 命名约定

- 项目名：`arcpy-scripting-skill`
- 技能目录：`skills/arcpy-scripting/`
- 技能文件：`skills/arcpy-scripting/SKILL.md`
