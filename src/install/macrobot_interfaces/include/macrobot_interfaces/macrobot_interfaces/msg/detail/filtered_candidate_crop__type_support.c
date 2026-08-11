// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from macrobot_interfaces:msg/FilteredCandidateCrop.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__rosidl_typesupport_introspection_c.h"
#include "macrobot_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__functions.h"
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__struct.h"


// Include directives for member types
// Member `result`
#include "macrobot_interfaces/msg/candidate_filter_result.h"
// Member `result`
#include "macrobot_interfaces/msg/detail/candidate_filter_result__rosidl_typesupport_introspection_c.h"
// Member `crop`
#include "macrobot_interfaces/msg/rgb_candidate_crop.h"
// Member `crop`
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  macrobot_interfaces__msg__FilteredCandidateCrop__init(message_memory);
}

void macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_fini_function(void * message_memory)
{
  macrobot_interfaces__msg__FilteredCandidateCrop__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_message_member_array[2] = {
  {
    "result",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__FilteredCandidateCrop, result),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "crop",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__FilteredCandidateCrop, crop),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_message_members = {
  "macrobot_interfaces__msg",  // message namespace
  "FilteredCandidateCrop",  // message name
  2,  // number of fields
  sizeof(macrobot_interfaces__msg__FilteredCandidateCrop),
  false,  // has_any_key_member_
  macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_message_member_array,  // message members
  macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_init_function,  // function to initialize message memory (memory has to be allocated)
  macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_message_type_support_handle = {
  0,
  &macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_message_members,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__FilteredCandidateCrop__get_type_hash,
  &macrobot_interfaces__msg__FilteredCandidateCrop__get_type_description,
  &macrobot_interfaces__msg__FilteredCandidateCrop__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_macrobot_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, macrobot_interfaces, msg, FilteredCandidateCrop)() {
  macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, macrobot_interfaces, msg, CandidateFilterResult)();
  macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, macrobot_interfaces, msg, RgbCandidateCrop)();
  if (!macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_message_type_support_handle.typesupport_identifier) {
    macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &macrobot_interfaces__msg__FilteredCandidateCrop__rosidl_typesupport_introspection_c__FilteredCandidateCrop_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
