// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from macrobot_interfaces:msg/DepthCandidate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/depth_candidate.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE__BUILDER_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "macrobot_interfaces/msg/detail/depth_candidate__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace macrobot_interfaces
{

namespace msg
{

namespace builder
{

class Init_DepthCandidate_touches_border
{
public:
  explicit Init_DepthCandidate_touches_border(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  ::macrobot_interfaces::msg::DepthCandidate touches_border(::macrobot_interfaces::msg::DepthCandidate::_touches_border_type arg)
  {
    msg_.touches_border = std::move(arg);
    return std::move(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_proposal_score
{
public:
  explicit Init_DepthCandidate_proposal_score(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_touches_border proposal_score(::macrobot_interfaces::msg::DepthCandidate::_proposal_score_type arg)
  {
    msg_.proposal_score = std::move(arg);
    return Init_DepthCandidate_touches_border(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_foreground_height_valid
{
public:
  explicit Init_DepthCandidate_foreground_height_valid(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_proposal_score foreground_height_valid(::macrobot_interfaces::msg::DepthCandidate::_foreground_height_valid_type arg)
  {
    msg_.foreground_height_valid = std::move(arg);
    return Init_DepthCandidate_proposal_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_foreground_height_m
{
public:
  explicit Init_DepthCandidate_foreground_height_m(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_foreground_height_valid foreground_height_m(::macrobot_interfaces::msg::DepthCandidate::_foreground_height_m_type arg)
  {
    msg_.foreground_height_m = std::move(arg);
    return Init_DepthCandidate_foreground_height_valid(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_area_ratio
{
public:
  explicit Init_DepthCandidate_area_ratio(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_foreground_height_m area_ratio(::macrobot_interfaces::msg::DepthCandidate::_area_ratio_type arg)
  {
    msg_.area_ratio = std::move(arg);
    return Init_DepthCandidate_foreground_height_m(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_fill_ratio
{
public:
  explicit Init_DepthCandidate_fill_ratio(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_area_ratio fill_ratio(::macrobot_interfaces::msg::DepthCandidate::_fill_ratio_type arg)
  {
    msg_.fill_ratio = std::move(arg);
    return Init_DepthCandidate_area_ratio(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_valid_depth_ratio
{
public:
  explicit Init_DepthCandidate_valid_depth_ratio(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_fill_ratio valid_depth_ratio(::macrobot_interfaces::msg::DepthCandidate::_valid_depth_ratio_type arg)
  {
    msg_.valid_depth_ratio = std::move(arg);
    return Init_DepthCandidate_fill_ratio(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_depth_std_m
{
public:
  explicit Init_DepthCandidate_depth_std_m(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_valid_depth_ratio depth_std_m(::macrobot_interfaces::msg::DepthCandidate::_depth_std_m_type arg)
  {
    msg_.depth_std_m = std::move(arg);
    return Init_DepthCandidate_valid_depth_ratio(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_far_depth_m
{
public:
  explicit Init_DepthCandidate_far_depth_m(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_depth_std_m far_depth_m(::macrobot_interfaces::msg::DepthCandidate::_far_depth_m_type arg)
  {
    msg_.far_depth_m = std::move(arg);
    return Init_DepthCandidate_depth_std_m(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_near_depth_m
{
public:
  explicit Init_DepthCandidate_near_depth_m(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_far_depth_m near_depth_m(::macrobot_interfaces::msg::DepthCandidate::_near_depth_m_type arg)
  {
    msg_.near_depth_m = std::move(arg);
    return Init_DepthCandidate_far_depth_m(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_median_depth_m
{
public:
  explicit Init_DepthCandidate_median_depth_m(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_near_depth_m median_depth_m(::macrobot_interfaces::msg::DepthCandidate::_median_depth_m_type arg)
  {
    msg_.median_depth_m = std::move(arg);
    return Init_DepthCandidate_near_depth_m(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_center_y
{
public:
  explicit Init_DepthCandidate_center_y(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_median_depth_m center_y(::macrobot_interfaces::msg::DepthCandidate::_center_y_type arg)
  {
    msg_.center_y = std::move(arg);
    return Init_DepthCandidate_median_depth_m(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_center_x
{
public:
  explicit Init_DepthCandidate_center_x(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_center_y center_x(::macrobot_interfaces::msg::DepthCandidate::_center_x_type arg)
  {
    msg_.center_x = std::move(arg);
    return Init_DepthCandidate_center_y(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_roi
{
public:
  explicit Init_DepthCandidate_roi(::macrobot_interfaces::msg::DepthCandidate & msg)
  : msg_(msg)
  {}
  Init_DepthCandidate_center_x roi(::macrobot_interfaces::msg::DepthCandidate::_roi_type arg)
  {
    msg_.roi = std::move(arg);
    return Init_DepthCandidate_center_x(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

class Init_DepthCandidate_id
{
public:
  Init_DepthCandidate_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DepthCandidate_roi id(::macrobot_interfaces::msg::DepthCandidate::_id_type arg)
  {
    msg_.id = std::move(arg);
    return Init_DepthCandidate_roi(msg_);
  }

private:
  ::macrobot_interfaces::msg::DepthCandidate msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::macrobot_interfaces::msg::DepthCandidate>()
{
  return macrobot_interfaces::msg::builder::Init_DepthCandidate_id();
}

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE__BUILDER_HPP_
