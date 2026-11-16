# Quick-start preparation helpers

[中文](README_zh.md) · [Main tutorial](../../../docs/en/quick_start/op_tool_quick_start.md)

The five command-line Bash helpers only check prerequisites, prepare teaching assets or
edit managed source configuration. They **never generate, build, deploy, detect,
debug or profile an operator**. Keep the tutorial's native commands visible and
execute them yourself. There is no command forwarding or `--force` overwrite mode.

A separate sourced script, `set_chip_soc_env.sh`, configures the chip environment
variable in the current Shell and its future child processes. By default it also
prepares login configuration, with a session-only fallback when persistence is
not permitted. It does not run an operator.

## Requirements and interfaces

Use Bash and Python 3.8+ from the documented CANN environment, with a complete msOT
checkout. The private implementation uses only the Python standard library and
resolves assets relative to the scripts, not the current directory. `bash SCRIPT`
does not require executable permission for the five command-line helpers. Use
`source set_chip_soc_env.sh` for environment setup, so the variable takes effect
in the current Shell. Every script provides `--help`; source the setup script
when requesting its help as well.

Run these examples from this directory, substituting your workspace paths:

```bash
source ./set_chip_soc_env.sh
bash check_env.sh --task core
bash check_env.sh --task mskpp
bash prepare_sample.sh --sample mskpp --dest "$HOME/ot_demo/workspace/mskpp"
bash prepare_sample.sh --sample opgen --dest "$HOME/ot_demo/workspace/src"
bash prepare_add_demo.sh --project "$HOME/ot_demo/workspace/src/AddCustom"
bash prepare_mode.sh --project "$HOME/ot_demo/workspace/src/AddCustom" --mode sanitizer --fixture oob
bash restore_demo.sh --project "$HOME/ot_demo/workspace/src/AddCustom"
bash prepare_mode.sh --project "$HOME/ot_demo/workspace/src/AddCustom" --mode debug
bash restore_demo.sh --project "$HOME/ot_demo/workspace/src/AddCustom"
bash prepare_mode.sh --project "$HOME/ot_demo/workspace/src/AddCustom" --mode profile
bash restore_demo.sh --project "$HOME/ot_demo/workspace/src/AddCustom"
```

The examples illustrate interfaces, **not a replacement end-to-end workflow**.
Generate the project using the tutorial's explicit `msopgen` command before
assembly, and build/deploy/run explicitly between preparation and restoration.
Keep explicit `cd` and `source` operations: the five command-line helpers cannot
change their parent Shell. The environment setup script is sourced specifically
to update the current Shell.

| Entry point | Observable behavior |
| --- | --- |
| `source set_chip_soc_env.sh [--session-only]` | Query `acl.get_soc_name()`, validate the model, remove the `Ascend` prefix and export `MY_STUDY_VAR_CHIP_SOC_TYPE` in the current Shell. By default create or reuse `/etc/profile.d/custom-env.sh`; warn and fall back to session-only setup on permission or read-only filesystem errors. Explicit `--session-only` skips profile access. |
| `check_env.sh --task core` | Check `/.dockerenv`, three environment variables, sample assets and four tool commands. Report all missing items and exit nonzero. Presence does not prove tool execution or device health. |
| `check_env.sh --task mskpp` | Read `npu-smi info -m` with a timeout. Distinguish failed/empty detection from an unsupported chip. Require detected models to be 910B or a numeric 910B suffix; do not broaden the tutorial's hardware support. |
| `prepare_sample.sh` | Copy only `mskpp_demo.py` or `msopgen_demo.json`. Reuse identical files; reject different files. Never execute or generate from them. |
| `prepare_add_demo.sh` | Validate a reviewed AddCustom template, preserve its single Host SoC, install the three teaching source files and four sibling `caller` assets, then save a normal teaching baseline. |
| `prepare_mode.sh` | Add exactly one `npu_op_kernel_options(ascendc_kernels ALL OPTIONS ...)` line. Sanitizer uses `-sanitizer` plus the explicitly selected `oob` source; debug uses `-g -O0`; profile uses `-g` and preserves the original optimization policy. |
| `restore_demo.sh` | Restore only managed Kernel source/CMake, leaving the project in normal mode. Built/deployed artifacts, environment variables, caller output and profiling results are unchanged. |

Return code 0 means this helper's preparation/check succeeded, not a business task
passed. Invalid arguments return 2; conflicts, missing dependencies, damaged state
and write failures return 1. Stop on any failure instead of pasting the next block.

Environment setup requires Python and the `acl` module from CANN, plus any device
permissions needed to query the model. Identical existing profile content is
reused without requiring a write lock. New configuration requires write access
to `/etc/profile.d/`, normally root inside the container. If access is denied or
the filesystem is read-only, `[WARNING]` explains that only the current session
will be configured; this fallback succeeds with exit status 0. Run `source`
again in each new terminal after a fallback or explicit `--session-only` use.
Login Shells must load the profile with the CANN environment available for
persistent setup to take effect. Conflicting content, interrupted state and
other write failures remain errors; preserve and inspect the existing files.
The script does not elevate privileges or delete existing configuration.
Fatal setup failures leave the existing variable unchanged and return to the
calling Shell.

## Supported projects and safety

Source recognition is limited to the reviewed `Ascend/msopgen` snapshot
`9a0f3041f09a`, the published AddCustom JSON and one generated SoC, or a byte-equivalent
teaching implementation (with CRLF/LF and outer whitespace normalized on adoption).
See [template provenance](templates/README.md). Matching a name or `AddConfig` alone
is insufficient; other/edited templates stop without overwriting source.

CANN supplies build scaffolding separately; its Kernel CMake must be nonempty and
free of manually inserted sanitizer/debug flags. The reviewed default conditional
Debug blocks using `add_ops_compile_options` or CANN 9.0.0's
`npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g -O0)` are allowed and preserved.
Only the reviewed complete blocks are recognized, not arbitrary conditional flags.
For profiling, retain Release/default
optimization in your build settings; the helper does not rewrite CMake presets,
cached builds or arbitrary compiler flags. Preparation alone does not establish
device/build-template compatibility; validate in the target CANN environment.

`.msot-demo/` contains checksummed normal teaching baselines, the current mode and
an unfinished-operation journal. Keep it with its project; do not edit or copy it
between projects. Same-mode repeats are no-ops; switching modes requires explicit
restoration. Changes to any managed file stop preparation and restoration, so user
edits are never silently discarded. A legacy `CMakeLists.txt.bak` prevents first
adoption; verify and preserve the old workspace or use a fresh supported project.

Paths containing spaces are supported. Symbolic links/junctions, `..` traversal,
special files and conflicting caller files are rejected. Other caller files and
build outputs are left alone. Ordinary write failures roll back written file
contents; helpers use private temporary files and an exclusive directory lock.
This is not a security sandbox against concurrent external editors.

**After interruption:** a leftover `.msot-prepare.lock`, `.msot-pending.json` or
`.msot-demo/pending.json` intentionally blocks further writes. First confirm no
helper process is running. Preserve the workspace, journal and your edits, inspect
the listed files and baseline, and recover into a fresh supported workspace when
integrity cannot be established. Do not blindly delete records or overwrite a
baseline. Cross-file atomicity across power loss is not guaranteed; a failed
rollback keeps its journal for diagnosis.

**After restoration:** only source files have returned to normal. The installed
operator may still contain the teaching defect or previous mode. Explicitly build
and deploy it using the tutorial before expecting restored runtime behavior.
