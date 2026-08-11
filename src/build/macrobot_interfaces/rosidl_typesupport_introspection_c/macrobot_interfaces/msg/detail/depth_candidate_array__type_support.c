// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from macrobot_interfaces:msg/DepthCandidateArray.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "macrobot_interfaces/msg/detail/depth_candidate_array__rosidl_typesupport_introspection_c.h"
#include "macrobot_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "macrobot_interfaces/msg/detail/depth_candidate_array__functions.h"
#include "macrobot_interfaces/msg/detail/depth_candidate_array__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `foreground_mask`
#include "sensor_msgs/msg/compressed_image.h"
// Member `foreground_mask`
#include "sensor_msgs/msg/detail/compressed_image__rosidl_typesupport_introspection_c.h"
// Member `candidates`
#include "macrobot_interfaces/msg/depth_candidate.h"
// Member `candidates`
#include "macrobot_interfaces/msg/detail/depth_candidate__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  macrobot_interfaces__msg__DepthCandidateArray__init(message_memory);
}

void macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_fini_function(void * message_memory)
{
  macrobot_interfaces__msg__DepthCandidateArray__fini(message_memory);
}

size_t macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__size_function__DepthCandidateArray__plane_coefficients(
  const void * untyped_member)
{
  (void)untyped_member;
  return 4;
}

const void * macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__get_const_function__DepthCandidateArray__plane_coefficients(
  const void * untyped_member, size_t index)
{
  const float * member =
    (const float *)(untyped_member);
  return &member[index];
}

void * macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__get_function__DepthCandidateArray__plane_coefficients(
  void * untyped_member, size_t index)
{
  float * member =
    (float *)(untyped_member);
  return &member[index];
}

void macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__fetch_function__DepthCandidateArray__plane_coefficients(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__get_const_function__DepthCandidateArray__plane_coefficients(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__assign_function__DepthCandidateArray__plane_coefficients(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__get_function__DepthCandidateArray__plane_coefficients(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

size_t macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__size_function__DepthCandidateArray__candidates(
  const void * untyped_member)
{
  const macrobot_interfaces__msg__DepthCandidate__Sequence * member =
    (const macrobot_interfaces__msg__DepthCandidate__Sequence *)(untyped_member);
  return member->size;
}

const void * macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__get_const_function__DepthCandidateArray__candidates(
  const void * untyped_member, size_t index)
{
  const macrobot_interfaces__msg__DepthCandidate__Sequence * member =
    (const macrobot_interfaces__msg__DepthCandidate__Sequence *)(untyped_member);
  return &member->data[index];
}

void * macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__get_function__DepthCandidateArray__candidates(
  void * untyped_member, size_t index)
{
  macrobot_interfaces__msg__DepthCandidate__Sequence * member =
    (macrobot_interfaces__msg__DepthCandidate__Sequence *)(untyped_member);
  return &member->data[index];
}

void macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__fetch_function__DepthCandidateArray__candidates(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const macrobot_interfaces__msg__DepthCandidate * item =
    ((const macrobot_interfaces__msg__DepthCandidate *)
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__get_const_function__DepthCandidateArray__candidates(untyped_member, index));
  macrobot_interfaces__msg__DepthCandidate * value =
    (macrobot_interfaces__msg__DepthCandidate *)(untyped_value);
  *value = *item;
}

void macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__assign_function__DepthCandidateArray__candidates(
  void * untyped_member, size_t index, const void * untyped_value)
{
  macrobot_interfaces__msg__DepthCandidate * item =
    ((macrobot_interfaces__msg__DepthCandidate *)
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__get_function__DepthCandidateArray__candidates(untyped_member, index));
  const macrobot_interfaces__msg__DepthCandidate * value =
    (const macrobot_interfaces__msg__DepthCandidate *)(untyped_value);
  *item = *value;
}

bool macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__resize_function__DepthCandidateArray__candidates(
  void * untyped_member, size_t size)
{
  macrobot_interfaces__msg__DepthCandidate__Sequence * member =
    (macrobot_interfaces__msg__DepthCandidate__Sequence *)(untyped_member);
  macrobot_interfaces__msg__DepthCandidate__Sequence__fini(member);
  return macrobot_interfaces__msg__DepthCandidate__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_message_member_array[9] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__DepthCandidateArray, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "image_width",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__DepthCandidateArray, image_width),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "image_height",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__DepthCandidateArray, image_height),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "plane_found",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__DepthCandidateArray, plane_found),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "plane_inlier_ratio",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__DepthCandidateArray, plane_inlier_ratio),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "plane_coefficients",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    4,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__DepthCandidateArray, plane_coefficients),  // bytes offset in struct
    NULL,  // default value
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__size_function__DepthCandidateArray__plane_coefficients,  // size() function pointer
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__get_const_function__DepthCandidateArray__plane_coefficients,  // get_const(index) function pointer
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__get_function__DepthCandidateArray__plane_coefficients,  // get(index) function pointer
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__fetch_function__DepthCandidateArray__plane_coefficients,  // fetch(index, &value) function pointer
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__assign_function__DepthCandidateArray__plane_coefficients,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "foreground_mask_available",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__DepthCandidateArray, foreground_mask_available),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "foreground_mask",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__DepthCandidateArray, foreground_mask),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "candidates",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__DepthCandidateArray, candidates),  // bytes offset in struct
    NULL,  // default value
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__size_function__DepthCandidateArray__candidates,  // size() function pointer
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__get_const_function__DepthCandidateArray__candidates,  // get_const(index) function pointer
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__get_function__DepthCandidateArray__candidates,  // get(index) function pointer
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__fetch_function__DepthCandidateArray__candidates,  // fetch(index, &value) function pointer
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__assign_function__DepthCandidateArray__candidates,  // assign(index, value) function pointer
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__resize_function__DepthCandidateArray__candidates  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_message_members = {
  "macrobot_interfaces__msg",  // message namespace
  "DepthCandidateArray",  // message name
  9,  // number of fields
  sizeof(macrobot_interfaces__msg__DepthCandidateArray),
  false,  // has_any_key_member_
  macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_message_member_array,  // message members
  macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_init_function,  // function to initialize message memory (memory has to be allocated)
  macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_message_type_support_handle = {
  0,
  &macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_message_members,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__DepthCandidateArray__get_type_hash,
  &macrobot_interfaces__msg__DepthCandidateArray__get_type_description,
  &macrobot_interfaces__msg__DepthCandidateArray__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_macrobot_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, macrobot_interfaces, msg, DepthCandidateArray)() {
  macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_message_member_array[7].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, sensor_msgs, msg, CompressedImage)();
  macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_message_member_array[8].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, macrobot_interfaces, msg, DepthCandidate)();
  if (!macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_message_type_support_handle.typesupport_identifier) {
    macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &macrobot_interfaces__msg__DepthCandidateArray__rosidl_typesupport_introspection_c__DepthCandidateArray_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
