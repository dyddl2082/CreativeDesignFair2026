// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from macrobot_interfaces:msg/RgbCandidateCrop.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/rgb_candidate_crop.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__RGB_CANDIDATE_CROP__BUILDER_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__RGB_CANDIDATE_CROP__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace macrobot_interfaces
{

namespace msg
{

namespace builder
{

class Init_RgbCandidateCrop_image
{
public:
  explicit Init_RgbCandidateCrop_image(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  ::macrobot_interfaces::msg::RgbCandidateCrop image(::macrobot_interfaces::msg::RgbCandidateCrop::_image_type arg)
  {
    msg_.image = std::move(arg);
    return std::move(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_size_limit_met
{
public:
  explicit Init_RgbCandidateCrop_size_limit_met(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_image size_limit_met(::macrobot_interfaces::msg::RgbCandidateCrop::_size_limit_met_type arg)
  {
    msg_.size_limit_met = std::move(arg);
    return Init_RgbCandidateCrop_image(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_jpeg_quality
{
public:
  explicit Init_RgbCandidateCrop_jpeg_quality(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_size_limit_met jpeg_quality(::macrobot_interfaces::msg::RgbCandidateCrop::_jpeg_quality_type arg)
  {
    msg_.jpeg_quality = std::move(arg);
    return Init_RgbCandidateCrop_size_limit_met(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_jpeg_size_bytes
{
public:
  explicit Init_RgbCandidateCrop_jpeg_size_bytes(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_jpeg_quality jpeg_size_bytes(::macrobot_interfaces::msg::RgbCandidateCrop::_jpeg_size_bytes_type arg)
  {
    msg_.jpeg_size_bytes = std::move(arg);
    return Init_RgbCandidateCrop_jpeg_quality(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_encoded_height
{
public:
  explicit Init_RgbCandidateCrop_encoded_height(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_jpeg_size_bytes encoded_height(::macrobot_interfaces::msg::RgbCandidateCrop::_encoded_height_type arg)
  {
    msg_.encoded_height = std::move(arg);
    return Init_RgbCandidateCrop_jpeg_size_bytes(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_encoded_width
{
public:
  explicit Init_RgbCandidateCrop_encoded_width(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_encoded_height encoded_width(::macrobot_interfaces::msg::RgbCandidateCrop::_encoded_width_type arg)
  {
    msg_.encoded_width = std::move(arg);
    return Init_RgbCandidateCrop_encoded_height(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_foreground_mask
{
public:
  explicit Init_RgbCandidateCrop_foreground_mask(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_encoded_width foreground_mask(::macrobot_interfaces::msg::RgbCandidateCrop::_foreground_mask_type arg)
  {
    msg_.foreground_mask = std::move(arg);
    return Init_RgbCandidateCrop_encoded_width(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_mask_fill_ratio
{
public:
  explicit Init_RgbCandidateCrop_mask_fill_ratio(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_foreground_mask mask_fill_ratio(::macrobot_interfaces::msg::RgbCandidateCrop::_mask_fill_ratio_type arg)
  {
    msg_.mask_fill_ratio = std::move(arg);
    return Init_RgbCandidateCrop_foreground_mask(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_foreground_mask_available
{
public:
  explicit Init_RgbCandidateCrop_foreground_mask_available(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_mask_fill_ratio foreground_mask_available(::macrobot_interfaces::msg::RgbCandidateCrop::_foreground_mask_available_type arg)
  {
    msg_.foreground_mask_available = std::move(arg);
    return Init_RgbCandidateCrop_mask_fill_ratio(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_plane_found
{
public:
  explicit Init_RgbCandidateCrop_plane_found(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_foreground_mask_available plane_found(::macrobot_interfaces::msg::RgbCandidateCrop::_plane_found_type arg)
  {
    msg_.plane_found = std::move(arg);
    return Init_RgbCandidateCrop_foreground_mask_available(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_color_time_offset_sec
{
public:
  explicit Init_RgbCandidateCrop_color_time_offset_sec(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_plane_found color_time_offset_sec(::macrobot_interfaces::msg::RgbCandidateCrop::_color_time_offset_sec_type arg)
  {
    msg_.color_time_offset_sec = std::move(arg);
    return Init_RgbCandidateCrop_plane_found(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_crop_roi
{
public:
  explicit Init_RgbCandidateCrop_crop_roi(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_color_time_offset_sec crop_roi(::macrobot_interfaces::msg::RgbCandidateCrop::_crop_roi_type arg)
  {
    msg_.crop_roi = std::move(arg);
    return Init_RgbCandidateCrop_color_time_offset_sec(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_candidate
{
public:
  explicit Init_RgbCandidateCrop_candidate(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_crop_roi candidate(::macrobot_interfaces::msg::RgbCandidateCrop::_candidate_type arg)
  {
    msg_.candidate = std::move(arg);
    return Init_RgbCandidateCrop_crop_roi(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_crop_index
{
public:
  explicit Init_RgbCandidateCrop_crop_index(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_candidate crop_index(::macrobot_interfaces::msg::RgbCandidateCrop::_crop_index_type arg)
  {
    msg_.crop_index = std::move(arg);
    return Init_RgbCandidateCrop_candidate(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_frame_crop_count
{
public:
  explicit Init_RgbCandidateCrop_frame_crop_count(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_crop_index frame_crop_count(::macrobot_interfaces::msg::RgbCandidateCrop::_frame_crop_count_type arg)
  {
    msg_.frame_crop_count = std::move(arg);
    return Init_RgbCandidateCrop_crop_index(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_source_candidate_count
{
public:
  explicit Init_RgbCandidateCrop_source_candidate_count(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_frame_crop_count source_candidate_count(::macrobot_interfaces::msg::RgbCandidateCrop::_source_candidate_count_type arg)
  {
    msg_.source_candidate_count = std::move(arg);
    return Init_RgbCandidateCrop_frame_crop_count(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_color_image_height
{
public:
  explicit Init_RgbCandidateCrop_color_image_height(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_source_candidate_count color_image_height(::macrobot_interfaces::msg::RgbCandidateCrop::_color_image_height_type arg)
  {
    msg_.color_image_height = std::move(arg);
    return Init_RgbCandidateCrop_source_candidate_count(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_color_image_width
{
public:
  explicit Init_RgbCandidateCrop_color_image_width(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_color_image_height color_image_width(::macrobot_interfaces::msg::RgbCandidateCrop::_color_image_width_type arg)
  {
    msg_.color_image_width = std::move(arg);
    return Init_RgbCandidateCrop_color_image_height(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_proposal_image_height
{
public:
  explicit Init_RgbCandidateCrop_proposal_image_height(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_color_image_width proposal_image_height(::macrobot_interfaces::msg::RgbCandidateCrop::_proposal_image_height_type arg)
  {
    msg_.proposal_image_height = std::move(arg);
    return Init_RgbCandidateCrop_color_image_width(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_proposal_image_width
{
public:
  explicit Init_RgbCandidateCrop_proposal_image_width(::macrobot_interfaces::msg::RgbCandidateCrop & msg)
  : msg_(msg)
  {}
  Init_RgbCandidateCrop_proposal_image_height proposal_image_width(::macrobot_interfaces::msg::RgbCandidateCrop::_proposal_image_width_type arg)
  {
    msg_.proposal_image_width = std::move(arg);
    return Init_RgbCandidateCrop_proposal_image_height(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

class Init_RgbCandidateCrop_proposal_header
{
public:
  Init_RgbCandidateCrop_proposal_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_RgbCandidateCrop_proposal_image_width proposal_header(::macrobot_interfaces::msg::RgbCandidateCrop::_proposal_header_type arg)
  {
    msg_.proposal_header = std::move(arg);
    return Init_RgbCandidateCrop_proposal_image_width(msg_);
  }

private:
  ::macrobot_interfaces::msg::RgbCandidateCrop msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::macrobot_interfaces::msg::RgbCandidateCrop>()
{
  return macrobot_interfaces::msg::builder::Init_RgbCandidateCrop_proposal_header();
}

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__RGB_CANDIDATE_CROP__BUILDER_HPP_
