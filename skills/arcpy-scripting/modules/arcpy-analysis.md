# arcpy.analysis 模块参数与返回值

## 模块定位

`arcpy.analysis` 是 ArcPy 中最常用的矢量空间分析模块，负责缓冲、裁剪、叠加、空间连接、邻近分析等核心分析任务。通常用于"准备分析输入 -> 生成分析结果图层"的中间与主处理阶段。

## 高频工具清单

- `Buffer`
- `Clip`
- `Intersect`
- `Union`
- `Erase`
- `Identity`
- `SpatialJoin`
- `Near`
- `GenerateNearTable`
- `PointDistance`
- `SelectLayerByLocation`
- `FeatureToLine`
- `FeatureToPoint`
- `MultipartToSinglepart`
- `Dissolve`
- `Eliminate`

## 工具 1：`Buffer`

### 参数

- `in_features`：输入要素。
- `out_feature_class`：输出要素类。
- `buffer_distance_or_field`：缓冲距离（字符串如 `"100 Meters"` 或数值）或字段名。
- `line_side`（可选）：`FULL` / `LEFT` / `RIGHT`。
- `line_end_type`（可选）：`ROUND` / `FLAT`。
- `dissolve_option`（可选）：`NONE` / `ALL` / `LIST`。
- `dissolve_field`（可选）：按字段融合。
- `method`（可选）：`PLANAR` / `GEODESIC`。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出要素路径。

### 示例

```python
result = arcpy.analysis.Buffer(in_fc, out_fc, "100 Meters", dissolve_option="ALL")
out_path = result[0]
# 使用字段缓冲
result = arcpy.analysis.Buffer(in_fc, out_fc, "BUFF_DIST")
```

## 工具 2：`Clip`

### 参数

- `in_features`：被裁剪要素。
- `clip_features`：裁剪边界。
- `out_feature_class`：输出要素类。
- `cluster_tolerance`（可选）：聚类容差。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为输出路径。

### 示例

```python
arcpy.analysis.Clip(in_fc, boundary_fc, out_fc)
```

## 工具 3：`Intersect`

### 参数

- `in_features`：输入要素集合（列表或单个路径，多个时逗号分隔字符串）。
- `out_feature_class`：输出要素类。
- `join_attributes`（可选）：`ALL` / `ONLY_FID` / `NO_FID`。
- `cluster_tolerance`（可选）：拓扑容差。
- `output_type`（可选）：`INPUT` / `LINE` / `POINT`。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.analysis.Intersect([roads_fc, district_fc], out_fc, output_type="LINE")
```

## 工具 4：`Union`

### 参数

- `in_features`：输入要素集合。
- `out_feature_class`：输出要素类。
- `join_attributes`（可选）：同上（`ALL` / `ONLY_FID` / `NO_FID`）。
- `cluster_tolerance`（可选）：同上。
- `gaps`（可选）：是否保留空白区域（`ALL` / `NO_GAPS`）。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.analysis.Union([zone_a, zone_b, zone_c], out_fc, gaps="NO_GAPS")
```

## 工具 5：`Erase`

### 参数

- `in_features`：输入要素。
- `erase_features`：擦除边界。
- `out_feature_class`：输出要素。
- `cluster_tolerance`（可选）：聚类容差。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
result = arcpy.analysis.Erase(in_fc, erase_fc, out_fc)
```

## 工具 6：`Identity`

### 参数

- `in_features`：输入要素。
- `identity_features`：身份叠加参考要素。
- `out_feature_class`：输出要素。
- `join_attributes`（可选）：`ALL` / `NO_FID` / `FID_ONLY`。
- `cluster_tolerance`（可选）：聚类容差。
- `relationship`（可选）：是否传递空间关系。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为输出路径。

## 工具 7：`SpatialJoin`

### 参数

- `target_features`：目标要素。
- `join_features`：连接要素。
- `out_feature_class`：输出要素。
- `join_operation`（可选）：`JOIN_ONE_TO_ONE` / `JOIN_ONE_TO_MANY`。
- `join_type`（可选）：`KEEP_ALL` / `KEEP_COMMON`。
- `match_option`（可选）：`INTERSECT` / `WITHIN_A_DISTANCE` / `CONTAINS` / `COMPLETELY_CONTAINS` / `CROSSES` / `WITHIN` / `ARE_IDENTICAL_TO` / `BOUNDARY_TOUCHES`。
- `search_radius`（可选）：匹配搜索半径（字符串如 `"100 Meters"`）。
- `distance_field_name`（可选）：输出距离字段名。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为输出要素路径。

### 示例

```python
result = arcpy.analysis.SpatialJoin(
    target_fc,
    join_fc,
    out_fc,
    join_operation="JOIN_ONE_TO_ONE",
    join_type="KEEP_ALL",
    match_option="INTERSECT",
    search_radius="500 Meters",
)
joined_fc = result[0]
```

## 工具 8：`Near`

### 参数

- `in_features`：输入要素。
- `near_features`：邻近参考要素。
- `search_radius`（可选）：搜索半径。
- `location`（可选）：`LOCATION` / `NO_LOCATION`，是否写入最近点坐标到字段。
- `angle`（可选）：`ANGLE` / `NO_ANGLE`，是否写入方位角。
- `method`（可选）：`PLANAR` / `GEODESIC`。
- `field_names`（可选，10.8+）：附加字段。

### 返回值

- 返回 `arcpy.Result`。
- 结果写入输入要素的字段（`NEAR_FID`、`NEAR_DIST`、`NEAR_X`、`NEAR_Y`、`NEAR_ANGLE`）。

### 示例

```python
arcpy.analysis.Near(in_fc, near_fc, search_radius="2000 Meters", location="LOCATION", angle="ANGLE")
```

## 工具 9：`GenerateNearTable`

### 参数

- `in_features`：输入要素。
- `near_features`：邻近参考要素。
- `out_table`：输出距离表（必须为 `.dbf` / `.gdb` 表）。
- `search_radius`（可选）：搜索半径。
- `closest`（可选）：最近邻数量。
- `closest_count`（可选，11+）：同 `closest`。
- `method`（可选）：`PLANAR` / `GEODESIC`。
- `distance_unit`（可选）：距离单位。
- `start_time`（可选）：开始时间（时空分析）。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
result = arcpy.analysis.GenerateNearTable(in_fc, near_fc, out_table, search_radius="1 Kilometers", closest="3")
```

## 工具 10：`PointDistance`

### 参数

- `in_features`：源点要素。
- `near_features`：邻近点要素。
- `out_table`：输出距离表。
- `search_radius`（可选）：搜索半径。
- `distance_unit`（可选）：`Meters` / `Kilometers` 等。
- `method`（可选）：`PLANAR` / `GEODESIC`。

### 返回值

- 返回 `arcpy.Result`。

## 工具 11：`SelectLayerByLocation`（`arcpy.management`）

### 参数

- `in_layer`：输入图层（需为图层对象，非要素类路径）。
- `overlap_type`：常用 `INTERSECT` / `WITHIN_A_DISTANCE` / `WITHIN` / `CONTAINS`（不同数据类型可用值存在差异，建议按工具帮助校验）。
- `select_features`：选择要素。
- `search_distance`（可选）：搜索距离（用于 `WITHIN_A_DISTANCE`）。
- `selection_type`：`NEW_SELECTION` / `ADD_TO_SELECTION` / `REMOVE_FROM_SELECTION` / `SUBSET_SELECTION` / `CLEAR_SELECTION`。
- `invert_clause`（可选）：`INVERT` / `NO_INVERT`。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
lyr = arcpy.management.MakeFeatureLayer(fc, "lyr")[0]
arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", buffer_fc)
```

## 工具 12：`Dissolve`（`arcpy.management`）

### 参数

- `in_features`：输入要素。
- `out_feature_class`：输出要素。
- `dissolve_field`（可选）：融合字段（列表或逗号分隔字符串）。
- `statistics_fields`（可选）：统计字段。
- `multi_part`（可选）：`MULTI_PART` / `SINGLE_PART`。
- `unsplit_field`（可选）：不融合字段。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.analysis.Dissolve(in_fc, out_fc, dissolve_field="ZONE_CODE", statistics_fields="AREA SUM")
```

## 工具 13：`FeatureToPoint`（`arcpy.management`）

### 参数

- `in_features`：输入要素。
- `out_feature_class`：输出点要素。
- `point_location`（可选）：`CENTROID` / `INSIDE`。

### 返回值

- 返回 `arcpy.Result`。

## 工具 14：`MultipartToSinglepart`（`arcpy.management`）

### 参数

- `in_features`：输入多部件要素。
- `out_feature_class`：输出单部件要素。

### 返回值

- 返回 `arcpy.Result`。

## 常见错误与排查

- 缓冲距离单位未显式写，导致结果单位混乱（如 `"100"` 被视为未知单位）。
- `SpatialJoin` 连接类型选择错误，造成记录丢失或爆炸（`JOIN_ONE_TO_MANY` 会产生 n*m 条记录）。
- `Near` 被当作新输出工具，实际默认写回输入数据的字段（如 `NEAR_DIST`）。
- `Intersect` 输入几何类型差异较大时，输出类型未显式控制导致结果不符合预期。
- `Erase` 输入与擦除层坐标系不一致，导致结果偏移或空结果。
- `SelectLayerByLocation` 需要图层对象，直接传要素类路径会报错。
- 融合字段列表应避免空字符串导致意外融合。

## 最小可运行骨架

```python
import arcpy

def spatial_analysis(in_fc: str, boundary_fc: str, out_gdb: str) -> str:
    arcpy.management.CreateFileGDB(out_dir, "analysis.gdb") if not arcpy.management.Exists(f"{out_gdb}") else None
    clipped = f"{out_gdb}/clipped"
    buffered = f"{out_gdb}/buffered"
    intersected = f"{out_gdb}/result"

    arcpy.analysis.Clip(in_fc, boundary_fc, clipped)
    arcpy.analysis.Buffer(boundary_fc, buffered, "500 Meters")
    arcpy.analysis.Intersect([clipped, buffered], intersected)

    count = int(arcpy.management.GetCount(intersected)[0])
    print(f"Analysis complete: {count} features")
    return intersected
```