// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from macrobot_interfaces:msg/DepthCandidate.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/depth_candidate__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "macrobot_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "macrobot_interfaces/msg/detail/depth_candidate__struct.h"
#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"
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

#include "sensor_msgs/msg/detail/region_of_interest__functions.h"  // roi

// forward declare type support functions

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
bool cdr_serialize_sensor_msgs__msg__RegionOfInterest(
  const sensor_msgs__msg__RegionOfInterest * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
bool cdr_deserialize_sensor_msgs__msg__RegionOfInterest(
  eprosima::fastcdr::Cdr & cdr,
  sensor_msgs__msg__RegionOfInterest * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t get_serialized_size_sensor_msgs__msg__RegionOfInterest(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t max_serialized_size_sensor_msgs__msg__RegionOfInterest(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
bool cdr_serialize_key_sensor_msgs__msg__RegionOfInterest(
  const sensor_msgs__msg__RegionOfInterest * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t get_serialized_size_key_sensor_msgs__msg__RegionOfInterest(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t max_serialized_size_key_sensor_msgs__msg__RegionOfInterest(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, sensor_msgs, msg, RegionOfInterest)();


using _DepthCandidate__ros_msg_type = macrobot_interfaces__msg__DepthCandidate;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_macrobot_interfaces__msg__DepthCandidate(
  const macrobot_interfaces__msg__DepthCandidate * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: id
  {
    cdr << ros_message->id;
  }

  // Field name: roi
  {
    cdr_serialize_sensor_msgs__msg__RegionOfInterest(
      &ros_message->roi, cdr);
  }

  // Field name: center_x
  {
    cdr << ros_message->center_x;
  }

  // Field name: center_y
  {
    cdr << ros_message->center_y;
  }

  // Field name: median_depth_m
  {
    cdr << ros_message->median_depth_m;
  }

  // Field name: near_depth_m
  {
    cdr << ros_message->near_depth_m;
  }

  // Field name: far_depth_m
  {
    cdr << ros_message->far_depth_m;
  }

  // Field name: depth_std_m
  {
    cdr << ros_message->depth_std_m;
  }

  // Field name: valid_depth_ratio
  {
    cdr << ros_message->valid_depth_ratio;
  }

  // Field name: fill_ratio
  {
    cdr << ros_message->fill_ratio;
  }

  // Field name: area_ratio
  {
    cdr << ros_message->area_ratio;
  }

  // Field name: foreground_height_m
  {
    cdr << ros_message->foreground_height_m;
  }

  // Field name: foreground_height_valid
  {
    cdr << (ros_message->foreground_height_valid ? true : false);
  }

  // Field name: proposal_score
  {
    cdr << ros_message->proposal_score;
  }

  // Field name: touches_border
  {
    cdr << (ros_message->touches_border ? true : false);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_deserialize_macrobot_interfaces__msg__DepthCandidate(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces__msg__DepthCandidate * ros_message)
{
  // Field name: id
  {
    cdr >> ros_message->id;
  }

  // Field name: roi
  {
    cdr_deserialize_sensor_msgs__msg__RegionOfInterest(cdr, &ros_message->roi);
  }

  // Field name: center_x
  {
    cdr >> ros_message->center_x;
  }

  // Field name: center_y
  {
    cdr >> ros_message->center_y;
  }

  // Field name: median_depth_m
  {
    cdr >> ros_message->median_depth_m;
  }

  // Field name: near_depth_m
  {
    cdr >> ros_message->near_depth_m;
  }

  // Field name: far_depth_m
  {
    cdr >> ros_message->far_depth_m;
  }

  // Field name: depth_std_m
  {
    cdr >> ros_message->depth_std_m;
  }

  // Field name: valid_depth_ratio
  {
    cdr >> ros_message->valid_depth_ratio;
  }

  // Field name: fill_ratio
  {
    cdr >> ros_message->fill_ratio;
  }

  // Field name: area_ratio
  {
    cdr >> ros_message->area_ratio;
  }

  // Field name: foreground_height_m
  {
    cdr >> ros_message->foreground_height_m;
  }

  // Field name: foreground_height_valid
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->foreground_height_valid = tmp ? true : false;
  }

  // Field name: proposal_score
  {
    cdr >> ros_message->proposal_score;
  }

  // Field name: touches_border
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->touches_border = tmp ? true : false;
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t get_serialized_size_macrobot_interfaces__msg__DepthCandidate(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _DepthCandidate__ros_msg_type * ros_message = static_cast<const _DepthCandidate__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: id
  {
    size_t item_size = sizeof(ros_message->id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: roi
  current_alignment += get_serialized_size_sensor_msgs__msg__RegionOfInterest(
    &(ros_message->roi), current_alignment);

  // Field name: center_x
  {
    size_t item_size = sizeof(ros_message->center_x);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: center_y
  {
    size_t item_size = sizeof(ros_message->center_y);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: median_depth_m
  {
    size_t item_size = sizeof(ros_message->median_depth_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: near_depth_m
  {
    size_t item_size = sizeof(ros_message->near_depth_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: far_depth_m
  {
    size_t item_size = sizeof(ros_message->far_depth_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: depth_std_m
  {
    size_t item_size = sizeof(ros_message->depth_std_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: valid_depth_ratio
  {
    size_t item_size = sizeof(ros_message->valid_depth_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: fill_ratio
  {
    size_t item_size = sizeof(ros_message->fill_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: area_ratio
  {
    size_t item_size = sizeof(ros_message->area_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_height_m
  {
    size_t item_size = sizeof(ros_message->foreground_height_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_height_valid
  {
    size_t item_size = sizeof(ros_message->foreground_height_valid);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: proposal_score
  {
    size_t item_size = sizeof(ros_message->proposal_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: touches_border
  {
    size_t item_size = sizeof(ros_message->touches_border);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t max_serialized_size_macrobot_interfaces__msg__DepthCandidate(
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

  // Field name: id
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: roi
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_sensor_msgs__msg__RegionOfInterest(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: center_x
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: center_y
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: median_depth_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: near_depth_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: far_depth_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: depth_std_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: valid_depth_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: fill_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: area_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: foreground_height_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: foreground_height_valid
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: proposal_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: touches_border
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }


  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = macrobot_interfaces__msg__DepthCandidate;
    is_plain =
      (
      offsetof(DataType, touches_border) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_key_macrobot_interfaces__msg__DepthCandidate(
  const macrobot_interfaces__msg__DepthCandidate * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: id
  {
    cdr << ros_message->id;
  }

  // Field name: roi
  {
    cdr_serialize_key_sensor_msgs__msg__RegionOfInterest(
      &ros_message->roi, cdr);
  }

  // Field name: center_x
  {
    cdr << ros_message->center_x;
  }

  // Field name: center_y
  {
    cdr << ros_message->center_y;
  }

  // Field name: median_depth_m
  {
    cdr << ros_message->median_depth_m;
  }

  // Field name: near_depth_m
  {
    cdr << ros_message->near_depth_m;
  }

  // Field name: far_depth_m
  {
    cdr << ros_message->far_depth_m;
  }

  // Field name: depth_std_m
  {
    cdr << ros_message->depth_std_m;
  }

  // Field name: valid_depth_ratio
  {
    cdr << ros_message->valid_depth_ratio;
  }

  // Field name: fill_ratio
  {
    cdr << ros_message->fill_ratio;
  }

  // Field name: area_ratio
  {
    cdr << ros_message->area_ratio;
  }

  // Field name: foreground_height_m
  {
    cdr << ros_message->foreground_height_m;
  }

  // Field name: foreground_height_valid
  {
    cdr << (ros_message->foreground_height_valid ? true : false);
  }

  // Field name: proposal_score
  {
    cdr << ros_message->proposal_score;
  }

  // Field name: touches_border
  {
    cdr << (ros_message->touches_border ? true : false);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t get_serialized_size_key_macrobot_interfaces__msg__DepthCandidate(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _DepthCandidate__ros_msg_type * ros_message = static_cast<const _DepthCandidate__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: id
  {
    size_t item_size = sizeof(ros_message->id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: roi
  current_alignment += get_serialized_size_key_sensor_msgs__msg__RegionOfInterest(
    &(ros_message->roi), current_alignment);

  // Field name: center_x
  {
    size_t item_size = sizeof(ros_message->center_x);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: center_y
  {
    size_t item_size = sizeof(ros_message->center_y);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: median_depth_m
  {
    size_t item_size = sizeof(ros_message->median_depth_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: near_depth_m
  {
    size_t item_size = sizeof(ros_message->near_depth_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: far_depth_m
  {
    size_t item_size = sizeof(ros_message->far_depth_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: depth_std_m
  {
    size_t item_size = sizeof(ros_message->depth_std_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: valid_depth_ratio
  {
    size_t item_size = sizeof(ros_message->valid_depth_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: fill_ratio
  {
    size_t item_size = sizeof(ros_message->fill_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: area_ratio
  {
    size_t item_size = sizeof(ros_message->area_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_height_m
  {
    size_t item_size = sizeof(ros_message->foreground_height_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_height_valid
  {
    size_t item_size = sizeof(ros_message->foreground_height_valid);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: proposal_score
  {
    size_t item_size = sizeof(ros_message->proposal_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: touches_border
  {
    size_t item_size = sizeof(ros_message->touches_border);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t max_serialized_size_key_macrobot_interfaces__msg__DepthCandidate(
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
  // Field name: id
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: roi
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_sensor_msgs__msg__RegionOfInterest(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: center_x
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: center_y
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: median_depth_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: near_depth_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: far_depth_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: depth_std_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: valid_depth_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: fill_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: area_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: foreground_height_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: foreground_height_valid
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: proposal_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: touches_border
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = macrobot_interfaces__msg__DepthCandidate;
    is_plain =
      (
      offsetof(DataType, touches_border) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _DepthCandidate__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const macrobot_interfaces__msg__DepthCandidate * ros_message = static_cast<const macrobot_interfaces__msg__DepthCandidate *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_macrobot_interfaces__msg__DepthCandidate(ros_message, cdr);
}

static bool _DepthCandidate__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  macrobot_interfaces__msg__DepthCandidate * ros_message = static_cast<macrobot_interfaces__msg__DepthCandidate *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_macrobot_interfaces__msg__DepthCandidate(cdr, ros_message);
}

static uint32_t _DepthCandidate__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_macrobot_interfaces__msg__DepthCandidate(
      untyped_ros_message, 0));
}

static size_t _DepthCandidate__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_macrobot_interfaces__msg__DepthCandidate(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_DepthCandidate = {
  "macrobot_interfaces::msg",
  "DepthCandidate",
  _DepthCandidate__cdr_serialize,
  _DepthCandidate__cdr_deserialize,
  _DepthCandidate__get_serialized_size,
  _DepthCandidate__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _DepthCandidate__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_DepthCandidate,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__DepthCandidate__get_type_hash,
  &macrobot_interfaces__msg__DepthCandidate__get_type_description,
  &macrobot_interfaces__msg__DepthCandidate__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, macrobot_interfaces, msg, DepthCandidate)() {
  return &_DepthCandidate__type_support;
}

#if defined(__cplusplus)
}
#endif
