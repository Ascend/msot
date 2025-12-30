#!/bin/sh

# default input file
launch_src_file="_gen_launch.cpp"
output_lib_file="_gen_module.so"

if [ $# -ge 1 ] ; then
    launch_src_file=$1
fi
if [ $# -ge 2 ]; then
    output_lib_file=$2
fi

launch_obj_file="${launch_src_file%.cpp}.o"
PYTHON_INCLUDE=$(python3 -c "import sysconfig; print(sysconfig.get_path('include'))")

cd "$(dirname "$0")"

# 编译算子为so 增加 -fPIC -c，去除 -L -l
ccec -O2 -std=c++17 -xcce --cce-aicore-arch=dav-c220-vec \
    -mllvm -cce-aicore-stack-size=0x8000 \
    -mllvm -cce-aicore-function-stack-size=0x8000 \
    -mllvm -cce-aicore-record-overflow=true \
    -mllvm -cce-aicore-addr-transform \
    -I$ASCEND_HOME_PATH/compiler/tikcpp \
    -I$ASCEND_HOME_PATH/compiler/tikcpp/tikcfw \
    -I$ASCEND_HOME_PATH/compiler/tikcpp/tikcfw/impl \
    -I$ASCEND_HOME_PATH/compiler/tikcpp/tikcfw/interface \
    -I$ASCEND_HOME_PATH/include \
    -I$ASCEND_HOME_PATH/include/experiment/runtime \
    -I$PYTHON_INCLUDE \
    -I../include \
    -I.. \
    -Wno-macro-redefined \
    -fPIC -c $launch_src_file -o $launch_obj_file

compile_ret=$? 
if [ $compile_ret -ne 0 ] ; then
    exit $compile_ret
fi

ccec --cce-fatobj-link -fPIC --cce-aicore-arch=dav-c220-vec -shared -o $output_lib_file $launch_obj_file -L$ASCEND_HOME_PATH/lib64 -L$ASCEND_HOME_PATH/aarch64-linux/simulator/Ascend910B1/lib -lruntime -lstdc++ -lascendcl -lm -ltiling_api -lplatform -lc_sec -ldl

exit $?
