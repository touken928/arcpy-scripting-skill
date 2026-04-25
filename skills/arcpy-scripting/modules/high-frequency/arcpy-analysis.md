# arcpy.analysis 模块参数与返回值

## 模块定位

`arcpy.analysis` 是 ArcPy 中最常用的矢量空间分析模块，负责缓冲、裁剪、叠加、空间连接、邻近分析等核心分析任务。通常用于“准备分析输入 -> 生成分析结果图层”的中间与主处理阶段。

## 高频工具清单

- `Buffer`
- `Clip`
- `Intersect`
- `Erase`
- `SpatialJoin`
- `Near`
- `Identity`

## 工具 1：`Buffer`

### 参数

- `in_features`：输入要素。
- `out_feature_class`：输出要素类。
- `buffer_distance_or_field`：缓冲距离或距离字段。
- `line_side`（可选）：线缓冲方向。
- `line_end_type`（可选）：端点样式。
- `dissolve_option`（可选）：`NONE` / `ALL` / `LIST`。
- `dissolve_field`（可选）：按字段融合。
- `method`（可选）：平面/测地线。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出要素路径。

### 示例

```python
result = arcpy.analysis.Buffer(in_fc, out_fc, "100 Meters", dissolve_option="ALL")
out_path = result[0]
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

- `in_features`：输入要素集合（可多个）。
- `out_feature_class`：输出要素类。
- `join_attributes`（可选）：属性处理策略。
- `cluster_tolerance`（可选）：拓扑容差。
- `output_type`（可选）：输出几何类型。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.analysis.Intersect([roads_fc, district_fc], out_fc)
```

## 工具 4：`Erase`

### 参数

- `in_features`：输入要素。
- `erase_features`：擦除边界。
- `out_feature_class`：输出要素。

### 返回值

- 返回 `arcpy.Result`。

## 工具 5：`SpatialJoin`

### 参数

- `target_features`：目标要素。
- `join_features`：连接要素。
- `out_feature_class`：输出要素。
- `join_operation`（可选）：`JOIN_ONE_TO_ONE` / `JOIN_ONE_TO_MANY`。
- `join_type`（可选）：内连接/外连接。
- `match_option`（可选）：空间匹配规则。
- `search_radius`（可选）：匹配搜索半径。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出要素路径。

### 示例

```python
result = arcpy.analysis.SpatialJoin(
    target_fc,
    join_fc,
    out_fc,
    join_operation="JOIN_ONE_TO_ONE",
    join_type="KEEP_ALL",
    match_option="INTERSECT",
)
joined_fc = result[0]
```

## 工具 6：`Near`

### 参数

- `in_features`：输入要素。
- `near_features`：邻近参考要素。
- `search_radius`（可选）：搜索半径。
- `location`（可选）：是否写入最近点坐标。
- `angle`（可选）：是否写入方位角。

### 返回值

- 返回 `arcpy.Result`。
- 结果通常写回输入要素字段（如 `NEAR_DIST`）。

### 示例

```python
arcpy.analysis.Near(in_fc, near_fc, search_radius="2000 Meters", location="LOCATION")
```

## 工具 7：`Identity`

### 参数

- `in_features`：输入要素。
- `identity_features`：身份叠加参考要素。
- `out_feature_class`：输出要素。
- `join_attributes`（可选）：属性保留策略。
- `cluster_tolerance`（可选）：聚类容差。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出路径。

## 常见错误与排查

- 缓冲距离单位未显式写，导致结果单位混乱。
- `SpatialJoin` 连接类型选择错误，造成记录丢失或爆炸。
- `Near` 被当作新输出工具，实际默认写回输入数据。
- `Intersect` 输入几何类型差异较大时，输出类型未显式控制导致结果不符合预期。
- `Erase` 输入与擦除层坐标系不一致，导致结果偏移或空结果。
