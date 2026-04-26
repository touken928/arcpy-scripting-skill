# arcpy-scripting-skill

`arcpy-scripting-skill` 是一个**面向大模型（LLM）**的 ArcPy 技能工程。  
它的核心目的不是做通用教程，而是给大模型提供稳定、结构化、可执行的 ArcPy 上下文，用于生成、补全、审阅和迭代本地 GIS 自动化脚本。

## 面向大模型的目标

- 提供高密度、低歧义的 ArcPy 高频模块知识（参数、返回值、常见陷阱）。
- 提供可直接运行的示例脚本，作为大模型生成代码时的参考样板。
- 提供可验证的测试用例，约束大模型输出结果的可运行性与正确性。
- 通过固定目录结构降低模型检索成本，提升回答稳定性。

## 适用范围

- 平台：Windows
- 运行环境：ArcGIS Pro（ArcPy）
- 场景：本地脚本自动化
- 不包含：Web/Portal 发布流程、ArcGIS Pro GUI 操作教学

## 当前支持

- 已支持：`skills/arcpy-scripting/modules/high-frequency`
- 暂不支持：中频与低频模块（已下线）

## 目录结构

- `skills/arcpy-scripting/SKILL.md`：主技能规范（模型优先读取入口）
- `skills/arcpy-scripting/modules/high-frequency/`：高频模块知识文件
- `skills/arcpy-scripting/examples/`：自包含示例脚本（无外部输入依赖）
- `tests/high-frequency/`：高频模块能力测试（每模块独立）
- `tests/example/`：示例脚本可执行性与结果校验

## 如何使用

以 Cursor 为例：

将技能放在项目级或用户级目录：

- 项目级（推荐）：`<your-project>/.cursor/skills/arcpy-scripting/`
- 用户级（全局）：`~/.cursor/skills/arcpy-scripting/`（Windows 常见为 `C:\Users\<you>\.cursor\skills\arcpy-scripting\`）

最小结构：

- `.cursor/skills/arcpy-scripting/SKILL.md`
- `.cursor/skills/arcpy-scripting/modules/high-frequency/*.md`
- `.cursor/skills/arcpy-scripting/examples/*.py`

## 快速开始

进入 ArcGIS Pro Python 环境：

```bat
cmd /k "C:\Program Files\ArcGIS\Pro\bin\Python\Scripts\proenv.bat"
```

## 运行测试

高频模块测试的标准命令（与 `tests/README.md`、`AGNETS.md` 一致）：

```bat
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\propy.bat" -m pytest tests/high-frequency -q
```

运行全部测试（含 `tests/example`）：

```bat
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\propy.bat" -m pytest tests -q
```
