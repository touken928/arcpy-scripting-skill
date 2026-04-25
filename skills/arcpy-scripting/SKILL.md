---
name: arcpy-scripting
description: 面向 Windows + ArcGIS Pro 已安装环境的 ArcPy 本地脚本开发标准技能。用于环境管理、模块选型、常见 GIS 数据处理流程、脚本工程化与异常处理。
---

# ArcPy Scripting

## 适用范围

- Windows 主机，已安装 ArcGIS Pro。
- 使用 ArcPy 进行本地 Python 脚本开发。
- 不涉及 ArcGIS Pro 图形界面操作。
- 不涉及 Portal、ArcGIS Online、Web 图层发布和网页端功能。

## 一、环境管理

- 独立脚本默认使用 `propy.bat`。
- 交互式命令行统一使用 `cmd /k "...\proenv.bat"` 作为官方环境入口。
- `arcgispro-py3` 作为基础环境，不直接修改。
- 项目依赖先克隆环境再安装，优先 conda，后用 pip。

```bat
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\propy.bat" "D:\gis\jobs\job.py"
```

```bat
cmd /k "C:\Program Files\ArcGIS\Pro\bin\Python\Scripts\proenv.bat"
conda create --clone arcgispro-py3 -n my_env
proswap my_env
conda install pandas -y
pip install python-dotenv
```

## 二、模块选型

- 工具调用优先模块式 API：`arcpy.management.*`、`arcpy.analysis.*`、`arcpy.conversion.*`。
- 属性批量读写优先 `arcpy.da`。
- 需要分支判断先用 `arcpy.Describe` / `arcpy.da.Describe`。
- 执行上下文优先 `arcpy.EnvManager`。
- 栅格分析按模块分工：`arcpy.sa`、`arcpy.ia`。

## 三、GIS 数据处理流程范式

1. 解析参数与路径。
2. 检查输入存在性、字段、空间参考和许可。
3. 设置环境（`workspace`、`overwriteOutput`、`scratchWorkspace`）。
4. 组织输出（文件夹或 `.gdb`）。
5. 用 `Describe` 和列表函数决定处理分支。
6. 执行工具链并保存 `Result`。
7. 必要时用 `arcpy.da` 游标处理属性逻辑。
8. 记录日志并清理临时数据。

实践要求：

- 输入先检：`arcpy.Exists`。
- 批处理前先设 `arcpy.env.workspace` 再 `ListFeatureClasses()`。
- 可选参数优先关键字参数。
- 默认写新输出，不直接改原数据。

## 四、脚本工程化

- 入口使用 `main()` + `if __name__ == "__main__":`。
- 参数使用 `argparse`，避免硬编码生产路径。
- 路径建议 `pathlib.Path`，传入 ArcPy 前转 `str`。
- 工具输出保存为 `Result`，需要数值时显式转换（如 `int(result[0])`）。

异常处理标准：

- 地理处理错误：`except arcpy.ExecuteError` + `arcpy.GetMessages(2)`。
- 其他错误：`except Exception` + traceback。
- 扩展许可：`CheckExtension` -> `CheckOutExtension` -> `finally` 中 `CheckInExtension`。

## 五、输出规范

给用户的脚本方案应包含：

- 可直接运行的命令或脚本入口。
- 输入、输出与环境假设。
- 关键 ArcPy API 选择理由。
- 错误处理和验证方式。

## 六、模块参数讲解（modules）

已按官方 `arcpy.*` 模块清单拆分为“一模块一文件”，并按本地脚本中的实际使用频率归档。

当前支持范围：

- 高频模块：已支持并持续维护。
- 中频模块：暂时不支持（相关文件已下线）。
- 低频模块：暂时不支持（相关文件已下线）。

### 示例脚本（examples）

`examples/` 目录提供可独立运行的 ArcPy 示例脚本，用于快速演示高频工作流与参数使用方式。

使用约束：

- 每个示例脚本必须自包含，不依赖同目录下其他 Python 文件。
- 示例默认可直接运行，不要求用户先准备外部输入数据（脚本内部自行构造最小示例数据）。
- 示例应包含 `argparse`、`main()` 入口、基础异常处理，并输出关键结果路径。
- 示例应保证可直接运行并输出可验证的结果。

示例清单：

- `examples/create_workspace_and_sample_data.py`：创建输出目录与 FileGDB，生成带属性字段的示例点要素类。
- `examples/buffer_and_clip_features.py`：自动生成点要素和裁剪边界，执行缓冲并输出裁剪结果。
- `examples/select_and_export_features.py`：自动生成点要素，按属性条件选择并导出结果要素类。
- `examples/batch_project_featureclasses.py`：自动生成点/线示例要素类，批量投影到目标坐标系。
- `examples/create_and_modify_aprx.py`：读取现有 `.aprx` 工程，检查地图/布局对象并另存为修改版工程（需预先准备输入工程）。

### 高频模块

- `modules/high-frequency/arcpy-management.md`：数据集、字段、投影、复制、删除、图层构造等基础数据管理。
- `modules/high-frequency/arcpy-analysis.md`：缓冲、裁剪、叠加、空间连接、邻近分析等矢量空间分析。
- `modules/high-frequency/arcpy-conversion.md`：要素、表、栅格与外部格式之间的转换和导出。
- `modules/high-frequency/arcpy-da.md`：高性能游标、编辑会话、Describe 字典、NumPy/Arrow 数据互转。
- `modules/high-frequency/arcpy-sa.md`：Spatial Analyst 栅格建模、地图代数、条件分析、邻域统计。
- `modules/high-frequency/arcpy-ia.md`：Image Analyst 影像处理、遥感指数、分类和分割。
- `modules/high-frequency/arcpy-mp.md`：本地 `.aprx` / `.lyrx` 工程自动化、图层更新和布局导出。
- `modules/high-frequency/arcpy-stats.md`：空间统计、热点、离群、空间自相关、回归和核密度分析。

### 中频模块（暂不支持）

中频模块内容已暂时下线，当前版本不提供对应模块文档与参数讲解。

### 低频模块（暂不支持）

低频模块内容已暂时下线，当前版本不提供对应模块文档与参数讲解。

使用规则：

1. 回答模块问题时，仅按 `modules/high-frequency` 目录定位对应模块文件。
2. 高频模块作为默认推荐；中频与低频模块需明确声明“暂不支持”。
3. 脚本生成时，按高频模块文件中的参数讲解框架展开输入/输出/关键业务参数。
4. 跨模块流程问题，优先在高频模块范围内组合实现。