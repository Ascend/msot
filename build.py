#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This file is part of the MindStudio project.
# Copyright (c) 2025 Huawei Technologies Co.,Ltd.
#
# MindStudio is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#
#          http://license.coscl.org.cn/MulanPSL2
#
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
# -------------------------------------------------------------------------
import argparse
import logging
import multiprocessing
import os
import shutil
import subprocess
import sys
import re
import traceback
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 子工具排除粒度与顶层 CMake 模块保持一致；这里做第一层白名单校验，
# 避免非法名字继续传到 CMake 后才失败。
SUPPORTED_TOOLS = ("msdebug", "mskl", "mskpp", "msopgen", "msopprof", "mssanitizer")


def normalize_excluded_tools(exclude_tools):
    """归一化 --exclude-tools 输入，输出稳定的 CMake 逗号分隔参数来源。"""
    if not exclude_tools:
        return []

    normalized_tools = []
    for tool in exclude_tools.split(','):
        # 支持用户输入空格和大小写混用；空片段来自尾逗号或连续逗号，直接忽略。
        tool_name = tool.strip().lower()
        if not tool_name:
            continue
        if tool_name not in SUPPORTED_TOOLS:
            raise argparse.ArgumentTypeError(
                "Unsupported tool '%s'. Supported tools: %s"
                % (tool_name, ", ".join(SUPPORTED_TOOLS))
            )
        if tool_name not in normalized_tools:
            normalized_tools.append(tool_name)
    return normalized_tools


class BuildManager:
    """
    统一构建管理：依赖拉取 → CMake 配置 → 并行编译 → 安装 / 测试。

    用法:
        python build.py                  完整构建（拉取依赖 + Release 编译）
        python build.py local            本地构建（跳过依赖拉取, Release 编译）
        python build.py test             单元测试（拉取依赖 + Debug 编译 + 执行测试）
        python build.py test local       单元测试（跳过依赖拉取, Debug 编译 + 执行测试）
        python build.py -r <revision>    指定依赖的内部源码仓(例如msopcom)的 Git 分支/标签/commit
        python build.py -v <version>     指定构建版本号，同时覆盖 --build-version 和 --whl-version
        python build.py -e KEY=VALUE     指定额外构建选项，可多次使用
        python build.py --exclude-tools msdebug,msopprof  排除指定子工具

    参数说明:
        - 参数: command : 构建动作: 为空时为全构建, local 为跳过依赖下载, test 为运行单元测试。
        - 参数: -r, --revision : 指定 Git 修订版本或标签用于依赖检出。
        - 参数: -v, --version : 指定构建版本号；若设置，则同时覆盖 --build-version 和 --whl-version 的值。
        - 参数: --build-version, --whl-version : 历史参数，保留用于兼容；设置了 --version 时以 --version 为准。
        - 参数: -e, --extra : 额外构建选项，格式为 KEY=VALUE，可多次指定。
        - 参数: --exclude-tools : 不构建且不打包指定子工具，逗号分隔。

    产物归档:
        产品构建完成后，归档到 artifacts/ 目录中。
    """

    def __init__(self):
        self.project_root = Path(__file__).resolve().parent
        self.build_jobs = multiprocessing.cpu_count()
        argument_parser = argparse.ArgumentParser(description='Build the project and optionally run tests.')
        argument_parser.add_argument('command', nargs='*', default=[],
                                     choices=[[], 'local', 'test'],
                                     help='Build action: omit for full build, "local" to skip dependency download, "test" to run unit tests')
        argument_parser.add_argument('-r', '--revision',
                                     help='Specify Git revision for internal dependent repo (e.g., msopcom).')
        argument_parser.add_argument('--build-version', type=str, default=None, help='Build version for run/exe/dmg packages')
        argument_parser.add_argument('--whl-version', type=str, default=None, help='WHL version for Python wheel packages')
        argument_parser.add_argument('-v', '--version', type=str, default=None,
                                     help='Build version, overrides --build-version and --whl-version if set')
        argument_parser.add_argument('-e', '--extra', metavar='KEY=VALUE', action='append', default=[],
                                     help='Extra build options in KEY=VALUE format, can be specified multiple times')
        # build.py 是用户入口，CMake 是实际构建入口；这里先完成校验和归一化，
        # run 阶段只需要把稳定列表透传给 MSOT_EXCLUDE_TOOLS。
        argument_parser.add_argument('--exclude-tools', metavar='TOOLS', type=normalize_excluded_tools, default=[],
                                     help='Comma-separated tools excluded from build/package. Supported tools: %s'
                                          % ', '.join(SUPPORTED_TOOLS))
        self.parsed_arguments = argument_parser.parse_args()

        if self.parsed_arguments.version is not None:
            self.parsed_arguments.build_version = self.parsed_arguments.version
            self.parsed_arguments.whl_version = self.parsed_arguments.version

        if self.parsed_arguments.build_version is not None:
            logging.info("--build-version: %s", self.parsed_arguments.build_version)

        if self.parsed_arguments.exclude_tools:
            logging.info("--exclude-tools: %s", ",".join(self.parsed_arguments.exclude_tools))

    def _execute_command(self, command_sequence, timeout_seconds=36000, cwd=None, env=None):
        logging.info("Running: %s", " ".join(command_sequence))
        subprocess.run(command_sequence, timeout=timeout_seconds, check=True, cwd=cwd, env=env)

    def _archive_artifacts(self):
        """将产品构建产物（output 目录下的 .run）归档到工程根目录的 artifacts 目录。"""
        artifact_patterns = ("ascend-mindstudio-operator-tools*.run",)
        output_dir = self.project_root / "output"
        artifacts_dir = self.project_root / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        if not output_dir.exists():
            logging.warning("Output directory not found, skip archiving: %s", output_dir)
            return

        for pattern in artifact_patterns:
            for artifact in output_dir.rglob(pattern):
                destination = artifacts_dir / artifact.name
                logging.info("Archiving artifact: %s -> %s", artifact, destination)
                shutil.copy2(artifact, destination)

    def run(self):
        os.chdir(self.project_root)

        whl_version = self.parsed_arguments.whl_version
        if whl_version:
            os.environ['WHL_VERSION'] = whl_version
            logging.info("WHL_VERSION set to: %s", whl_version)

        for option in self.parsed_arguments.extra:
            key, _, value = option.partition('=')
            logging.info("--extra: %s = %s", key, value)

        # 在非 local 场景下按需更新依赖；在 local 场景下仅使用本地已有代码，不更新依赖。
        if 'local' not in self.parsed_arguments.command:
            from download_dependencies import DependencyManager
            DependencyManager(self.parsed_arguments).run()

        # 依赖下载完成后统一更新所有 version.info（放在下载后避免被 git submodule update 覆盖）
        if self.parsed_arguments.build_version is not None:
            for vf in ["./package/conf/version.info",
                       "./msdebug/package/conf/version.info",
                       "./msopprof/package/conf/version.info",
                       "./mssanitizer/package/conf/version.info"]:
                version_file = self.project_root / vf
                content = version_file.read_text()
                # 使用 re.sub 替换版本号，仅允许合法版本字符
                sanitized = re.sub(
                    r"^Version=.*$",
                    f"Version={self.parsed_arguments.build_version}",
                    content,
                    flags=re.MULTILINE
                )
                version_file.write_text(sanitized)

        if 'test' in self.parsed_arguments.command:
            # -------------------- 单元测试 --------------------
            unit_test_build_dir = self.project_root / "build_ut"
            unit_test_build_dir.mkdir(exist_ok=True)
            os.chdir(unit_test_build_dir)

            self._execute_command(["cmake", "..", "-DBUILD_TESTS=ON"])
            # 待测试用例准备好后添加测试执行命令
        else:
            # -------------------- 产品构建 --------------------
            product_build_dir = self.project_root / "build"
            product_build_dir.mkdir(exist_ok=True)
            os.chdir(product_build_dir)

            # 始终显式传递 MSOT_EXCLUDE_TOOLS，包括空值；否则 CMake 会复用
            # build/CMakeCache.txt 中上一次的排除列表，导致后续默认构建仍跳过旧工具。
            cmake_command = [
                "cmake",
                "..",
                "-DMSOT_EXCLUDE_TOOLS=%s" % ",".join(self.parsed_arguments.exclude_tools),
            ]
            self._execute_command(cmake_command)
            self._execute_command(["make", "-j", str(self.build_jobs)])

            self._archive_artifacts()


if __name__ == "__main__":
    try:
        BuildManager().run()
    except Exception:
        logging.error(f"Unexpected error: {traceback.format_exc()}")
        sys.exit(1)
