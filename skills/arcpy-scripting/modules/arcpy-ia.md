# arcpy.ia 模块参数与返回值

## 模块定位

`arcpy.ia` 用于影像分析与高级栅格处理，适合遥感指数、影像分类、分割与影像增强等自动化流程。该模块的所有函数均基于 `Raster` 对象（延迟计算），需显式调用 `.save()` 落盘。

## 许可前置

- 通常需要 Image Analyst 扩展许可。
- 建议显式检查并管理 checkout/checkin：

```python
if arcpy.CheckExtension("ImageAnalyst") == "Available":
    arcpy.CheckOutExtension("ImageAnalyst")
else:
    raise RuntimeError("Image Analyst license unavailable")
```

## 环境参数（建议显式固定）

- `arcpy.env.cellSize`：分析像元大小。
- `arcpy.env.extent`：分析空间范围。
- `arcpy.env.snapRaster`：对齐基准栅格。
- `arcpy.env.outputCoordinateSystem`：输出坐标系。
- `arcpy.env.mask`：分析掩膜。

## 高频函数清单

### 分析类

- `Aggregate`
- `Anomaly`
- `ComputeChange`
- `DetectChangeUsingChangeAnalysis`
- `Gradient`
- `HeatIndex`
- `WindChill`
- `Threshold`

### 分类/分割

- `Classify`
- `MLClassify`
- `SegMeanShift`
- `RegionGrow`
- `LinearUnmixing`

### 波段指数

- `NDVI`
- `NDWI`
- `NDBI`
- `EVI`
- `SAVI`
- `NBR` / `NBR2`
- `MSAVI`
- `GNDVI`
- `VARI`
- `IronOxide`
- `ClayMinerals`
- `FerrousMinerals`

### 表面/转换

- `TasseledCap`
- `Apply`
- `CompositeBand`
- `ColormapToRGB`
- `Grayscale`
- `UnitConversion`
- `VectorField`
- `XarrayToRaster`
- `RasterToXarray`

## 函数 1：`NDVI`

### 参数

- `in_raster`：多波段栅格路径或 `Raster` 对象。
- `nir_band`（可选，11.0+）：近红外波段索引（从 1 开始，默认为 `4`）。
- `red_band`（可选，11.0+）：红光波段索引（默认为 `3`）。

### 返回值

- 返回指数 `Raster` 对象（值域通常 `[-1, 1]`）。
- 需 `.save()` 持久化。

### 示例

```python
ndvi = arcpy.ia.NDVI(in_multiband_raster, nir_band=4, red_band=3)
ndvi.save(out_ndvi)
```

## 函数 2：`NDWI`

### 参数

- `in_raster`：输入多波段栅格。
- `nir_band`（可选）：近红外波段索引。
- `green_band`（可选）：绿光波段索引（默认 `2`）。

### 返回值

- 返回水体指数 `Raster` 对象。

### 示例

```python
ndwi = arcpy.ia.NDWI(in_raster, green_band=2, nir_band=4)
```

## 函数 3：`NDBI`

### 参数

- `in_raster`：输入多波段栅格。
- `nir_band`（可选）：近红外波段索引。
- `swir_band`（可选，短波红外，默认 `6`）。

### 返回值

- 返回建筑指数 `Raster` 对象。

## 函数 4：`Aggregate`

### 参数

- `in_raster`：输入栅格。
- `cell_factor`：聚合因子（整数值，如 `4` 表示 4×4 聚合）。
- `aggregation_type`（可选）：`CELL_CENTER` / `SUM` / `MAX` / `MIN` / `MEAN` / `MEDIAN`。
- `expand_ratio`（可选）：扩展比。
- `variance_ratio`（可选）：方差比。

### 返回值

- 返回聚合后 `Raster` 对象。

### 示例

```python
agg = arcpy.ia.Aggregate(in_raster, cell_factor=4, aggregation_type="MEAN")
```

## 函数 5：`Classify`

### 参数

- `in_raster`：输入影像栅格。
- `in_classifier_definition`：分类器定义文件（`.ecd`，由 `TrainClassifier` 生成）。
- `in_additional_raster`（可选）：附加栅格（如 DEM 用于辅助分类）。

### 返回值

- 返回分类结果 `Raster` 对象。

### 示例

```python
classified = arcpy.ia.Classify(in_raster, classifier_def)
classified.save(out_classified)
```

## 函数 6：`MLClassify`

### 参数

- `in_raster`：输入栅格。
- `signature_file`：签名文件（`.gsg`，由 `胞格统计` 或 `训练样本管理器` 生成）。

### 返回值

- 返回分类 `Raster` 对象。

### 示例

```python
result = arcpy.ia.MLClassify(in_raster, signature_file)
```

## 函数 7：`SegMeanShift`

### 参数

- `in_raster`：输入影像。
- `spectral_detail`（可选）：光谱细节（1-20，越高分割越细）。
- `spatial_detail`（可选）：空间细节（1-20）。
- `min_segment_size`：最小分割块大小（像素数）。
- `band_indexes`（可选）：参与分割的波段索引（如 `"1 2 3 4 5"`）。

### 返回值

- 返回分割结果 `Raster` 对象。

### 示例

```python
segments = arcpy.ia.SegMeanShift(
    in_raster,
    spectral_detail=15,
    spatial_detail=10,
    min_segment_size=100,
    band_indexes="1 2 3 4"
)
```

## 函数 8：`RegionGrow`

### 参数

- `in_raster`：输入栅格。
- `seed_points`：种子点（要素类或坐标列表）。
- `similarity_values`（可选）：相似性阈值。
- `max_resolution`（可选）：最大分辨率。

### 返回值

- 返回区域生长 `Raster` 对象。

## 函数 9：`Anomaly`

### 参数

- `in_raster`：输入栅格。
- `anomaly_type`（可选）：`DIFFERENCE` / `PERCENT_DIFFERENCE`。
- `core_radius`（可选）：核心半径。
- `in_mean_raster`（可选）：均值栅格（用于计算局部异常）。

### 返回值

- 返回异常检测 `Raster` 对象。

## 函数 10：`ComputeChange`

### 参数

- `in_raster1`：时相 1 栅格。
- `in_raster2`：时相 2 栅格。
- `change_type`（可选）：`ABSOLUTE` / `RELATIVE` / `CATEGORICAL`。
- `kernel`（可选）：核大小。
- `in_weight_raster`（可选）：权重栅格。

### 返回值

- 返回变化检测 `Raster` 对象。

## 函数 11：`Threshold`

### 参数

- `in_raster`：输入栅格。
- `threshold_type`（可选）：`OTSU` / `HISTOGRAM` / `PERCENTILE`。
- `threshold_count`（可选）：阈值/百分位数。

### 返回值

- 返回二值化 `Raster` 对象。

## 函数 12：`Gradient`

### 参数

- `in_raster`：输入高程/数值栅格。
- `gradient_type`（可选）：`DEGREE` / `PERCENT` / `RADIAN`。
- `unit`（可选）：`METER` / `FOOT` / `KILOMETER`。

### 返回值

- 返回坡度 `Raster` 对象。

## 函数 13：`TasseledCap`

### 参数

- `in_raster`：输入多波段栅格（通常为 Landsat 或 Sentinel-2）。
- `sensor`（可选）：传感器类型（`LandsatTM` / `LandsatETM` / `Sentinel2` 等，自动推断时可省略）。

### 返回值

- 返回三个波段（亮度、绿度、湿度）的复合 `Raster` 对象。

### 示例

```python
tasseled = arcpy.ia.TasseledCap(in_raster, sensor="Sentinel2")
tasseled.save(out_tc)
```

## 函数 14：`UnitConversion`

### 参数

- `in_raster`：输入栅格。
- `from_units`：源单位。
- `to_units`：目标单位。
- `cell_size`（可选）：像元大小。

### 返回值

- 返回转换后 `Raster` 对象。

### 示例

```python
converted = arcpy.ia.UnitConversion(dem, "METER", "KILOMETER")
```

## 函数 15：`ColormapToRGB`

### 参数

- `in_raster`：输入单波段色表栅格。
- `colormap`（可选）：色表类型（如 `DEM` / `IMG` / `DEFAULT`）。

### 返回值

- 返回三波段 `Raster` 对象。

### 示例

```python
rgb = arcpy.ia.ColormapToRGB(in_single_band)
rgb.save(out_rgb)
```

## 函数 16：`Grayscale`

### 参数

- `in_raster`：输入多波段栅格。
- `weighted`（可选）：加权系数列表（如 `[0.3, 0.59, 0.11]`）。

### 返回值

- 返回灰度 `Raster` 对象。

## 函数 17：`VectorField`

### 参数

- `in_raster_u`：U 方向栅格。
- `in_raster_v`：V 方向栅格。
- `velocity_method`（可选）：速度计算方式。
- `in_reference_system`（可选）：参考系统。

### 返回值

- 返回向量场 `Raster` 对象（可分解为方向/幅度）。

## 函数 18：`XarrayToRaster` / `RasterToXarray`

### 参数（XarrayToRaster）

- `in_xarray`：`xarray.DataArray` 对象。
- `template_raster`（可选）：模板栅格（用于元数据）。
- `x_coords`（可选）：X 坐标维度名。
- `y_coords`（可选）：Y 坐标维度名。

### 参数（RasterToXarray）

- `in_raster`：输入栅格。

### 返回值

- `XarrayToRaster` 返回新栅格。
- `RasterToXarray` 返回 `xarray.DataArray`。

### 示例

```python
import xarray as xr
xds = arcpy.ia.RasterToXarray(in_raster)
print(xds.attrs)
out_raster = arcpy.ia.XarrayToRaster(xds, template_raster=in_raster)
```

## 类：`PixelBlock`

`PixelBlock` 是 `arcpy.ia` 中的低级影像操作对象，用于直接读取/操作像素块。创建方式：

```python
pbc = arcpy.ia.PixelBlockCollection(rasters)
pixel_block = pbc.read(block_x=0, block_y=0, width=256, height=256)
```

## 类：`Mensuration`

用于测量影像中的对象（高度、面积等）：

```python
mens = arcpy.ia.Mensuration(in_raster)
height = mens.measureHeight(point_a, point_b)
```

## 类：`RasterCollection`

用于批量影像集合管理：

```python
rc = arcpy.ia.RasterCollection(["raster1.tif", "raster2.tif"])
filtered = rc.filterByTime("2023-01-01", "2023-12-31")
```

## 常见错误与排查

- 波段顺序理解错误导致指数计算错误（建议先读 `arcpy.env.rasterStatistics` 确认元数据）。
- 输出未调用 `.save()` 导致结果未持久化（内存释放后丢失）。
- 影像分析环境参数未固定导致跨批次结果不一致。
- 分类前未统一像元大小和投影，导致训练与推理结果偏差。
- `SegMeanShift` 的 `spectral_detail` 设得太高导致过度分割。
- `XarrayToRaster` 时坐标顺序错误导致空间参考错位（N 最后放）。
- `PixelBlock` 操作后未正确写入导致修改未生效。

## 最小可运行骨架

```python
import arcpy
from pathlib import Path

def analyze_imagery(in_multiband: str, out_dir: str) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ndvi = arcpy.ia.NDVI(in_multiband, nir_band=4, red_band=3)
    ndvi.save(str(out_dir / "ndvi.tif"))

    segments = arcpy.ia.SegMeanShift(in_multiband, 15, 10, 100)
    segments.save(str(out_dir / "segments.tif"))

    classified = arcpy.ia.Classify(segments, classifier_def)
    classified.save(str(out_dir / "landcover.tif"))

    ndwi = arcpy.ia.NDWI(in_multiband)
    ndwi.save(str(out_dir / "ndwi.tif"))

    return {"ndvi": str(out_dir / "ndvi.tif"), "classified": str(out_dir / "landcover.tif")}
```