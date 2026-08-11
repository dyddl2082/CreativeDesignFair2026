// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from macrobot_interfaces:msg/RgbCandidateCrop.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/rgb_candidate_crop.h"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__RGB_CANDIDATE_CROP__STRUCT_H_
#define MACROBOT_INTERFACES__MSG__DETAIL__RGB_CANDIDATE_CROP__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'proposal_header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'candidate'
#include "macrobot_interfaces/msg/detail/depth_candidate__struct.h"
// Member 'crop_roi'
#include "sensor_msgs/msg/detail/region_of_interest__struct.h"
// Member 'foreground_mask'
// Member 'image'
#include "sensor_msgs/msg/detail/compressed_image__struct.h"

/// Struct defined in msg/RgbCandidateCrop in the package macrobot_interfaces.
/**
  * One JPEG-compressed RGB crop associated with a depth proposal.
  * A frame can produce zero or more messages on the crop topic.
 */
typedef struct macrobot_interfaces__msg__RgbCandidateCrop
{
  /// Header copied from the source aligned-depth proposal frame.
  std_msgs__msg__Header proposal_header;
  /// Dimensions of the proposal frame and matched RGB frame before cropping.
  uint32_t proposal_image_width;
  uint32_t proposal_image_height;
  uint32_t color_image_width;
  uint32_t color_image_height;
  /// Frame grouping metadata for per-candidate messages.
  uint32_t source_candidate_count;
  uint32_t frame_crop_count;
  uint32_t crop_index;
  /// Original depth candidate metadata. candidate.roi remains in proposal coordinates.
  macrobot_interfaces__msg__DepthCandidate candidate;
  /// Actual RGB region used after coordinate scaling and optional extra padding.
  sensor_msgs__msg__RegionOfInterest crop_roi;
  /// Matched RGB timestamp minus proposal timestamp. Near zero is ideal.
  float color_time_offset_sec;
  /// Whether the source proposal frame had a valid fitted background plane.
  bool plane_found;
  /// Candidate-local mask transformed to the encoded RGB crop dimensions.
  bool foreground_mask_available;
  float mask_fill_ratio;
  sensor_msgs__msg__CompressedImage foreground_mask;
  /// Encoded crop diagnostics.
  uint32_t encoded_width;
  uint32_t encoded_height;
  uint32_t jpeg_size_bytes;
  uint8_t jpeg_quality;
  bool size_limit_met;
  /// Header is copied from the matched RGB frame.
  sensor_msgs__msg__CompressedImage image;
} macrobot_interfaces__msg__RgbCandidateCrop;

// Struct for a sequence of macrobot_interfaces__msg__RgbCandidateCrop.
typedef struct macrobot_interfaces__msg__RgbCandidateCrop__Sequence
{
  macrobot_interfaces__msg__RgbCandidateCrop * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} macrobot_interfaces__msg__RgbCandidateCrop__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__RGB_CANDIDATE_CROP__STRUCT_H_
