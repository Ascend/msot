# Reviewed generated source templates

These files are **recognition data**, not an alternate project generator.
`__SOC__` is replaced only for comparison with a generated Host file.

Provenance: `Ascend/msopgen` commit `9a0f3041f09a`, input
`example/quick_start/msopgen/msopgen_demo.json`, language `cpp`, one `ai_core` SoC.

- Host: `OpFileAiCore._generate_cpp_opdef`, `OPTmpl.OP_HOST_*`.
- Kernel: `OpFileAiCore._generate_cpp_impl`.
- Tiling header: `OpFileAiCore._generate_cpp_tiling`, `OPTmpl.OP_HOST_TILING_DEF_H`.

Only outer whitespace and CRLF/LF are normalized during recognition. All other
content must match; an arbitrary `AddConfig` or `TODO` is not proof of an unedited
generated file. Older/other templates require separate review and regression
fixtures before support is added. No installed generator is executed by a helper.

CANN supplies the build scaffolding separately; these source snapshots do not
claim compatibility with every CANN build-template version.
