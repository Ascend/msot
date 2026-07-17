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
    def _extract_npu_ids(npu_smi_output):
        npu_ids = []
        lines = npu_smi_output.strip().split('\n')

        in_first_table = False
        get_next_line = False  # 新增标志位：是否抓取下一行

        for line in lines:
            # 检测到第二张表的表头（进程表），结束解析
            if "Process id" in line and "Process name" in line:
                break

            # 检测到第一张表的表头，标记进入第一张表数据区
            if "NPU" in line and "Name" in line and "Health" in line:
                in_first_table = True
                continue

            if in_first_table:
                # 如果当前行是 "+==================" 分隔线，则标记需要抓取下一行
                if "+===" in line:
                    get_next_line = True
                    continue

                # 如果 get_next_line 为 True，说明当前行就是 "+===" 的下一行
                if get_next_line and line.startswith('|'):
                    parts = line.split('|')
                    if len(parts) > 1:
                        first_column = parts[1].strip()
                        tokens = first_column.split()

                        # 确保提取到内容并且是数字
                        if tokens and tokens[0].isdigit():
                            npu_ids.append(int(tokens[0]))

                    # 提取完毕后重置标志位，跳过后面的行，直到遇到下一个 "+==="
                    get_next_line = False

        return npu_ids

    @staticmethod
    def find_idle() -> int:
        result = subprocess.run(["npu-smi", "info"], capture_output=True, text=True)
        if result.returncode != 0:
            sys.exit(f"ERROR: npu-smi info failed: {result.stderr.strip()}")

        npu_ids = OpRunner._extract_npu_ids(result.stdout)
        print("[INFO] Detected NPU IDs: " + str(npu_ids))

        idle = list(re.findall(r"No running processes found in NPU\s+(\d+)", result.stdout))
        idle = [int(x) for x in idle]
        print("[INFO] Available (idle) NPU IDs:" + str(idle))
        if len(idle) == 0:
            sys.exit("[WARNING]: No idle NPU, please free resources or retry later.")

        idle_npu_seq_no = npu_ids.index(idle[0])
        print("[INFO] Selected idle NPU sequence number:" + str(idle_npu_seq_no))

        return idle_npu_seq_no

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
            print(f"[INFO] Running operator on specified NPU {npu_id}.")
        else:
            print(f"[INFO] Running operator on idle NPU {npu_id}.")
        binary = os.path.join(self.build_dir, "execute_add_op")
        run_env = os.environ.copy()
        opp_lib = os.path.join(self.install_path, "opp", "vendors", "customize", "op_api", "lib")
        run_env["LD_LIBRARY_PATH"] = opp_lib + os.pathsep + run_env.get("LD_LIBRARY_PATH", "")
        self._exec([binary, str(npu_id)], cwd=self.build_dir, env=run_env)


def main():
    runner = OpRunner()
    runner.build()
    runner.run()


if __name__ == "__main__":
    main()
