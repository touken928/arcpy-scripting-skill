# arcpy.conversion 模块参数与返回值

## 模块定位

`arcpy.conversion` 用于在要素类、表、栅格及部分外部格式之间做结构化转换。该模块通常用于数据入库、标准化输出、批量导出与格式桥接。

## 高频工具清单

- `FeatureClassToFeatureClass`
- `TableToTable`
- `FeatureToPoint`
- `RasterToPolygon`
- `PolygonToRaster`
- `ExportFeatures`

## 工具 1：`FeatureClassToFeatureClass`

### 参数

- `in_features`：输入要素类。
- `out_path`：输出工作空间。
- `out_name`：输出名称。
- `where_clause`（可选）：筛选条件。
- `field_mapping`（可选）：字段映射。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出要素类路径。

### 示例

```python
result = arcpy.conversion.FeatureClassToFeatureClass(in_fc, out_gdb, "roads_a", "ROAD_CLASS = 'A'")
out_fc = result[0]
```

## 工具 2：`TableToTable`

### 参数

- `in_rows`：输入表。
- `out_path`：输出路径。
- `out_name`：输出表名。
- `where_clause`（可选）：筛选。
- `field_mapping`（可选）：字段映射。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出表路径。

### 示例

```python
out_table = arcpy.conversion.TableToTable(in_table, out_gdb, "poi_tbl")[0]
```

## 工具 3：`ExportFeatures`

### 参数

- `in_features`：输入要素。
- `out_features`：输出要素路径。
- `where_clause`（可选）：筛选条件。
- `use_field_alias_as_name`（可选）：字段别名输出策略。
- `field_mapping`（可选）：字段映射。
- `sort_field`（可选）：输出排序字段。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出要素路径。

## 工具 4：`RasterToPolygon`

### 参数

- `in_raster`：输入栅格。
- `out_polygon_features`：输出面要素。
- `simplify`（可选）：是否平滑边界。
- `raster_field`（可选）：值字段。
- `create_multipart_features`（可选）：是否多部件输出。
- `max_vertices_per_feature`（可选）：单要素最大顶点数。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出面要素路径。

## 工具 5：`PolygonToRaster`

### 参数

- `in_features`：输入面要素。
- `value_field`：栅格值字段。
- `out_rasterdataset`：输出栅格。
- `cell_assignment`（可选）：像元赋值规则。
- `cellsize`（可选）：像元大小。
- `priority_field`（可选）：优先级字段。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出栅格路径。

## 工具 6：`FeatureToPoint`

### 参数

- `in_features`：输入要素（常为面或线）。
- `out_feature_class`：输出点要素。
- `point_location`（可选）：`CENTROID` / `INSIDE`。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出点要素路径。

## 常见错误与排查

- 输出路径与输出名混淆（`out_path` 与 `out_name`）。
- 字段映射不显式设置导致字段丢失。
- 栅格转换未固定 `cellsize` 导致结果不可比。
- 在循环中复用同一个 `out_name` 导致覆盖或执行失败。
- `where_clause` 语法与数据源 SQL 方言不匹配导致空输出。
