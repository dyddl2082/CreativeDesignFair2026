// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from macrobot_interfaces:msg/EmbeddingMatchedCandidate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/embedding_matched_candidate.h"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__STRUCT_H_
#define MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__STRUCT_H_

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
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__struct.h"
// Member 'filtered_crop'
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__struct.h"

/// Struct defined in msg/EmbeddingMatchedCandidate in the package macrobot_interfaces.
/**
  * Candidate forwarded to temporal confirmation after embedding retrieval.
 */
typedef struct macrobot_interfaces__msg__EmbeddingMatchedCandidate
{
  macrobot_interfaces__msg__EmbeddingRetrievalResult result;
  macrobot_interfaces__msg__FilteredCandidateCrop filtered_crop;
} macrobot_interfaces__msg__EmbeddingMatchedCandidate;

// Struct for a sequence of macrobot_interfaces__msg__EmbeddingMatchedCandidate.
typedef struct macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence
{
  macrobot_interfaces__msg__EmbeddingMatchedCandidate * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__STRUCT_H_
