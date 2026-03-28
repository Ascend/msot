#!/usr/bin/env python3
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

import os
import re
import shutil
import subprocess
import sys


class OpRunner:
    def __init__(self):
        self.install_path = os.environ.get("REAL_ASCEND_INSTALL_PATH", "")
        if not self.install_path:
            sys.exit("ERROR: REAL_ASCEND_INSTALL_PATH not set. Please run via run.sh.")
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.build_dir = os.path.join(self.project_dir, "build")

    @staticmethod
    def _exec(cmd, **kwargs):
        print(f"+ {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
        subprocess.run(cmd, check=True, **kwargs)

    @staticmethod
    def find_idle() -> str:
        result = subprocess.run(["npu-smi", "info"], capture_output=True, text=True)
        if result.returncode != 0:
            sys.exit(f"ERROR: npu-smi info failed: {result.stderr.strip()}")

        idle = set(re.findall(r"No running processes found in NPU (\d+)", result.stdout))
        if not idle:
            sys.exit("[WARNING]: No idle NPU, please free resources or retry later.")
        return idle.pop()

    def build(self):
        if os.path.isdir(self.build_dir):
            shutil.rmtree(self.build_dir)
        os.makedirs(self.build_dir)

        self._exec(["cmake", "-B", "build", "-DCMAKE_SKIP_RPATH=TRUE"], cwd=self.project_dir)
        self._exec(["cmake", "--build", "build", "-j"], cwd=self.project_dir)

    def run(self):
        npu_id = self.find_idle()
        if len(sys.argv) > 1 and sys.argv[1]:
            npu_id = sys.argv[1]
            print(f"[INFO]: Running operator on specified NPU {npu_id}.")
        else:
            print(f"[INFO]: Running operator on idle NPU {npu_id}.")
        binary = os.path.join(self.build_dir, "execute_add_op")
        run_env = os.environ.copy()
        opp_lib = os.path.join(self.install_path, "opp", "vendors", "customize", "op_api", "lib")
        run_env["LD_LIBRARY_PATH"] = opp_lib + os.pathsep + run_env.get("LD_LIBRARY_PATH", "")
        self._exec([binary, npu_id], cwd=self.build_dir, env=run_env)


def main():
    runner = OpRunner()
    runner.build()
    runner.run()


if __name__ == "__main__":
    main()
