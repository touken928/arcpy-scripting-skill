# arcpy.management 模块参数与返回值

## 模块定位

`arcpy.management` 是本地 ArcPy 脚本最核心的数据管理模块，负责数据集创建、复制、字段维护、投影、删除、重命名和基础统计等工作。它通常承担"数据准备 + 产出落盘"两个关键环节。

## 高频工具清单

- `CreateFileGDB`
- `CreateFeatureclass`
- `CreateFolder`
- `CopyFeatures`
- `CopyRaster`
- `Append`
- `Merge`
- `AddField`
- `CalculateField`
- `DeleteField`
- `GetCount`
- `Exists`
- `Rename`
- `Delete`
- `Project`
- `MakeFeatureLayer`
- `MakeTableView`
- `SelectLayerByAttribute`
- `SelectLayerByLocation`
- `Intersect`（见 `arcpy.analysis`）
- `Buffer`（见 `arcpy.analysis`）

## 工具 1：`Exists`（`arcpy` 顶层函数）

### 参数

- `data`：数据集路径或名称。

### 返回值

- 返回 `bool`，`True` 表示存在。

### 示例

```python
if arcpy.Exists(out_fc):
    arcpy.Delete(out_fc)
```

## 工具 2：`CreateFileGDB`

### 参数

- `out_folder_path`：父目录。
- `out_name`：新建地理数据库名称（通常带 `.gdb`）。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为新建 `.gdb` 路径。

### 示例

```python
gdb = arcpy.management.CreateFileGDB(out_folder, "work.gdb")[0]
```

## 工具 3：`CreateFolder`

### 参数

- `out_folder_path`：父目录。
- `out_name`：新建文件夹名称。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为新建文件夹路径。

### 示例

```python
folder = arcpy.management.CreateFolder(work_dir, "intermediate")[0]
```

## 工具 4：`CreateFeatureclass`

### 参数

- `out_path`：输出工作空间（目录或 `.gdb`）。
- `out_name`：输出要素类名称。
- `geometry_type`：`POINT` / `POLYLINE` / `POLYGON` 等。
- `template`（可选）：继承字段结构。
- `spatial_reference`（建议显式设置）：避免空间参考漂移。
- `has_m`（可选）：`ENABLED` / `DISABLED` / `SAME_AS_TEMPLATE`。
- `has_z`（可选）：`ENABLED` / `DISABLED` / `SAME_AS_TEMPLATE`。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为新建要素类路径。

### 示例

```python
result = arcpy.management.CreateFeatureclass(out_gdb, "roads_clean", "POLYLINE", spatial_reference=sr)
new_fc = result[0]
```

## 工具 5：`CopyFeatures`

### 参数

- `in_features`：输入要素类或图层。
- `out_feature_class`：输出要素类路径（建议显式写到目标 `.gdb`）。
- `config_keyword`（可选）：存储配置关键字。
- `spatial_grid_n`（可选）：空间网格参数。
- `attributes`（可选）：属性传递策略。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出要素类路径。

### 示例

```python
result = arcpy.management.CopyFeatures(in_fc, out_fc)
copied_fc = result[0]
```

## 工具 6：`CopyRaster`

### 参数

- `in_raster`：输入栅格。
- `out_raster_dataset`：输出栅格路径。
- `config_keyword`（可选）：存储配置。
- `background_value`（可选）：背景值。
- `nodata_value`（可选）：NoData 值。
- `onebit_to_eightbit`（可选）：单波段转8位。
- `pixel_type`（可选）：像素类型。
- `scale_pixel_value`（可选）：缩放像素值。
- `RGB_to_Colormap`（可选）：RGB转色表。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为输出栅格路径。

### 示例

```python
out_raster = arcpy.management.CopyRaster(in_raster, out_path)[0]
```

## 工具 7：`Append`

### 参数

- `inputs`：输入要素类（列表或单个路径）。
- `target`：目标要素类。
- `schema_type`（可选）：`NO_TEST` / `TEST` / `DETAILED`。
- `field_mapping`（可选）：字段映射。
- `append_fields`（可选）：要追加的字段列表。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.management.Append([fc1, fc2], target_fc, "NO_TEST")
```

## 工具 8：`Merge`

### 参数

- `inputs`：输入数据集列表。
- `output`：输出合并结果。
- `field_mapping`（可选）：字段映射。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为输出路径。

### 示例

```python
result = arcpy.management.Merge([fc1, fc2, fc3], out_merged)
merged_fc = result[0]
```

## 工具 9：`Rename`

### 参数

- `in_data`：原数据路径。
- `out_data`：新名称或路径。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.management.Rename(in_fc, out_fc)
```

## 工具 10：`Delete`

### 参数

- `in_data`：待删除数据（路径、列表或通配符）。
- `data_type`（可选）：数据类型（`FeatureClass`、`Raster`、`Table` 等）。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.management.Delete(out_fc)
arcpy.management.Delete("in_memory/temp_layer")
```

## 工具 11：`AddField`

### 参数

- `in_table`：目标表/要素类。
- `field_name`：字段名。
- `field_type`：如 `TEXT`、`LONG`、`DOUBLE`、`DATE`、`SHORT`、`FLOAT`、`BLOB`、`GUID`、`GEOMETRY`。
- `field_length`（可选）：文本字段长度（`TEXT` 时关键）。
- `field_alias`（可选）：字段别名。
- `field_is_nullable`（可选）：是否可空。
- `field_is_required`（可选）：是否必填。
- `field_domain`（可选）：字段域。

### 返回值

- 返回 `arcpy.Result`（通常用于消息检查，不常取 `result[0]`）。

### 示例

```python
arcpy.management.AddField(fc, "STATUS", "TEXT", field_length=20, field_is_nullable="NULLABLE")
arcpy.management.AddField(fc, "AREA", "DOUBLE", field_alias="面积")
```

## 工具 12：`CalculateField`

### 参数

- `in_table`：目标表/要素类。
- `field`：待计算字段。
- `expression`：表达式（Python/SQL 取决于表达式类型）。
- `expression_type`：常用 `PYTHON3`、`PYTHON`、`SQL`（在企业级数据库中更推荐）。
- `code_block`（可选）：复杂逻辑函数体（仅 `PYTHON3` 支持）。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.management.CalculateField(fc, "STATUS", "(!STATUS! or '').upper()", "PYTHON3")
arcpy.management.CalculateField(fc, "AREA", "!SHAPE.area!", "PYTHON3")
```

多行函数示例：

```python
code = """
def calc_class(area):
    if area < 1000:
        return 'SMALL'
    elif area < 10000:
        return 'MEDIUM'
    return 'LARGE'
"""
arcpy.management.CalculateField(fc, "CLASS", "calc_class(!AREA!)", "PYTHON3", code)
```

## 工具 13：`DeleteField`

### 参数

- `in_table`：目标表/要素类。
- `drop_field`：待删除字段（单个字段名字符串或字段列表）。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.management.DeleteField(fc, ["TMP_A", "TMP_B"])
```

## 工具 14：`GetCount`

### 参数

- `in_rows`：输入表或要素类。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 是字符串，使用时应转为 `int`。

### 示例

```python
count = int(arcpy.management.GetCount(fc)[0])
if count == 0:
    raise ValueError("Feature class is empty")
```

## 工具 15：`Project`

### 参数

- `in_dataset`：输入要素类/栅格。
- `out_dataset`：输出路径。
- `out_coor_system`：目标空间参考（`SpatialReference` 对象、WKT 字符串或 EPSG 代码）。
- `transform_method`（可选）：坐标转换方法（仅在需要地理转换且方法有效时设置）。
- `in_coor_system`（可选）：源坐标系。
- `preserve_shape`（可选）：保留形状参数。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为投影后输出路径。

### 示例

```python
sr = arcpy.SpatialReference(3857)
result = arcpy.management.Project(in_fc, out_fc, sr, transform_method="WGS_1984_To_WGS_1984_1")
projected_fc = result[0]
```

## 工具 16：`MakeFeatureLayer`

### 参数

- `in_features`：输入要素类或图层。
- `out_layer`：输出图层名称。
- `where_clause`（可选）：筛选条件。
- `workspace`（可选）：工作空间路径。
- `field_info`（可选）：字段信息字符串。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为图层对象。

### 示例

```python
lyr = arcpy.management.MakeFeatureLayer(fc, "roads_lyr")[0]
```

## 工具 17：`MakeTableView`

### 参数

- `in_table`：输入表。
- `out_view`：输出视图名称。
- `where_clause`（可选）：筛选条件。
- `workspace`（可选）：工作空间路径。
- `field_info`（可选）：字段信息。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为表视图对象。

## 工具 18：`SelectLayerByAttribute`

### 参数

- `in_layer_or_view`：输入图层或表视图。
- `selection_type`：`NEW_SELECTION` / `ADD_TO_SELECTION` / `REMOVE_FROM_SELECTION` / `SUBSET_SELECTION` / `CLEAR_SELECTION`。
- `where_clause`：SQL 筛选表达式。

### 返回值

- 返回 `arcpy.Result`，消息中含选中数量。

### 示例

```python
lyr = arcpy.management.MakeFeatureLayer(fc, "roads_lyr")[0]
arcpy.management.SelectLayerByAttribute(lyr, "NEW_SELECTION", "ROAD_CLASS = 'A'")
count = int(arcpy.management.GetCount(lyr)[0])
```

## 工具 19：`SelectLayerByLocation`

### 参数

- `in_layer`：输入图层。
- `overlap_type`：常用 `INTERSECT` / `WITHIN_A_DISTANCE`（其余关系在不同几何组合下可能无效）。
- `select_features`：选择要素。
- `search_distance`（可选）：搜索距离。
- `selection_type`：常用 `NEW_SELECTION` / `ADD_TO_SELECTION` / `REMOVE_FROM_SELECTION` / `SUBSET_SELECTION` / `SWITCH_SELECTION`。
- `invert Spatial`（可选）：是否反转选择。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", buffer_fc, search_distance="100 Meters")
```

## 常见错误与排查

- 输出路径写到不存在的工作空间：先 `Exists` 校验父路径。
- `GetCount` 未转 `int`：后续数值比较会出错。
- 字段计算表达式与 `expression_type` 不匹配。
- 在同一流程中多次重名输出：要么显式清理，要么使用唯一命名策略。
- `Append` 时 schema_type 不匹配导致字段丢失。
- `Project` 时 transform_method 缺失导致坐标偏移。
- 企业级数据库编辑未在编辑会话中进行。
- 字段名包含特殊字符需用 `AddFieldDelimiters` 转义。

## 最小可运行骨架

```python
import arcpy

def prepare_data(in_fc: str, out_gdb: str) -> str:
    out_fc = f"{out_gdb}/roads_prepared"
    if arcpy.management.Exists(out_fc):
        arcpy.management.Delete(out_fc)
    arcpy.management.CopyFeatures(in_fc, out_fc)
    arcpy.management.AddField(out_fc, "STATUS", "TEXT", field_length=20)
    arcpy.management.CalculateField(out_fc, "STATUS", "'READY'", "PYTHON3")
    count = int(arcpy.management.GetCount(out_fc)[0])
    print(f"Prepared {count} features")
    return out_fc
```