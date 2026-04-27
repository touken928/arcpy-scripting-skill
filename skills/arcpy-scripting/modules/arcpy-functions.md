# arcpy 常用函数速查

## 模块定位

本文档覆盖 ArcPy 顶层常用函数（`arcpy.func()` 形式），涵盖数据查询、描述、环境管理、几何构造、旧版游标、字段处理等内容。`arcpy.management` / `arcpy.analysis` 等模块工具不在此文档范围内，请参考各模块专属文档。

## 环境管理

### `ListEnvironments()`

返回所有可用地理处理环境设置名称。

### 返回值

字符串列表。

### 示例

```python
envs = arcpy.ListEnvironments()
print([e for e in envs if "cell" in e.lower()])  # ['cellSize', 'rasterStatistics']
```

### `GetSystemEnvironment({variable})`

获取系统环境变量值。

### 参数

- `variable`（可选）：变量名（默认 `"TEMP"`）。

### 返回值

字符串（环境变量值）。

### 示例

```python
temp_dir = arcpy.GetSystemEnvironment("TEMP")
```

### `ClearEnvironment(env_name)`

重置单个环境设置为默认值。

### 示例

```python
arcpy.ClearEnvironment("cellSize")
```

### `ResetEnvironments()`

重置所有环境设置为默认值。

### 示例

```python
arcpy.ResetEnvironments()
```

## 数据描述

### `arcpy.Describe(dataset)`

描述数据集并返回 `Describe` 对象（属性动态取决于数据类型）。

### 参数

- `dataset`：数据集路径。

### 返回值

`Describe` 对象，属性组包括：

**通用属性**

| 属性 | 说明 | 数据类型 |
|---|---|---|
| `catalogPath` | 完整路径 | String |
| `dataType` | 数据类型 | String |
| `name` | 名称 | String |
| `baseName` | 基础名 | String |
| `file` | 是否为文件 | Boolean |
| `extension` | 扩展名 | String |
| `children` | 子对象集合 | List |
| `path` | 父路径 | String |

**要素类额外属性**

| 属性 | 说明 |
|---|---|
| `shapeType` | `Point`/`Polyline`/`Polygon` 等 |
| `shapeFieldName` | 几何字段名 |
| `spatialReference` | `SpatialReference` 对象 |
| `hasZ` | 是否有 Z 值 |
| `hasM` | 是否有 M 值 |
| `featureType` | 要素类型 |

**栅格额外属性**

| 属性 | 说明 |
|---|---|
| `bandCount` | 波段数 |
| `compressionType` | 压缩类型 |
| `pixelType` | 像素类型 |
| `sensor` | 传感器类型 |

### 示例

```python
desc = arcpy.Describe(fc)
print(f"Type: {desc.dataType}, Shape: {desc.shapeType}")
sr = desc.spatialReference
print(f"Spatial reference: {sr.name}")

# 检查要素类属性
if desc.dataType == "FeatureClass":
    print(f"Has Z: {desc.hasZ}")

# 检查栅格属性
desc_r = arcpy.Describe(raster_path)
print(f"Bands: {desc_r.bandCount}, Pixel type: {desc_r.pixelType}")
```

## 字段操作

### `AddFieldDelimiters(dataset, field_name)`

为字段名添加正确的分隔符（工作空间相关）。

### 参数

- `dataset`：数据集路径（用于判断工作空间类型）。
- `field_name`：字段名。

### 返回值

带分隔符的字段名字符串（FileGDB 用双引号， shapefile 用单引号，EGDB 用双引号）。

### 示例

```python
# FileGDB 中：'"NAME"'，Shapefile 中："'NAME'"
delimited = arcpy.AddFieldDelimiters(fc, "NAME")
cursor = arcpy.da.SearchCursor(fc, ["OID@", delimited])
```

### `ParseFieldName(full_field_name, {workspace})`

解析全限定字段名为各组成部分。

### 参数

- `full_field_name`：全限定字段名（如 `database.owner.table.field`）。
- `workspace`（可选）：工作空间路径。

### 返回值

字符串（逗号分隔：`database,owner,table,field`）。

### 示例

```python
parts = arcpy.ParseFieldName("work.gdb.owner.TABLENAME.MY_FIELD")
print(parts)  # "work.gdb,owner,TABLENAME,MY_FIELD"
```

### `ValidateFieldName(field_name, database)`

返回数据库合法的字段名（无效字符替换为下划线）。

### 参数

- `field_name`：字段名。
- `database`：数据库路径。

### 示例

```python
valid = arcpy.ValidateFieldName("My Field/Invalid!", gdb)
print(valid)  # "My_Field__Invalid_"
```

## 数据查询

### `Exists(dataset)`

判断数据是否存在。

### 参数

- `dataset`：数据路径。

### 返回值

`bool`。

### 示例

```python
if arcpy.Exists(fc):
    print("Feature class exists")
if arcpy.Exists(f"{gdb}/my_gdb"):
    print("Geodatabase exists")
```

### `TestSchemaLock(dataset)`

测试能否获取数据集的方案锁（修改数据结构需要方案锁）。

### 参数

- `dataset`：数据集路径。

### 返回值

`bool`（`True` 表示可获取锁）。

### 示例

```python
if not arcpy.TestSchemaLock(fc):
    print("Cannot acquire schema lock, another process is using it")
    raise RuntimeError("Schema lock unavailable")
arcpy.management.AddField(fc, "NEW_FIELD", "TEXT")
```

### `ParseTableName(full_table_name, {workspace})`

解析全限定表名为各组成部分。

### 参数

- `full_table_name`：全限定表名。
- `workspace`（可选）：工作空间路径。

### 返回值

字符串（逗号分隔：`database,owner,table`）。

### 示例

```python
parts = arcpy.ParseTableName("work.gdb.owner.MYTABLE")
```

### `ValidateTableName(table_name, database)`

返回数据库合法的表名。

### 参数

- `table_name`：表名。
- `database`：数据库路径。

### 示例

```python
valid = arcpy.ValidateTableName("My Table!", gdb)  # "My_Table_"
```

## 数据列举

所有 `List*` 函数遵循 `arcpy.env.workspace` 工作空间限制。

### `ListDatasets({wildcard}, {feature_type})`

列出工作空间中的数据集。

### 参数

- `wildcard`（可选）：名称通配。
- `feature_type`（可选）：`Coverage` / `Feature` / `Raster` / `Terrain` 等。

### 返回值

字符串列表。

### 示例

```python
arcpy.env.workspace = r"D:\data\work.gdb"
fcs = arcpy.ListDatasets("Zone*", "Feature")
```

### `ListFeatureClasses({wildcard}, {feature_type}, {dataset})`

列出要素类。

### 参数

- `wildcard`（可选）：名称通配。
- `feature_type`（可选）：`Point` / `Polyline` / `Polygon` / `Multipoint` / `Annotation` / `Dimension` / `Any`。
- `dataset`（可选）：数据集名称。

### 返回值

字符串列表。

### 示例

```python
polys = arcpy.ListFeatureClasses("Zone*", "Polygon")
points = arcpy.ListFeatureClasses(feature_type="Point")
```

### `ListFields(dataset, {wildcard}, {field_type})`

列出数据集的字段。

### 参数

- `dataset`：数据集路径。
- `wildcard`（可选）：字段名通配。
- `field_type`（可选）：`String` / `Integer` / `Double` / `Date` / `Geometry` 等。

### 返回值

`Field` 对象列表（可用 `[f.name for f in arcpy.ListFields(fc)]`）。

### 示例

```python
for fld in arcpy.ListFields(fc, field_type="String"):
    print(f"{fld.name}: {fld.type}, length={fld.length}")
```

### `ListIndexes(dataset, {wildcard})`

列出数据集的索引。

### 参数

- `dataset`：数据集路径。
- `wildcard`（可选）：索引名通配。

### 返回值

`Index` 对象列表。

### 示例

```python
for idx in arcpy.ListIndexes(fc):
    print(f"{idx.name} on {idx.fields}, ascending={idx.isAscending}")
```

### `ListRasters({wildcard}, {raster_type})`

列出工作空间中的栅格。

### 参数

- `wildcard`（可选）：名称通配。
- `raster_type`（可选）：`BMP` / `GIF` / `IMG` / `JPEG` / `PNG` / `TIFF` / `GRID` / `All`。

### 返回值

字符串列表。

### 示例

```python
tiffs = arcpy.ListRasters("dem*", "TIFF")
all_rasters = arcpy.ListRasters()
```

### `ListTables({wildcard}, {table_type})`

列出工作空间中的表。

### 参数

- `wildcard`（可选）：名称通配。
- `table_type`（可选）：`dBASE` / `Shapefile` / `All`。

### 返回值

字符串列表。

### 示例

```python
tables = arcpy.ListTables("lookup*", "dBASE")
```

### `ListFiles({wildcard})`

列出当前工作空间中的文件。

### 参数

- `wildcard`（可选）：名称通配。

### 返回值

字符串列表。

### 示例

```python
txt_files = arcpy.ListFiles("*.txt")
```

### `ListVersions({workspace})`

列出企业级数据库中的版本。

### 参数

- `workspace`（可选）：数据库连接路径（默认 `arcpy.env.workspace`）。

### 返回值

字符串列表（如 `["sde.DEFAULT", "editor.branch1"]`）。

### 示例

```python
arcpy.env.workspace = r"D:\connections\egdb.sde"
versions = arcpy.ListVersions()
print(versions)
```

### `ListWorkspaces({wildcard}, {workspace_type})`

列出工作空间中的子工作空间（如数据库连接、文件夹）。

### 参数

- `wildcard`（可选）：名称通配。
- `workspace_type`（可选）：`Access` / `ArcInfo` / `Coverages` / `FileGDB` / `Folder` / `OLEDB` / `SDE` / `All`。

### 返回值

字符串列表。

### 示例

```python
fgdbs = arcpy.ListWorkspaces("*", "FileGDB")
```

### `ListPrinterNames()`

返回系统可用打印机名称列表。

### 返回值

字符串列表。

### 示例

```python
printers = arcpy.ListPrinterNames()
```

## 几何函数

### `FromWKT(geometry_text, {spatial_reference})`

从 WKT 字符串创建几何对象。

### 参数

- `geometry_text`：WKT 字符串。
- `spatial_reference`（可选）：`SpatialReference` 对象。

### 返回值

`Geometry`（具体类型取决于 WKT 内容）。

### 示例

```python
geom = arcpy.FromWKT("POINT (120.0 30.0)", sr)
poly = arcpy.FromWKT("POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))", sr)
```

### `FromWKB(wkb, {spatial_reference}, {has_z}, {has_m})`

从 WKB（熟知二进制）创建几何对象。

### 参数

- `wkb`：`bytearray` 或 `bytes` 对象。
- `spatial_reference`（可选）：`SpatialReference` 对象。

### 返回值

`Geometry` 对象。

### 示例

```python
import json
geom = arcpy.FromWKB(bytes(wkb_data), sr)
```

### `AsShape(geometry_text, {esri_json})`

从 Esri JSON 或 GeoJSON 字符串创建几何。

### 参数

- `geometry_text`：Esri JSON 或 GeoJSON 几何字符串。
- `esri_json`（可选）：`True` 表示 Esri JSON，`False` 表示 GeoJSON。

### 返回值

`Geometry` 对象。

### 示例

```python
json_geom = '{"x": 120.0, "y": 30.0, "spatialReference": {"wkid": 4326}}'
pt = arcpy.AsShape(json_geom, True)
```

### `FromCoordString(coord_string, spatial_reference)`

从坐标系注记字符串创建 PointGeometry。

### 参数

- `coord_string`：坐标字符串（如 `"GEOGCS['GCS_WGS_1984...`"）。
- `spatial_reference`：`SpatialReference` 对象。

### 返回值

`PointGeometry` 对象。

### 示例

```python
pt = arcpy.FromCoordString("120d30'15\"E 30d15'20\"N", sr_wgs84)
```

### `FromGeohash(geohash)`

将 geohash 字符串转换为 WGS84 的 Extent。

### 参数

- `geohash`：geohash 字符串。

### 返回值

`Extent` 对象。

### 示例

```python
extent = arcpy.FromGeohash("wtm37k")
print(f"Bounds: {extent.XMin}, {extent.YMin} to {extent.XMax}, {extent.YMax}")
```

## 常规函数

### `Usage(tool_name)`

返回工具或函数的语法字符串。

### 参数

- `tool_name`：工具名（如 `"CopyFeatures"` 或完整工具箱路径）。

### 返回值

字符串。

### 示例

```python
print(arcpy.Usage("Buffer"))
print(arcpy.Usage("arcpy.management.CopyFeatures"))
```

### `Command(tool_name, {args})`

将工具作为单字符串命令执行（返回结果消息）。

### 参数

- `tool_name`：工具名。
- `args`（可选）：工具参数字符串。

### 返回值

`Result` 对象。

### 示例

```python
result = arcpy.Command("CopyFeatures in_fc out_fc")
```

### `CreateScratchName({prefix}, {suffix}, {data_type}, {workspace})`

创建唯一临时路径名。

### 参数

- `prefix`（可选）：前缀（默认 `"scratch"`）。
- `suffix`（可选）：后缀。
- `data_type`（可选）：数据类型（如 `"FeatureClass"`）。
- `workspace`（可选）：工作空间。

### 返回值

字符串（临时路径）。

### 示例

```python
temp_fc = arcpy.CreateScratchName("temp", "fc", "FeatureClass", arcpy.env.scratchGDB)
```

### `CreateUniqueName(base_name, {workspace})`

在指定工作空间中创建唯一名称（通过追加数字）。

### 参数

- `base_name`：基础名称。
- `workspace`（可选）：工作空间路径。

### 返回值

字符串。

### 示例

```python
unique = arcpy.CreateUniqueName("output.shp", out_dir)
```

### `CreateObject(type, {constructor_args})`

创建地理处理对象（如 `ValueTable`）。

### 参数

- `type`：对象类型（如 `"ValueTable"`）。
- `constructor_args`（可选）：构造参数。

### 返回值

地理处理对象。

### 示例

```python
vt = arcpy.CreateObject("ValueTable", 3)  # 3列
vt.addRow("val1 val2 val3")
```

### `CreateRandomValueGenerator(seed, distribution)`

创建随机数生成器。

### 参数

- `seed`：随机种子（整数值，0 表示随机）。
- `distribution`：分布字符串（例如 `"UNIFORM 0 1"`）。

### 返回值

`RandomNumberGenerator` 对象。

### 示例

```python
rng = arcpy.CreateRandomValueGenerator(42, "UNIFORM 0 1")
rand_val = rng.random()
```

### `AIOFileOpen(uri, {mode}, {config_dict})`

打开本地或云文件句柄（支持上下文管理器）。

### 参数

- `uri`：文件/云存储 URI（如 `s3://bucket/file.tif`）。
- `mode`（可选）：`r` / `w`（默认 `r`）。
- `config_dict`（可选）：云存储配置。

### 返回值

文件对象。

### 示例

```python
with arcpy.AIOFileOpen("s3://mybucket/data.tif") as f:
    data = f.read()
```

### `GetSTACInfo(url)`

从 STAC（时空资产目录）URL 获取元数据。

### 参数

- `url`：STAC API 端点 URL。

### 返回值

字典（包含 `title`、`description`、`bounds`、`assets` 等）。

### 示例

```python
stac_info = arcpy.GetSTACInfo("https://planetarycomputer.microsoft.com/api/stac/v1")
```

### `AlterAliasName(dataset, alias)`

更新表或要素类的别名。

### 参数

- `dataset`：数据集路径。
- `alias`：新别名。

### 返回值

字符串。

### 示例

```python
arcpy.AlterAliasName(fc, "道路要素")
```

### `IsBeingEdited(dataset)`

判断数据集或工作空间是否处于编辑会话中。

### 参数

- `dataset`：数据集路径。

### 返回值

`bool`。

### 示例

```python
if arcpy.IsBeingEdited(fc):
    print("Data is being edited")
```

### `RefreshLayer(layer)`

刷新地图图层视图（仅在 Pro 内运行有效）。

### 参数

- `layer`：`Layer` 对象或图层名。

### 返回值

无。

### 示例

```python
arcpy.RefreshLayer(lyr_object)
```

### `ArealUnitConversionFactor(from_unit, to_unit)`

返回面积单位转换因子。

### 参数

- `from_unit` / `to_unit`：面积单位名（如 `"SQUARE_MILES"`、`"HECTARES"`）。

### 返回值

`float`（转换系数）。

### 示例

```python
factor = arcpy.ArealUnitConversionFactor("ACRES", "SQUAREMETERS")
sq_km = acres * factor
```

### `LinearUnitConversionFactor(from_unit, to_unit)`

返回线性单位转换因子。

### 参数

- `from_unit` / `to_unit`：线性单位名（如 `"METERS"`、`"FEET"`）。

### 返回值

`float`。

### 示例

```python
factor = arcpy.LinearUnitConversionFactor("FEET", "METERS")
meters = feet * factor
```

## 数据存储管理

### `AddDataStoreItem(server_folder, connection_info)`

向 ArcGIS Server 注册数据存储（文件夹或数据库）。

### 参数

- `server_folder`：服务器文件夹路径。
- `connection_info`：连接信息字典。

### 返回值

字符串（`"success"` 或错误信息）。

### 示例

```python
arcpy.AddDataStoreItem(
    "/arcgis/rest/services",
    {"type": "folder", "path": r"D:\data", "connection": "registered"}
)
```

### `ListDataStoreItems(server, {datastore_type})`

列出 Server 已注册的数据存储。

### 参数

- `server`：服务器 URL。
- `datastore_type`（可选）：`DATASTORE` / `FOLDER` / `DATABASE` / `CLOUD` / `ALL`。

### 返回值

字典列表（每个字典包含 `path`、`type`、`name`、`provider` 等）。

### 示例

```python
items = arcpy.ListDataStoreItems("http://myserver:6080/arcgis", "FOLDER")
```

### `ValidateDataStoreItem(server_folder, connection_info)`

验证数据存储项是否有效。

### 参数

- `server_folder`：服务器文件夹路径。
- `connection_info`：连接信息字典。

### 返回值

字符串（`"success"` / `"failed"` / `"warning"`）。

### 示例

```python
status = arcpy.ValidateDataStoreItem("/arcgis/rest/services", conn_info)
```

### `RemoveDataStoreItem(server_folder, item_path)`

注销数据存储项。

### 参数

- `server_folder`：服务器文件夹。
- `item_path`：数据存储项路径。

### 返回值

字符串。

## 企业级地理数据库管理

### `AcceptConnections(database_connection, accept)`

允许/禁止非管理员用户连接企业级数据库。

### 参数

- `database_connection`：数据库连接文件路径（`.sde`）。
- `accept`：`True` / `False`。

### 返回值

无。

### 示例

```python
arcpy.AcceptConnections(r"D:\connections\egdb.sde", False)
```

### `DisconnectUser(database_connection, users)`

断开指定用户连接。

### 参数

- `database_connection`：数据库连接文件。
- `users`：用户 ID 列表或逗号分隔字符串。

### 返回值

无。

### 示例

```python
arcpy.DisconnectUser(r"D:\connections\egdb.sde", [5, 12, 18])
```

### `ListUsers(database_connection)`

返回连接用户信息。

### 返回值

元组列表，每个元组为 `(user_name, user_id, connected, idle_time, arcgis_server_version)`。

### 示例

```python
users = arcpy.ListUsers(r"D:\connections\egdb.sde")
for user in users:
    print(f"{user[0]} (ID={user[1]}, connected={user[2]})")
```

## 旧版游标函数

> **提示**：`arcpy.da` 模块的游标（`arcpy.da.SearchCursor` 等）性能更优、功能更强，建议优先使用。以下仅用于维护旧版脚本。

### `arcpy.SearchCursor(dataset, {where_clause}, {spatial_reference}, {fields}, {sort_fields})`

返回要素类/表的只读游标（旧版）。

### 参数

- `dataset`：数据集路径。
- `where_clause`（可选）：过滤条件。
- `spatial_reference`（可选）：空间参考。
- `fields`（可选）：字段列表（分号分隔字符串）。
- `sort_fields`（可选）：排序字段（`"FIELD A;FIELD2 D"`）。

### 返回值

旧版 `Cursor` 对象，使用 `row.getValue(field)` 读取值。

### 示例

```python
cursor = arcpy.SearchCursor(fc, "NAME IS NOT NULL", "", "NAME;TYPE", "NAME A")
for row in cursor:
    print(row.getValue("NAME"))
```

### `arcpy.UpdateCursor(dataset, {where_clause}, {spatial_reference}, {fields}, {sort_fields})`

返回可更新游标（旧版）。

### 示例

```python
cursor = arcpy.UpdateCursor(fc, "STATUS = 'OLD'")
for row in cursor:
    row.setValue("STATUS", "DONE")
    cursor.updateRow(row)
```

### `arcpy.InsertCursor(dataset, {spatial_reference})`

返回插入游标（旧版）。

### 示例

```python
cursor = arcpy.InsertCursor(fc)
for i in range(10):
    row = cursor.newRow()
    row.setValue("ID", i)
    cursor.insertRow(row)
del cursor
```

## 消息与错误

### `arcpy.AddMessage(message)`

向工具消息添加信息级消息。

### 参数

- `message`：消息字符串。

### 返回值

无。

### 示例

```python
arcpy.AddMessage(f"Processed {count} features")
```

### `arcpy.AddWarning(message)`

添加警告级消息。

### 示例

```python
arcpy.AddWarning("Output exceeds 10000 records, may be slow")
```

### `arcpy.AddError(message)`

添加错误级消息。

### 示例

```python
arcpy.AddError("Invalid spatial reference")
```

### `arcpy.AddIDMessage(message_type, message_id, {add_argument1}, {add_argument2})`

添加带 ID 的消息。

### 参数

- `message_type`：`ERROR` / `WARNING` / `INFO`。
- `message_id`：消息 ID 字符串。
- `add_argument1` / `add_argument2`（可选）：消息参数。

### 示例

```python
arcpy.AddIDMessage("INFORMATIVE", 12, "Input dataset")
```

### `arcpy.GetMessages({severity})`

获取工具消息。

### 参数

- `severity`（可选）：`0`（信息）/ `1`（警告）/ `2`（错误）。

### 返回值

字符串（多行消息）。

### 示例

```python
msgs = arcpy.GetMessages(1)  # 获取警告消息
```

### `arcpy.GetMessage(index)`

获取指定索引的消息文本。

### 示例

```python
msg = arcpy.GetMessage(0)
```

### `arcpy.GetMessageCount()`

返回消息总数。

### 示例

```python
count = arcpy.GetMessageCount()
```

### `arcpy.GetMaxSeverity()`

返回消息最大严重级别（`0`=信息，`1`=警告，`2`=错误）。

### 示例

```python
if arcpy.GetMaxSeverity() >= 2:
    print("Error occurred")
```

## 环境快捷访问

除了 `arcpy.env` 对象上的属性访问外，还可通过函数快速访问/设置关键环境：

### 常用 `arcpy.env` 属性

| 属性 | 说明 | 默认值 |
|---|---|---|
| `workspace` | 当前工作空间 | - |
| `scratchGDB` | 临时地理数据库 | 系统临时目录 |
| `scratchFolder` | 临时文件夹 | 系统临时目录 |
| `cellSize` | 像元大小 | 输入栅格最大 |
| `extent` | 分析范围 | 全局 |
| `snapRaster` | 对齐基准栅格 | - |
| `outputCoordinateSystem` | 输出坐标系 | 与输入相同 |
| `mask` | 分析掩膜 | - |
| `compression` | 压缩方式 | - |
| `parallelProcessingFactor` | 并行处理线程数 | - |

### 示例

```python
arcpy.env.workspace = r"D:\data\work.gdb"
arcpy.env.scratchGDB = r"D:\data\temp\scratch.gdb"
arcpy.env.cellSize = 30
arcpy.env.extent = "MAXOF"
arcpy.env.mask = mask_raster
```

## 常见错误与排查

- `List*` 函数返回空列表：确认 `arcpy.env.workspace` 设置正确。
- `TestSchemaLock` 返回 `False`：其他进程持有方案锁，需等待或关闭。
- `Exists` 对云存储路径始终返回 `False`（取决于存储类型和驱动）。
- `AddFieldDelimiters` 对 shapefile 用单引号、EGDB 用双引号，写 SQL 时必须加否则语法错误。
- 旧版游标（`arcpy.SearchCursor`）未用 `del` 释放导致锁残留，建议换用 `arcpy.da` 游标的 `with` 语句。
- `RefreshLayer` 仅在 ArcGIS Pro 内有效，离线脚本中调用无效果。
- `GetSTACInfo` 需要网络访问，离线环境需预先缓存。
- `CreateRandomValueGenerator` 的 `seed=0` 表示基于时间生成（每次不同），整数种子可复现。

## 最小可运行骨架

```python
import arcpy

def analyze_workspace(workspace: str) -> dict:
    arcpy.env.workspace = workspace

    desc = arcpy.Describe(workspace)
    print(f"Workspace type: {desc.dataType}")

    feature_classes = arcpy.ListFeatureClasses(feature_type="Polygon")
    print(f"Found {len(feature_classes)} polygon feature classes")

    for fc in feature_classes:
        fc_desc = arcpy.Describe(fc)
        print(f"  {fc}: shape={fc_desc.shapeType}, SR={fc_desc.spatialReference.name}")
        for fld in arcpy.ListFields(fc, field_type="String"):
            print(f"    Field: {fld.name}, length={fld.length}")

    return {"fc_count": len(feature_classes)}
```