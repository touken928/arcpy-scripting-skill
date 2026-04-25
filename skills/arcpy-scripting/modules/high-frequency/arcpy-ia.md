# arcpy.ia 模块参数与返回值

## 模块定位

`arcpy.ia` 用于影像分析与高级栅格处理，适合遥感指数、影像分类、分割与影像增强等自动化流程。

## 许可前置

- 通常需要 Image Analyst 扩展许可。
- 建议显式检查并管理 checkout/checkin。

## 环境参数（建议显式固定）

- `arcpy.env.cellSize`
- `arcpy.env.extent`
- `arcpy.env.snapRaster`
- `arcpy.env.outputCoordinateSystem`

## 高频函数清单

- `NDVI`
- `NDBI`
- `NDWI`
- `Classify`
- `SegmentMeanShift`

## 函数 1：`NDVI`

### 参数

- 主要输入为多波段栅格。
- 关键参数：近红外波段、红波段索引。
- 波段索引必须与影像波段顺序一致（不同传感器顺序可能不同）。

### 返回值

- 返回 `Raster` 对象。
- 需 `.save()` 持久化。

### 示例

```python
ndvi = arcpy.ia.NDVI(in_multiband_raster, 4, 3)
ndvi.save(out_ndvi)
```

## 函数 2：`Classify`

### 参数

- 输入影像栅格。
- 分类器/训练样本参数。
- 分类方法参数。

### 返回值

- 返回分类结果 `Raster` 对象。

## 函数 3：`SegmentMeanShift`

### 参数

- `in_raster`：输入影像。
- `spectral_detail`：光谱细节参数。
- `spatial_detail`：空间细节参数。
- `min_segment_size`：最小分割块大小。
- `band_indexes`（可选）：参与分割的波段。

### 返回值

- 返回分割结果 `Raster` 对象。

## 函数 4：`NDBI` / `NDWI`

### 参数

- 输入多波段栅格。
- 指定目标波段索引（建筑指数/水体指数所需波段）。

### 返回值

- 返回指数栅格 `Raster` 对象。

## 常见错误与排查

- 波段顺序理解错误导致指数计算错误。
- 输出未落盘。
- 影像分析环境参数未固定。
- 分类前未统一像元大小和投影，导致训练与推理结果偏差。
