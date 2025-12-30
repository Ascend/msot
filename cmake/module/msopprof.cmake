include(ExternalProject)
set(MSOPPROF_PATH ${ROOT_DIR}/msopprof)
ExternalProject_Add(package_msopprof
                    SOURCE_DIR  ${MSOPPROF_PATH}/cmake
                    CMAKE_ARGS  -DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}/msopprof
                    BUILD_COMMAND $(MAKE)
                    INSTALL_COMMAND ""
                    EXCLUDE_FROM_ALL FALSE
)
