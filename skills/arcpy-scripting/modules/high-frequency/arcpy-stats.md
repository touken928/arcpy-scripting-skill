# arcpy.stats 模块参数与返回值

## 模块定位

`arcpy.stats` 对应空间统计分析工作流，用于热点分析、离群识别、空间自相关、核密度估计和回归建模。

## 高频工具清单

- `HotSpots`
- `ClusterOutlierAnalysis`
- `SpatialAutocorrelation`
- `AverageNearestNeighbor`
- `KernelDensity`
- `OrdinaryLeastSquares`

## 工具 1：`HotSpots`

### 参数

- `in_features`：输入要素。
- `input_field`：分析字段。
- `out_feature_class`：输出结果要素类。
- `distance_band_or_threshold_distance`（关键）：阈值距离。
- `conceptualization_of_spatial_relationships`（可选）：空间关系模型。
- `standardization`（可选）：标准化方式。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出要素路径。
- 输出属性常含 z-score、p-value、分箱字段。

### 示例

```python
result = arcpy.stats.HotSpots(in_fc, "VALUE", out_fc, distance_band_or_threshold_distance="1000 Meters")
out_fc = result[0]
```

## 工具 2：`SpatialAutocorrelation`

### 参数

- `in_features`：输入要素。
- `input_field`：分析字段。
- `generate_report`（可选）：是否生成报告。
- `distance_band_or_threshold_distance`（可选）：阈值距离。
- `conceptualization_of_spatial_relationships`（可选）：空间关系。
- `standardization`（可选）：标准化方式。

### 返回值

- 返回 `arcpy.Result`。
- 统计指标通常在消息中提供（Moran's I、z-score、p-value）。

### 示例

```python
result = arcpy.stats.SpatialAutocorrelation(in_fc, "VALUE", "GENERATE_REPORT")
messages = result.getMessages()
```

## 工具 3：`ClusterOutlierAnalysis`

### 参数

- `in_features`：输入要素。
- `input_field`：分析字段。
- `out_feature_class`：输出要素。
- `distance_band_or_threshold_distance`（可选）：阈值距离。
- `conceptualization_of_spatial_relationships`（可选）：空间关系。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出路径；输出中常含 LISA/聚类类型字段。

## 工具 4：`AverageNearestNeighbor`

### 参数

- `in_features`：输入要素。
- `distance_method`（可选）：距离计算方法。
- `generate_report`（可选）：是否生成报告。

### 返回值

- 返回 `arcpy.Result`。
- 主要统计值通过消息给出（ANN 比率、z-score、p-value）。

## 工具 5：`KernelDensity`

### 参数

- `in_features`：输入点/线要素。
- `population_field`（可选）：权重字段。
- `cell_size`（可选）：输出像元大小。
- `search_radius`（可选）：搜索半径。
- `area_unit_scale_factor`（可选）：面积单位缩放。

### 返回值

- 返回 `arcpy.Result`。
- `result[0]` 为输出栅格路径。

## 工具 6：`OrdinaryLeastSquares`

### 参数

- `in_features`：输入要素。
- `dependent_variable`：因变量。
- `explanatory_variables`：解释变量列表。
- `out_feature_class`：输出结果要素类。
- 其它可选输出参数：用于落盘系数表/诊断表（具体参数名随工具版本定义，调用前应以本机帮助签名为准）。

### 返回值

- 返回 `arcpy.Result`。
- 可能包含多个派生输出（要素类、系数表、诊断表）。

## 常见错误与排查

- 距离参数未显式设置导致统计解释偏差。
- 回归变量类型不符合统计前提。
- 只看地图输出，不读取消息中的统计显著性指标。
- 统计模型输出未落盘（报告/表）导致结果不可追溯。
