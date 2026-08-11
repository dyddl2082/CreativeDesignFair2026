// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from macrobot_interfaces:msg/FilteredCandidateCrop.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/filtered_candidate_crop.h"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__STRUCT_H_
#define MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'result'
#include "macrobot_interfaces/msg/detail/candidate_filter_result__struct.h"
// Member 'crop'
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__struct.h"

/// Struct defined in msg/FilteredCandidateCrop in the package macrobot_interfaces.
/**
  * Accepted candidate passed to embedding retrieval or another downstream stage.
 */
typedef struct macrobot_interfaces__msg__FilteredCandidateCrop
{
  macrobot_interfaces__msg__CandidateFilterResult result;
  macrobot_interfaces__msg__RgbCandidateCrop crop;
} macrobot_interfaces__msg__FilteredCandidateCrop;

// Struct for a sequence of macrobot_interfaces__msg__FilteredCandidateCrop.
typedef struct macrobot_interfaces__msg__FilteredCandidateCrop__Sequence
{
  macrobot_interfaces__msg__FilteredCandidateCrop * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} macrobot_interfaces__msg__FilteredCandidateCrop__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__STRUCT_H_
