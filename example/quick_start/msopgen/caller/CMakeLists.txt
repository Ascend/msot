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


# 本 CMakeLists.txt：编译「调用自定义算子 execute_add」的 Host 侧可执行程序。
# 依赖昇腾 CANN 环境变量 ASCEND_HOME_PATH，并链接自定义算子包（customize/op_api）。

# -----------------------------------------------------------------------------
# 基本工程设置
# -----------------------------------------------------------------------------

# 本工程用到的 CMake 语法/指令至少需要此版本（低于该版本的 CMake 会报错退出）
cmake_minimum_required(VERSION 3.5.1)

# 定义工程名；同时会设置 ${PROJECT_NAME} 等变量（本文件中也可手写为 acl_execute_add）
project(acl_execute_add)

# Host 侧 C++ 源码按 C++11 标准编译（与 main.cpp 中使用的语言特性一致）
add_compile_options(-std=c++11)

# 可执行文件输出目录：相对于当前构建目录（build）为 ./，便于与脚本、算子包路径配合
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "./")

# -----------------------------------------------------------------------------
# 昇腾 CANN 路径与自定义算子 API 包路径
#
# ASCEND_HOME_PATH：通常指向 CANN 根目录（安装后需先在 shell 里 source set_env.sh 等脚本）。
# CUST_PKG_PATH  ：OPP 下厂商自定义算子的 op_api，内含头文件与 libcust_opapi 等。
# -----------------------------------------------------------------------------

set(INC_PATH $ENV{ASCEND_HOME_PATH})
message(STATUS "env INC_PATH: ${INC_PATH}")

# 自定义算子对外 API 的安装根目录（include / lib 在其下）
set(CUST_PKG_PATH "${INC_PATH}/opp/vendors/customize/op_api")

# CANN 运行时与 ACL 相关动态库所在目录（常见为 lib64）
set(LIB_PATH ${INC_PATH}/lib64)
message(STATUS "env LIB_PATH: ${LIB_PATH}")

# -----------------------------------------------------------------------------
# 头文件搜索路径（include_directories 对后续所有目标生效）
# -----------------------------------------------------------------------------

include_directories(
    ${INC_PATH}/include         # ACL / 运行时等公共头文件
    ${CUST_PKG_PATH}/include    # 自定义算子对外 API 声明（如算子注册生成的头文件）
)

# -----------------------------------------------------------------------------
# 链接时库搜索路径（link_directories 对后续所有可执行/库目标生效）
# -----------------------------------------------------------------------------

link_directories(
    ${LIB_PATH}             # libascendcl.so 等
    ${CUST_PKG_PATH}/lib   # libcust_opapi.so 等
)

# -----------------------------------------------------------------------------
# 可执行目标：由 main.cpp 单一源码生成 execute_add_op（或 Windows 下带 .exe）
# -----------------------------------------------------------------------------

add_executable(execute_add_op
    main.cpp
)

# 链接库说明：
# - ascendcl      ：ACL 主库，设备/流/内存等 Host API
# - cust_opapi    ：自定义算子包提供的调用封装（与 CUST_PKG_PATH 中头文件/库对应）
# - acl_op_compiler / nnopbase ：算子编译、基础依赖（具体以当前 CANN 版本文档为准）
# - stdc++        ：显式链接 C++ 标准库（部分环境下链接行为更明确）
target_link_libraries(execute_add_op
    ascendcl
    cust_opapi
    acl_op_compiler
    nnopbase
    stdc++
)
