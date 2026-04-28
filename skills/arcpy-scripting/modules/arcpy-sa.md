# arcpy.sa 模块参数与返回值

## 模块定位

`arcpy.sa` 用于 Spatial Analyst 栅格分析建模，支持地图代数、邻域统计、成本距离、地形分析、重分类和条件分析等流程。与 `arcpy.ia` 类似，所有函数均返回 `Raster` 对象（延迟计算），需显式 `.save()` 落盘。

## 环境参数

- `arcpy.env.cellSize`：分析像元大小（未设置时默认取输入栅格最大值）。
- `arcpy.env.extent`：分析空间范围。
- `arcpy.env.snapRaster`：空间对齐基准栅格。
- `arcpy.env.mask`：分析掩膜（限制处理范围）。
- `arcpy.env.outputCoordinateSystem`：输出坐标系。
- `arcpy.env.compression`：输出压缩方式。
- `arcpy.env.tileSize`：分块大小。

这些参数会直接改变像元对齐、分析范围和结果可比性。未固定会导致跨批次结果差异。

## 高频函数清单

### 条件与逻辑

- `Con`（条件函数）
- `SetNull`（设为空）
- `Pick`（按位置取值）
- `IsNull`（空值检测）
- `Power`（幂函数）
- `Square`（平方）
- `SquareRoot`（平方根）

### 重分类

- `Reclassify`（需配合 RemapRange / RemapValue）
- `RemapRange`（区间映射）
- `RemapValue`（值映射）

### 邻域统计

- `FocalStatistics`
- `BlockStatistics`

### 距离分析

- `CostDistance`
- `CostPath`
- `CostBackLink`
- `EucDistance`
- `EucAllocation`
- `EucDirection`
- `PathDistance`
- `PathAllocation`

### 表面分析

- `Slope`
- `Aspect`
- `Hillshade`
- `Curvature`
- `Contour`
- `Hillshade`
- `Viewshed`
- `CutFill`

### 地图代数运算符

- `+`, `-`, `*`, `/`（算术运算符，重载 Raster 对象）
- `==`, `>`, `<`, `>=`, `<=`（关系运算符）
- `&`, `|`, `^`（逻辑运算符）
- `//`, `%`（整除、取模）

### 局部/全局统计

- `CellStatistics`
- `ZonalStatistics`
- `ZonalGeometry`
- `ZonalHistogram`

### 密度分析

- `KernelDensity`（核密度）
- `PointDensity`（点密度）
- `LineDensity`（线密度）

### 插值

- `Kriging`
- `NaturalNeighbor`
- `Trend`
- `Spline`

### 其他

- `FlowDirection`（流向分析）
- `Watershed`（流域分析）
- `Snake`（图像 Snake 轮廓）

## 函数 1：`Con`（条件函数）

### 参数

- `in_conditional_raster`：条件栅格（布尔或关系表达式）。
- `in_true_raster_or_constant`：条件为真时的输出值（栅格或常数）。
- `in_false_raster_or_constant`（可选）：条件为假时的输出值（默认 NoData）。
- `where_clause`（可选）：附加 SQL 条件表达式。

### 返回值

- 返回 `Raster` 对象（延迟计算）。

### 示例

```python
out_raster = arcpy.sa.Con(in_raster > 5, 1, 0)
out_raster.save(out_path)

# 使用 where_clause 做二次筛选
out_raster = arcpy.sa.Con(in_raster > 5, in_raster, 0, "VALUE > 3")

# 多条件
out_raster = arcpy.sa.Con((in_raster > 5) & (in_raster < 10), 1, 0)
```

## 函数 2：`Reclassify`

### 参数

- `in_raster`：输入栅格。
- `reclass_field`：重分类字段（通常 `"Value"`）。
- `remap`：重映射规则（`RemapRange` 或 `RemapValue` 对象）。
- `missing_values`（可选）：`DATA`（保留原值）或 `NODATA`（设为 NoData）。

### 返回值

- 返回重分类 `Raster` 对象。

### 示例

```python
remap_range = arcpy.sa.RemapRange([[0, 10, 1], [10, 30, 2], [30, 9999, 3]])
out_r = arcpy.sa.Reclassify(in_raster, "Value", remap_range)
out_r.save(out_path)

# 值为映射
remap_val = arcpy.sa.RemapValue([[1, 5], [2, 10], [3, 20], ["NODATA", 0]])
out_r = arcpy.sa.Reclassify(in_raster, "Value", remap_val)
```

## 函数 3：`RemapRange`

### 参数

- `remap_table`：映射表，二维列表 `[[old_min, old_max, new_val], ...]`。

### 示例

```python
remap = arcpy.sa.RemapRange([[0, 1000, 1], [1000, 5000, 2], [5000, 100000, 3]])
```

## 函数 4：`RemapValue`

### 参数

- `remap_table`：映射表，二维列表 `[[old_val, new_val], ...]`。

### 示例

```python
remap = arcpy.sa.RemapValue([[0, 1], [1, 1], [2, 2], [255, "NODATA"]])
```

## 函数 5：`FocalStatistics`

### 参数

- `in_raster`：输入栅格。
- `neighborhood`：邻域形状（`NbrRectangle(3, 3)` / `NbrCircle(3, "CELL")` / `NbrWedge(5, 45, 90)` / `NbrAnnulus(3, 5)` 等）。
- `statistics_type`：`MEAN` / `SUM` / `STD` / `MINIMUM` / `MAXIMUM` / `RANGE` / `MEDIAN` / `MAJORITY` / `MINORITY` / `VARIETY`。
- `ignore_nodata`（可选）：`DATA` / `NODATA`。

### 返回值

- 返回统计 `Raster` 对象。

### 示例

```python
nbr_rect = arcpy.sa.NbrRectangle(5, 5, "CELL")
out_stats = arcpy.sa.FocalStatistics(in_dem, nbr_rect, "MEAN", "DATA")
```

## 函数 6：`BlockStatistics`

### 参数

- 与 `FocalStatistics` 类似，但输出为按块聚合的栅格（块大小由邻域定义）。

### 示例

```python
nbr = arcpy.sa.NbrRectangle(4, 4, "CELL")
out_block = arcpy.sa.BlockStatistics(in_raster, nbr, "SUM")
```

## 函数 7：`Slope`

### 参数

- `in_raster`：输入高程栅格。
- `output_measurement`（可选）：`DEGREE`（度）/ `PERCENT_RISE`（百分比）。
- `z_factor`（可选）：Z 倍率（高程单位转换，如 米转英尺用 0.3048）。
- `method`（可选）：`PLANAR`（平面）/ `GEODESIC`（测地线，更精确）。
- `projected_unit`（可选）：投影单位。
- `preserve_elevation_unit`（可选）：保留高程单位。

### 返回值

- 返回坡度 `Raster` 对象。

### 示例

```python
slope = arcpy.sa.Slope(in_dem, "DEGREE", z_factor=0.3048, method="GEODESIC")
slope.save(out_slope)
```

## 函数 8：`Aspect`

### 参数

- `in_raster`：输入栅格。
- `method`（可选）：`PLANAR` / `GEODESIC`。

### 返回值

- 返回坡向 `Raster` 对象（0-360 度，-1 表示平坦区域）。

### 示例

```python
aspect = arcpy.sa.Aspect(in_dem, method="GEODESIC")
```

## 函数 9：`Hillshade`

### 参数

- `in_raster`：输入高程栅格。
- `azimuth`（可选）：方位角（0-360，默认 315/西北）。
- `altitude`（可选）：高度角（0-90，默认 45）。
- `model_shadows`（可选）：`MODEL_SHADOWS`（考虑自身阴影）/ `NO_SHADOWS`。
- `z_factor`（可选）：Z 倍率。

### 返回值

- 返回山体阴影 `Raster` 对象（0-255）。

### 示例

```python
hillshade = arcpy.sa.Hillshade(in_dem, azimuth=315, altitude=45, model_shadows="MODEL_SHADOWS")
```

## 函数 10：`Curvature`

### 参数

- `in_raster`：输入栅格。
- `z_factor`（可选）：Z 倍率。
- `projected_grid_size`（可选）：投影网格大小。

### 返回值

- 返回曲率 `Raster` 对象（主曲率/平面曲率/剖面曲率）。

### 示例

```python
curvature = arcpy.sa.Curvature(in_dem, z_factor=1.0)
```

## 函数 11：`CostDistance`

### 参数

- `in_source_data`：源点数据（栅格或要素）。
- `in_cost_raster`：成本栅格。
- `out_distance_raster`：输出距离栅格。
- `maximum_distance`（可选）：最大扩散距离。
- `out_backlink_raster`（可选）：回溯方向栅格。
- `source_cost_multiplier`（可选）：成本倍率。
- `source_start_cost`（可选）：初始成本。
- `source_resistance`（可选）：阻力系数。
- `source_capacity`（可选）：最大累积成本。
- `source_direction`（可选）：`FROM_SOURCE` / `TO_SOURCE`。

### 返回值

- 返回成本距离 `Raster` 对象（若指定 `out_distance_raster`）。

### 示例

```python
cost_dist = arcpy.sa.CostDistance(source_fc, cost_raster, out_dist, maximum_distance=5000)
cost_path = arcpy.sa.CostPath(to_point, cost_dist, backlink)
```

## 函数 12：`EucDistance`

### 参数

- `in_source_data`：源数据。
- `out_distance_raster`（可选）：输出距离栅格。
- `cell_size`（可选）：像元大小。
- `maximum_distance`（可选）：最大距离。
- `out_direction_raster`（可选）：方向栅格。

### 返回值

- 返回距离 `Raster` 对象。

### 示例

```python
euc_dist = arcpy.sa.EucDistance(source_points, maximum_distance=1000)
euc_alloc = arcpy.sa.EucAllocation(source_points)
```

在地理坐标系或范围参数不匹配时，`EucDistance` 可能报范围无效；建议优先使用投影坐标系并显式设置 `cell_size`。

## 函数 13：`ZonalStatistics`

### 参数

- `in_zone_data`：区域数据（栅格或要素）。
- `zone_field`：区域字段。
- `in_value_raster`：值栅格。
- `statistics_type`（可选）：`SUM` / `MEAN` / `MAXIMUM` / `MINIMUM` / `RANGE` / `STD` / `VARIETY` / `MAJORITY` / `MINORITY` / `MEDIAN`。
- `ignore_nodata`（可选）：`DATA` / `NODATA`。
- `process_as_multidimensional`（可选）：是否处理多维。
- `percentile_values`（可选）：百分位数（如 `[25, 50, 75]`）。
- `underflow_value`（可选）：溢出值。

### 返回值

- 返回统计 `Raster` 对象。

### 示例

```python
zone_stats = arcpy.sa.ZonalStatistics(zone_fc, "ZONE_ID", dem, "MEAN", "DATA")
```

## 函数 14：`ZonalGeometry`

### 参数

- `in_zone_data`：区域数据。
- `zone_field`：区域字段。
- `geometry_type`：`AREA` / `PERIMETER` / `THICKNESS` / `CENTROID`。

### 返回值

- 返回几何统计 `Raster` 对象。

## 函数 15：`CellStatistics`

### 参数

- `in_rasters`：输入栅格列表或列表。
- `statistics_type`：`SUM` / `MEAN` / `MEDIAN` / `MINIMUM` / `MAXIMUM` / `RANGE` / `STD` / `VARIETY` / `MAJORITY` / `MINORITY` / `PERCENTILE`。
- `ignore_nodata`（可选）：是否忽略 NoData。

### 返回值

- 返回逐像元统计 `Raster` 对象。

### 示例

```python
sum_r = arcpy.sa.CellStatistics([dem1, dem2, dem3], "SUM", "DATA")
```

## 函数 16：`Watershed`

### 参数

- `in_flow_direction_raster`：流向栅格（由 `flow()` 函数生成）。
- `in_pour_point_data`：倾泻点数据。
- `pour_point_field`（可选）：倾泻点字段。

### 返回值

- 返回流域 `Raster` 对象。

### 示例

```python
fdir = arcpy.sa.FlowDirection(in_dem)
ws = arcpy.sa.Watershed(fdir, pour_points)
```

## 函数 17：`Kriging`

### 参数

- `in_point_features`：输入点要素。
- `z_field`：Z 值字段。
- `kriging_model`：克里金模型（`KrigingModelOrdinary` / `KrigingModelUniversal`）。
- `cell_size`（可选）：像元大小。
- `search_radius`（可选）：搜索半径。
- `variogram_model`（可选）：变异函数模型。

### 返回值

- 返回插值 `Raster` 对象。

### 示例

```python
krig_model = arcpy.sa.KrigingModelOrdinary("Spherical", 1000, 0.5)
out_krig = arcpy.sa.Kriging(in_points, "ELEVATION", krig_model, cell_size=30)
```

## 函数 18：`KernelDensity`

### 参数

- `in_features`：输入点/线要素。
- `population_field`（可选）：权重字段（默认 `NONE` 即每个要素权重为 1）。
- `cell_size`（可选）：输出像元大小。
- `search_radius`（可选）：搜索半径（默认根据输入计算）。
- `area_unit_scale_factor`（可选）：`SQUARE_MILES` / `SQUARE_KILOMETERS` 等。
- `out_population_field`（可选）：输出像元中的值类型。

### 返回值

- 返回栅格对象（`Raster`），不是 `arcpy.Result`。
- 需要通过 `.save(output_path)` 写出结果栅格。

### 示例

```python
result = arcpy.sa.KernelDensity(
    crime_points, "WEIGHT",
    cell_size=30,
    search_radius=500,
    area_unit_scale_factor="SQUARE_KILOMETERS"
)
result.save(out_density_raster)
```

## 函数 19：`PointDensity`

### 参数

- `in_features`：输入点要素。
- `population_field`（可选）：权重字段。
- `cell_size`（可选）：像元大小。
- `neighborhood`（可选）：邻域形状（`NbrCircle` 等）。
- `area_unit_scale_factor`（可选）：面积单位比例因子。

### 返回值

- 返回 `Raster` 对象。

### 示例

```python
density = arcpy.sa.PointDensity(in_points, "POP", cell_size=30)
density.save(out_density)
```

## 函数 20：`LineDensity`

### 参数

- `in_features`：输入线要素。
- `population_field`（可选）：权重字段。
- `cell_size`（可选）：像元大小。
- `search_radius`（可选）：搜索半径。
- `area_unit_scale_factor`（可选）：面积单位比例因子。

### 返回值

- 返回 `Raster` 对象。

### 示例

```python
density = arcpy.sa.LineDensity(in_lines, "TRAFFIC", cell_size=30, search_radius=500)
density.save(out_density)
```

## 邻域对象类（Nbr*）

### 常用邻域类

| 类 | 说明 |
|---|---|
| `NbrRectangle(width, height, "CELL"|"MAP")` | 矩形邻域 |
| `NbrCircle(radius, "CELL"|"MAP")` | 圆形邻域 |
| `NbrWedge(radius, start_angle, end_angle, "CELL"|"MAP")` | 楔形邻域 |
| `NbrAnnulus(inner_radius, outer_radius, "CELL"|"MAP")` | 环形邻域 |
| `NbrIrregular(kernel_template_file)` | 不规则邻域 |
| `NbrWeight(kernel_weight_file)` | 加权邻域 |

### 示例

```python
nbr_circle = arcpy.sa.NbrCircle(3, "CELL")
nbr_rect = arcpy.sa.NbrRectangle(3, 3, "MAP")
```

## 距离分析结果对象

`CostDistance` / `EucDistance` 等返回的栅格可配合以下函数使用：

- `CostPath`：最优路径。
- `CostBackLink`：回溯方向。
- `EucDirection`：欧氏方向。
- `EucAllocation`：欧氏分配。

## 地图代数运算符

ArcPy 栅格运算符重载了 Python 运算符，可直接对 `Raster` 对象进行代数运算：

```python
out = (raster1 + raster2) / 2.0
out = arcpy.sa.Power(raster, 2)
out = (dem - raster1) ** 2
out = arcpy.sa.Con(raster > threshold, raster, 0)
```

所有运算符均延迟执行，调用 `.save()` 时才真正计算。

## 常见错误与排查

- 忽略环境参数（`cellSize`、`extent`、`snapRaster`）导致结果不可复现。
- 忽略 `.save()` 导致结果未持久化（内存释放后丢失）。
- 多步骤栅格运算中混用不同像元大小，导致后续统计偏差。
- `CostDistance` 的 `source_direction` 与分析目标不匹配（如从源向外 vs 向源）。
- `Slope` 的 `z_factor` 未根据高程单位调整（默认假设米，如数据是英尺应设为 0.3048）。
- `Reclassify` 的 `RemapRange` 区间有重叠时行为不确定。
- 流向栅格（`flow()` 输出）用于 `Watershed` 时方向必须正确。
- 邻域统计中使用过大的邻域导致内存溢出。

## 最小可运行骨架

```python
import arcpy
from pathlib import Path

def terrain_analysis(dem_path: str, out_dir: str) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dem = dem_path

    slope = arcpy.sa.Slope(dem, "DEGREE", z_factor=1.0)
    slope.save(str(out_dir / "slope.tif"))

    aspect = arcpy.sa.Aspect(dem)
    aspect.save(str(out_dir / "aspect.tif"))

    hillshade = arcpy.sa.Hillshade(dem, azimuth=315, altitude=45)
    hillshade.save(str(out_dir / "hillshade.tif"))

    remap = arcpy.sa.RemapRange([[0, 10, 1], [10, 25, 2], [25, 90, 3]])
    reclass = arcpy.sa.Reclassify(dem, "Value", remap)
    reclass.save(str(out_dir / "reclass.tif"))

    return {
        "slope": str(out_dir / "slope.tif"),
        "aspect": str(out_dir / "aspect.tif"),
        "hillshade": str(out_dir / "hillshade.tif"),
        "reclass": str(out_dir / "reclass.tif"),
    }
```