// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from macrobot_interfaces:msg/EmbeddingRetrievalResult.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/embedding_retrieval_result.h"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_RETRIEVAL_RESULT__STRUCT_H_
#define MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_RETRIEVAL_RESULT__STRUCT_H_

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
// Member 'model_id'
// Member 'pooling'
// Member 'device'
// Member 'best_positive_path'
// Member 'best_negative_path'
// Member 'top_positive_paths'
// Member 'top_negative_paths'
// Member 'reject_reason'
#include "rosidl_runtime_c/string.h"
// Member 'top_positive_scores'
// Member 'top_negative_scores'
#include "rosidl_runtime_c/primitives_sequence.h"
// Member 'candidate'
#include "macrobot_interfaces/msg/detail/depth_candidate__struct.h"
// Member 'crop_roi'
#include "sensor_msgs/msg/detail/region_of_interest__struct.h"

/// Struct defined in msg/EmbeddingRetrievalResult in the package macrobot_interfaces.
/**
  * Per-candidate DINOv2 retrieval and negative-margin result.
 */
typedef struct macrobot_interfaces__msg__EmbeddingRetrievalResult
{
  std_msgs__msg__Header proposal_header;
  std_msgs__msg__Header image_header;
  uint32_t candidate_id;
  uint32_t crop_index;
  uint32_t frame_crop_count;
  rosidl_runtime_c__String target_object;
  rosidl_runtime_c__String model_id;
  rosidl_runtime_c__String pooling;
  rosidl_runtime_c__String device;
  uint32_t embedding_dim;
  bool positive_bank_available;
  uint32_t positive_reference_count;
  bool negative_bank_available;
  uint32_t negative_reference_count;
  bool foreground_mask_used;
  /// Copied from CandidateFilterResult when available. -1 means unavailable.
  float objectness_score;
  float target_hint_score;
  /// positive_similarity and negative_similarity are top-k means.
  /// best_* fields are the single highest cosine similarities.
  float positive_similarity;
  float best_positive_similarity;
  float negative_similarity;
  float best_negative_similarity;
  float margin;
  rosidl_runtime_c__String best_positive_path;
  rosidl_runtime_c__String best_negative_path;
  rosidl_runtime_c__String__Sequence top_positive_paths;
  rosidl_runtime_c__float__Sequence top_positive_scores;
  rosidl_runtime_c__String__Sequence top_negative_paths;
  rosidl_runtime_c__float__Sequence top_negative_scores;
  /// Observation mode forwards evaluated candidates even when these thresholds fail.
  bool thresholds_enforced;
  bool passed_positive_threshold;
  bool passed_margin_threshold;
  bool accepted;
  rosidl_runtime_c__String reject_reason;
  float preprocessing_ms;
  float inference_ms;
  float matching_ms;
  macrobot_interfaces__msg__DepthCandidate candidate;
  sensor_msgs__msg__RegionOfInterest crop_roi;
} macrobot_interfaces__msg__EmbeddingRetrievalResult;

// Struct for a sequence of macrobot_interfaces__msg__EmbeddingRetrievalResult.
typedef struct macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence
{
  macrobot_interfaces__msg__EmbeddingRetrievalResult * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_RETRIEVAL_RESULT__STRUCT_H_
