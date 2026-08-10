include(ExternalProject)
set(MSKPP_PATH ${ROOT_DIR}/mskpp)
set(MSKPP_OUTPUT_DIR ${CMAKE_INSTALL_PREFIX}/mskpp)

ExternalProject_Add(package_mskpp
    SOURCE_DIR  ${MSKPP_PATH}
    CMAKE_ARGS  -DCMAKE_INSTALL_PREFIX=${MSKPP_OUTPUT_DIR}
    # make install 产出 wheel 后，使用 auditwheel repair 为 wheel 添加完整 manylinux 兼容标签，
    # 使 wheel 能在更老的 manylinux 系统上安装。若环境中没有 auditwheel 脚本会静默跳过。	
    BUILD_COMMAND bash -c "$(MAKE) install && bash ${ROOT_DIR}/cmake/script/repair_mskpp_wheel.sh ${MSKPP_OUTPUT_DIR}"
    INSTALL_COMMAND ""
    EXCLUDE_FROM_ALL FALSE
)
