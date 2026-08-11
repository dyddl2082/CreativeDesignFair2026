// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from macrobot_interfaces:msg/FilteredCandidateCrop.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__rosidl_typesupport_fastrtps_cpp.hpp"
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__functions.h"
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__struct.hpp"

#include <cstddef>
#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions
namespace macrobot_interfaces
{
namespace msg
{
namespace typesupport_fastrtps_cpp
{
bool cdr_serialize(
  const macrobot_interfaces::msg::CandidateFilterResult &,
  eprosima::fastcdr::Cdr &);
bool cdr_deserialize(
  eprosima::fastcdr::Cdr &,
  macrobot_interfaces::msg::CandidateFilterResult &);
size_t get_serialized_size(
  const macrobot_interfaces::msg::CandidateFilterResult &,
  size_t current_alignment);
size_t
max_serialized_size_CandidateFilterResult(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
bool cdr_serialize_key(
  const macrobot_interfaces::msg::CandidateFilterResult &,
  eprosima::fastcdr::Cdr &);
size_t get_serialized_size_key(
  const macrobot_interfaces::msg::CandidateFilterResult &,
  size_t current_alignment);
size_t
max_serialized_size_key_CandidateFilterResult(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
}  // namespace typesupport_fastrtps_cpp
}  // namespace msg
}  // namespace macrobot_interfaces

namespace macrobot_interfaces
{
namespace msg
{
namespace typesupport_fastrtps_cpp
{
bool cdr_serialize(
  const macrobot_interfaces::msg::RgbCandidateCrop &,
  eprosima::fastcdr::Cdr &);
bool cdr_deserialize(
  eprosima::fastcdr::Cdr &,
  macrobot_interfaces::msg::RgbCandidateCrop &);
size_t get_serialized_size(
  const macrobot_interfaces::msg::RgbCandidateCrop &,
  size_t current_alignment);
size_t
max_serialized_size_RgbCandidateCrop(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
bool cdr_serialize_key(
  const macrobot_interfaces::msg::RgbCandidateCrop &,
  eprosima::fastcdr::Cdr &);
size_t get_serialized_size_key(
  const macrobot_interfaces::msg::RgbCandidateCrop &,
  size_t current_alignment);
size_t
max_serialized_size_key_RgbCandidateCrop(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
}  // namespace typesupport_fastrtps_cpp
}  // namespace msg
}  // namespace macrobot_interfaces


namespace macrobot_interfaces
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{


bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
cdr_serialize(
  const macrobot_interfaces::msg::FilteredCandidateCrop & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: result
  macrobot_interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.result,
    cdr);

  // Member: crop
  macrobot_interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.crop,
    cdr);

  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces::msg::FilteredCandidateCrop & ros_message)
{
  // Member: result
  macrobot_interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.result);

  // Member: crop
  macrobot_interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.crop);

  return true;
}  // NOLINT(readability/fn_size)


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
get_serialized_size(
  const macrobot_interfaces::msg::FilteredCandidateCrop & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: result
  current_alignment +=
    macrobot_interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.result, current_alignment);

  // Member: crop
  current_alignment +=
    macrobot_interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.crop, current_alignment);

  return current_alignment - initial_alignment;
}


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
max_serialized_size_FilteredCandidateCrop(
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

  // Member: result
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        macrobot_interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_CandidateFilterResult(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // Member: crop
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        macrobot_interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_RgbCandidateCrop(
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
    using DataType = macrobot_interfaces::msg::FilteredCandidateCrop;
    is_plain =
      (
      offsetof(DataType, crop) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
cdr_serialize_key(
  const macrobot_interfaces::msg::FilteredCandidateCrop & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: result
  macrobot_interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize_key(
    ros_message.result,
    cdr);

  // Member: crop
  macrobot_interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize_key(
    ros_message.crop,
    cdr);

  return true;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
get_serialized_size_key(
  const macrobot_interfaces::msg::FilteredCandidateCrop & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: result
  current_alignment +=
    macrobot_interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size_key(
    ros_message.result, current_alignment);

  // Member: crop
  current_alignment +=
    macrobot_interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size_key(
    ros_message.crop, current_alignment);

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
max_serialized_size_key_FilteredCandidateCrop(
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

  // Member: result
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        macrobot_interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_key_CandidateFilterResult(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: crop
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        macrobot_interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_key_RgbCandidateCrop(
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
    using DataType = macrobot_interfaces::msg::FilteredCandidateCrop;
    is_plain =
      (
      offsetof(DataType, crop) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}


static bool _FilteredCandidateCrop__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const macrobot_interfaces::msg::FilteredCandidateCrop *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _FilteredCandidateCrop__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<macrobot_interfaces::msg::FilteredCandidateCrop *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _FilteredCandidateCrop__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const macrobot_interfaces::msg::FilteredCandidateCrop *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _FilteredCandidateCrop__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_FilteredCandidateCrop(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _FilteredCandidateCrop__callbacks = {
  "macrobot_interfaces::msg",
  "FilteredCandidateCrop",
  _FilteredCandidateCrop__cdr_serialize,
  _FilteredCandidateCrop__cdr_deserialize,
  _FilteredCandidateCrop__get_serialized_size,
  _FilteredCandidateCrop__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _FilteredCandidateCrop__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_FilteredCandidateCrop__callbacks,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__FilteredCandidateCrop__get_type_hash,
  &macrobot_interfaces__msg__FilteredCandidateCrop__get_type_description,
  &macrobot_interfaces__msg__FilteredCandidateCrop__get_type_description_sources,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace macrobot_interfaces

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_macrobot_interfaces
const rosidl_message_type_support_t *
get_message_type_support_handle<macrobot_interfaces::msg::FilteredCandidateCrop>()
{
  return &macrobot_interfaces::msg::typesupport_fastrtps_cpp::_FilteredCandidateCrop__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, macrobot_interfaces, msg, FilteredCandidateCrop)() {
  return &macrobot_interfaces::msg::typesupport_fastrtps_cpp::_FilteredCandidateCrop__handle;
}

#ifdef __cplusplus
}
#endif
