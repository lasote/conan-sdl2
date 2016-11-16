PROJECT(MyHello)
cmake_minimum_required(VERSION 3.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(timer sdl_timer.c)
TARGET_LINK_LIBRARIES(timer ${CONAN_LIBS})
