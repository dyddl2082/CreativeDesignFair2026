// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from macrobot_interfaces:msg/TemporalConfirmationResult.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/temporal_confirmation_result.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__TEMPORAL_CONFIRMATION_RESULT__BUILDER_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__TEMPORAL_CONFIRMATION_RESULT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "macrobot_interfaces/msg/detail/temporal_confirmation_result__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace macrobot_interfaces
{

namespace msg
{

namespace builder
{

class Init_TemporalConfirmationResult_latest_result
{
public:
  explicit Init_TemporalConfirmationResult_latest_result(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  ::macrobot_interfaces::msg::TemporalConfirmationResult latest_result(::macrobot_interfaces::msg::TemporalConfirmationResult::_latest_result_type arg)
  {
    msg_.latest_result = std::move(arg);
    return std::move(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_suggested_turn
{
public:
  explicit Init_TemporalConfirmationResult_suggested_turn(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_latest_result suggested_turn(::macrobot_interfaces::msg::TemporalConfirmationResult::_suggested_turn_type arg)
  {
    msg_.suggested_turn = std::move(arg);
    return Init_TemporalConfirmationResult_latest_result(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_horizontal_error_norm
{
public:
  explicit Init_TemporalConfirmationResult_horizontal_error_norm(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_suggested_turn horizontal_error_norm(::macrobot_interfaces::msg::TemporalConfirmationResult::_horizontal_error_norm_type arg)
  {
    msg_.horizontal_error_norm = std::move(arg);
    return Init_TemporalConfirmationResult_suggested_turn(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_depth_std_m
{
public:
  explicit Init_TemporalConfirmationResult_depth_std_m(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_horizontal_error_norm depth_std_m(::macrobot_interfaces::msg::TemporalConfirmationResult::_depth_std_m_type arg)
  {
    msg_.depth_std_m = std::move(arg);
    return Init_TemporalConfirmationResult_horizontal_error_norm(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_center_std_px
{
public:
  explicit Init_TemporalConfirmationResult_center_std_px(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_depth_std_m center_std_px(::macrobot_interfaces::msg::TemporalConfirmationResult::_center_std_px_type arg)
  {
    msg_.center_std_px = std::move(arg);
    return Init_TemporalConfirmationResult_depth_std_m(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_depth_m
{
public:
  explicit Init_TemporalConfirmationResult_depth_m(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_center_std_px depth_m(::macrobot_interfaces::msg::TemporalConfirmationResult::_depth_m_type arg)
  {
    msg_.depth_m = std::move(arg);
    return Init_TemporalConfirmationResult_center_std_px(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_center_y
{
public:
  explicit Init_TemporalConfirmationResult_center_y(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_depth_m center_y(::macrobot_interfaces::msg::TemporalConfirmationResult::_center_y_type arg)
  {
    msg_.center_y = std::move(arg);
    return Init_TemporalConfirmationResult_depth_m(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_center_x
{
public:
  explicit Init_TemporalConfirmationResult_center_x(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_center_y center_x(::macrobot_interfaces::msg::TemporalConfirmationResult::_center_x_type arg)
  {
    msg_.center_x = std::move(arg);
    return Init_TemporalConfirmationResult_center_y(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_roi
{
public:
  explicit Init_TemporalConfirmationResult_roi(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_center_x roi(::macrobot_interfaces::msg::TemporalConfirmationResult::_roi_type arg)
  {
    msg_.roi = std::move(arg);
    return Init_TemporalConfirmationResult_center_x(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_mean_objectness_score
{
public:
  explicit Init_TemporalConfirmationResult_mean_objectness_score(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_roi mean_objectness_score(::macrobot_interfaces::msg::TemporalConfirmationResult::_mean_objectness_score_type arg)
  {
    msg_.mean_objectness_score = std::move(arg);
    return Init_TemporalConfirmationResult_roi(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_min_margin_in_window
{
public:
  explicit Init_TemporalConfirmationResult_min_margin_in_window(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_mean_objectness_score min_margin_in_window(::macrobot_interfaces::msg::TemporalConfirmationResult::_min_margin_in_window_type arg)
  {
    msg_.min_margin_in_window = std::move(arg);
    return Init_TemporalConfirmationResult_mean_objectness_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_mean_margin
{
public:
  explicit Init_TemporalConfirmationResult_mean_margin(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_min_margin_in_window mean_margin(::macrobot_interfaces::msg::TemporalConfirmationResult::_mean_margin_type arg)
  {
    msg_.mean_margin = std::move(arg);
    return Init_TemporalConfirmationResult_min_margin_in_window(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_mean_negative_similarity
{
public:
  explicit Init_TemporalConfirmationResult_mean_negative_similarity(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_mean_margin mean_negative_similarity(::macrobot_interfaces::msg::TemporalConfirmationResult::_mean_negative_similarity_type arg)
  {
    msg_.mean_negative_similarity = std::move(arg);
    return Init_TemporalConfirmationResult_mean_margin(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_mean_positive_similarity
{
public:
  explicit Init_TemporalConfirmationResult_mean_positive_similarity(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_mean_negative_similarity mean_positive_similarity(::macrobot_interfaces::msg::TemporalConfirmationResult::_mean_positive_similarity_type arg)
  {
    msg_.mean_positive_similarity = std::move(arg);
    return Init_TemporalConfirmationResult_mean_negative_similarity(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_stability_score
{
public:
  explicit Init_TemporalConfirmationResult_stability_score(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_mean_positive_similarity stability_score(::macrobot_interfaces::msg::TemporalConfirmationResult::_stability_score_type arg)
  {
    msg_.stability_score = std::move(arg);
    return Init_TemporalConfirmationResult_mean_positive_similarity(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_temporal_score
{
public:
  explicit Init_TemporalConfirmationResult_temporal_score(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_stability_score temporal_score(::macrobot_interfaces::msg::TemporalConfirmationResult::_temporal_score_type arg)
  {
    msg_.temporal_score = std::move(arg);
    return Init_TemporalConfirmationResult_stability_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_hit_ratio
{
public:
  explicit Init_TemporalConfirmationResult_hit_ratio(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_temporal_score hit_ratio(::macrobot_interfaces::msg::TemporalConfirmationResult::_hit_ratio_type arg)
  {
    msg_.hit_ratio = std::move(arg);
    return Init_TemporalConfirmationResult_temporal_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_consecutive_misses
{
public:
  explicit Init_TemporalConfirmationResult_consecutive_misses(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_hit_ratio consecutive_misses(::macrobot_interfaces::msg::TemporalConfirmationResult::_consecutive_misses_type arg)
  {
    msg_.consecutive_misses = std::move(arg);
    return Init_TemporalConfirmationResult_hit_ratio(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_consecutive_hits
{
public:
  explicit Init_TemporalConfirmationResult_consecutive_hits(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_consecutive_misses consecutive_hits(::macrobot_interfaces::msg::TemporalConfirmationResult::_consecutive_hits_type arg)
  {
    msg_.consecutive_hits = std::move(arg);
    return Init_TemporalConfirmationResult_consecutive_misses(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_misses_in_window
{
public:
  explicit Init_TemporalConfirmationResult_misses_in_window(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_consecutive_hits misses_in_window(::macrobot_interfaces::msg::TemporalConfirmationResult::_misses_in_window_type arg)
  {
    msg_.misses_in_window = std::move(arg);
    return Init_TemporalConfirmationResult_consecutive_hits(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_hits_in_window
{
public:
  explicit Init_TemporalConfirmationResult_hits_in_window(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_misses_in_window hits_in_window(::macrobot_interfaces::msg::TemporalConfirmationResult::_hits_in_window_type arg)
  {
    msg_.hits_in_window = std::move(arg);
    return Init_TemporalConfirmationResult_misses_in_window(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_matched_frames_in_window
{
public:
  explicit Init_TemporalConfirmationResult_matched_frames_in_window(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_hits_in_window matched_frames_in_window(::macrobot_interfaces::msg::TemporalConfirmationResult::_matched_frames_in_window_type arg)
  {
    msg_.matched_frames_in_window = std::move(arg);
    return Init_TemporalConfirmationResult_hits_in_window(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_samples_in_window
{
public:
  explicit Init_TemporalConfirmationResult_samples_in_window(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_matched_frames_in_window samples_in_window(::macrobot_interfaces::msg::TemporalConfirmationResult::_samples_in_window_type arg)
  {
    msg_.samples_in_window = std::move(arg);
    return Init_TemporalConfirmationResult_matched_frames_in_window(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_required_hits
{
public:
  explicit Init_TemporalConfirmationResult_required_hits(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_samples_in_window required_hits(::macrobot_interfaces::msg::TemporalConfirmationResult::_required_hits_type arg)
  {
    msg_.required_hits = std::move(arg);
    return Init_TemporalConfirmationResult_samples_in_window(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_window_size
{
public:
  explicit Init_TemporalConfirmationResult_window_size(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_required_hits window_size(::macrobot_interfaces::msg::TemporalConfirmationResult::_window_size_type arg)
  {
    msg_.window_size = std::move(arg);
    return Init_TemporalConfirmationResult_required_hits(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_track_age_frames
{
public:
  explicit Init_TemporalConfirmationResult_track_age_frames(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_window_size track_age_frames(::macrobot_interfaces::msg::TemporalConfirmationResult::_track_age_frames_type arg)
  {
    msg_.track_age_frames = std::move(arg);
    return Init_TemporalConfirmationResult_window_size(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_confirmed
{
public:
  explicit Init_TemporalConfirmationResult_confirmed(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_track_age_frames confirmed(::macrobot_interfaces::msg::TemporalConfirmationResult::_confirmed_type arg)
  {
    msg_.confirmed = std::move(arg);
    return Init_TemporalConfirmationResult_track_age_frames(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_event
{
public:
  explicit Init_TemporalConfirmationResult_event(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_confirmed event(::macrobot_interfaces::msg::TemporalConfirmationResult::_event_type arg)
  {
    msg_.event = std::move(arg);
    return Init_TemporalConfirmationResult_confirmed(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_state
{
public:
  explicit Init_TemporalConfirmationResult_state(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_event state(::macrobot_interfaces::msg::TemporalConfirmationResult::_state_type arg)
  {
    msg_.state = std::move(arg);
    return Init_TemporalConfirmationResult_event(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_frame_index
{
public:
  explicit Init_TemporalConfirmationResult_frame_index(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_state frame_index(::macrobot_interfaces::msg::TemporalConfirmationResult::_frame_index_type arg)
  {
    msg_.frame_index = std::move(arg);
    return Init_TemporalConfirmationResult_state(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_track_id
{
public:
  explicit Init_TemporalConfirmationResult_track_id(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_frame_index track_id(::macrobot_interfaces::msg::TemporalConfirmationResult::_track_id_type arg)
  {
    msg_.track_id = std::move(arg);
    return Init_TemporalConfirmationResult_frame_index(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_target_object
{
public:
  explicit Init_TemporalConfirmationResult_target_object(::macrobot_interfaces::msg::TemporalConfirmationResult & msg)
  : msg_(msg)
  {}
  Init_TemporalConfirmationResult_track_id target_object(::macrobot_interfaces::msg::TemporalConfirmationResult::_target_object_type arg)
  {
    msg_.target_object = std::move(arg);
    return Init_TemporalConfirmationResult_track_id(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

class Init_TemporalConfirmationResult_header
{
public:
  Init_TemporalConfirmationResult_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TemporalConfirmationResult_target_object header(::macrobot_interfaces::msg::TemporalConfirmationResult::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_TemporalConfirmationResult_target_object(msg_);
  }

private:
  ::macrobot_interfaces::msg::TemporalConfirmationResult msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::macrobot_interfaces::msg::TemporalConfirmationResult>()
{
  return macrobot_interfaces::msg::builder::Init_TemporalConfirmationResult_header();
}

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__TEMPORAL_CONFIRMATION_RESULT__BUILDER_HPP_
