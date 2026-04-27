# arcpy.mp 模块参数与返回值

## 模块定位

`arcpy.mp` 用于 `.aprx` / `.lyrx` 的本地工程自动化，覆盖工程对象读取、图层数据源修复、布局导出、地图系列输出等任务。所有方法均针对离线脚本设计（除非明确标注需要 `CURRENT`）。

## 高频对象/方法清单

- `ArcGISProject`（构造/属性/方法）
- `Map`、`MapView`
- `Layer`、`LayerFile`
- `Layout`
- `MapFrame`、`MapSeries`
- `listMaps`、`listLayouts`、`listLayers`
- `updateConnectionProperties`
- `exportToPDF`、`exportToPNG`、`exportToAIX`
- `createExportFormat` / `CreateExportOptions`
- `save`、`saveACopy`

## 函数：`ArcGISProject(path_or_CURRENT)`

### 参数

- `path_or_CURRENT`：工程文件路径（绝对路径）或字符串 `"CURRENT"`（仅在 ArcGIS Pro 内运行时有效）。

### 返回值

- 返回 `ArcGISProject` 对象。

### 示例

```python
# 离线脚本
aprx = arcpy.mp.ArcGISProject(r"D:\projects\city.aprx")

# ArcGIS Pro 内运行
aprx = arcpy.mp.ArcGISProject("CURRENT")
```

## 属性/方法：ArcGISProject

### 重要属性

| 属性 | 说明 | 读写 |
|------|------|------|
| `filePath` | 工程文件完整路径（只读） | 只读 |
| `defaultGeodatabase` | 默认地理数据库路径 | 读写 |
| `defaultToolbox` | 默认工具箱路径 | 读写 |
| `homeFolder` | 工程主文件夹 | 读写 |
| `dateSaved` | 上次保存时间（datetime） | 只读 |
| `documentVersion` | 文档版本字符串 | 只读 |
| `isReadOnly` | 是否只读 | 只读 |
| `activeMap` | 活动地图（仅内部运行） | 只读 |
| `activeView` | 活动视图（Layout 或 MapView，仅内部运行） | 只读 |
| `databases` | 数据库连接信息字典列表 | 只读 |
| `folderConnections` | 文件夹连接信息字典列表 | 只读 |

### 重要方法

- `listMaps(wildcard)`：返回 `Map` 对象列表。
- `listLayouts(wildcard)`：返回 `Layout` 对象列表。
- `listReports(wildcard)`：返回 `Report` 对象列表。
- `createMap(name, {map_type})`：创建新地图。
- `createLayout(page_width, page_height, page_units, {name})`：创建新布局。
- `createReport(map, report_name, {report_layout})`：创建报表。
- `importDocument(doc_path, {option})`：导入 `.mxd`、`.3dd`、`.sxd`、`.mapx`、`.pagx`、`.rptx`。
- `updateFolderConnections(connections)`：批量更新文件夹连接。
- `updateDatabases(connections)`：批量更新数据库连接。
- `copyItem(item, destination)`：复制工程项目。
- `deleteItem(item)`：删除工程项目。
- `save()`：保存工程（需非只读）。
- `saveACopy(file_name)`：另存副本。
- `closeViews(view_type)`：关闭视图（仅内部运行）。

### 示例

```python
aprx = arcpy.mp.ArcGISProject(project_path)
aprx.defaultGeodatabase = r"D:\data\work.gdb"
m = aprx.createMap("分析地图")
layout = aprx.createLayout(8.5, 11, "INCH", "输出布局")
aprx.save()
```

## 对象：`Map`

### 重要方法

- `listLayers(wildcard, {wildcard})`：返回图层列表。
- `listTables(wildcard)`：返回表列表。
- `addLayer(layer, {add_position})`：添加图层（`TOP` / `BOTTOM`）。
- `addDataFromPath(data_path)`：从路径添加数据。
- `removeLayer(layer)`：移除图层。
- `moveLayer(target_layer, add_position, layer)`：移动图层位置。

### 属性

- `name`：地图名称。
- `mapSeries`：关联的地图系列（如有）。
- `description`：地图描述。

## 对象：`MapView`

用于控制地图视图的显示范围和相机：

- `camera`：返回 `Camera` 对象（用于设置视角）。
- `zoomToAllLayers()`：缩放至所有图层范围。
- `zoomToExtent(extent)`：缩放至指定范围。
- `panToExtent(extent)`：平移至指定范围。
- `isActiveView`：是否为活动视图（只读）。

## 对象：`Layer` / `LayerFile`

### 创建方式

```python
# 从 .lyrx 文件
lyrx = arcpy.mp.LayerFile(r"D:\layers\roads.lyrx")

# 从 Map 中获取
lyr = m.listLayers("roads*")[0]
```

### 重要方法（Layer）

- `replaceDataSource(target_table, workspace_type, {validate})`：替换数据源。
- `updateConnectionProperties(current, new, {auto_join})`：更新连接。
- `findAndReplaceWorkspacePath(old_path, new_path, {validate})`：更新工作空间路径。
- `isBroken`：属性，返回图层数据源是否断裂。
- `longName`：完整图层名（含组）。
- `shortName`：简短图层名。
- `visible`：是否可见。

### 重要方法（LayerFile）

- `save()`：保存修改后的图层文件。
- `mapName`：关联的地图名。

## 对象：`Layout`

### 重要属性

- `name`：布局名称。
- `pageWidth` / `pageHeight`：页面尺寸。
- `pageUnits`：`CENTIMETER` / `INCH` / `MILLIMETER` / `POINT`。
- `colorModel`：`CMYK` / `RGB`。
- `mapSeries`：地图系列（如启用）。

### 重要方法

- `listElements({element_type}, {wildcard})`：返回布局元素列表。
- `createMapFrame(geometry, {map}, {name})`：创建地图框。
- `createMapSurroundElement(geometry, surround_type, {mapframe}, {style_item}, {name})`：创建地图周围元素（如指北针、比例尺）。
- `createTableFrameElement(geometry, {mapframe}, {table}, {fields}, {style_item}, {name})`：创建表格框架。
- `deleteElement(element)`：删除元素。
- `changePageSize(page_width, page_height, {resize_elements})`：更改页面大小。

### 导出方法

- `exportToPDF(out_path, {options})`
- `exportToPNG(out_path, {options})`
- `exportToBMP(out_path, {options})`
- `exportToEMF(out_path, {options})`
- `exportToEPS(out_path, {options})`
- `exportToGIF(out_path, {options})`
- `exportToJPEG(out_path, {options})`
- `exportToSVG(out_path, {options})`
- `exportToTIFF(out_path, {options})`

### 导出选项（CreateExportFormat / CreateExportOptions）

```python
pdf_format = arcpy.mp.CreateExportFormat("PDF", out_pdf)
pdf_format.resolution = 300
pdf_format.compressVectorGraphics = True
layout.export(pdf_format)
```

## 对象：`MapFrame`

- `camera`：返回 `Camera` 对象，可设置 `latitude`、`longitude`、`scale`、`heading`、`pitch`、`roll`。
- `zoomToAllLayers()`：缩放至所有图层。
- `panToExtent(extent)`：平移。
- `getLayerVisibility()`：获取图层可见性。
- `setLayerVisibility(layers, visibility)`：设置图层可见性。

## 对象：`MapSeries`

- `enabled`：是否启用。
- `currentIndex`：当前索引。
- `pageCount`：总页数。
- `startPage`：起始页。
- `nextPage()`：下一页。
- `previousPage()`：上一页。
- `firstPage()`：首页。
- `lastPage()`：末页。
- `goToPage(page_number)`：跳转到指定页。

### BookmarkMapSeries

```python
bms = layout.createBookmarkMapSeries(mapframe, bookmarks=["A区", "B区"])
for bm in bms.bookmarks:
    print(bm.name)
```

## 对象：`GraphicElement` / `TextElement` / `PictureElement`

### 通用属性

- `name`：元素名称。
- `visible`：可见性。
- `elementPositionX` / `elementPositionY`：位置。
- `elementWidth` / `elementHeight`：尺寸。
- `rotation`：旋转角度。

### TextElement 特有

- `text`：文本内容。
- `fontSize`：字号。
- `fontWeight`：字重。
- `fontStyle`：样式。
- `textColor`：颜色。
- `horizontalAlignment`：`LEFT` / `CENTER` / `RIGHT`。

### PictureElement 特有

- `sourceImage`：图片路径。
- `linked`：是否链接（而非嵌入）。

## 数据源修复模式

### 模式 1：按路径替换

```python
aprx = arcpy.mp.ArcGISProject(project_path)
for m in aprx.listMaps():
    for lyr in m.listLayers():
        if lyr.isBroken:
            old_ds = lyr.connectionProperties.get("workspaceFactory", "")
            if old_ds.startswith("Database"):
                lyr.findAndReplaceWorkspacePath(old_path, new_path, validate=True)
```

### 模式 2：按连接信息字典

```python
new_conn = {"database": new_gdb_path}
for m in aprx.listMaps():
    for lyr in m.listLayers():
        lyr.updateConnectionProperties(old_gdb_path, new_conn, auto_join=True)
```

### 模式 3：高级参数

```python
changed = aprx.updateConnectionProperties(
    {"workspaceFactory": "FileGDB", "workspace": old_gdb},
    {"workspaceFactory": "FileGDB", "workspace": new_gdb},
    validate=True,
    auto_update_joins_and_relates=True,
    ignore_case=True
)
```

## 地图系列导出

```python
layout = aprx.listLayouts("输出地图")[0]
ms = layout.mapSeries
if ms and ms.enabled:
    pdf_options = arcpy.mp.CreateExportFormat("PDF", output_pdf)
    pdf_options.resolution = 300
    ms.exportToPDF(pdf_options, "CURRENT")
```

## 常见错误与排查

- 在离线脚本中误用 `CURRENT`（返回 `None`）。
- 修改后忘记 `save()`。
- 导出路径所在目录不存在。
- 批量 `listLayouts()[0]` 直接取首项，未校验空列表。
- 替换数据源时路径格式不匹配（`\\` vs `/`）。
- `updateConnectionProperties` 的字典 key 与实际不匹配（检查 `connectionProperties` 属性先）。
- 布局元素 `name` 不唯一导致误操作。
- `MapFrame.camera` 设置后未重新导入视图。
- 企业级数据库工作空间连接信息包含额外认证字段，更新时需包含完整连接属性。

## 最小可运行骨架

```python
import arcpy
from pathlib import Path

def export_maps(aprx_path: str, out_dir: str) -> list[str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_files = []

    aprx = arcpy.mp.ArcGISProject(aprx_path)
    for layout in aprx.listLayouts():
        pdf_path = out_dir / f"{layout.name}.pdf"
        pdf_format = arcpy.mp.CreateExportFormat("PDF", str(pdf_path))
        pdf_format.resolution = 300
        layout.export(pdf_format)
        output_files.append(str(pdf_path))

    aprx.save()
    return output_files

def repair_datasources(aprx_path: str, old_gdb: str, new_gdb: str) -> int:
    aprx = arcpy.mp.ArcGISProject(aprx_path)
    count = 0
    for m in aprx.listMaps():
        for lyr in m.listLayers():
            if lyr.isBroken:
                lyr.findAndReplaceWorkspacePath(old_gdb, new_gdb, validate=True)
                count += 1
    aprx.save()
    return count
```