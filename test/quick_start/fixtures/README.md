# CANN build-scaffold regression fixtures

`cann_9_0_0_kernel.CMakeLists.txt` is the unmodified Kernel CMake file from
an AddCustom project generated with the CANN 9.0.0 aarch64 installation:

```bash
msopgen gen -i msopgen_demo.json -c ai_core-ascend910B2 -lan cpp -out AddCustom
```

The input is `example/quick_start/msopgen/msopgen_demo.json`. The default
`CMakePresets.json` uses `Release`; the fixture's `-g -O0` options apply only to
`Debug`. Keep the complete reviewed conditional block and verify that preparation,
all three modes and restoration preserve the original CMake bytes. Extra manual
flags or edited conditional blocks must still be rejected.
