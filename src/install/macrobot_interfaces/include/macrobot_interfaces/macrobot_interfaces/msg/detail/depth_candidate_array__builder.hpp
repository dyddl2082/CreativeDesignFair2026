// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from macrobot_interfaces:msg/DepthCandidateArray.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/depth_candidate_array.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE_ARRAY__BUILDER_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "macrobot_interfaces/msg/detail/depth_candidate_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace macrobot_interfaces
{

namespace msg
{

namespace builder
{

class Init_DepthCandidateArray_candidates
{
public:
  explicit Init_DepthCandidateArray_candidates(::macrobot_interfaces::msg::DepthCandidateArray & msg)
  : msg_(msg)
  {}
  ::macrobot_interfaces::msg::DepthCandidateArray candidates(::macrobot_interfaces::msg::DepthCandidateArray::_candidates_type arg)
  {
    msg_.candidates = std::move(arg);
    return std::move(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidateArray msg_;
};

class Init_DepthCandidateArray_foreground_mask
{
public:
  explicit Init_DepthCandidateArray_foreground_mask(::macrobot_interfaces::msg::DepthCandidateArray & msg)
  : msg_(msg)
  {}
  Init_DepthCandidateArray_candidates foreground_mask(::macrobot_interfaces::msg::DepthCandidateArray::_foreground_mask_type arg)
  {
    msg_.foreground_mask = std::move(arg);
    return Init_DepthCandidateArray_candidates(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidateArray msg_;
};

class Init_DepthCandidateArray_foreground_mask_available
{
public:
  explicit Init_DepthCandidateArray_foreground_mask_available(::macrobot_interfaces::msg::DepthCandidateArray & msg)
  : msg_(msg)
  {}
  Init_DepthCandidateArray_foreground_mask foreground_mask_available(::macrobot_interfaces::msg::DepthCandidateArray::_foreground_mask_available_type arg)
  {
    msg_.foreground_mask_available = std::move(arg);
    return Init_DepthCandidateArray_foreground_mask(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidateArray msg_;
};

class Init_DepthCandidateArray_plane_coefficients
{
public:
  explicit Init_DepthCandidateArray_plane_coefficients(::macrobot_interfaces::msg::DepthCandidateArray & msg)
  : msg_(msg)
  {}
  Init_DepthCandidateArray_foreground_mask_available plane_coefficients(::macrobot_interfaces::msg::DepthCandidateArray::_plane_coefficients_type arg)
  {
    msg_.plane_coefficients = std::move(arg);
    return Init_DepthCandidateArray_foreground_mask_available(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidateArray msg_;
};

class Init_DepthCandidateArray_plane_inlier_ratio
{
public:
  explicit Init_DepthCandidateArray_plane_inlier_ratio(::macrobot_interfaces::msg::DepthCandidateArray & msg)
  : msg_(msg)
  {}
  Init_DepthCandidateArray_plane_coefficients plane_inlier_ratio(::macrobot_interfaces::msg::DepthCandidateArray::_plane_inlier_ratio_type arg)
  {
    msg_.plane_inlier_ratio = std::move(arg);
    return Init_DepthCandidateArray_plane_coefficients(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidateArray msg_;
};

class Init_DepthCandidateArray_plane_found
{
public:
  explicit Init_DepthCandidateArray_plane_found(::macrobot_interfaces::msg::DepthCandidateArray & msg)
  : msg_(msg)
  {}
  Init_DepthCandidateArray_plane_inlier_ratio plane_found(::macrobot_interfaces::msg::DepthCandidateArray::_plane_found_type arg)
  {
    msg_.plane_found = std::move(arg);
    return Init_DepthCandidateArray_plane_inlier_ratio(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidateArray msg_;
};

class Init_DepthCandidateArray_image_height
{
public:
  explicit Init_DepthCandidateArray_image_height(::macrobot_interfaces::msg::DepthCandidateArray & msg)
  : msg_(msg)
  {}
  Init_DepthCandidateArray_plane_found image_height(::macrobot_interfaces::msg::DepthCandidateArray::_image_height_type arg)
  {
    msg_.image_height = std::move(arg);
    return Init_DepthCandidateArray_plane_found(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidateArray msg_;
};

class Init_DepthCandidateArray_image_width
{
public:
  explicit Init_DepthCandidateArray_image_width(::macrobot_interfaces::msg::DepthCandidateArray & msg)
  : msg_(msg)
  {}
  Init_DepthCandidateArray_image_height image_width(::macrobot_interfaces::msg::DepthCandidateArray::_image_width_type arg)
  {
    msg_.image_width = std::move(arg);
    return Init_DepthCandidateArray_image_height(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidateArray msg_;
};

class Init_DepthCandidateArray_header
{
public:
  Init_DepthCandidateArray_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DepthCandidateArray_image_width header(::macrobot_interfaces::msg::DepthCandidateArray::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_DepthCandidateArray_image_width(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidateArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::macrobot_interfaces::msg::DepthCandidateArray>()
{
  return macrobot_interfaces::msg::builder::Init_DepthCandidateArray_header();
}

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE_ARRAY__BUILDER_HPP_
