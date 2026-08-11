// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from macrobot_interfaces:msg/EmbeddingMatchedCandidate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/embedding_matched_candidate.h"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__FUNCTIONS_H_
#define MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/action_type_support_struct.h"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_runtime_c/service_type_support_struct.h"
#include "rosidl_runtime_c/type_description/type_description__struct.h"
#include "rosidl_runtime_c/type_description/type_source__struct.h"
#include "rosidl_runtime_c/type_hash.h"
#include "rosidl_runtime_c/visibility_control.h"
#include "macrobot_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "macrobot_interfaces/msg/detail/embedding_matched_candidate__struct.h"

/// Initialize msg/EmbeddingMatchedCandidate message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * macrobot_interfaces__msg__EmbeddingMatchedCandidate
 * )) before or use
 * macrobot_interfaces__msg__EmbeddingMatchedCandidate__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
bool
macrobot_interfaces__msg__EmbeddingMatchedCandidate__init(macrobot_interfaces__msg__EmbeddingMatchedCandidate * msg);

/// Finalize msg/EmbeddingMatchedCandidate message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
void
macrobot_interfaces__msg__EmbeddingMatchedCandidate__fini(macrobot_interfaces__msg__EmbeddingMatchedCandidate * msg);

/// Create msg/EmbeddingMatchedCandidate message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * macrobot_interfaces__msg__EmbeddingMatchedCandidate__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
macrobot_interfaces__msg__EmbeddingMatchedCandidate *
macrobot_interfaces__msg__EmbeddingMatchedCandidate__create(void);

/// Destroy msg/EmbeddingMatchedCandidate message.
/**
 * It calls
 * macrobot_interfaces__msg__EmbeddingMatchedCandidate__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
void
macrobot_interfaces__msg__EmbeddingMatchedCandidate__destroy(macrobot_interfaces__msg__EmbeddingMatchedCandidate * msg);

/// Check for msg/EmbeddingMatchedCandidate message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
bool
macrobot_interfaces__msg__EmbeddingMatchedCandidate__are_equal(const macrobot_interfaces__msg__EmbeddingMatchedCandidate * lhs, const macrobot_interfaces__msg__EmbeddingMatchedCandidate * rhs);

/// Copy a msg/EmbeddingMatchedCandidate message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
bool
macrobot_interfaces__msg__EmbeddingMatchedCandidate__copy(
  const macrobot_interfaces__msg__EmbeddingMatchedCandidate * input,
  macrobot_interfaces__msg__EmbeddingMatchedCandidate * output);

/// Retrieve pointer to the hash of the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
const rosidl_type_hash_t *
macrobot_interfaces__msg__EmbeddingMatchedCandidate__get_type_hash(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
const rosidl_runtime_c__type_description__TypeDescription *
macrobot_interfaces__msg__EmbeddingMatchedCandidate__get_type_description(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the single raw source text that defined this type.
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
const rosidl_runtime_c__type_description__TypeSource *
macrobot_interfaces__msg__EmbeddingMatchedCandidate__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the recursive raw sources that defined the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
const rosidl_runtime_c__type_description__TypeSource__Sequence *
macrobot_interfaces__msg__EmbeddingMatchedCandidate__get_type_description_sources(
  const rosidl_message_type_support_t * type_support);

/// Initialize array of msg/EmbeddingMatchedCandidate messages.
/**
 * It allocates the memory for the number of elements and calls
 * macrobot_interfaces__msg__EmbeddingMatchedCandidate__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
bool
macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__init(macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence * array, size_t size);

/// Finalize array of msg/EmbeddingMatchedCandidate messages.
/**
 * It calls
 * macrobot_interfaces__msg__EmbeddingMatchedCandidate__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
void
macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__fini(macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence * array);

/// Create array of msg/EmbeddingMatchedCandidate messages.
/**
 * It allocates the memory for the array and calls
 * macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence *
macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__create(size_t size);

/// Destroy array of msg/EmbeddingMatchedCandidate messages.
/**
 * It calls
 * macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
void
macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__destroy(macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence * array);

/// Check for msg/EmbeddingMatchedCandidate message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
bool
macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__are_equal(const macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence * lhs, const macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence * rhs);

/// Copy an array of msg/EmbeddingMatchedCandidate messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
bool
macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__copy(
  const macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence * input,
  macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__FUNCTIONS_H_
