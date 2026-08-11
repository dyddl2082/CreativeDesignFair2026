// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from macrobot_interfaces:msg/FilteredCandidateCrop.idl
// generated code does not contain a copyright notice
#ifndef MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "macrobot_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_macrobot_interfaces__msg__FilteredCandidateCrop(
  const macrobot_interfaces__msg__FilteredCandidateCrop * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_deserialize_macrobot_interfaces__msg__FilteredCandidateCrop(
  eprosima::fastcdr::Cdr &,
  macrobot_interfaces__msg__FilteredCandidateCrop * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t get_serialized_size_macrobot_interfaces__msg__FilteredCandidateCrop(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t max_serialized_size_macrobot_interfaces__msg__FilteredCandidateCrop(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_key_macrobot_interfaces__msg__FilteredCandidateCrop(
  const macrobot_interfaces__msg__FilteredCandidateCrop * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t get_serialized_size_key_macrobot_interfaces__msg__FilteredCandidateCrop(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t max_serialized_size_key_macrobot_interfaces__msg__FilteredCandidateCrop(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, macrobot_interfaces, msg, FilteredCandidateCrop)();

#ifdef __cplusplus
}
#endif

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
