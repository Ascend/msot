set(MSKL_PATH ${ROOT_DIR}/mskl)

add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/package_mskl.flag
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_INSTALL_PREFIX}/mskl/*.whl
    COMMAND cd ${MSKL_PATH} && ${PYTHON} setup.py bdist_wheel --dist-dir ${CMAKE_INSTALL_PREFIX}/mskl
    COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/package_mskl.flag
    COMMENT "make mskl whl package"
)

add_custom_target(package_mskl ALL DEPENDS
                    ${MSKL_PATH}/MANIFEST.in
                    ${MSKL_PATH}/README.md
                    ${MSKL_PATH}/setup.py
                    ${CMAKE_CURRENT_BINARY_DIR}/package_mskl.flag)