"""Project-local teaching state and reviewed AddCustom source assembly.

Copyright (c) 2026 Huawei Technologies Co., Ltd.
Licensed under Mulan PSL v2. See the repository LICENSE.
"""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

from _files import PreparationError, apply_changes, check_copy, directory_lock, read_file, safe_path


EXAMPLES = Path(__file__).resolve().parent.parent
TEMPLATES = Path(__file__).resolve().parent / "templates"
SOURCE_TEMPLATES = {
    "op_host/add_custom.cpp": "add_custom.cpp.in",
    "op_kernel/add_custom.cpp": "kernel.cpp.in",
    "op_kernel/add_custom_tiling.h": "add_custom_tiling.h.in",
}
CMAKE = "op_kernel/CMakeLists.txt"
MANAGED = (*SOURCE_TEMPLATES, CMAKE)
CALLER_FILES = ("CMakeLists.txt", "exec.py", "main.cpp", "run.sh")
OPTIONS = {"sanitizer": "-sanitizer", "debug": "-g -O0", "profile": "-g"}
SOC_NAME_PATTERN = r"ascend[a-z0-9][a-z0-9_-]*"
SOC = re.compile(r'\.AddConfig\("(' + SOC_NAME_PATTERN + r')"\)')


def digest(content):
    return hashlib.sha256(content).hexdigest()


def text(content):
    return content.decode("utf-8").replace("\r\n", "\n")


def canonical(content):
    return text(content).strip()


def extract_soc(host):
    values = SOC.findall(text(host))
    # Reject unrecognized or multiple calls, rather than silently dropping targets.
    if len(values) != 1 or text(host).count("AddConfig") != 1:
        raise PreparationError("Expected exactly one generated .AddConfig(\"ascend...\") SoC")
    return values[0]


def normal_sources(soc):
    result = {relative: text(read_file(EXAMPLES / "msopgen/code" / relative)).encode("utf-8")
              for relative in SOURCE_TEMPLATES}
    result["op_host/add_custom.cpp"] = SOC.sub(
        lambda _: '.AddConfig("{}")'.format(soc), text(result["op_host/add_custom.cpp"])).encode("utf-8")
    if extract_soc(result["op_host/add_custom.cpp"]) != soc:
        raise PreparationError("Teaching Host source failed SoC preservation")
    return result


def project_path(value):
    project = safe_path(value)
    if not project.is_dir():
        raise PreparationError("Project directory is missing: " + str(project))
    for relative in (*MANAGED, "build.sh", "CMakeLists.txt", "CMakePresets.json", "op_host/CMakeLists.txt"):
        read_file(project / relative)
    return project


def check_clean_cmake(content):
    # Default conditional Debug configurations are left intact. Only these reviewed
    # blocks may contain -g/-O0; unconditional/manual flags are not a trusted baseline.
    cmake = text(content)
    default_debug_blocks = (
        'if ("${CMAKE_BUILD_TYPE}x" STREQUAL "Debugx")\n'
        '    add_ops_compile_options(ALL OPTIONS -g -O0 --cce-ignore-always-inline=true)\n'
        'endif()',
        'if ("${CMAKE_BUILD_TYPE}x" STREQUAL "Debugx")\n'
        '    npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g -O0)\n'
        'endif()',
    )
    for block in default_debug_blocks:
        cmake = cmake.replace(block, "")
    uncommented = "\n".join(line.split("#", 1)[0] for line in cmake.splitlines())
    if not content.strip() or re.search(r"(?<![\w-])-(?:g\b|O0\b|sanitizer\b)", uncommented):
        raise PreparationError("Unmanaged compilation flags; restore a verified clean teaching CMake first")


def expected_files(normal, mode):
    result = dict(normal)
    if mode != "normal":
        result[CMAKE] = ("npu_op_kernel_options(ascendc_kernels ALL OPTIONS {})\n".format(OPTIONS[mode])
                         .encode("utf-8") + normal[CMAKE])
        if mode == "sanitizer":
            result["op_kernel/add_custom.cpp"] = text(read_file(
                EXAMPLES / "mssanitizer/bug_code/add_custom.cpp")).encode("utf-8")
    return result


def make_state(soc, mode, normal, current):
    return {"format": 1, "soc": soc, "mode": mode,
            "baseline": {name: digest(data) for name, data in normal.items()},
            "current": {name: digest(data) for name, data in current.items()}}


def state_bytes(state):
    return (json.dumps(state, sort_keys=True, indent=2) + "\n").encode("utf-8")


def load_state(project):
    directory = safe_path(project / ".msot-demo")
    if (directory / "pending.json").exists():
        raise PreparationError("Unfinished transaction; inspect .msot-demo/pending.json and managed files")
    try:
        state = json.loads(read_file(directory / "state.json"))
    except (ValueError, PreparationError) as error:
        raise PreparationError("Missing or damaged .msot-demo state; do not guess or overwrite a baseline") from error
    if (not isinstance(state, dict) or set(state) != {"format", "soc", "mode", "baseline", "current"}
            or type(state["format"]) is not int or state["format"] != 1
            or not isinstance(state["soc"], str) or not re.fullmatch(SOC_NAME_PATTERN, state["soc"])
            or not isinstance(state["mode"], str) or state["mode"] not in ("normal", *OPTIONS)):
        raise PreparationError("Unrecognized .msot-demo state schema")
    for field in ("baseline", "current"):
        values = state[field]
        if (not isinstance(values, dict) or set(values) != set(MANAGED)
                or any(not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{64}", value)
                       for value in values.values())):
            raise PreparationError("Unrecognized managed file names or hashes in state")
    normal = {name: read_file(directory / "baseline" / name) for name in MANAGED}
    check_clean_cmake(normal[CMAKE])
    teaching = normal_sources(state["soc"])
    if any(normal[name] != teaching[name] for name in SOURCE_TEMPLATES):
        raise PreparationError("Teaching baseline content is damaged or belongs to another helper version")
    current = expected_files(normal, state["mode"])
    if state != make_state(state["soc"], state["mode"], normal, current):
        raise PreparationError("State/baseline checksums do not match; refusing restoration")
    for name, data in current.items():
        if read_file(project / name) != data:
            raise PreparationError("Managed file conflict (user edits or damaged state); preserve your edits: " + name)
    return state, normal


def prepare_add_demo(value):
    project = project_path(value)
    caller = safe_path(project.parent / "caller")
    if caller == project:
        raise PreparationError("The project must not also be the sibling caller directory")
    with directory_lock(project):
        directory = safe_path(project / ".msot-demo")
        changes = {}
        if directory.exists():
            state, normal = load_state(project)
            if state["mode"] != "normal":
                raise PreparationError("Restore the active mode before preparing teaching sources again")
        else:
            if safe_path(project / (CMAKE + ".bak")).exists():
                raise PreparationError("A legacy .bak exists; verify and restore the old tutorial or use a fresh project")
            original = {name: read_file(project / name) for name in MANAGED}
            soc = extract_soc(original["op_host/add_custom.cpp"])
            normal = normal_sources(soc)
            generated = {name: read_file(TEMPLATES / template).replace(b"__SOC__", soc.encode("ascii"))
                         for name, template in SOURCE_TEMPLATES.items()}
            is_generated = all(canonical(original[name]) == canonical(generated[name]) for name in SOURCE_TEMPLATES)
            is_teaching = all(canonical(original[name]) == canonical(normal[name]) for name in SOURCE_TEMPLATES)
            if not (is_generated or is_teaching):
                raise PreparationError("Unknown/edited AddCustom template; no sources overwritten. Use a fresh supported project")
            check_clean_cmake(original[CMAKE])
            normal[CMAKE] = original[CMAKE]
            state = make_state(soc, "normal", normal, normal)
            changes.update({project / name: data for name, data in normal.items()})
            changes.update({directory / "baseline" / name: data for name, data in normal.items()})
            changes[directory / "state.json"] = state_bytes(state)
        caller_data = {caller / name: read_file(EXAMPLES / "msopgen/caller" / name) for name in CALLER_FILES}
        for name, data in caller_data.items():
            check_copy(name, data)
        with directory_lock(caller):
            if safe_path(caller / ".msot-pending.json").exists():
                raise PreparationError("Unfinished caller transaction")
            for name, data in caller_data.items():
                check_copy(name, data)
            changes.update(caller_data)
            apply_changes(changes, directory / "pending.json")
    messages = (
        "Teaching implementation prepared; preserved SoC: " + state["soc"],
        "Prepare sample script successful.",
        "The project path is: {}".format(project),
        "The caller path is: {}".format(caller),
    )
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for message in messages:
        print("{} [INFO] {}".format(timestamp, message))


def prepare_mode(value, mode, fixture=None):
    if mode not in OPTIONS:
        raise PreparationError("Unknown teaching mode: " + str(mode))
    if (mode == "sanitizer" and fixture != "oob") or (mode != "sanitizer" and fixture is not None):
        raise PreparationError("Only sanitizer accepts (and requires) the explicit --fixture oob")
    project = project_path(value)
    with directory_lock(project):
        state, normal = load_state(project)
        if state["mode"] not in ("normal", mode):
            raise PreparationError("Restore the active {} mode before selecting {}".format(state["mode"], mode))
        current = expected_files(normal, mode)
        changes = {project / name: current[name] for name in (CMAKE, "op_kernel/add_custom.cpp")}
        changes[project / ".msot-demo/state.json"] = state_bytes(make_state(state["soc"], mode, normal, current))
        apply_changes(changes, project / ".msot-demo/pending.json")
    messages = ["Successfully prepared {} mode: {} -> {}".format(mode, CMAKE, OPTIONS[mode])]
    if fixture:
        messages.append("Teaching fixture oob -> op_kernel/add_custom.cpp: DataCopy reads twice the tile length.")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for message in messages:
        print("{} [INFO] {}".format(timestamp, message))


def restore_demo(value):
    project = project_path(value)
    with directory_lock(project):
        state, normal = load_state(project)
        changes = {project / name: normal[name] for name in (CMAKE, "op_kernel/add_custom.cpp")}
        changes[project / ".msot-demo/state.json"] = state_bytes(make_state(state["soc"], "normal", normal, normal))
        apply_changes(changes, project / ".msot-demo/pending.json")
    messages = (
        "Successfully restored source files: {}, op_kernel/add_custom.cpp.".format(CMAKE),
        "Note: The deployed build artifacts have not been restored. "
        "To restore them, please re-run the build and deployment process.",
    )
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for message in messages:
        print("{} [INFO] {}".format(timestamp, message))
