# Copyright (c) Huawei Technologies Co., Ltd. 2024. All rights reserved.

# CMake lowest version requirement
cmake_minimum_required(VERSION 3.5.1)

# project information
project(acl_execute_add)

# Compile options
add_compile_options(-std=c++11)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "./")

set(INC_PATH $ENV{ASCEND_HOME_PATH})
message(STATUS "env INC_PATH: ${INC_PATH}")

set(CUST_PKG_PATH "${INC_PATH}/opp/vendors/customize/op_api")

set(LIB_PATH ${INC_PATH}/lib64)
message(STATUS "env LIB_PATH: ${LIB_PATH}")

# Header path
include_directories(
    ${INC_PATH}/include
    ${CUST_PKG_PATH}/include
)

# add host lib path
link_directories(
    ${LIB_PATH}
    ${CUST_PKG_PATH}/lib
)

add_executable(execute_add_op
    main.cpp
)

target_link_libraries(execute_add_op
    ascendcl
    cust_opapi
    acl_op_compiler
    nnopbase
    stdc++
)

install(TARGETS execute_add_op DESTINATION ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
