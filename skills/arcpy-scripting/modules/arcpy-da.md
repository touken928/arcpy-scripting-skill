# arcpy.da 模块参数与返回值

## 模块定位

`arcpy.da` 是 ArcPy 的高性能数据访问层，核心用于游标读写、编辑会话、结构描述以及与 NumPy/Arrow 的高效数据互转。

## 高频对象/函数清单

- `SearchCursor`
- `UpdateCursor`
- `InsertCursor`
- `Describe`
- `TableToNumPyArray`
- `FeatureClassToNumPyArray`

## 对象 1：`SearchCursor`

### 参数

- `in_table`：输入表/要素类。
- `field_names`：字段列表（建议最小字段集）。
- `where_clause`（可选）：过滤条件。
- `sql_clause`（可选）：排序/分组等 SQL 子句。
- `spatial_filter`（可选）：空间过滤对象（版本相关能力，使用前请确认本机 ArcGIS Pro 版本）。

### 返回值

- 返回可迭代游标对象。
- 每次迭代返回一行元组（字段顺序与 `field_names` 一致）。
- 常用 token：`OID@`、`SHAPE@`、`SHAPE@XY`、`SHAPE@AREA`。

### 示例

```python
with arcpy.da.SearchCursor(fc, ["OID@", "NAME"], "NAME IS NOT NULL") as rows:
    for oid, name in rows:
        pass
```

## 对象 2：`UpdateCursor`

### 参数

- 与 `SearchCursor` 基本一致。
- `explicit`（可选）：显式空值策略。

### 返回值

- 返回可写游标对象。
- 通过 `updateRow`/`deleteRow` 写回。

### 示例

```python
with arcpy.da.UpdateCursor(fc, ["STATUS"], "STATUS IS NULL") as rows:
    for row in rows:
        row[0] = "NEW"
        rows.updateRow(row)
```

## 对象 3：`InsertCursor`

### 参数

- `in_table`：目标表/要素类。
- `field_names`：插入字段顺序。
- `datum_transformation`（可选）：坐标转换。

### 返回值

- 返回可插入游标对象。
- `insertRow` 执行插入；返回值形态与数据源有关（脚本中建议仅依赖“插入成功”语义）。

### 示例

```python
with arcpy.da.InsertCursor(fc, ["NAME", "SHAPE@XY"]) as rows:
    oid = rows.insertRow(["A-01", (120.1, 30.2)])
```

## 函数：`arcpy.da.Describe`

### 参数

- `dataset`：目标数据集。

### 返回值

- 返回字典。
- 常用键：`dataType`、`shapeType`、`spatialReference`、`fields`。
- 可用键随数据类型动态变化（读取前建议先判定 `dataType`）。

## 函数：`TableToNumPyArray` / `FeatureClassToNumPyArray`

### 参数

- `in_table` / `in_feature_class`：输入数据集。
- `field_names`：字段列表。
- `where_clause`（可选）：筛选条件。
- `skip_nulls`（可选）：空值跳过策略。
- `null_value`（可选）：空值替代值。

### 返回值

- 返回 NumPy 结构化数组（`numpy.ndarray`）。
- 字段名与 dtypes 由输入字段和参数决定。

## 常见错误与排查

- 未用 `with` 管理游标导致锁释放不及时。
- 字段顺序与 row 索引不一致导致写错字段。
- 盲目使用 `*` 导致性能下降和语义不清。
- 更新游标中同时修改几何和属性但未控制事务，导致部分写入。
- 在 enterprise geodatabase 环境中忽略编辑会话要求，写入失败。
