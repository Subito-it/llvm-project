# -*- Python -*-

import os
import platform
import re
import subprocess
import sys

import lit.formats
import lit.util

from lit.llvm import llvm_config
from lit.llvm.subst import ToolSubst
from lit.llvm.subst import FindTool

# Configuration file for the 'lit' test runner.

# name: The name of this test suite.
config.name = 'Flang'

# testFormat: The test format to use to interpret tests.
#
# For now we require '&&' between commands, until they get globally killed and
# the test runner updated.
config.test_format = lit.formats.ShTest(not llvm_config.use_lit_shell)

# suffixes: A list of file extensions to treat as test files.
config.suffixes = ['.c', '.cpp', '.f', '.F', '.ff', '.FOR', '.for', '.f77', '.f90', '.F90',
                   '.ff90', '.f95', '.F95', '.ff95', '.fpp', '.FPP', '.cuf'
                   '.CUF', '.f18', '.F18', '.fir', '.f03', '.F03', '.f08', '.F08']

config.substitutions.append(('%PATH%', config.environment['PATH']))
config.substitutions.append(('%llvmshlibdir', config.llvm_shlib_dir))
config.substitutions.append(('%pluginext', config.llvm_plugin_ext))

llvm_config.use_default_substitutions()

# excludes: A list of directories to exclude from the testsuite. The 'Inputs'
# subdirectories contain auxiliary inputs for various tests in their parent
# directories.
config.excludes = ['Inputs', 'CMakeLists.txt', 'README.txt', 'LICENSE.txt']

# If the new Flang driver is enabled, add the corresponding feature to
# config.
config.available_features.add('new-flang-driver')

# If the flang examples are built, add examples to the config
if config.flang_examples:
    config.available_features.add('examples')

# Plugins (loadable modules)
if config.has_plugins:
    config.available_features.add('plugins')

# test_source_root: The root path where tests are located.
config.test_source_root = os.path.dirname(__file__)

# test_exec_root: The root path where tests should be run.
config.test_exec_root = os.path.join(config.flang_obj_root, 'test')

# Tweak the PATH to include the tools dir.
llvm_config.with_environment('PATH', config.flang_tools_dir, append_path=True)
llvm_config.with_environment('PATH', config.llvm_tools_dir, append_path=True)

if config.flang_standalone_build:
    # For builds with FIR, set path for tco and enable related tests
    if config.flang_llvm_tools_dir != "":
        config.available_features.add('fir')
        if config.llvm_tools_dir != config.flang_llvm_tools_dir:
            llvm_config.with_environment('PATH', config.flang_llvm_tools_dir, append_path=True)

# For each occurrence of a flang tool name, replace it with the full path to
# the build directory holding that tool.
tools = [
        ToolSubst('%flang', command=FindTool('flang-new'), unresolved='fatal'),
    ToolSubst('%flang_fc1', command=FindTool('flang-new'), extra_args=['-fc1'],
        unresolved='fatal')]

# Define some variables to help us test that the flang runtime doesn't depend on
# the C++ runtime libraries. For this we need a C compiler. If for some reason
# we don't have one, we can just disable the test.
if config.cc:
    libruntime = os.path.join(config.flang_lib_dir, 'libFortranRuntime.a')
    includes = os.path.join(config.flang_src_dir, 'runtime')

    if os.path.isfile(libruntime) and os.path.isdir(includes):
        config.available_features.add('c-compiler')
        tools.append(ToolSubst('%cc', command=config.cc, unresolved='fatal'))
        tools.append(ToolSubst('%libruntime', command=libruntime,
            unresolved='fatal'))
        tools.append(ToolSubst('%runtimeincludes', command=includes,
            unresolved='fatal'))

if config.flang_standalone_build:
    llvm_config.add_tool_substitutions(tools, [config.flang_llvm_tools_dir])
else:
    llvm_config.add_tool_substitutions(tools, config.llvm_tools_dir)

# Enable libpgmath testing
result = lit_config.params.get("LIBPGMATH")
if result:
    config.environment["LIBPGMATH"] = True
