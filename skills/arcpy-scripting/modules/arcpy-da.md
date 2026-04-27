# arcpy.da 模块参数与返回值

## 模块定位

`arcpy.da` 是 ArcPy 的高性能数据访问层，核心用于游标读写、编辑会话、结构描述以及与 NumPy/Arrow 的高效数据互转。与旧版 `arcpy` 游标相比，性能更优、功能更强（支持更多令牌、空间过滤等）。

## 高频对象/函数清单

- `SearchCursor`
- `UpdateCursor`
- `InsertCursor`
- `Editor`
- `Describe`
- `TableToNumPyArray`
- `FeatureClassToNumPyArray`
- `NumPyToFeatures`
- `NumPyToTable`
- `ExtendTable`
- `ListFields`
- `ListIndexes`
- `Domain`
- `Version`

## 对象 1：`SearchCursor`

### 参数

- `in_table`：输入表/要素类/图层/表视图。
- `field_names`：字段列表（如 `["OID@", "NAME", "SHAPE@"]`）。使用 `*` 获取所有字段（除 BLOB）性能较差。
- `where_clause`（可选）：过滤条件（SQL 表达式）。
- `spatial_reference`（可选）：坐标系约束。
- `explode_to_points`（可选）：多部件是否展开为单部件点。
- `sql_clause`（可选）：`("START WITH", "GROUP BY")` 等 SQL 子句对。
- `datum_transformation`（可选）：坐标转换。
- `spatial_filter`（可选）：空间过滤对象（需 ArcGIS Pro 2.5+）。
- `spatial_relationship`（可选）：`INTERSECT` / `WITHIN_A_DISTANCE` 等。
- `search_order`（可选）：`OBJECTID` / `SPATIAL`（默认 `OBJECTID`）。

### 返回值

- 返回可迭代游标对象。
- 每次迭代返回一行元组（字段顺序与 `field_names` 一致）。
- 常用 token：
  - `OID@`：对象 ID
  - `SHAPE@`：完整几何对象
  - `SHAPE@XY`：质心 x,y 元组
  - `SHAPE@X` / `SHAPE@Y` / `SHAPE@Z`：坐标分量
  - `SHAPE@AREA`：面积
  - `SHAPE@LENGTH`：长度
  - `SHAPE@JSON` / `SHAPE@WKB` / `SHAPE@WKT`：几何序列化
  - `CREATED@` / `CREATOR@` / `EDITED@` / `EDITOR@`：元数据
  - `GLOBALID@` / `SUBTYPE@`

### 示例

```python
with arcpy.da.SearchCursor(fc, ["OID@", "NAME", "SHAPE@"], "NAME IS NOT NULL") as rows:
    for oid, name, shape in rows:
        centroid = shape.centroid
        print(f"{oid}: {name} at ({centroid.X}, {centroid.Y})")
```

带空间过滤示例：

```python
import arcpy.geom
sf = arcpy.geom.SearchFilter("SHAPE", "INTERSECT", buffer_shape)
with arcpy.da.SearchCursor(fc, ["OID@", "SHAPE@"], spatial_filter=sf) as rows:
    for oid, shape in rows:
        pass
```

## 对象 2：`UpdateCursor`

### 参数

- 与 `SearchCursor` 基本一致。
- `explode_to_points`（可选）：多部件是否展开。
- `datum_transformation`（可选）：坐标转换。

### 返回值

- 返回可写游标对象。
- 通过 `updateRow(row)` 写回修改。
- 通过 `deleteRow()` 删除当前行。

### 示例

```python
with arcpy.da.UpdateCursor(fc, ["STATUS", "AREA"], "STATUS IS NULL") as rows:
    for row in rows:
        if row[1] < 1000:
            row[0] = "SMALL"
        else:
            row[0] = "LARGE"
        rows.updateRow(row)
```

删除行示例：

```python
with arcpy.da.UpdateCursor(fc, ["STATUS"]) as rows:
    for row in rows:
        if row[0] == "DELETE":
            rows.deleteRow()
```

## 对象 3：`InsertCursor`

### 参数

- `in_table`：目标表/要素类。
- `field_names`：插入字段顺序列表。
- `datum_transformation`（可选）：坐标转换。

### 返回值

- 返回可插入游标对象。
- `insertRow(row)` 执行插入，返回 `OID`（对于数据库）或 `None`（对于 shapefile）。

### 示例

```python
with arcpy.da.InsertCursor(fc, ["NAME", "SHAPE@XY"]) as rows:
    oid = rows.insertRow(["A-01", (120.1, 30.2)])
    oid2 = rows.insertRow(["B-02", (120.2, 30.3)])
```

带几何对象插入：

```python
import arcpy.geom
pt = arcpy.geom.Point(120.1, 30.2)
with arcpy.da.InsertCursor(fc, ["NAME", "SHAPE@"]) as rows:
    rows.insertRow(["POINT_A", pt])
```

## 对象 4：`Editor`

### 概述

用于企业级数据库（EGDB）的编辑会话管理。必须在编辑会话中进行写操作，且支持事务（可通过 `startOperation` / `stopOperation` 控制撤销块）。

### 方法

- `startEditing(with_undo, with_schema_lock)`：开始编辑会话。
- `startOperation()`：开始操作块（可撤销）。
- `stopOperation()`：停止操作块。
- `stopEditing(save=True)`：停止编辑会话。

### 示例

```python
edit = arcpy.da.Editor(gdb)
edit.startEditing(True, False)
edit.startOperation()
try:
    with arcpy.da.UpdateCursor(fc, ["NAME"], "NAME = 'OLD'") as rows:
        for row in rows:
            row[0] = "NEW"
            rows.updateRow(row)
    edit.stopOperation()
    edit.stopEditing(True)
except Exception:
    edit.stopEditing(False)
    raise
```

## 函数：`arcpy.da.Describe`

### 参数

- `dataset`：目标数据集路径。

### 返回值

- 返回字典。
- 常用键：
  - `dataType`：数据类型字符串（如 `FeatureClass`、`Table`、`Dataset`）
  - `shapeType`：`Point` / `Polyline` / `Polygon` 等
  - `shapeFieldName`：几何字段名
  - `spatialReference`：空间参考对象
  - `fields`：字段对象列表（可用 `[f.name for f in desc['fields']]`）
  - `indexes`：索引对象列表
  - `children`：子数据集列表
  - `catalogPath`：完整路径

### 示例

```python
desc = arcpy.da.Describe(fc)
print(f"Type: {desc['dataType']}, Shape: {desc['shapeType']}")
if desc['dataType'] == 'FeatureClass':
    sr = desc['spatialReference']
    print(f"Spatial reference: {sr.name}")
```

## 函数：`TableToNumPyArray` / `FeatureClassToNumPyArray`

### 参数（共用）

- `in_table` / `in_feature_class`：输入数据集。
- `field_names`：字段列表。
- `where_clause`（可选）：筛选条件。
- `skip_nulls`（可选）：`True` 跳过 null 值，`False` 用 `null_value` 替代。
- `null_value`（可选）：null 值替代。
- `explode_to_points`（可选）：多部件是否展开。
- `geometry_type`（可选）：指定几何类型约束。

### 返回值

- 返回 NumPy 结构化数组（`numpy.ndarray`，dtype 由字段类型决定）。

### 示例

```python
import numpy as np
arr = arcpy.da.FeatureClassToNumPyArray(fc, ["OID@", "AREA"], "AREA > 1000")
print(f"Records: {len(arr)}, dtype: {arr.dtype}")
print(f"First area: {arr['AREA'][0]}")
```

## 函数：`NumPyToFeatureClass` / `NumPyToTable`

### 参数

- `in_array`：NumPy 结构化数组。
- `out_table` / `out_feature_class`：输出路径。
- `geometry_type`（可选，`NumPyToFeatureClass`）：`POINT` / `POLYLINE` / `POLYGON`。
- `spatial_reference`（可选）：空间参考。
- `coordinate_system`（可选）：同 `spatial_reference`。
- `config_keyword`（可选）：存储配置。

### 返回值

- 无（输出到文件）。

### 示例

```python
import numpy as np
data = np.array([(1, 120.1, 30.2), (2, 120.3, 30.4)],
                dtype=[("ID", "i4"), ("X", "f8"), ("Y", "f8")])
# 先创建点要素类
arcpy.management.CreateFeatureclass(out_gdb, "points", "POINT", spatial_reference=sr)
arcpy.da.NumPyToFeatureClass(data, f"{out_gdb}/points", ["X", "Y"])
```

## 函数：`ExtendTable`

### 参数

- `in_table`：要扩展的表/要素类。
- `table_field`：连接字段名。
- `in_array`：NumPy 数组。
- `array_field`：数组中对应连接字段名。
- `just_join`（可选）：`True` 仅连接（不新增字段），`False` 执行真正的字段扩展。
- `append`（可选）：`True` 追加模式，`False` 替换匹配行。

### 返回值

- 无（原地修改）。

### 示例

```python
arr = arcpy.da.TableToNumPyArray(stats_table, ["ZONE", "MEAN_AREA"])
arcpy.da.ExtendTable(fc, "ZONE_CODE", arr, "ZONE", just_join=True)
```

## 函数：`ListFields`

### 参数

- `dataset`：数据集路径。
- `wildcard`（可选）：字段名通配过滤。
- `field_type`（可选）：`String` / `Integer` / `Double` / `Date` / `Geometry` 等。

### 返回值

- 返回 `Field` 对象列表。

### 示例

```python
for fld in arcpy.da.ListFields(fc, field_type="String"):
    print(f"{fld.name}: {fld.type}, length={fld.length}")
```

## 函数：`ListIndexes`

### 参数

- `table`：表/要素类路径。
- `wildcard`（可选）：索引名通配。

### 返回值

- 返回 `Index` 对象列表。

### 示例

```python
for idx in arcpy.da.ListIndexes(fc):
    print(f"{idx.name}: fields={idx.fields}, isAscending={idx.isAscending}")
```

## 对象：`Domain` / `Version` / `Editor`

### Domain

- `Domain(gdb, domain_name)`：创建域对象。
- 属性：`type`、`description`、`fieldType`、`mergePolicy`、`splitPolicy`、`codedValues`。

### Version

- `Version(gdb, version_name)`：版本管理对象。
- 方法：`switchVersion` 切换连接版本。

### Editor

见上方编辑器章节。

## 常见错误与排查

- 未用 `with` 管理游标导致锁释放不及时，在 EGDB 环境中尤其严重。
- 字段顺序与 row 索引不一致导致写错字段。
- 盲目使用 `*` 导致性能下降和语义不清（大型表尤甚）。
- 更新游标中同时修改几何和属性但未控制事务，导致部分写入。
- 在 EGDB 环境中忽略编辑会话要求，写入失败。
- `NumPyToFeatureClass` 前未创建目标要素类。
- `ExtendTable` 的连接字段类型不匹配（如字符串 vs 整数）。
- 几何令牌使用不当（如在只需要质心时使用 `SHAPE@` 导致性能损耗）。
- 空间过滤对象（`SearchFilter`）使用前确认本机 ArcGIS Pro 版本支持。

## 最小可运行骨架

```python
import arcpy
import numpy as np

def read_and_analyze(fc: str, field: str) -> dict:
    desc = arcpy.da.Describe(fc)
    print(f"Feature class: {desc['catalogPath']}, type={desc['shapeType']}")

    data = arcpy.da.FeatureClassToNumPyArray(fc, ["OID@", field], f"{field} IS NOT NULL")
    return {
        "count": len(data),
        "mean": float(np.mean(data[field])),
        "min": float(np.min(data[field])),
        "max": float(np.max(data[field])),
    }

def batch_update(fc: str, gdb: str) -> int:
    edit = arcpy.da.Editor(gdb)
    edit.startEditing(True, False)
    count = 0
    try:
        with arcpy.da.UpdateCursor(fc, ["STATUS", "AREA"], "STATUS = 'PENDING'") as rows:
            for row in rows:
                row[0] = "DONE"
                rows.updateRow(row)
                count += 1
        edit.stopEditing(True)
    except Exception:
        edit.stopEditing(False)
        raise
    return count
```