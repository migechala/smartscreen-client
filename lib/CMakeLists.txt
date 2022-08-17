cmake_minimum_required(VERSION 3.20)

project(smartscreen)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/")

find_package(SDL2 REQUIRED)
find_package(SDL2_image REQUIRED)
find_package(SDL2_ttf REQUIRED)

include_directories(${SDL2_INCLUDE_DIRS})

add_executable(${PROJECT_NAME} main.cpp)

IF(APPLE)
set_target_properties(${PROJECT_NAME} PROPERTIES OSX_ARCHITECTURES arm64)
ENDIF(APPLE)

target_link_libraries(${PROJECT_NAME}
    ${SDL2_LIBRARY}
    ${SDL2_IMAGE_LIBRARIES}
    ${SDL2_TTF_LIBRARIES}
    ${CMAKE_DL_LIBS}
)

install(CODE "execute_process(COMMAND bash/install.sh)")