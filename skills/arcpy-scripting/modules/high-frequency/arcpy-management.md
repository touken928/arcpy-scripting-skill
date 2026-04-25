# arcpy.management 模块参数与返回值

## 模块定位

`arcpy.management` 是本地 ArcPy 脚本最核心的数据管理模块，负责数据集创建、复制、字段维护、投影、删除、重命名和基础统计等工作。它通常承担“数据准备 + 产出落盘”两个关键环节。

## 高频工具清单

- `CopyFeatures`
- `CreateFileGDB`
- `CreateFeatureclass`
- `AddField`
- `CalculateField`
- `DeleteField`
- `GetCount`
- `Project`
- `MakeFeatureLayer`
- `SelectLayerByAttribute`

## 工具 1：`CopyFeatures`

### 参数

- `in_features`：输入要素类或图层。
- `out_feature_class`：输出要素类路径（建议显式写到目标 `.gdb`）。
- 其他参数通常保持默认。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出要素类路径。

### 示例

```python
result = arcpy.management.CopyFeatures(in_fc, out_fc)
copied_fc = result[0]
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

## 工具 3：`CreateFeatureclass`

### 参数

- `out_path`：输出工作空间（目录或 `.gdb`）。
- `out_name`：输出要素类名称。
- `geometry_type`：`POINT` / `POLYLINE` / `POLYGON` 等。
- `template`（可选）：继承字段结构。
- `spatial_reference`（建议显式设置）：避免空间参考漂移。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为新建要素类路径。

### 示例

```python
result = arcpy.management.CreateFeatureclass(out_gdb, "roads_clean", "POLYLINE", spatial_reference=sr)
new_fc = result[0]
```

## 工具 4：`AddField`

### 参数

- `in_table`：目标表/要素类。
- `field_name`：字段名。
- `field_type`：如 `TEXT`、`LONG`、`DOUBLE`、`DATE`。
- `field_length`：文本字段长度（`TEXT` 时关键）。
- `field_is_nullable`：是否可空。
- `field_domain`：字段域（按需）。

### 返回值

- 返回 `arcpy.Result`（通常用于消息检查，不常取 `result[0]`）。

### 示例

```python
arcpy.management.AddField(fc, "STATUS", "TEXT", field_length=20, field_is_nullable="NULLABLE")
```

## 工具 5：`CalculateField`

### 参数

- `in_table`：目标表/要素类。
- `field`：待计算字段。
- `expression`：表达式（Python/SQL 取决于表达式类型）。
- `expression_type`：常用 `PYTHON3`。
- `code_block`（可选）：复杂逻辑函数体。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.management.CalculateField(fc, "STATUS", "(!STATUS! or '').upper()", "PYTHON3")
```

## 工具 6：`DeleteField`

### 参数

- `in_table`：目标表/要素类。
- `drop_field`：待删除字段（单个或列表）。
- `method`（可选）：保留字段模式或删除字段模式。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.management.DeleteField(fc, ["TMP_A", "TMP_B"])
```

## 工具 7：`GetCount`

### 参数

- `in_rows`：输入表或要素类。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 是字符串，使用时应转为 `int`。

### 示例

```python
count = int(arcpy.management.GetCount(fc)[0])
```

## 工具 8：`Project`

### 参数

- `in_dataset`：输入要素类。
- `out_dataset`：输出要素类。
- `out_coor_system`：目标空间参考（`SpatialReference`）。
- `transform_method`（可选但关键）：坐标转换方法。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为投影后输出路径。

### 示例

```python
sr = arcpy.SpatialReference(3857)
result = arcpy.management.Project(in_fc, out_fc, sr)
projected_fc = result[0]
```

## 工具 9：`MakeFeatureLayer` + `SelectLayerByAttribute`

### 参数

- `MakeFeatureLayer(in_features, out_layer, {where_clause})`
- `SelectLayerByAttribute(in_layer_or_view, selection_type, where_clause)`

### 返回值

- 两者均返回 `arcpy.Result`。
- `SelectLayerByAttribute` 的消息中可读取选中数量。

### 示例

```python
lyr = arcpy.management.MakeFeatureLayer(fc, "roads_lyr")[0]
arcpy.management.SelectLayerByAttribute(lyr, "NEW_SELECTION", "ROAD_CLASS = 'A'")
```

## 常见错误与排查

- 输出路径写到不存在的工作空间：先 `Exists` 校验父路径。
- `GetCount` 未转 `int`：后续数值比较会出错。
- 字段计算表达式与 `expression_type` 不匹配。
- 在同一流程中多次重名输出：要么显式清理，要么使用唯一命名策略。

## 最小可运行骨架

```python
import arcpy

def prepare_data(in_fc: str, out_gdb: str) -> str:
    out_fc = f"{out_gdb}/roads_prepared"
    arcpy.management.CopyFeatures(in_fc, out_fc)
    arcpy.management.AddField(out_fc, "STATUS", "TEXT", field_length=20)
    arcpy.management.CalculateField(out_fc, "STATUS", "'READY'", "PYTHON3")
    return out_fc
```
