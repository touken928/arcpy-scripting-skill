# arcpy.sa 模块参数与返回值

## 模块定位

`arcpy.sa` 用于 Spatial Analyst 栅格分析建模，支持地图代数、邻域统计、成本距离、地形分析、重分类和条件分析等流程。

## 许可前置

- `arcpy.CheckExtension("Spatial")`
- `arcpy.CheckOutExtension("Spatial")`
- `finally` 中 `arcpy.CheckInExtension("Spatial")`

## 环境参数（强约束）

- `arcpy.env.cellSize`
- `arcpy.env.extent`
- `arcpy.env.snapRaster`
- `arcpy.env.mask`
- `arcpy.env.outputCoordinateSystem`

这些参数会直接改变像元对齐、分析范围和结果可比性。

## 高频函数清单

- `Con`
- `Reclassify`
- `FocalStatistics`
- `Slope`
- `CostDistance`

## 函数 1：`Con`

### 参数

- `in_conditional_raster`：条件栅格。
- `in_true_raster_or_constant`：条件为真输出。
- `in_false_raster_or_constant`（可选）：条件为假输出。
- `where_clause`（可选）：条件表达式。
- 若输入为 Raster 对象表达式，通常无需 `where_clause`。

### 返回值

- 返回 `Raster` 对象（未落盘）。
- 使用 `.save(out_path)` 落盘。

### 示例

```python
out_raster = arcpy.sa.Con(in_raster > 5, 1, 0)
out_raster.save(out_path)
```

## 函数 2：`Reclassify`

### 参数

- `in_raster`：输入栅格。
- `reclass_field`：重分类字段（常用 `Value`）。
- `remap`：重分类规则对象。
- `missing_values`（可选）：遗漏值处理。
- `missing_values` 常见取值：`DATA` / `NODATA`（按函数定义）。

### 返回值

- 返回 `Raster` 对象。

### 示例

```python
remap = arcpy.sa.RemapRange([[0, 10, 1], [10, 30, 2], [30, 9999, 3]])
out_r = arcpy.sa.Reclassify(in_raster, "Value", remap)
out_r.save(out_path)
```

## 函数 3：`FocalStatistics`

### 参数

- `in_raster`：输入栅格。
- `neighborhood`：邻域窗口定义。
- `statistics_type`：统计类型。
- `ignore_nodata`（可选）：NoData 处理策略。

### 返回值

- 返回 `Raster` 对象。

## 函数 4：`Slope`

### 参数

- `in_raster`：输入高程栅格。
- `output_measurement`（可选）：`DEGREE` / `PERCENT_RISE`。
- `z_factor`（可选）：Z 倍率。
- `method`（可选）：计算方法。

### 返回值

- 返回坡度 `Raster` 对象。

## 函数 5：`CostDistance`

### 参数

- `in_source_data`：源点数据。
- `in_cost_raster`：成本栅格。
- `maximum_distance`（可选）：最大扩散距离。
- 可选输出参数：可按需求生成回溯/方向类辅助结果（具体参数名与函数版本定义有关）。

### 返回值

- 返回成本距离 `Raster` 对象。
- 若配置辅助输出，需额外保存/读取对应结果栅格。

## 常见错误与排查

- 忽略环境参数（`cellSize`、`extent`、`snapRaster`）导致结果不可复现。
- 忽略 `.save()` 导致结果未持久化。
- 未处理许可 checkout/checkin。
- 多步骤栅格运算中混用不同像元大小，导致后续统计偏差。
