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
4. 组织输出（优先 `.gpkg`；仅在工具或工作流明确需要时使用 `.gdb`）。
5. 用 `Describe` 和列表函数决定处理分支。
6. 执行工具链并保存 `Result`。
7. 必要时用 `arcpy.da` 游标处理属性逻辑。
8. 记录日志并清理临时数据。

实践要求：

- 输入先检：`arcpy.Exists`。
- 批处理前先设 `arcpy.env.workspace` 再 `ListFeatureClasses()`。
- 可选参数优先关键字参数。
- 默认写新输出，不直接改原数据。
- GeoPackage（`.gpkg`）作为现代、开放、单文件的地理信息存储格式优先推荐；用户未明确要求输出格式时，矢量结果统一输出为 `.gpkg`。
- 脚本中创建空 GeoPackage：`arcpy.management.CreateSQLiteDatabase(path, "GEOPACKAGE")`。

### 坐标系与 GeoPackage

- **矢量数据**：一般使用 **EPSG:4326（WGS 84）** 作为默认地理坐标系（分析、交换、与多数文本/JSON/WKT 场景一致时优先）。
- **栅格与瓦片**：面向 Web 底图、切片缓存或在线叠加时，一般使用 **EPSG:3857（Web Mercator）**。
- **GPKG 与空间参考元数据**：GeoPackage 基于 SQLite；每个 `.gpkg` 文件内包含 **`gpkg_spatial_ref_sys`** 表，用于记录该库中所引用坐标系的定义与参数（各图层通过 SRS 与之关联）。
- **同一文件内的约定**：规范允许同一 GeoPackage 中不同图层使用不同空间参考；实际工作中为便于管理、减少重投影与协作歧义，**建议单个 `.gpkg` 内各图层保持同一坐标系**，除非用户或工作流明确要求混存多套 CRS。

## 四、脚本工程化

- **交付形态**：可复用、需分发或在 Pro 中当工具跑的脚本**默认用 `.pyt`**（`Toolbox`、工具类、`execute()`、受保护命令行块）；一次性逻辑用 `.py`。`.tbx` / `.atbx` 不作为新工具首选（不透明或偏 GUI 维护）。
- **常规模板**：`argparse` 接参；路径用 `pathlib.Path`，传入 ArcPy 时 `str()`；地理处理结果用 `Result`，取值时显式类型转换。
- **`.pyt` 实现**：`snake_case.pyt` 与稳定的 `snake_case` `Toolbox.alias`；`Toolbox` 只挂 `label` / `alias` / `tools`，不在 import 或 `__init__` 里跑 GP；工具类提供 `label`、`description`、`getParameterInfo()`、`execute()`，用 `arcpy.Parameter` 描述参数；GP 与派生输出全写在 `execute()`（读 `parameters[i].valueAsText`，用 `messages.addMessage` 记录），**禁止**为命令行再写一套平行实现。类定义用 `class Toolbox:` / `class MyTool:`，**不要**写 `(object)`（Python 2 遗留，与 Pro 无关）。推荐同一文件顺序：常量区 → `Toolbox` / 工具类 → `execute()` → 受保护 CLI。
- **CLI 与防递归**：命令行块仅作本地调试与测试；在 `Path(sys.argv[0]).resolve() == Path(__file__).resolve()` 且环境变量门闩置位后再 `ImportToolbox` 并调用工具，避免加载 `.pyt` 时自递归。矢量默认 `.gpkg` 与空库创建（`CreateSQLiteDatabase(..., "GEOPACKAGE")`）见第三节；`*.pyt.xml` 为生成物，**`.gitignore` 排除**。
- **异常与扩展许可**：`except arcpy.ExecuteError` 配 `GetMessages(2)`；其余异常带 traceback；扩展须先 `CheckExtension` 再 `CheckOutExtension`，在 `finally` 里 `CheckInExtension`。

## 五、输出规范

给用户的脚本方案应包含：

- 可直接运行的命令或脚本入口。
- 输入、输出与环境假设。
- 输出格式默认采用 `.gpkg`；如改用 Shapefile、FileGDB、GeoJSON 等格式，需说明原因或基于用户明确要求。
- 关键 ArcPy API 选择理由。
- 错误处理和验证方式。

## 六、模块参数讲解（modules）

已按官方 `arcpy.*` 模块清单拆分为“一模块一文件”，并按本地脚本中的实际使用频率归档。

当前支持范围：

- 高频模块：已支持并持续维护。
- 中频模块：暂时不支持（相关文件已下线）。
- 低频模块：暂时不支持（相关文件已下线）。

### 示例工具箱（examples）

`examples/` 目录提供可独立运行的 Python 工具箱（`.pyt`），用于快速演示高频工作流与参数使用方式。

使用约束：

- 每个示例文件必须自包含，不依赖同目录下其他 Python 文件。
- 示例应保持独立工具属性，不内置测试数据；测试所需输入由 `tests/` 代码创建。
- 示例默认使用 `.pyt`；`.pyt` 示例应包含 `Toolbox` 类、至少一个工具类、受保护的本地运行块，以及用于测试验证的最小命令行参数。
- 示例应保证可直接运行并输出可验证的结果。

示例清单：

- `examples/csv_to_geopackage.pyt`：从 CSV（`geom_type` + `WKT` 及可选属性列）写入 GeoPackage 点/线/面要素类。
- `examples/buffer_clip.pyt`：对输入点要素缓冲并按面要素裁剪。
- `examples/select_export.pyt`：按 SQL 条件选择要素并导出为新要素类。
- `examples/batch_project.pyt`：将输入工作空间内的全部要素类批量投影到目标坐标系。
- `examples/convert_vector_formats.pyt`：在 Shapefile、工作空间要素类、GeoPackage 图层、GeoJSON 等格式之间导出或复制。

### 高频模块

仅当需要核对**具体工具或函数的名称、参数含义与默认值、返回值**，或确认其归属的 **`arcpy` 子模块**时，再打开下表对应 Markdown 文件。

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