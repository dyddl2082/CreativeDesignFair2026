// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from macrobot_interfaces:msg/CandidateFilterResult.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/candidate_filter_result.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__CANDIDATE_FILTER_RESULT__BUILDER_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__CANDIDATE_FILTER_RESULT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "macrobot_interfaces/msg/detail/candidate_filter_result__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace macrobot_interfaces
{

namespace msg
{

namespace builder
{

class Init_CandidateFilterResult_crop_roi
{
public:
  explicit Init_CandidateFilterResult_crop_roi(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  ::macrobot_interfaces::msg::CandidateFilterResult crop_roi(::macrobot_interfaces::msg::CandidateFilterResult::_crop_roi_type arg)
  {
    msg_.crop_roi = std::move(arg);
    return std::move(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_candidate
{
public:
  explicit Init_CandidateFilterResult_candidate(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_crop_roi candidate(::macrobot_interfaces::msg::CandidateFilterResult::_candidate_type arg)
  {
    msg_.candidate = std::move(arg);
    return Init_CandidateFilterResult_crop_roi(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_sync_offset_abs_sec
{
public:
  explicit Init_CandidateFilterResult_sync_offset_abs_sec(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_candidate sync_offset_abs_sec(::macrobot_interfaces::msg::CandidateFilterResult::_sync_offset_abs_sec_type arg)
  {
    msg_.sync_offset_abs_sec = std::move(arg);
    return Init_CandidateFilterResult_candidate(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_estimated_height_m
{
public:
  explicit Init_CandidateFilterResult_estimated_height_m(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_sync_offset_abs_sec estimated_height_m(::macrobot_interfaces::msg::CandidateFilterResult::_estimated_height_m_type arg)
  {
    msg_.estimated_height_m = std::move(arg);
    return Init_CandidateFilterResult_sync_offset_abs_sec(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_estimated_width_m
{
public:
  explicit Init_CandidateFilterResult_estimated_width_m(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_estimated_height_m estimated_width_m(::macrobot_interfaces::msg::CandidateFilterResult::_estimated_width_m_type arg)
  {
    msg_.estimated_width_m = std::move(arg);
    return Init_CandidateFilterResult_estimated_height_m(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_aspect_ratio
{
public:
  explicit Init_CandidateFilterResult_aspect_ratio(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_estimated_width_m aspect_ratio(::macrobot_interfaces::msg::CandidateFilterResult::_aspect_ratio_type arg)
  {
    msg_.aspect_ratio = std::move(arg);
    return Init_CandidateFilterResult_estimated_width_m(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_color_similarity
{
public:
  explicit Init_CandidateFilterResult_color_similarity(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_aspect_ratio color_similarity(::macrobot_interfaces::msg::CandidateFilterResult::_color_similarity_type arg)
  {
    msg_.color_similarity = std::move(arg);
    return Init_CandidateFilterResult_aspect_ratio(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_mask_solidity
{
public:
  explicit Init_CandidateFilterResult_mask_solidity(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_color_similarity mask_solidity(::macrobot_interfaces::msg::CandidateFilterResult::_mask_solidity_type arg)
  {
    msg_.mask_solidity = std::move(arg);
    return Init_CandidateFilterResult_color_similarity(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_mask_fill_ratio
{
public:
  explicit Init_CandidateFilterResult_mask_fill_ratio(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_mask_solidity mask_fill_ratio(::macrobot_interfaces::msg::CandidateFilterResult::_mask_fill_ratio_type arg)
  {
    msg_.mask_fill_ratio = std::move(arg);
    return Init_CandidateFilterResult_mask_solidity(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_edge_density
{
public:
  explicit Init_CandidateFilterResult_edge_density(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_mask_fill_ratio edge_density(::macrobot_interfaces::msg::CandidateFilterResult::_edge_density_type arg)
  {
    msg_.edge_density = std::move(arg);
    return Init_CandidateFilterResult_mask_fill_ratio(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_bright_clip_ratio
{
public:
  explicit Init_CandidateFilterResult_bright_clip_ratio(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_edge_density bright_clip_ratio(::macrobot_interfaces::msg::CandidateFilterResult::_bright_clip_ratio_type arg)
  {
    msg_.bright_clip_ratio = std::move(arg);
    return Init_CandidateFilterResult_edge_density(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_dark_ratio
{
public:
  explicit Init_CandidateFilterResult_dark_ratio(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_bright_clip_ratio dark_ratio(::macrobot_interfaces::msg::CandidateFilterResult::_dark_ratio_type arg)
  {
    msg_.dark_ratio = std::move(arg);
    return Init_CandidateFilterResult_bright_clip_ratio(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_mean_brightness
{
public:
  explicit Init_CandidateFilterResult_mean_brightness(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_dark_ratio mean_brightness(::macrobot_interfaces::msg::CandidateFilterResult::_mean_brightness_type arg)
  {
    msg_.mean_brightness = std::move(arg);
    return Init_CandidateFilterResult_dark_ratio(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_sharpness
{
public:
  explicit Init_CandidateFilterResult_sharpness(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_mean_brightness sharpness(::macrobot_interfaces::msg::CandidateFilterResult::_sharpness_type arg)
  {
    msg_.sharpness = std::move(arg);
    return Init_CandidateFilterResult_mean_brightness(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_physical_size_score
{
public:
  explicit Init_CandidateFilterResult_physical_size_score(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_sharpness physical_size_score(::macrobot_interfaces::msg::CandidateFilterResult::_physical_size_score_type arg)
  {
    msg_.physical_size_score = std::move(arg);
    return Init_CandidateFilterResult_sharpness(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_shape_score
{
public:
  explicit Init_CandidateFilterResult_shape_score(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_physical_size_score shape_score(::macrobot_interfaces::msg::CandidateFilterResult::_shape_score_type arg)
  {
    msg_.shape_score = std::move(arg);
    return Init_CandidateFilterResult_physical_size_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_color_score
{
public:
  explicit Init_CandidateFilterResult_color_score(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_shape_score color_score(::macrobot_interfaces::msg::CandidateFilterResult::_color_score_type arg)
  {
    msg_.color_score = std::move(arg);
    return Init_CandidateFilterResult_shape_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_quality_score
{
public:
  explicit Init_CandidateFilterResult_quality_score(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_color_score quality_score(::macrobot_interfaces::msg::CandidateFilterResult::_quality_score_type arg)
  {
    msg_.quality_score = std::move(arg);
    return Init_CandidateFilterResult_color_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_depth_score
{
public:
  explicit Init_CandidateFilterResult_depth_score(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_quality_score depth_score(::macrobot_interfaces::msg::CandidateFilterResult::_depth_score_type arg)
  {
    msg_.depth_score = std::move(arg);
    return Init_CandidateFilterResult_quality_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_filter_score
{
public:
  explicit Init_CandidateFilterResult_filter_score(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_depth_score filter_score(::macrobot_interfaces::msg::CandidateFilterResult::_filter_score_type arg)
  {
    msg_.filter_score = std::move(arg);
    return Init_CandidateFilterResult_depth_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_target_hint_score
{
public:
  explicit Init_CandidateFilterResult_target_hint_score(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_filter_score target_hint_score(::macrobot_interfaces::msg::CandidateFilterResult::_target_hint_score_type arg)
  {
    msg_.target_hint_score = std::move(arg);
    return Init_CandidateFilterResult_filter_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_objectness_score
{
public:
  explicit Init_CandidateFilterResult_objectness_score(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_target_hint_score objectness_score(::macrobot_interfaces::msg::CandidateFilterResult::_objectness_score_type arg)
  {
    msg_.objectness_score = std::move(arg);
    return Init_CandidateFilterResult_target_hint_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_reject_reason
{
public:
  explicit Init_CandidateFilterResult_reject_reason(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_objectness_score reject_reason(::macrobot_interfaces::msg::CandidateFilterResult::_reject_reason_type arg)
  {
    msg_.reject_reason = std::move(arg);
    return Init_CandidateFilterResult_objectness_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_reject_stage
{
public:
  explicit Init_CandidateFilterResult_reject_stage(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_reject_reason reject_stage(::macrobot_interfaces::msg::CandidateFilterResult::_reject_stage_type arg)
  {
    msg_.reject_stage = std::move(arg);
    return Init_CandidateFilterResult_reject_reason(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_accepted
{
public:
  explicit Init_CandidateFilterResult_accepted(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_reject_stage accepted(::macrobot_interfaces::msg::CandidateFilterResult::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_CandidateFilterResult_reject_stage(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_foreground_mask_available
{
public:
  explicit Init_CandidateFilterResult_foreground_mask_available(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_accepted foreground_mask_available(::macrobot_interfaces::msg::CandidateFilterResult::_foreground_mask_available_type arg)
  {
    msg_.foreground_mask_available = std::move(arg);
    return Init_CandidateFilterResult_accepted(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_foreground_height_valid
{
public:
  explicit Init_CandidateFilterResult_foreground_height_valid(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_foreground_mask_available foreground_height_valid(::macrobot_interfaces::msg::CandidateFilterResult::_foreground_height_valid_type arg)
  {
    msg_.foreground_height_valid = std::move(arg);
    return Init_CandidateFilterResult_foreground_mask_available(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_plane_found
{
public:
  explicit Init_CandidateFilterResult_plane_found(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_foreground_height_valid plane_found(::macrobot_interfaces::msg::CandidateFilterResult::_plane_found_type arg)
  {
    msg_.plane_found = std::move(arg);
    return Init_CandidateFilterResult_foreground_height_valid(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_camera_info_available
{
public:
  explicit Init_CandidateFilterResult_camera_info_available(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_plane_found camera_info_available(::macrobot_interfaces::msg::CandidateFilterResult::_camera_info_available_type arg)
  {
    msg_.camera_info_available = std::move(arg);
    return Init_CandidateFilterResult_plane_found(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_reference_image_count
{
public:
  explicit Init_CandidateFilterResult_reference_image_count(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_camera_info_available reference_image_count(::macrobot_interfaces::msg::CandidateFilterResult::_reference_image_count_type arg)
  {
    msg_.reference_image_count = std::move(arg);
    return Init_CandidateFilterResult_camera_info_available(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_reference_profile_available
{
public:
  explicit Init_CandidateFilterResult_reference_profile_available(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_reference_image_count reference_profile_available(::macrobot_interfaces::msg::CandidateFilterResult::_reference_profile_available_type arg)
  {
    msg_.reference_profile_available = std::move(arg);
    return Init_CandidateFilterResult_reference_image_count(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_target_object
{
public:
  explicit Init_CandidateFilterResult_target_object(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_reference_profile_available target_object(::macrobot_interfaces::msg::CandidateFilterResult::_target_object_type arg)
  {
    msg_.target_object = std::move(arg);
    return Init_CandidateFilterResult_reference_profile_available(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_frame_crop_count
{
public:
  explicit Init_CandidateFilterResult_frame_crop_count(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_target_object frame_crop_count(::macrobot_interfaces::msg::CandidateFilterResult::_frame_crop_count_type arg)
  {
    msg_.frame_crop_count = std::move(arg);
    return Init_CandidateFilterResult_target_object(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_crop_index
{
public:
  explicit Init_CandidateFilterResult_crop_index(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_frame_crop_count crop_index(::macrobot_interfaces::msg::CandidateFilterResult::_crop_index_type arg)
  {
    msg_.crop_index = std::move(arg);
    return Init_CandidateFilterResult_frame_crop_count(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_candidate_id
{
public:
  explicit Init_CandidateFilterResult_candidate_id(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_crop_index candidate_id(::macrobot_interfaces::msg::CandidateFilterResult::_candidate_id_type arg)
  {
    msg_.candidate_id = std::move(arg);
    return Init_CandidateFilterResult_crop_index(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_image_header
{
public:
  explicit Init_CandidateFilterResult_image_header(::macrobot_interfaces::msg::CandidateFilterResult & msg)
  : msg_(msg)
  {}
  Init_CandidateFilterResult_candidate_id image_header(::macrobot_interfaces::msg::CandidateFilterResult::_image_header_type arg)
  {
    msg_.image_header = std::move(arg);
    return Init_CandidateFilterResult_candidate_id(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

class Init_CandidateFilterResult_proposal_header
{
public:
  Init_CandidateFilterResult_proposal_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CandidateFilterResult_image_header proposal_header(::macrobot_interfaces::msg::CandidateFilterResult::_proposal_header_type arg)
  {
    msg_.proposal_header = std::move(arg);
    return Init_CandidateFilterResult_image_header(msg_);
  }

private:
  ::macrobot_interfaces::msg::CandidateFilterResult msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::macrobot_interfaces::msg::CandidateFilterResult>()
{
  return macrobot_interfaces::msg::builder::Init_CandidateFilterResult_proposal_header();
}

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__CANDIDATE_FILTER_RESULT__BUILDER_HPP_
