# 快速开始辅助脚本

[English](README.md) · [主线教程](../../../docs/zh/quick_start/op_tool_quick_start.md)

五个 Bash 入口只检查前置条件、准备教学资产或修改受管理的源码配置，**不会生成、构建、部署、检测、调试或采集算子**。请在正文中保留原生工具及参数，并自行显式执行。不支持参数透传或 `--force` 强制覆盖。

另提供需通过 `source` 加载的 `set_chip_soc_env.sh`，设置当前 Shell 及其后续子进程的芯片环境变量，默认准备登录配置，无权限持久化时自动降级为单 session，不运行算子。

## 环境与接口

使用文档规定的 CANN 环境中的 Bash、Python 3.8+，以及完整的 msOT 仓库。私有实现只依赖 Python 标准库，按脚本位置定位样例，不依赖当前工作目录。五个命令行入口通过 `bash SCRIPT` 调用，无需增加可执行权限；环境设置脚本必须使用 `source set_chip_soc_env.sh`，才能修改当前 Shell 的变量。每个入口均支持 `--help`，环境设置脚本的帮助也需通过 `source` 调用。

下列示例在本目录执行，请替换工作区路径：

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

以上只是接口示意，**不是替代主线的一键流程**。装配前先显式使用教程中的 `msopgen` 命令生成工程；准备和恢复之间的构建、部署、执行仍须手工调用原始入口。`cd`、`source` 也继续显式保留，五个命令行辅助子进程不能修改父 Shell 的目录或环境，环境设置脚本通过 `source` 在当前 Shell 中执行。

| 入口 | 可观察的行为 |
| --- | --- |
| `source set_chip_soc_env.sh [--session-only]` | 通过 `acl.get_soc_name()` 查询并校验型号，移除 `Ascend` 前缀，在当前 Shell 导出 `MY_STUDY_VAR_CHIP_SOC_TYPE`。默认创建或复用 `/etc/profile.d/custom-env.sh`；权限不足或文件系统只读时输出警告，退回单 session。显式 `--session-only` 跳过配置文件访问。 |
| `check_env.sh --task core` | 检查 `/.dockerenv`、三项环境变量、样例文件及四个工具入口；汇总全部缺失项，失败非零。命令存在不代表业务通过或设备健康。 |
| `check_env.sh --task mskpp` | 带超时只读执行 `npu-smi info -m`，区分探测失败/空结果与芯片不支持；要求探测型号为 910B 或带数字后缀的 910B，不扩大教程的支持承诺。 |
| `prepare_sample.sh` | 仅复制 `mskpp_demo.py` 或 `msopgen_demo.json`；相同内容复用，不同内容拒绝覆盖，不运行样例或生成工程。 |
| `prepare_add_demo.sh` | 校验已审查的 AddCustom 模板，保留 Host 中单一 SoC，装配三份教学源码及相邻 `caller` 的四个样例文件，保存正常教学基线。 |
| `prepare_mode.sh` | 插入一份 `npu_op_kernel_options(ascendc_kernels ALL OPTIONS ...)`：sanitizer 为 `-sanitizer` 并显式选择 `oob` 源码；debug 为 `-g -O0`；profile 为 `-g`，保留原优化策略。 |
| `restore_demo.sh` | 仅恢复受管理的 Kernel 源码和 CMake，回到正常模式；不修改构建/部署产物、环境变量、caller 输出或采集结果。 |

退出码 0 仅表示本次检查/准备成功；非法参数返回 2；缺依赖、文件冲突、状态损坏和写入失败返回 1。任何失败都应先处理，不能继续粘贴下一代码块。

环境设置依赖 Python、CANN 的 `acl` 模块及型号查询所需的设备权限。已有相同内容配置无需创建写锁即可复用；新建配置需要 `/etc/profile.d/` 写权限，通常由容器内 root 用户执行。权限不足或文件系统只读时输出 `[WARNING]` 并自动降级为当前 session，返回码为 `0`；自动降级或显式 `--session-only` 后，每个新终端需重新 `source`。持久化需由登录 Shell 在 CANN 环境可用时加载配置。内容冲突、未完成状态及其他写入失败仍报错，请保留并核查已有文件。脚本不会自动提权或删除配置；不可恢复的设置失败会保留原变量值并返回调用方 Shell。

## 模板范围与安全约定

生成源码识别仅覆盖已审查的 `Ascend/msopgen` 快照 `9a0f3041f09a`、本仓发布的 AddCustom JSON 和单一生成 SoC，或内容一致的正常教学实现。首次接管只归一化 CRLF/LF 与文件首尾空白，详见[模板来源](templates/README.md)。文件名、`AddConfig` 或 `TODO` 不是未修改模板的充分证据；未知版本、不同模板或用户源码会停止，不做宽松匹配覆盖。

构建骨架由 CANN 另行提供；Kernel CMake 必须非空，且没有手工插入的检测/调试选项。允许并原样保留已审查的默认条件 Debug 配置块，包括使用 `add_ops_compile_options` 的版本和 CANN 9.0.0 中使用 `npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g -O0)` 的版本；仅识别已审查的完整配置块，不放行任意条件中的编译选项。调优时请保留工程的 Release/默认优化设置；脚本不改 CMakePresets、构建缓存或任意编译标志。完成辅助准备不等于 CANN 构建模板或设备兼容性验收，仍需在目标 CANN 环境验证。

`.msot-demo/` 保存正常教学文件、校验值、活动模式和未完成操作记录。请与所属工程一起保留，不要手改或跨工程复制。相同模式重复准备无额外变更，切换模式前必须显式恢复。任一受管理文件被修改后，准备与恢复均会停止，以保护用户编辑。首次接管遇到旧教程的 `CMakeLists.txt.bak` 时拒绝推断基线；请核实并保留旧工作区，或重新使用受支持的干净工程。

路径可含空格；拒绝符号链接/junction、`..` 路径穿越、特殊文件及不同内容的 caller 文件。其他 caller 文件和构建结果不删除。普通写入失败会回滚本次已写文件的内容；使用私有临时文件和排他目录锁，但不作为对抗外部并发编辑者的安全沙箱。

**中断之后：**遗留的 `.msot-prepare.lock`、`.msot-pending.json` 或 `.msot-demo/pending.json` 会阻止继续写入。先确认没有辅助进程运行，保留工作区、记录和自己的编辑，检查记录列出的文件及基线。无法确认完整性时，应在新的受支持工作区重新准备，不要直接删除记录或覆盖基线。断电时不保证跨文件原子性；回滚失败也会保留事务记录供排查。

**恢复之后：**只保证源文件回到正常教学状态，已安装算子可能仍含教学缺陷或前一模式。要让实际执行行为恢复，仍需按教程显式重新构建和部署。
