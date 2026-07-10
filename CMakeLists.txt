cmake_minimum_required(VERSION 3.13)
project(msopt)
set(CMAKE_SKIP_RPATH TRUE)

get_filename_component(ROOT_DIR ${CMAKE_CURRENT_LIST_DIR} ABSOLUTE)

# 检查是否可用 ccache
find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    message(STATUS "Using ccache: ${CCACHE_PROGRAM}")
    set(CMAKE_C_COMPILER_LAUNCHER ${CCACHE_PROGRAM})
    set(CMAKE_CXX_COMPILER_LAUNCHER ${CCACHE_PROGRAM})
else()
    message(STATUS "ccache not found, using native compiler.")
endif()

# 检查是否可用 python
find_program(PYTHON NAMES python3 python)
if(NOT PYTHON)
    message(FATAL_ERROR "Could not find python3 or python in PATH!")
else()
    message(STATUS "Found Python: ${PYTHON}")
endif()

# 为了适用于工程本身构建，也适用于其它工程调用此工程，CMAKE_INSTALL_PREFIX的判断方式需要判断是否未设定或者系统默认路径
if (${CMAKE_INSTALL_PREFIX} STREQUAL "/usr/local" OR ${CMAKE_INSTALL_PREFIX} STREQUAL "/usr" OR NOT DEFINED CMAKE_INSTALL_PREFIX)
    set(CMAKE_INSTALL_PREFIX ${ROOT_DIR}/output CACHE STRING "install prefix" FORCE)
    message(STATUS "No install prefix selected, default to ${CMAKE_INSTALL_PREFIX}")
endif() 
file(MAKE_DIRECTORY ${CMAKE_INSTALL_PREFIX})

option(BUILD_TESTS "build unit tests" OFF)
if(BUILD_TESTS)
    set(BUILD_ARG test)
endif()

# 顶层总包支持的子工具列表。排除能力按这些 CMake 模块粒度生效，
# 其中 msopgen 模块会同时产出 msopgen 与 msopst 两个 whl。
set(MSOT_VALID_TOOLS msdebug mskl mskpp msopgen msopprof mssanitizer)

# CMake 直接调用时也可以使用该变量；build.py 的 --exclude-tools 会透传到这里。
set(MSOT_EXCLUDE_TOOLS "" CACHE STRING "Comma-separated msOT sub-tools excluded from build/package")

# 将用户传入的逗号分隔字符串归一化为列表：去空、转小写、去重，并做白名单校验。
set(MSOT_EXCLUDED_TOOL_LIST "")
if(MSOT_EXCLUDE_TOOLS)
    string(REPLACE "," ";" MSOT_EXCLUDE_TOOL_RAW_LIST "${MSOT_EXCLUDE_TOOLS}")
    foreach(TOOL_NAME IN LISTS MSOT_EXCLUDE_TOOL_RAW_LIST)
        string(STRIP "${TOOL_NAME}" TOOL_NAME)
        string(TOLOWER "${TOOL_NAME}" TOOL_NAME)
        if(TOOL_NAME STREQUAL "")
            continue()
        endif()
        list(FIND MSOT_VALID_TOOLS "${TOOL_NAME}" TOOL_INDEX)
        if(TOOL_INDEX EQUAL -1)
            message(FATAL_ERROR "Unsupported MSOT_EXCLUDE_TOOLS item: ${TOOL_NAME}. Supported tools: ${MSOT_VALID_TOOLS}")
        endif()
        list(FIND MSOT_EXCLUDED_TOOL_LIST "${TOOL_NAME}" EXISTING_TOOL_INDEX)
        if(EXISTING_TOOL_INDEX EQUAL -1)
            list(APPEND MSOT_EXCLUDED_TOOL_LIST "${TOOL_NAME}")
        endif()
    endforeach()
endif()

# 归一化后的字符串用于传给 parser，也写入配置依赖文件，保证排除项变化会重新触发打包。
string(JOIN "," MSOT_EXCLUDE_TOOLS_NORMALIZED ${MSOT_EXCLUDED_TOOL_LIST})
if(MSOT_EXCLUDE_TOOLS_NORMALIZED)
    message(STATUS "Exclude msOT sub-tools: ${MSOT_EXCLUDE_TOOLS_NORMALIZED}")
endif()

# 只 include 未排除的子工具模块。被排除模块不会创建对应 package_* target，
# 因而既不会构建，也不会作为 package_msot 的前置依赖。
set(MSOT_PACKAGE_TARGETS "")
foreach(TOOL_NAME IN LISTS MSOT_VALID_TOOLS)
    list(FIND MSOT_EXCLUDED_TOOL_LIST "${TOOL_NAME}" TOOL_INDEX)
    if(TOOL_INDEX EQUAL -1)
        include(cmake/module/${TOOL_NAME}.cmake)
        list(APPEND MSOT_PACKAGE_TARGETS package_${TOOL_NAME})
    else()
        message(STATUS "Skip msOT sub-tool target: ${TOOL_NAME}")
    endif()
endforeach()

# 根据构建环境信息生成scene.info
string(TOLOWER "${CMAKE_SYSTEM_NAME}" SYSTEM)
set(ENV_INFO "os=${SYSTEM}\narch=${CMAKE_SYSTEM_PROCESSOR}")
file(WRITE "${CMAKE_INSTALL_PREFIX}/scene.info" "${ENV_INFO}")

                
# 读取version.info，并从中获取包名及版本信息
file(READ "${ROOT_DIR}/package/conf/version.info" FILE_CONTENT)
if(FILE_CONTENT MATCHES "\\[PACKAGE\\]([^\\[]+)")
    set(TMP_SECTION "${CMAKE_MATCH_1}")
    
    # 提取 name
    if(TMP_SECTION MATCHES "Name=([^\n]+)")
        string(STRIP "${CMAKE_MATCH_1}" NAME)
        message(STATUS "Name: ${NAME}")
    endif()
    
    # 提取 version
    if(TMP_SECTION MATCHES "Version=([^\\n]+)")
        string(STRIP "${CMAKE_MATCH_1}" PACKAGE_VERSION)
        message(STATUS "Version: ${PACKAGE_VERSION}")
    endif()
endif()

set(packageName "ascend-${NAME}_${PACKAGE_VERSION}_${CMAKE_SYSTEM_PROCESSOR}.run")
set(makeselfTool  ${ROOT_DIR}/thirdparty/makeself/makeself.sh)
set(makeselfHeader ${ROOT_DIR}/thirdparty/makeself/makeself-header.sh)
set(helpInfo ${ROOT_DIR}/package/conf/help.info)
set(installShell share/info/${NAME}/script/install.sh)
set(comments "ASCEND MINDSTUDIO SANITIZER RUN PACKAGE")
file(GLOB_RECURSE PACAKGE_SCRIPT_FILES ${ROOT_DIR}/package/**/*)

# 自定义命令的 DEPENDS 需要一个可跟踪文件；排除列表变化时更新该文件，
# 避免 CMake 认为 package.flag 已经是最新而复用上一次的总包内容。
set(MSOT_PACKAGE_CONFIG_FILE ${CMAKE_CURRENT_BINARY_DIR}/msot_package_config.txt)
file(WRITE "${MSOT_PACKAGE_CONFIG_FILE}" "MSOT_EXCLUDE_TOOLS=${MSOT_EXCLUDE_TOOLS_NORMALIZED}\n")

# parser 负责生成 filelist.csv 并复制总包内容；这里把同一份排除列表传进去，
# 让最终 run 包目录也跳过对应 whl/run 文件。
set(MSOT_PARSER_EXCLUDE_ARGS "")
if(MSOT_EXCLUDE_TOOLS_NORMALIZED)
    list(APPEND MSOT_PARSER_EXCLUDE_ARGS --exclude_tools ${MSOT_EXCLUDE_TOOLS_NORMALIZED})
endif()

file(GLOB_RECURSE MAKESELF_TAR_FILE_GLOB ${ROOT_DIR}/thirdparty/makeself/makeself-*.tar.gz)
file(GLOB_RECURSE MAKESELF_PATCH_FILE_GLOB ${ROOT_DIR}/thirdparty/makeself/makeself-*.patch)
list(GET MAKESELF_TAR_FILE_GLOB 0 MAKESELF_TAR_FILE)
list(GET MAKESELF_PATCH_FILE_GLOB 0 MAKESELF_PATCH_FILE)
message(STATUS "Use makeself tar file: ${MAKESELF_TAR_FILE}")
message(STATUS "Use makeself patch file: ${MAKESELF_PATCH_FILE}")

add_custom_command(
    OUTPUT ${makeselfTool} ${makeselfHeader}
    COMMENT "Extract makeself component from ${MAKESELF_TAR_FILE}"
    # 跳过最外层目录，直接将内容解压到当前目录
    COMMAND tar xf ${MAKESELF_TAR_FILE} --strip-components=1
    COMMAND git apply ${MAKESELF_PATCH_FILE}
    # git 应用 patch 后不一定会更新akeself.sh 文件的时间戳，此处需要手动更新一下，
    # 保证 makeself 解压流程完成后重新触发打包
    COMMAND touch ${makeselfTool} ${makeselfHeader}
    DEPENDS ${MAKESELF_TAR_FILE} ${MAKESELF_PATCH_FILE}
    WORKING_DIRECTORY ${ROOT_DIR}/thirdparty/makeself/
)

# 解析打包配置文件filelist.xml，并完成打包
add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/package.flag
    COMMAND ${CMAKE_COMMAND} -E copy "${ROOT_DIR}/package/conf/version.info" ${CMAKE_INSTALL_PREFIX}
    # 清理总包 staging 目录，防止前一次构建留下的已排除子包被 makeself 再次打入 run 包。
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_INSTALL_PREFIX}/${NAME}
    COMMAND cd ${ROOT_DIR}/package/script/ && ${PYTHON} parser.py -x ${ROOT_DIR}/package/conf/filelist.xml
            --delivery_path ${CMAKE_INSTALL_PREFIX} -o ${CMAKE_SYSTEM_PROCESSOR} ${MSOT_PARSER_EXCLUDE_ARGS}
    COMMAND cd ${CMAKE_INSTALL_PREFIX} && ${makeselfTool} --header ${makeselfHeader} --help-header ${helpInfo} --pigz
            --complevel 4 --nocrc --nomd5 --sha256 --chown --tar-quietly --tar-format posix ${NAME} ${packageName} ${comments} ${installShell}
    COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/package.flag
    COMMAND chmod 750 ${CMAKE_INSTALL_PREFIX}/*.run
    # package.flag 依赖未排除子工具 target，确保保留的子包产物先生成，再执行总包打包。
    DEPENDS ${MSOT_PACKAGE_TARGETS} ${PACAKGE_SCRIPT_FILES} ${ROOT_DIR}/package/conf/version.info
            ${MSOT_PACKAGE_CONFIG_FILE} ${makeselfTool} ${makeselfHeader}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)
# ALL 目标也只挂未排除子工具，避免 excluded 子工具在默认 make 中被构建。
add_custom_target(package_msot ALL DEPENDS ${MSOT_PACKAGE_TARGETS} ${CMAKE_CURRENT_BINARY_DIR}/package.flag)
