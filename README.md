# arcpy-scripting-skill

`arcpy-scripting-skill` 是一个面向大模型（LLM）的 ArcPy 技能工程，用来为本地 GIS 自动化脚本生成、补全、审阅和迭代提供稳定上下文。

它不是通用 ArcPy 教程，而是一套可被模型快速读取的工程化材料：主技能规范、按模块拆分的 ArcPy 高频知识、可运行的 Python 工具箱示例，以及验证这些示例和知识点的测试。

## 适用范围

- 平台：Windows
- 运行环境：ArcGIS Pro / ArcPy
- 主要场景：本地 GIS 脚本、Python 工具箱（`.pyt`）、数据处理自动化
- 不包含：ArcGIS Pro GUI 操作教学、Portal / ArcGIS Online / Web 图层发布流程

## 项目内容

- `skills/arcpy-scripting/SKILL.md`：主技能入口，定义脚本生成规范、输出约定、示例清单和模块阅读规则。
- `skills/arcpy-scripting/modules/high-frequency/`：高频 `arcpy` 子模块参数说明，覆盖管理、分析、转换、游标、栅格、影像、地图工程和空间统计。
- `skills/arcpy-scripting/examples/`：自包含示例 Python 工具箱（`.pyt`），用于展示推荐脚本结构和常见工作流。
- `tests/high-frequency/`：高频模块知识与行为测试。
- `tests/example/`：示例工具箱的命令行运行和结果校验。

当前只维护高频模块；中频与低频模块暂不提供。

## 在 Cursor 中使用

将 `skills/arcpy-scripting/` 放入项目级或用户级 skills 目录：

- 项目级（推荐）：`<your-project>/.cursor/skills/arcpy-scripting/`
- 用户级：`~/.cursor/skills/arcpy-scripting/`（Windows 常见为 `C:\Users\<you>\.cursor\skills\arcpy-scripting\`）

最小结构：

```text
.cursor/skills/arcpy-scripting/
├── SKILL.md
├── modules/high-frequency/
└── examples/
```

使用时，模型应优先读取 `SKILL.md`；仅当需要核对具体 ArcPy 工具、参数、返回值或模块归属时，再读取 `modules/high-frequency/` 下的对应文件。

## 运行环境

建议使用 ArcGIS Pro 自带 Python。进入交互环境：

```bat
cmd /k "C:\Program Files\ArcGIS\Pro\bin\Python\Scripts\proenv.bat"
```

直接运行脚本或测试时使用 `propy.bat`：

```bat
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\propy.bat" -m pytest tests -q
```

## 运行测试

只运行高频模块测试：

```bat
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\propy.bat" -m pytest tests/high-frequency -q
```

只运行示例工具箱测试：

```bat
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\propy.bat" -m pytest tests/example -q
```

运行全部测试：

```bat
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\propy.bat" -m pytest tests -q
```
