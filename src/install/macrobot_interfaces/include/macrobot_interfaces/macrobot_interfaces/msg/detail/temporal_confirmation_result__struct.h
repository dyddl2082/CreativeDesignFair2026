// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from macrobot_interfaces:msg/TemporalConfirmationResult.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/temporal_confirmation_result.h"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__TEMPORAL_CONFIRMATION_RESULT__STRUCT_H_
#define MACROBOT_INTERFACES__MSG__DETAIL__TEMPORAL_CONFIRMATION_RESULT__STRUCT_H_

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
// Member 'target_object'
// Member 'state'
// Member 'event'
// Member 'suggested_turn'
#include "rosidl_runtime_c/string.h"
// Member 'roi'
#include "sensor_msgs/msg/detail/region_of_interest__struct.h"
// Member 'latest_result'
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__struct.h"

/// Struct defined in msg/TemporalConfirmationResult in the package macrobot_interfaces.
/**
  * Multi-frame state for one spatially consistent object-candidate track.
 */
typedef struct macrobot_interfaces__msg__TemporalConfirmationResult
{
  std_msgs__msg__Header header;
  rosidl_runtime_c__String target_object;
  uint32_t track_id;
  uint64_t frame_index;
  /// state: tentative, confirmed, lost
  /// event: update, confirmed, deconfirmed, expired
  rosidl_runtime_c__String state;
  rosidl_runtime_c__String event;
  bool confirmed;
  uint32_t track_age_frames;
  uint32_t window_size;
  uint32_t required_hits;
  uint32_t samples_in_window;
  uint32_t matched_frames_in_window;
  uint32_t hits_in_window;
  uint32_t misses_in_window;
  uint32_t consecutive_hits;
  uint32_t consecutive_misses;
  float hit_ratio;
  /// Temporal confidence is not a calibrated probability.
  float temporal_score;
  float stability_score;
  float mean_positive_similarity;
  float mean_negative_similarity;
  float mean_margin;
  float min_margin_in_window;
  float mean_objectness_score;
  sensor_msgs__msg__RegionOfInterest roi;
  float center_x;
  float center_y;
  float depth_m;
  float center_std_px;
  float depth_std_m;
  /// Normalized horizontal displacement from the image center, approximately [-1, 1].
  float horizontal_error_norm;
  rosidl_runtime_c__String suggested_turn;
  /// Most recent per-candidate retrieval result associated with this track.
  macrobot_interfaces__msg__EmbeddingRetrievalResult latest_result;
} macrobot_interfaces__msg__TemporalConfirmationResult;

// Struct for a sequence of macrobot_interfaces__msg__TemporalConfirmationResult.
typedef struct macrobot_interfaces__msg__TemporalConfirmationResult__Sequence
{
  macrobot_interfaces__msg__TemporalConfirmationResult * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} macrobot_interfaces__msg__TemporalConfirmationResult__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__TEMPORAL_CONFIRMATION_RESULT__STRUCT_H_
