include(ExternalProject)
set(MSKPP_PATH ${ROOT_DIR}/mskpp)
ExternalProject_Add(package_mskpp
                    SOURCE_DIR  ${MSKPP_PATH}
                    CMAKE_ARGS  -DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}/mskpp
                    BUILD_COMMAND $(MAKE) install
                    INSTALL_COMMAND ""
                    EXCLUDE_FROM_ALL FALSE
)
