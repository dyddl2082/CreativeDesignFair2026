# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_macrobot_safe_region_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED macrobot_safe_region_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(macrobot_safe_region_FOUND FALSE)
  elseif(NOT macrobot_safe_region_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(macrobot_safe_region_FOUND FALSE)
  endif()
  return()
endif()
set(_macrobot_safe_region_CONFIG_INCLUDED TRUE)

# output package information
if(NOT macrobot_safe_region_FIND_QUIETLY)
  message(STATUS "Found macrobot_safe_region: 0.1.0 (${macrobot_safe_region_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'macrobot_safe_region' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT macrobot_safe_region_DEPRECATED_QUIET)
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(macrobot_safe_region_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${macrobot_safe_region_DIR}/${_extra}")
endforeach()
