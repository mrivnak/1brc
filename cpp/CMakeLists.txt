cmake_minimum_required(VERSION 3.17)
project(OneBillionRows)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug)
endif ()

# Generate compile_commands.json for IDEs 
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Use LLVM's lld linker
find_program(LLD lld)
if (CMAKE_CXX_COMPILER_ID STREQUAL "Clang" AND LLD)
    message(STATUS "Using LLVM's lld linker")
    add_link_options("-fuse-ld=lld")
    set(USE_LLD TRUE)
endif ()

# Set warning flags
if (CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    message(STATUS "Enabling Clang warnings")
    add_compile_options(-Wall -Wextra -Wpedantic -Wshadow -Wdouble-promotion -Wimplicit-fallthrough)
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    message(STATUS "Enabling GCC warnings")
    add_compile_options(-Wall -Wextra -Wpedantic -Wshadow -Wdouble-promotion -Wimplicit-fallthrough)
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    message(STATUS "Enabling MSVC warnings")
    add_compile_options(/W4)
endif ()

add_executable(one-billion-rows src/main.cpp)
target_include_directories(one-billion-rows PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
