# arcpy.mp 模块参数与返回值

## 模块定位

`arcpy.mp` 用于 `.aprx` / `.lyrx` 的本地工程自动化，覆盖工程对象读取、图层数据源修复、布局导出、地图系列输出等任务。

## 高频对象/方法清单

- `ArcGISProject`
- `listMaps` / `listLayouts`
- `updateConnectionProperties`
- `export`
- `save`
- `saveACopy`

## 对象 1：`ArcGISProject(path_or_CURRENT)`

### 参数

- `path_or_CURRENT`：工程路径或 `"CURRENT"`。

### 返回值

- 返回 `ArcGISProject` 对象。

### 示例

```python
aprx = arcpy.mp.ArcGISProject(r"D:\projects\city.aprx")
```

## 方法：`updateConnectionProperties`

### 参数

- `current_connection_info`：旧连接信息。
- `new_connection_info`：新连接信息。
- `validate`（可选）：是否校验目标连接。
- `auto_update_joins_and_relates`（可选）：是否同步更新连接关系。
- `ignore_case`（可选）：路径大小写匹配策略。

### 返回值

- 返回更新结果（不同对象/版本实现可能存在差异，脚本中建议以异常与后续对象状态校验为准）。

### 示例

```python
changed = aprx.updateConnectionProperties(old_gdb, new_gdb, validate=True)
```

## 方法：`export`（布局/地图视图对象）

### 参数

- 导出格式对象（如 PDF）。
- 输出路径与格式参数（分辨率、页范围等）。
- 具体参数取决于导出对象（如 PDF/PNG/JPEG）。

### 返回值

- 通常返回 `None`，输出文件写入磁盘。

### 示例

```python
pdf = arcpy.mp.CreateExportFormat("PDF", out_pdf)
layout.export(pdf)
```

## 方法：`listMaps` / `listLayouts`

### 参数

- `wildcard`（可选）：名称通配过滤。

### 返回值

- 返回对象列表（`Map` / `Layout`）。

## 方法：`save` / `saveACopy`

### 参数

- `save()`：无参数，覆盖当前工程文件。
- `saveACopy(file_name)`：另存副本路径。

### 返回值

- 通常返回 `None`。

## 常见错误与排查

- 在离线脚本中误用 `CURRENT`。
- 修改后忘记 `save()`。
- 导出路径不存在。
- 批量 `listLayouts()[0]` 直接取首项，未校验空列表。
