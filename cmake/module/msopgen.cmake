set(MSOPGEN_PATH ${ROOT_DIR}/msopgen)

add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/package_msopgen.flag
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_INSTALL_PREFIX}/msopgen/*.whl
    COMMAND cd ${MSOPGEN_PATH} && ${PYTHON} setup.py bdist_wheel --dist-dir ${CMAKE_INSTALL_PREFIX}/msopgen
    COMMAND cd ${MSOPGEN_PATH}/tools && ${PYTHON} setup.py bdist_wheel --dist-dir ${CMAKE_INSTALL_PREFIX}/msopgen
    COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/package_msopgen.flag
    COMMENT "make msopgen and msopst whl package"
)

add_custom_target(package_msopgen ALL DEPENDS
                    ${MSOPGEN_PATH}/README.md
                    ${MSOPGEN_PATH}/setup.py
                    ${MSOPGEN_PATH}/tools/MANIFEST.in
                    ${MSOPGEN_PATH}/tools/README.md
                    ${MSOPGEN_PATH}/tools/setup.py
                    ${CMAKE_CURRENT_BINARY_DIR}/package_msopgen.flag)