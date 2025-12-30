set(MSDEBUG_PATH ${ROOT_DIR}/msdebug)
set(ARGS
    "-DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}/msdebug"
    "-DCMAKE_BUILD_TYPE=Release"
)

# 查找 Ninja
find_program(NINJA ninja)
if(NINJA)
    list(APPEND ARGS "-G Ninja")  # 使用 list(APPEND) 追加，避免覆盖
    set(BUILD_CMD ${NINJA})
else()
    set(BUILD_CMD $(MAKE))
endif()
add_custom_command(
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/msdebug_build.done
        COMMAND ${CMAKE_COMMAND} -E make_directory build_msdebug
        COMMAND cd build_msdebug && cmake ${MSDEBUG_PATH} ${ARGS}
        COMMAND cd build_msdebug && unset MAKEFLAGS && ${BUILD_CMD}
        COMMAND touch ${CMAKE_CURRENT_BINARY_DIR}/msdebug_build.done
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
add_custom_target(package_msdebug DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/msdebug_build.done)