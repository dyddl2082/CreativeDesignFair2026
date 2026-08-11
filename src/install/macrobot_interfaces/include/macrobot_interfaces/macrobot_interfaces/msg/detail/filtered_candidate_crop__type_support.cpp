// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from macrobot_interfaces:msg/FilteredCandidateCrop.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__functions.h"
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace macrobot_interfaces
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void FilteredCandidateCrop_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) macrobot_interfaces::msg::FilteredCandidateCrop(_init);
}

void FilteredCandidateCrop_fini_function(void * message_memory)
{
  auto typed_message = static_cast<macrobot_interfaces::msg::FilteredCandidateCrop *>(message_memory);
  typed_message->~FilteredCandidateCrop();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember FilteredCandidateCrop_message_member_array[2] = {
  {
    "result",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<macrobot_interfaces::msg::CandidateFilterResult>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces::msg::FilteredCandidateCrop, result),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "crop",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<macrobot_interfaces::msg::RgbCandidateCrop>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces::msg::FilteredCandidateCrop, crop),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers FilteredCandidateCrop_message_members = {
  "macrobot_interfaces::msg",  // message namespace
  "FilteredCandidateCrop",  // message name
  2,  // number of fields
  sizeof(macrobot_interfaces::msg::FilteredCandidateCrop),
  false,  // has_any_key_member_
  FilteredCandidateCrop_message_member_array,  // message members
  FilteredCandidateCrop_init_function,  // function to initialize message memory (memory has to be allocated)
  FilteredCandidateCrop_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t FilteredCandidateCrop_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &FilteredCandidateCrop_message_members,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__FilteredCandidateCrop__get_type_hash,
  &macrobot_interfaces__msg__FilteredCandidateCrop__get_type_description,
  &macrobot_interfaces__msg__FilteredCandidateCrop__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace macrobot_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<macrobot_interfaces::msg::FilteredCandidateCrop>()
{
  return &::macrobot_interfaces::msg::rosidl_typesupport_introspection_cpp::FilteredCandidateCrop_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, macrobot_interfaces, msg, FilteredCandidateCrop)() {
  return &::macrobot_interfaces::msg::rosidl_typesupport_introspection_cpp::FilteredCandidateCrop_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
