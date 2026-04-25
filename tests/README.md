# ArcPy Tests

本目录包含两类测试：

- `tests/high-frequency`：校验 `skills/arcpy-scripting/modules/high-frequency` 的 8 个模块文档对应能力。
- `tests/example`：执行 `skills/arcpy-scripting/examples` 中的示例脚本，并验证输出结果正确。

## 设计约束

- high-frequency 采用“一模块一测试文件”，不合并到单个大测试。
- example 测试通过子进程运行脚本，验证脚本可独立执行。
- 默认不依赖任何 `ARCPY_*` 环境变量。
- `arcpy.sa`、`arcpy.ia` 走免许可可运行校验，不做许可验证。
- `arcpy.mp` 优先尝试自动创建临时 `.aprx`，不可用时回退免依赖校验。

## 环境准备

在 ArcGIS Pro Python 环境中执行：

```bat
cmd /k "C:\Program Files\ArcGIS\Pro\bin\Python\Scripts\proenv.bat"
conda create --clone arcgispro-py3 -n arcpy_test
proswap arcpy_test
conda install pytest numpy -y
```

## 运行命令

- 运行 high-frequency：

```bat
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\propy.bat" -m pytest tests/high-frequency -q
```

- 运行 examples 可执行性校验：

```bat
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\propy.bat" -m pytest tests/example -q
```

- 运行全部测试：

```bat
"%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\propy.bat" -m pytest tests -q
```
