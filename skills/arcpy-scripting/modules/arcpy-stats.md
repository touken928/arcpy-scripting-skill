# arcpy.stats 模块参数与返回值

## 模块定位

`arcpy.stats` 对应 ArcGIS Pro 的空间统计与常规统计工具箱，用于热点分析、离群识别、空间自相关、核密度估计、回归建模和多变量分析。所有工具均返回 `arcpy.Result`。

## 高频工具清单

### 空间格局分析

- `HotSpots`（ Anselin Local Moran's I）
- `ClusterOutlierAnalysis`（聚类/离群分析，LISA）
- `SpatialAutocorrelation`（全局 Moran's I）
- `AverageNearestNeighbor`（最近邻指数）
- `SpatialQuick鸦`（见下方）
- `HighHighClustering` / `LowLowClustering`

### 分布分析

- `KernelDensity`
- `PointDensity`
- `LineDensity`
- `CalculateDensity`

### 回归分析

- `OrdinaryLeastSquares`（OLS）
- `GeographicallyWeightedRegression`（GWR）
- `ExploreTrends`（趋势探索）

### 多变量分析

- `PrincipleComponentsAnalysis`（主成分分析）
- `DiscriminantAnalysis`（判别分析）
- `MultivariateClustering`（多变量聚类）
- `GroupingAnalysis`（分组分析）

### Utility / 数据准备

- `ExportXYv`（将要素类转为 CSV/ASCII）
- `CountRenderer`（计数渲染）

## 工具 1：`HotSpots`（热点分析）

### 参数

- `in_features`：输入要素。
- `input_field`：分析字段（数值型）。
- `out_feature_class`：输出结果要素类。
- `distance_band_or_threshold_distance`（关键）：空间权重矩阵阈值距离（字符串如 `"1000 Meters"`）。
- `conceptualization_of_spatial_relationships`（可选）：
  - `INVERSE_DISTANCE` / `INVERSE_DISTANCE_SQUARED`
  - `FIXED_DISTANCE_BAND`
  - `CONTIGUITY_EDGES_ONLY` / `CONTIGUITY_EDGES_CORNERS`
  - `K_NEAREST_NEIGHBORS`
  - `GET_SPATIAL_WEIGHTS_FROM_FILE`（需配合 weights_matrix_file）
- `standardization`（可选）：`ROW`（按行标准化）或空。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为输出要素路径。
- 输出要素属性包括 `GiZScore`（Z 得分）、`GiPValue`（P 值）、`GiCluster`（聚类类型：
  - `1`：高-高（热点）
  - `2`：低-低（冷点）
  - `3`：高-低（离群）
  - `4`：低-高（离群）
  - `0`：无统计显著性）。

### 示例

```python
result = arcpy.stats.HotSpots(
    in_fc, "CRIME_RATE", out_fc,
    distance_band_or_threshold_distance="1000 Meters",
    conceptualization_of_spatial_relationships="FIXED_DISTANCE_BAND",
    standardization="ROW"
)
out_fc = result[0]
print(result.getMessages())
```

## 工具 2：`ClusterOutlierAnalysis`（聚类与离群分析）

### 参数

- 与 `HotSpots` 基本一致。
- `distance_band_or_threshold_distance`：同上（关键参数）。
- `conceptualization_of_spatial_relationships`：同上。
- `out_weight_matrix_file`（可选）：输出权重矩阵文件。

### 返回值

- 返回 `arcpy.Result`。
- 输出要素属性：`COType`（1=HH, 2=LL, 3=HL, 4=LH, 0=无显著）、`LZiScore`、`LPValue`。

## 工具 3：`SpatialAutocorrelation`（全局空间自相关）

### 参数

- `in_features`：输入要素。
- `input_field`：分析字段。
- `generate_report`（可选）：`GENERATE_REPORT`（输出 PDF 报告）或空。
- `distance_band_or_threshold_distance`（可选）：阈值距离。
- `conceptualization_of_spatial_relationships`（可选）：同上。
- `standardization`（可选）：同上。

### 返回值

- 返回 `arcpy.Result`。
- 统计指标通过 `result.getMessages()` 获取：
  - Moran's I 指数
  - 期望值（I）
  - 方差
  - Z 得分
  - P 值

### 示例

```python
result = arcpy.stats.SpatialAutocorrelation(
    in_fc, "INCOME",
    distance_band_or_threshold_distance="5000 Meters",
    conceptualization_of_spatial_relationships="INVERSE_DISTANCE"
)
for msg in result.getMessages():
    print(msg)
```

## 工具 4：`AverageNearestNeighbor`（平均最近邻）

### 参数

- `in_features`：输入要素。
- `distance_method`（可选）：`EUCLIDEAN`（欧氏）/ `MANHATTAN`（曼哈顿）。
- `generate_report`（可选）：`GENERATE_REPORT`（输出 PDF）。
- `area`（可选）：区域面积值（用于计算密度）。

### 返回值

- 返回 `arcpy.Result`。
- 消息输出：ANN 比率、z-score、p-value、平均观测距离、预期平均距离。

## 工具 5：`KernelDensity`

### 参数

- `in_features`：输入点/线要素。
- `population_field`（可选）：权重字段（默认 `NONE` 即每个要素权重为 1）。
- `cell_size`（可选）：输出像元大小。
- `search_radius`（可选）：搜索半径（默认根据输入计算）。
- `area_unit_scale_factor`（可选）：`SQUARE_MILES` / `SQUARE_KILOMETERS` 等。
- `out_population_field`（可选）：输出像元中的值类型。

### 返回值

- 返回 `arcpy.Result`，`result[0]` 为输出栅格路径。

### 示例

```python
result = arcpy.stats.KernelDensity(
    crime_points, "WEIGHT",
    cell_size=30,
    search_radius=500,
    area_unit_scale_factor="SQUARE_KILOMETERS"
)
out_density_raster = result[0]
```

## 工具 6：`PointDensity` / `LineDensity`

### 参数

- 与 `KernelDensity` 类似（专属点/线密度）。

## 工具 7：`CalculateDensity`（多维数据密度）

### 参数

- `in_features`：输入要素。
- `bin_size`（可选）：格网大小。
- `radius_multiplier`（可选）：半径倍率。
- `out_cell_size`（可选）：输出像元大小。
- `spatial_reference`（可选）：输出空间参考。

### 返回值

- 返回 `arcpy.Result`。

## 工具 8：`OrdinaryLeastSquares`（OLS 回归）

### 参数

- `in_features`：输入要素。
- `dependent_variable`：因变量字段。
- `explanatory_variables`：解释变量列表（如 `["X1", "X2", "X3"]`）。
- `out_feature_class`：输出结果要素类。
- `coefficient_output_table`（可选）：系数输出表路径。
- `diagnostic_output_table`（可选）：诊断输出表路径。
- `connectivity`（可选）：空间权重矩阵连接方式。

### 返回值

- 返回 `arcpy.Result`。
- 输出要素包含残差字段，可结合 `ClusterOutlierAnalysis` 分析残差聚集。
- 系数表包含各解释变量的系数、标准误、t-stat、p-val、VIF 等。

### 示例

```python
result = arcpy.stats.OrdinaryLeastSquares(
    in_fc, "PRICE",
    ["SQFT", "BEDROOMS", "AGE"],
    out_fc,
    coefficient_output_table=f"{work_dir}/ols_coef.dbf",
    diagnostic_output_table=f"{work_dir}/ols_diag.dbf"
)
print(result.getMessages())
```

## 工具 9：`GeographicallyWeightedRegression`（GWR）

### 参数

- `in_features`：输入要素。
- `dependent_variable`：因变量。
- `explanatory_variables`：解释变量。
- `out_feature_class`：输出要素类。
- `kernel_type`（可选）：`GAUSSIAN` / `BISQUARE`。
- `bandwidth_method`（可选）：`AICc` / `BANDWIDTH_PARAMETER`。
- `distance_band`（可选）：固定带宽值。
- `weight_field`（可选）：权重字段。

### 返回值

- 返回 `arcpy.Result`。
- 输出属性包含局部 R²、残差等。

## 工具 10：`ExploreTrends`（趋势探索）

### 参数

- `in_features`：输入要素。
- `z_field`：Z 值字段。
- `out_report`：输出 PDF 报告路径。
- `cell_size`（可选）：像元大小。
- `search_radius`（可选）：搜索半径。

### 返回值

- 返回 `arcpy.Result`。

## 工具 11：`PrincipalComponentsAnalysis`（主成分分析）

### 参数

- `in_table`：输入表或要素类。
- `output_features`：输出要素类。
- `number_of_components`（可选）：主成分数量。
- `variables`（必需）：分析变量列表。

### 返回值

- 返回 `arcpy.Result`。

## 工具 12：`GroupingAnalysis`（分组分析）

### 参数

- `in_features`：输入要素。
- `group_by_field`（可选）：分组字段（如果进行监督分组）。
- `output_features`：输出要素类。
- `number_of_groups`（必需）：分组数。
- `analysis_fields`：分析字段列表。
- `spatial_constraints`（可选）：`NO_SPATIAL_CONSTRAINT` / `CONTIGUITY_EDGES_ONLY` / `CONTIGUITY_EDGES_CORNERS` / `GET_SPATIAL_WEIGHTS_FROM_FILE`。
- `create_graph`（可选）：是否输出聚类图。

### 返回值

- 返回 `arcpy.Result`。
- 输出要素包含 `SSQ`、`SC_Label` 等字段。

## 工具 13：`MultivariateClustering`（多变量聚类）

### 参数

- 与 `GroupingAnalysis` 类似。
- `min_outliers`（可选）：最小离群值数。

### 返回值

- 返回 `arcpy.Result`。

## 工具 14：`ExportXYv`（ASCII/CSV 导出）

### 参数

- `in_table`：输入表或要素类。
- `out_file`：输出文件路径（`.txt`、`.csv` 或空格分隔的 `.dat`）。
- `fields`：导出字段列表（逗号分隔字符串）。
- `coords_spec`（可选）：坐标规范。

### 返回值

- 返回 `arcpy.Result`。

### 示例

```python
arcpy.stats.ExportXYv(in_fc, out_csv, "OID@;X;Y;VALUE", "COMMA")
```

## 输出字段速查

### 热点/聚类分析输出字段

| 字段 | 说明 |
|------|------|
| `GiZScore` | Z 得分（热点） |
| `GiPValue` | P 值（热点） |
| `GiCluster` | 聚类类型（1=HH, 2=LL, 3=HL, 4=LH, 0=NS） |
| `COType` | 聚类/离群类型（同上，LISA） |
| `LZiScore` | LISA Z 得分 |
| `LPValue` | LISA P 值 |

### OLS 输出字段

| 字段 | 说明 |
|------|------|
| `Residual` | 回归残差 |
| `Predicted` | 预测值 |
| `StdResidual` | 标准化残差 |

## 常见错误与排查

- 距离参数未显式设置导致统计解释偏差（无意义的空间临近假设）。
- 回归变量存在多重共线性（VIF > 7.5 通常表明问题）。
- 只看地图输出，不读取消息中的统计显著性指标。
- 统计模型输出未落盘（报告/表）导致结果不可追溯。
- 空间约束聚类（`CONTIGUITY_*`）时输入要素没有邻接关系导致无法聚类。
- `HotSpots` 的 `distance_band` 设得过大导致所有位置均显著或均不显著。
- 全局 Moran's I 和局部 LISA 结果不一致时，说明存在空间非平稳性（考虑用 GWR）。
- 输入字段存在空值（NoData）导致工具跳过整条记录。
- 回归分析残差存在空间自相关时，说明 OLS 假设不完整（考虑空间滞后/误差模型）。

## 最小可运行骨架

```python
import arcpy

def spatial_analysis(in_fc: str, field: str, out_dir: str) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 热点分析
    hs_out = out_dir / "hotspots.shp"
    result = arcpy.stats.HotSpots(
        in_fc, field, str(hs_out),
        distance_band_or_threshold_distance="1000 Meters",
        conceptualization_of_spatial_relationships="FIXED_DISTANCE_BAND",
        standardization="ROW"
    )
    print(result.getMessages())

    # 全局自相关
    sa_result = arcpy.stats.SpatialAutocorrelation(
        in_fc, field,
        distance_band_or_threshold_distance="1000 Meters",
        generate_report="GENERATE_REPORT"
    )

    # OLS 回归
    ols_out = out_dir / "ols_result.shp"
    coef_table = out_dir / "ols_coef.dbf"
    diag_table = out_dir / "ols_diag.dbf"
    arcpy.stats.OrdinaryLeastSquares(
        in_fc, field, ["X1", "X2"], str(ols_out),
        coefficient_output_table=str(coef_table),
        diagnostic_output_table=str(diag_table)
    )

    return {"hotspots": str(hs_out), "ols": str(ols_out)}
```