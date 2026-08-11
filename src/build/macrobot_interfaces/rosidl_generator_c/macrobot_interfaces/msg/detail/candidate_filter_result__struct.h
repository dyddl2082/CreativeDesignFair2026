// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from macrobot_interfaces:msg/CandidateFilterResult.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/candidate_filter_result.h"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__CANDIDATE_FILTER_RESULT__STRUCT_H_
#define MACROBOT_INTERFACES__MSG__DETAIL__CANDIDATE_FILTER_RESULT__STRUCT_H_

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
// Member 'image_header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'target_object'
// Member 'reject_stage'
// Member 'reject_reason'
#include "rosidl_runtime_c/string.h"
// Member 'candidate'
#include "macrobot_interfaces/msg/detail/depth_candidate__struct.h"
// Member 'crop_roi'
#include "sensor_msgs/msg/detail/region_of_interest__struct.h"

/// Struct defined in msg/CandidateFilterResult in the package macrobot_interfaces.
/**
  * Per-candidate filtering decision produced by the PC-side candidate filter.
 */
typedef struct macrobot_interfaces__msg__CandidateFilterResult
{
  std_msgs__msg__Header proposal_header;
  std_msgs__msg__Header image_header;
  uint32_t candidate_id;
  uint32_t crop_index;
  uint32_t frame_crop_count;
  rosidl_runtime_c__String target_object;
  bool reference_profile_available;
  uint32_t reference_image_count;
  bool camera_info_available;
  bool plane_found;
  bool foreground_height_valid;
  bool foreground_mask_available;
  bool accepted;
  rosidl_runtime_c__String reject_stage;
  rosidl_runtime_c__String reject_reason;
  /// Generic score: is this a valid, stable physical-object candidate?
  float objectness_score;
  /// Weak target-specific hint from color and optional physical size.
  /// This is not the final Buds3 confidence.
  float target_hint_score;
  /// Temporary compatibility alias. Set equal to objectness_score.
  /// Remove after old log-analysis tools have been migrated.
  float filter_score;
  float depth_score;
  float quality_score;
  float color_score;
  float shape_score;
  float physical_size_score;
  float sharpness;
  float mean_brightness;
  float dark_ratio;
  float bright_clip_ratio;
  float edge_density;
  float mask_fill_ratio;
  float mask_solidity;
  float color_similarity;
  float aspect_ratio;
  float estimated_width_m;
  float estimated_height_m;
  float sync_offset_abs_sec;
  macrobot_interfaces__msg__DepthCandidate candidate;
  sensor_msgs__msg__RegionOfInterest crop_roi;
} macrobot_interfaces__msg__CandidateFilterResult;

// Struct for a sequence of macrobot_interfaces__msg__CandidateFilterResult.
typedef struct macrobot_interfaces__msg__CandidateFilterResult__Sequence
{
  macrobot_interfaces__msg__CandidateFilterResult * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} macrobot_interfaces__msg__CandidateFilterResult__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__CANDIDATE_FILTER_RESULT__STRUCT_H_
