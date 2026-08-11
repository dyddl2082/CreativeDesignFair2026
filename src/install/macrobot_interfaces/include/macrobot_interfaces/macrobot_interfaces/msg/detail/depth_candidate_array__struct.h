// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from macrobot_interfaces:msg/DepthCandidateArray.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/depth_candidate_array.h"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE_ARRAY__STRUCT_H_
#define MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE_ARRAY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'foreground_mask'
#include "sensor_msgs/msg/detail/compressed_image__struct.h"
// Member 'candidates'
#include "macrobot_interfaces/msg/detail/depth_candidate__struct.h"

/// Struct defined in msg/DepthCandidateArray in the package macrobot_interfaces.
/**
  * Header copied from the source aligned-depth image.
 */
typedef struct macrobot_interfaces__msg__DepthCandidateArray
{
  std_msgs__msg__Header header;
  uint32_t image_width;
  uint32_t image_height;
  /// Background-plane diagnostics for this frame.
  bool plane_found;
  float plane_inlier_ratio;
  float plane_coefficients[4];
  /// Full-frame binary foreground mask in proposal/depth coordinates.
  /// Pixel values are 0 for background and 255 for foreground.
  bool foreground_mask_available;
  sensor_msgs__msg__CompressedImage foreground_mask;
  macrobot_interfaces__msg__DepthCandidate__Sequence candidates;
} macrobot_interfaces__msg__DepthCandidateArray;

// Struct for a sequence of macrobot_interfaces__msg__DepthCandidateArray.
typedef struct macrobot_interfaces__msg__DepthCandidateArray__Sequence
{
  macrobot_interfaces__msg__DepthCandidateArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} macrobot_interfaces__msg__DepthCandidateArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE_ARRAY__STRUCT_H_
