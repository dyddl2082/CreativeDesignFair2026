# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target macrobot_interfaces::macrobot_interfaces
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${macrobot_interfaces_TARGETS}.
if(macrobot_interfaces_TARGETS AND NOT TARGET macrobot_interfaces::macrobot_interfaces)
  add_library(macrobot_interfaces::macrobot_interfaces INTERFACE IMPORTED)
  set_target_properties(macrobot_interfaces::macrobot_interfaces PROPERTIES
    INTERFACE_LINK_LIBRARIES "${macrobot_interfaces_TARGETS}")
endif()
