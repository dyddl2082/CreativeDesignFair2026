// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from macrobot_interfaces:msg/FilteredCandidateCrop.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/filtered_candidate_crop.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__BUILDER_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace macrobot_interfaces
{

namespace msg
{

namespace builder
{

class Init_FilteredCandidateCrop_crop
{
public:
  explicit Init_FilteredCandidateCrop_crop(::macrobot_interfaces::msg::FilteredCandidateCrop & msg)
  : msg_(msg)
  {}
  ::macrobot_interfaces::msg::FilteredCandidateCrop crop(::macrobot_interfaces::msg::FilteredCandidateCrop::_crop_type arg)
  {
    msg_.crop = std::move(arg);
    return std::move(msg_);
  }

private:
  ::macrobot_interfaces::msg::FilteredCandidateCrop msg_;
};

class Init_FilteredCandidateCrop_result
{
public:
  Init_FilteredCandidateCrop_result()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_FilteredCandidateCrop_crop result(::macrobot_interfaces::msg::FilteredCandidateCrop::_result_type arg)
  {
    msg_.result = std::move(arg);
    return Init_FilteredCandidateCrop_crop(msg_);
  }

private:
  ::macrobot_interfaces::msg::FilteredCandidateCrop msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::macrobot_interfaces::msg::FilteredCandidateCrop>()
{
  return macrobot_interfaces::msg::builder::Init_FilteredCandidateCrop_result();
}

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__BUILDER_HPP_
