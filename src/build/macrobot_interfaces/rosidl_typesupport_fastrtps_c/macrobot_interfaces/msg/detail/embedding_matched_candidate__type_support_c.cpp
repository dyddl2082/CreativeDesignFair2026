// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from macrobot_interfaces:msg/EmbeddingMatchedCandidate.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/embedding_matched_candidate__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "macrobot_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "macrobot_interfaces/msg/detail/embedding_matched_candidate__struct.h"
#include "macrobot_interfaces/msg/detail/embedding_matched_candidate__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__functions.h"  // result
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__functions.h"  // filtered_crop

// forward declare type support functions

bool cdr_serialize_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  const macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool cdr_deserialize_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message);

size_t get_serialized_size_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

bool cdr_serialize_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  const macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message,
  eprosima::fastcdr::Cdr & cdr);

size_t get_serialized_size_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, macrobot_interfaces, msg, EmbeddingRetrievalResult)();

bool cdr_serialize_macrobot_interfaces__msg__FilteredCandidateCrop(
  const macrobot_interfaces__msg__FilteredCandidateCrop * ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool cdr_deserialize_macrobot_interfaces__msg__FilteredCandidateCrop(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces__msg__FilteredCandidateCrop * ros_message);

size_t get_serialized_size_macrobot_interfaces__msg__FilteredCandidateCrop(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_macrobot_interfaces__msg__FilteredCandidateCrop(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

bool cdr_serialize_key_macrobot_interfaces__msg__FilteredCandidateCrop(
  const macrobot_interfaces__msg__FilteredCandidateCrop * ros_message,
  eprosima::fastcdr::Cdr & cdr);

size_t get_serialized_size_key_macrobot_interfaces__msg__FilteredCandidateCrop(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_key_macrobot_interfaces__msg__FilteredCandidateCrop(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, macrobot_interfaces, msg, FilteredCandidateCrop)();


using _EmbeddingMatchedCandidate__ros_msg_type = macrobot_interfaces__msg__EmbeddingMatchedCandidate;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_macrobot_interfaces__msg__EmbeddingMatchedCandidate(
  const macrobot_interfaces__msg__EmbeddingMatchedCandidate * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: result
  {
    cdr_serialize_macrobot_interfaces__msg__EmbeddingRetrievalResult(
      &ros_message->result, cdr);
  }

  // Field name: filtered_crop
  {
    cdr_serialize_macrobot_interfaces__msg__FilteredCandidateCrop(
      &ros_message->filtered_crop, cdr);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_deserialize_macrobot_interfaces__msg__EmbeddingMatchedCandidate(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces__msg__EmbeddingMatchedCandidate * ros_message)
{
  // Field name: result
  {
    cdr_deserialize_macrobot_interfaces__msg__EmbeddingRetrievalResult(cdr, &ros_message->result);
  }

  // Field name: filtered_crop
  {
    cdr_deserialize_macrobot_interfaces__msg__FilteredCandidateCrop(cdr, &ros_message->filtered_crop);
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t get_serialized_size_macrobot_interfaces__msg__EmbeddingMatchedCandidate(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _EmbeddingMatchedCandidate__ros_msg_type * ros_message = static_cast<const _EmbeddingMatchedCandidate__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: result
  current_alignment += get_serialized_size_macrobot_interfaces__msg__EmbeddingRetrievalResult(
    &(ros_message->result), current_alignment);

  // Field name: filtered_crop
  current_alignment += get_serialized_size_macrobot_interfaces__msg__FilteredCandidateCrop(
    &(ros_message->filtered_crop), current_alignment);

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t max_serialized_size_macrobot_interfaces__msg__EmbeddingMatchedCandidate(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // Field name: result
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_macrobot_interfaces__msg__EmbeddingRetrievalResult(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: filtered_crop
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_macrobot_interfaces__msg__FilteredCandidateCrop(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }


  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = macrobot_interfaces__msg__EmbeddingMatchedCandidate;
    is_plain =
      (
      offsetof(DataType, filtered_crop) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_key_macrobot_interfaces__msg__EmbeddingMatchedCandidate(
  const macrobot_interfaces__msg__EmbeddingMatchedCandidate * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: result
  {
    cdr_serialize_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
      &ros_message->result, cdr);
  }

  // Field name: filtered_crop
  {
    cdr_serialize_key_macrobot_interfaces__msg__FilteredCandidateCrop(
      &ros_message->filtered_crop, cdr);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t get_serialized_size_key_macrobot_interfaces__msg__EmbeddingMatchedCandidate(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _EmbeddingMatchedCandidate__ros_msg_type * ros_message = static_cast<const _EmbeddingMatchedCandidate__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: result
  current_alignment += get_serialized_size_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
    &(ros_message->result), current_alignment);

  // Field name: filtered_crop
  current_alignment += get_serialized_size_key_macrobot_interfaces__msg__FilteredCandidateCrop(
    &(ros_message->filtered_crop), current_alignment);

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t max_serialized_size_key_macrobot_interfaces__msg__EmbeddingMatchedCandidate(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;
  // Field name: result
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: filtered_crop
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_macrobot_interfaces__msg__FilteredCandidateCrop(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = macrobot_interfaces__msg__EmbeddingMatchedCandidate;
    is_plain =
      (
      offsetof(DataType, filtered_crop) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _EmbeddingMatchedCandidate__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const macrobot_interfaces__msg__EmbeddingMatchedCandidate * ros_message = static_cast<const macrobot_interfaces__msg__EmbeddingMatchedCandidate *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_macrobot_interfaces__msg__EmbeddingMatchedCandidate(ros_message, cdr);
}

static bool _EmbeddingMatchedCandidate__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  macrobot_interfaces__msg__EmbeddingMatchedCandidate * ros_message = static_cast<macrobot_interfaces__msg__EmbeddingMatchedCandidate *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_macrobot_interfaces__msg__EmbeddingMatchedCandidate(cdr, ros_message);
}

static uint32_t _EmbeddingMatchedCandidate__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_macrobot_interfaces__msg__EmbeddingMatchedCandidate(
      untyped_ros_message, 0));
}

static size_t _EmbeddingMatchedCandidate__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_macrobot_interfaces__msg__EmbeddingMatchedCandidate(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_EmbeddingMatchedCandidate = {
  "macrobot_interfaces::msg",
  "EmbeddingMatchedCandidate",
  _EmbeddingMatchedCandidate__cdr_serialize,
  _EmbeddingMatchedCandidate__cdr_deserialize,
  _EmbeddingMatchedCandidate__get_serialized_size,
  _EmbeddingMatchedCandidate__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _EmbeddingMatchedCandidate__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_EmbeddingMatchedCandidate,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__EmbeddingMatchedCandidate__get_type_hash,
  &macrobot_interfaces__msg__EmbeddingMatchedCandidate__get_type_description,
  &macrobot_interfaces__msg__EmbeddingMatchedCandidate__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, macrobot_interfaces, msg, EmbeddingMatchedCandidate)() {
  return &_EmbeddingMatchedCandidate__type_support;
}

#if defined(__cplusplus)
}
#endif
