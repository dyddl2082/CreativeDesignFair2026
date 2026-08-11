// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from macrobot_interfaces:msg/DepthCandidateArray.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "macrobot_interfaces/msg/detail/depth_candidate_array__functions.h"
#include "macrobot_interfaces/msg/detail/depth_candidate_array__struct.hpp"
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

void DepthCandidateArray_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) macrobot_interfaces::msg::DepthCandidateArray(_init);
}

void DepthCandidateArray_fini_function(void * message_memory)
{
  auto typed_message = static_cast<macrobot_interfaces::msg::DepthCandidateArray *>(message_memory);
  typed_message->~DepthCandidateArray();
}

size_t size_function__DepthCandidateArray__plane_coefficients(const void * untyped_member)
{
  (void)untyped_member;
  return 4;
}

const void * get_const_function__DepthCandidateArray__plane_coefficients(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::array<float, 4> *>(untyped_member);
  return &member[index];
}

void * get_function__DepthCandidateArray__plane_coefficients(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::array<float, 4> *>(untyped_member);
  return &member[index];
}

void fetch_function__DepthCandidateArray__plane_coefficients(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const float *>(
    get_const_function__DepthCandidateArray__plane_coefficients(untyped_member, index));
  auto & value = *reinterpret_cast<float *>(untyped_value);
  value = item;
}

void assign_function__DepthCandidateArray__plane_coefficients(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<float *>(
    get_function__DepthCandidateArray__plane_coefficients(untyped_member, index));
  const auto & value = *reinterpret_cast<const float *>(untyped_value);
  item = value;
}

size_t size_function__DepthCandidateArray__candidates(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<macrobot_interfaces::msg::DepthCandidate> *>(untyped_member);
  return member->size();
}

const void * get_const_function__DepthCandidateArray__candidates(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<macrobot_interfaces::msg::DepthCandidate> *>(untyped_member);
  return &member[index];
}

void * get_function__DepthCandidateArray__candidates(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<macrobot_interfaces::msg::DepthCandidate> *>(untyped_member);
  return &member[index];
}

void fetch_function__DepthCandidateArray__candidates(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const macrobot_interfaces::msg::DepthCandidate *>(
    get_const_function__DepthCandidateArray__candidates(untyped_member, index));
  auto & value = *reinterpret_cast<macrobot_interfaces::msg::DepthCandidate *>(untyped_value);
  value = item;
}

void assign_function__DepthCandidateArray__candidates(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<macrobot_interfaces::msg::DepthCandidate *>(
    get_function__DepthCandidateArray__candidates(untyped_member, index));
  const auto & value = *reinterpret_cast<const macrobot_interfaces::msg::DepthCandidate *>(untyped_value);
  item = value;
}

void resize_function__DepthCandidateArray__candidates(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<macrobot_interfaces::msg::DepthCandidate> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember DepthCandidateArray_message_member_array[9] = {
  {
    "header",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::Header>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces::msg::DepthCandidateArray, header),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "image_width",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces::msg::DepthCandidateArray, image_width),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "image_height",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces::msg::DepthCandidateArray, image_height),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "plane_found",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces::msg::DepthCandidateArray, plane_found),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "plane_inlier_ratio",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces::msg::DepthCandidateArray, plane_inlier_ratio),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "plane_coefficients",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    4,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces::msg::DepthCandidateArray, plane_coefficients),  // bytes offset in struct
    nullptr,  // default value
    size_function__DepthCandidateArray__plane_coefficients,  // size() function pointer
    get_const_function__DepthCandidateArray__plane_coefficients,  // get_const(index) function pointer
    get_function__DepthCandidateArray__plane_coefficients,  // get(index) function pointer
    fetch_function__DepthCandidateArray__plane_coefficients,  // fetch(index, &value) function pointer
    assign_function__DepthCandidateArray__plane_coefficients,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "foreground_mask_available",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces::msg::DepthCandidateArray, foreground_mask_available),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "foreground_mask",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<sensor_msgs::msg::CompressedImage>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces::msg::DepthCandidateArray, foreground_mask),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "candidates",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<macrobot_interfaces::msg::DepthCandidate>(),  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces::msg::DepthCandidateArray, candidates),  // bytes offset in struct
    nullptr,  // default value
    size_function__DepthCandidateArray__candidates,  // size() function pointer
    get_const_function__DepthCandidateArray__candidates,  // get_const(index) function pointer
    get_function__DepthCandidateArray__candidates,  // get(index) function pointer
    fetch_function__DepthCandidateArray__candidates,  // fetch(index, &value) function pointer
    assign_function__DepthCandidateArray__candidates,  // assign(index, value) function pointer
    resize_function__DepthCandidateArray__candidates  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers DepthCandidateArray_message_members = {
  "macrobot_interfaces::msg",  // message namespace
  "DepthCandidateArray",  // message name
  9,  // number of fields
  sizeof(macrobot_interfaces::msg::DepthCandidateArray),
  false,  // has_any_key_member_
  DepthCandidateArray_message_member_array,  // message members
  DepthCandidateArray_init_function,  // function to initialize message memory (memory has to be allocated)
  DepthCandidateArray_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t DepthCandidateArray_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &DepthCandidateArray_message_members,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__DepthCandidateArray__get_type_hash,
  &macrobot_interfaces__msg__DepthCandidateArray__get_type_description,
  &macrobot_interfaces__msg__DepthCandidateArray__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace macrobot_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<macrobot_interfaces::msg::DepthCandidateArray>()
{
  return &::macrobot_interfaces::msg::rosidl_typesupport_introspection_cpp::DepthCandidateArray_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, macrobot_interfaces, msg, DepthCandidateArray)() {
  return &::macrobot_interfaces::msg::rosidl_typesupport_introspection_cpp::DepthCandidateArray_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
