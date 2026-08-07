cmake_minimum_required(VERSION 3.8)
project(macrobot_safe_region)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(shape_msgs REQUIRED)
find_package(moveit_core REQUIRED)
find_package(moveit_ros_planning REQUIRED)
find_package(moveit_msgs REQUIRED)

add_executable(safe_region_generator src/safe_region_generator.cpp)
ament_target_dependencies(safe_region_generator
  rclcpp
  std_msgs
  geometry_msgs
  shape_msgs
  moveit_core
  moveit_ros_planning
  moveit_msgs
)

target_compile_options(safe_region_generator PRIVATE -Wall -Wextra -Wpedantic)

install(TARGETS safe_region_generator
  DESTINATION lib/${PROJECT_NAME}
)
install(DIRECTORY config launch scripts
  DESTINATION share/${PROJECT_NAME}
  USE_SOURCE_PERMISSIONS
)

ament_package()
