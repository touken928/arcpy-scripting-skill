# arcpy.conversion 模块参数与返回值

## 模块定位

`arcpy.conversion` 用于在要素类、表、栅格及部分外部格式之间做结构化转换。该模块通常用于数据入库、标准化输出、批量导出与格式桥接。所有工具均返回 `arcpy.Result`。

## 高频工具清单

- `FeatureClassToFeatureClass`
- `TableToTable`
- `ExportFeatures`
- `ExportRaster`
- `FeatureToPoint`
- `FeatureToLine`
- `FeatureToPolygon`
- `RasterToPolygon`
- `PolygonToRaster`
- `RasterToOtherFormat`
- `ShapefileToFeatureClass`
- `JSONToFeatureClass`
- `FeatureClassToJSON`
- `GeoJSONToFeatures`
- `FeaturesToGeoJSON`
- `ValidateDataset`

## 工具 1：`FeatureClassToFeatureClass`

### 参数

- `in_features`：输入要素类或图层。
- `out_path`：输出工作空间（`.gdb` 或文件夹）。
- `out_name`：输出要素类名称。
- `where_clause`（可选）：筛选条件。
- `field_mapping`（可选）：字段映射表达式（如 `"NAME \"名称\" true true false 50 Text..."`）。
- `config_keyword`（可选）：存储配置关键字。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为输出要素类路径。

### 示例

```python
result = arcpy.conversion.FeatureClassToFeatureClass(
    in_fc,
    out_gdb,
    "roads_a",
    "ROAD_CLASS = 'A'",
    field_mapping='NAME "名称" true true false 50 Text...'
)
out_fc = result[0]
```

## 工具 2：`TableToTable`

### 参数

- `in_rows`：输入表（`.dbf`、`.csv`、`.gdb` 表等）。
- `out_path`：输出路径。
- `out_name`：输出表名。
- `where_clause`（可选）：筛选。
- `field_mapping`（可选）：字段映射。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为输出表路径。

### 示例

```python
out_table = arcpy.conversion.TableToTable(in_table, out_gdb, "poi_tbl")[0]
```

## 工具 3：`ExportFeatures`

### 参数

- `in_features`：输入要素。
- `out_features`：输出要素路径。
- `where_clause`（可选）：筛选条件。
- `use_field_alias_as_name`（可选）：`USE_ALIAS` / `NO_USE_ALIAS`。
- `field_mapping`（可选）：字段映射。
- `sort_field`（可选）：输出排序字段。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为输出要素路径。

### 示例

```python
result = arcpy.conversion.ExportFeatures(fc, out_fc, sort_field="NAME A")
```

## 工具 4：`ExportRaster`

### 参数

- `in_raster`：输入栅格。
- `out_raster_dataset`：输出栅格路径。
- `configuration_keyword`（可选）：存储配置。
- `options`（可选）：附加选项。
- `maintenance`（可选）：维护选项。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.conversion.ExportRaster(out_raster, output_path)
```

## 工具 5：`FeatureToPoint`

### 参数

- `in_features`：输入要素。
- `out_feature_class`：输出点要素。
- `point_location`（可选）：`CENTROID` / `INSIDE`。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
result = arcpy.conversion.FeatureToPoint(in_fc, out_fc, "INSIDE")[0]
```

## 工具 6：`FeatureToLine`

### 参数

- `in_features`：输入要素。
- `out_feature_class`：输出线要素。
- `line_field`（可选）：线拆分字段（如按要素 ID 生成独立线）。
- `join_attributes`（可选）：属性传递策略。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.conversion.FeatureToLine(boundary_fc, out_line_fc, "ZONE_ID")
```

## 工具 7：`FeatureToPolygon`

### 参数

- `in_features`：输入要素。
- `out_feature_class`：输出面要素。
- `point_location`（可选）：点定位方式。
- `join_attributes`（可选）：属性传递策略。
- `label_features`（可选）：标注要素。

### 返回值

- 返回 `arcpy.Result`。

## 工具 8：`RasterToPolygon`

### 参数

- `in_raster`：输入栅格。
- `out_polygon_features`：输出面要素。
- `simplify`（可选）：`SIMPLIFY` / `NO_SIMPLIFY`。`SIMPLIFY` 会平滑边界。
- `raster_field`（可选）：值字段（默认 `Value`）。
- `create_multipart_features`（可选）：`MULTIPLE_PART` / `SINGLE_PART`。
- `max_vertices_per_feature`（可选）：单要素最大顶点数。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为输出面要素路径。

### 示例

```python
result = arcpy.conversion.RasterToPolygon(
    in_raster, out_fc, simplify="SIMPLIFY",
    raster_field="LANDCOVER", create_multipart_features="MULTIPLE_PART"
)
```

## 工具 9：`PolygonToRaster`

### 参数

- `in_features`：输入面要素。
- `value_field`：栅格值字段（默认 `OID`）。
- `out_rasterdataset`：输出栅格路径。
- `cell_assignment`（可选）：`CELL_CENTER` / `MAX_AREA` / `MAX_COMBINED_AREA`。
- `cellsize`（可选）：像元大小。
- `priority_field`（可选）：优先级字段。
- `build_rat`（可选）：`BUILD_RAT` / `NO_BUILD_RAT`（栅格属性表）。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为输出栅格路径。

### 示例

```python
result = arcpy.conversion.PolygonToRaster(
    zone_fc, "ZONE_CODE", out_raster,
    cellsize=30, build_rat="BUILD_RAT"
)
```

## 工具 10：`RasterToOtherFormat`

### 参数

- `input_rasters`：输入栅格（列表或空格分隔字符串）。
- `output_location`：输出位置。
- `raster_format`：目标格式（如 `JPEG` / `TIFF` / `PNG` / `BMP` / `GIF`）。
- `convert_single_band`（可选）：是否转换为单波段。
- `color_mode`（可选）：颜色模式（`CMA_AUTO` / `CMA_MATCH` 等）。
- `compression`（可选）：压缩方式。
- `jpeg_quality`（可选）：JPEG 质量（1-100）。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.conversion.RasterToOtherFormat(in_raster, out_folder, "JPEG", compression="LZW")
```

## 工具 11：`ShapefileToFeatureClass`

### 参数

- `Input_Files`：输入 shp 文件或文件夹。
- `Output_Location`：输出位置。
- `out_name`（可选）：输出名称（批量时忽略）。
- `config_keyword`（可选）：存储配置。
- `outSpatial_Reference`（可选）：输出空间参考。

### 返回值

- 返回 `arcpy.Result`。

## 工具 12：`JSONToFeatureClass`

### 参数

- `in_json_file`：输入 GeoJSON 文件路径。
- `out_feature_class`：输出要素类路径。
- `geometry_type`（可选）：`POINT` / `MULTIPOINT` / `POLYLINE` / `POLYGON`（通常从 JSON 自动推断）。
- `spatial_reference`（可选）：空间参考。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.conversion.JSONToFeatureClass(geojson_path, out_fc, spatial_reference=4326)
```

## 工具 13：`FeatureClassToJSON`

### 参数

- `in_features`：输入要素类。
- `out_json_file`：输出 JSON 文件路径。
- `include_fields`（可选）：是否包含字段。
- `format_coords`（可选）：坐标格式（如 `-122.0, 37.0`）。
- `geoJSON`（可选）：是否输出 GeoJSON 格式。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.conversion.FeatureClassToJSON(fc, out_json, geoJSON="GEOJSON")
```

## 工具 14：`GeoJSONToFeatures`

### 参数

- `in_json_file`：输入 GeoJSON 文件路径。
- `out_features`：输出要素类路径。
- `geometry_type`（可选）：几何类型约束。

### 返回值

- 返回 `arcpy.Result`。

## 工具 15：`FeaturesToGeoJSON`

### 参数

- `in_features`：输入要素类。
- `out_json_file`：输出 GeoJSON 文件路径。
- `geoJSON`（可选）：是否输出标准 GeoJSON（替代 Esri JSON）。

### 返回值

- 返回 `arcpy.Result`。

## 工具 16：`ValidateDataset`

### 参数

- `in_dataset`：待验证数据集。
- `in_tolerance_value`（可选）：容差值。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为 `Boolean`（验证通过/失败）。

### 示例

```python
if not arcpy.conversion.ValidateDataset(in_fc):
    print("Dataset invalid")
```

## 常见错误与排查

- 输出路径与输出名混淆（`out_path` 与 `out_name` 位置颠倒）。
- 字段映射不显式设置导致字段丢失或命名不符预期。
- 栅格转换未固定 `cellsize` 导致结果不可比。
- 在循环中复用同一个 `out_name` 导致覆盖或执行失败。
- `where_clause` 语法与数据源 SQL 方言不匹配导致空输出。
- `RasterToPolygon` 的 `simplify="SIMPLIFY"` 在边界复杂时可能导致面粘连。
- `PolygonToRaster` 未设置 `build_rat="BUILD_RAT"` 导致无法进行像元统计查询。
- JSON/GeoJSON 转换时坐标系未统一导致位置偏移。
- `FeatureToLine` 的 `line_field` 为空时所有要素合并为单一线。

## 最小可运行骨架

```python
import arcpy

def convert_and_export(in_fc: str, in_raster: str, out_gdb: str) -> tuple:
    if not arcpy.management.Exists(out_gdb):
        arcpy.management.CreateFileGDB(out_dir, "converted.gdb")
    out_point = f"{out_gdb}/points"
    out_zone = f"{out_gdb}/zones"
    out_raster = f"{out_gdb}/zones_raster"

    arcpy.conversion.FeatureToPoint(in_fc, out_point, "CENTROID")
    arcpy.conversion.RasterToPolygon(in_raster, out_zone, "SIMPLIFY")
    arcpy.conversion.PolygonToRaster(out_zone, "ZONE_ID", out_raster, cellsize=30)

    return out_point, out_zone, out_raster
```