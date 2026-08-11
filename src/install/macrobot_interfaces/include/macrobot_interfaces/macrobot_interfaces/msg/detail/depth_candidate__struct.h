// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from macrobot_interfaces:msg/DepthCandidate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/depth_candidate.h"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE__STRUCT_H_
#define MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'roi'
#include "sensor_msgs/msg/detail/region_of_interest__struct.h"

/// Struct defined in msg/DepthCandidate in the package macrobot_interfaces.
/**
  * Frame-local identifier. It is not a persistent tracking ID.
 */
typedef struct macrobot_interfaces__msg__DepthCandidate
{
  uint32_t id;
  /// Padded region that can be applied directly to the aligned RGB image.
  sensor_msgs__msg__RegionOfInterest roi;
  /// Connected-component centroid in image pixels.
  float center_x;
  float center_y;
  /// Robust depth statistics computed from the component pixels.
  float median_depth_m;
  float near_depth_m;
  float far_depth_m;
  float depth_std_m;
  /// Component-quality descriptors.
  float valid_depth_ratio;
  float fill_ratio;
  float area_ratio;
  /// Median optical-axis separation from the fitted background plane.
  /// Zero when plane removal was unavailable and fallback mode was used.
  float foreground_height_m;
  /// True only when foreground_height_m was measured from a valid fitted plane.
  /// False means the height is unavailable, not that the measured height is zero.
  bool foreground_height_valid;
  /// Heuristic proposal score in the range [0, 1].
  float proposal_score;
  /// True when the unpadded component touches the configured image border.
  bool touches_border;
} macrobot_interfaces__msg__DepthCandidate;

// Struct for a sequence of macrobot_interfaces__msg__DepthCandidate.
typedef struct macrobot_interfaces__msg__DepthCandidate__Sequence
{
  macrobot_interfaces__msg__DepthCandidate * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} macrobot_interfaces__msg__DepthCandidate__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE__STRUCT_H_
