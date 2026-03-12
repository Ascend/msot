#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
"""
import argparse
import os
import re
import tempfile

CACHE_FILE = os.path.join(tempfile.gettempdir(), "addconfig_cache.txt")
PATTERN = re.compile(r'(\.AddConfig\()"([^"]*)"(\))')


def get_config(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    match = PATTERN.search(content)
    if not match:
        print(f"未在 {filepath} 中找到 AddConfig(...)")
        return
    value = match.group(2)
    with open(CACHE_FILE, "w") as f:
        f.write(value)


def set_config(filepath):
    if not os.path.exists(CACHE_FILE):
        print(f"缓存文件不存在: {CACHE_FILE}，请先执行 get")
        return
    with open(CACHE_FILE, "r") as f:
        saved_value = f.read().strip()
    with open(filepath, "r") as f:
        content = f.read()
    if not PATTERN.search(content):
        print(f"未在 {filepath} 中找到 AddConfig(...)")
        return
    new_content = PATTERN.sub(rf'\1"{saved_value}"\3', content)
    with open(filepath, "w") as f:
        f.write(new_content)
    print(f"Restore Soc Info: {saved_value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="管理 AddConfig 参数")
    parser.add_argument("action", choices=["get", "set"], help="get: 读取并缓存参数; set: 从缓存恢复参数")
    parser.add_argument("file", help="要操作的 C++ 源文件路径")
    args = parser.parse_args()

    if args.action == "get":
        get_config(args.file)
    else:
        set_config(args.file)
