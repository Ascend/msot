include(ExternalProject)
set(MSSANITIZER_PATH ${ROOT_DIR}/mssanitizer)
ExternalProject_Add(package_mssanitizer
                    SOURCE_DIR  ${MSSANITIZER_PATH}/cmake
                    CMAKE_ARGS  -DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}/mssanitizer
                    BUILD_COMMAND $(MAKE)
                    INSTALL_COMMAND ""
                    EXCLUDE_FROM_ALL FALSE
)
