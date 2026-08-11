// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from macrobot_interfaces:msg/TemporalConfirmationResult.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/temporal_confirmation_result.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__TEMPORAL_CONFIRMATION_RESULT__TRAITS_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__TEMPORAL_CONFIRMATION_RESULT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "macrobot_interfaces/msg/detail/temporal_confirmation_result__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'roi'
#include "sensor_msgs/msg/detail/region_of_interest__traits.hpp"
// Member 'latest_result'
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__traits.hpp"

namespace macrobot_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const TemporalConfirmationResult & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: target_object
  {
    out << "target_object: ";
    rosidl_generator_traits::value_to_yaml(msg.target_object, out);
    out << ", ";
  }

  // member: track_id
  {
    out << "track_id: ";
    rosidl_generator_traits::value_to_yaml(msg.track_id, out);
    out << ", ";
  }

  // member: frame_index
  {
    out << "frame_index: ";
    rosidl_generator_traits::value_to_yaml(msg.frame_index, out);
    out << ", ";
  }

  // member: state
  {
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << ", ";
  }

  // member: event
  {
    out << "event: ";
    rosidl_generator_traits::value_to_yaml(msg.event, out);
    out << ", ";
  }

  // member: confirmed
  {
    out << "confirmed: ";
    rosidl_generator_traits::value_to_yaml(msg.confirmed, out);
    out << ", ";
  }

  // member: track_age_frames
  {
    out << "track_age_frames: ";
    rosidl_generator_traits::value_to_yaml(msg.track_age_frames, out);
    out << ", ";
  }

  // member: window_size
  {
    out << "window_size: ";
    rosidl_generator_traits::value_to_yaml(msg.window_size, out);
    out << ", ";
  }

  // member: required_hits
  {
    out << "required_hits: ";
    rosidl_generator_traits::value_to_yaml(msg.required_hits, out);
    out << ", ";
  }

  // member: samples_in_window
  {
    out << "samples_in_window: ";
    rosidl_generator_traits::value_to_yaml(msg.samples_in_window, out);
    out << ", ";
  }

  // member: matched_frames_in_window
  {
    out << "matched_frames_in_window: ";
    rosidl_generator_traits::value_to_yaml(msg.matched_frames_in_window, out);
    out << ", ";
  }

  // member: hits_in_window
  {
    out << "hits_in_window: ";
    rosidl_generator_traits::value_to_yaml(msg.hits_in_window, out);
    out << ", ";
  }

  // member: misses_in_window
  {
    out << "misses_in_window: ";
    rosidl_generator_traits::value_to_yaml(msg.misses_in_window, out);
    out << ", ";
  }

  // member: consecutive_hits
  {
    out << "consecutive_hits: ";
    rosidl_generator_traits::value_to_yaml(msg.consecutive_hits, out);
    out << ", ";
  }

  // member: consecutive_misses
  {
    out << "consecutive_misses: ";
    rosidl_generator_traits::value_to_yaml(msg.consecutive_misses, out);
    out << ", ";
  }

  // member: hit_ratio
  {
    out << "hit_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.hit_ratio, out);
    out << ", ";
  }

  // member: temporal_score
  {
    out << "temporal_score: ";
    rosidl_generator_traits::value_to_yaml(msg.temporal_score, out);
    out << ", ";
  }

  // member: stability_score
  {
    out << "stability_score: ";
    rosidl_generator_traits::value_to_yaml(msg.stability_score, out);
    out << ", ";
  }

  // member: mean_positive_similarity
  {
    out << "mean_positive_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.mean_positive_similarity, out);
    out << ", ";
  }

  // member: mean_negative_similarity
  {
    out << "mean_negative_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.mean_negative_similarity, out);
    out << ", ";
  }

  // member: mean_margin
  {
    out << "mean_margin: ";
    rosidl_generator_traits::value_to_yaml(msg.mean_margin, out);
    out << ", ";
  }

  // member: min_margin_in_window
  {
    out << "min_margin_in_window: ";
    rosidl_generator_traits::value_to_yaml(msg.min_margin_in_window, out);
    out << ", ";
  }

  // member: mean_objectness_score
  {
    out << "mean_objectness_score: ";
    rosidl_generator_traits::value_to_yaml(msg.mean_objectness_score, out);
    out << ", ";
  }

  // member: roi
  {
    out << "roi: ";
    to_flow_style_yaml(msg.roi, out);
    out << ", ";
  }

  // member: center_x
  {
    out << "center_x: ";
    rosidl_generator_traits::value_to_yaml(msg.center_x, out);
    out << ", ";
  }

  // member: center_y
  {
    out << "center_y: ";
    rosidl_generator_traits::value_to_yaml(msg.center_y, out);
    out << ", ";
  }

  // member: depth_m
  {
    out << "depth_m: ";
    rosidl_generator_traits::value_to_yaml(msg.depth_m, out);
    out << ", ";
  }

  // member: center_std_px
  {
    out << "center_std_px: ";
    rosidl_generator_traits::value_to_yaml(msg.center_std_px, out);
    out << ", ";
  }

  // member: depth_std_m
  {
    out << "depth_std_m: ";
    rosidl_generator_traits::value_to_yaml(msg.depth_std_m, out);
    out << ", ";
  }

  // member: horizontal_error_norm
  {
    out << "horizontal_error_norm: ";
    rosidl_generator_traits::value_to_yaml(msg.horizontal_error_norm, out);
    out << ", ";
  }

  // member: suggested_turn
  {
    out << "suggested_turn: ";
    rosidl_generator_traits::value_to_yaml(msg.suggested_turn, out);
    out << ", ";
  }

  // member: latest_result
  {
    out << "latest_result: ";
    to_flow_style_yaml(msg.latest_result, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TemporalConfirmationResult & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: target_object
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "target_object: ";
    rosidl_generator_traits::value_to_yaml(msg.target_object, out);
    out << "\n";
  }

  // member: track_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "track_id: ";
    rosidl_generator_traits::value_to_yaml(msg.track_id, out);
    out << "\n";
  }

  // member: frame_index
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "frame_index: ";
    rosidl_generator_traits::value_to_yaml(msg.frame_index, out);
    out << "\n";
  }

  // member: state
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << "\n";
  }

  // member: event
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "event: ";
    rosidl_generator_traits::value_to_yaml(msg.event, out);
    out << "\n";
  }

  // member: confirmed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "confirmed: ";
    rosidl_generator_traits::value_to_yaml(msg.confirmed, out);
    out << "\n";
  }

  // member: track_age_frames
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "track_age_frames: ";
    rosidl_generator_traits::value_to_yaml(msg.track_age_frames, out);
    out << "\n";
  }

  // member: window_size
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "window_size: ";
    rosidl_generator_traits::value_to_yaml(msg.window_size, out);
    out << "\n";
  }

  // member: required_hits
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "required_hits: ";
    rosidl_generator_traits::value_to_yaml(msg.required_hits, out);
    out << "\n";
  }

  // member: samples_in_window
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "samples_in_window: ";
    rosidl_generator_traits::value_to_yaml(msg.samples_in_window, out);
    out << "\n";
  }

  // member: matched_frames_in_window
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "matched_frames_in_window: ";
    rosidl_generator_traits::value_to_yaml(msg.matched_frames_in_window, out);
    out << "\n";
  }

  // member: hits_in_window
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "hits_in_window: ";
    rosidl_generator_traits::value_to_yaml(msg.hits_in_window, out);
    out << "\n";
  }

  // member: misses_in_window
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "misses_in_window: ";
    rosidl_generator_traits::value_to_yaml(msg.misses_in_window, out);
    out << "\n";
  }

  // member: consecutive_hits
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "consecutive_hits: ";
    rosidl_generator_traits::value_to_yaml(msg.consecutive_hits, out);
    out << "\n";
  }

  // member: consecutive_misses
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "consecutive_misses: ";
    rosidl_generator_traits::value_to_yaml(msg.consecutive_misses, out);
    out << "\n";
  }

  // member: hit_ratio
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "hit_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.hit_ratio, out);
    out << "\n";
  }

  // member: temporal_score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "temporal_score: ";
    rosidl_generator_traits::value_to_yaml(msg.temporal_score, out);
    out << "\n";
  }

  // member: stability_score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stability_score: ";
    rosidl_generator_traits::value_to_yaml(msg.stability_score, out);
    out << "\n";
  }

  // member: mean_positive_similarity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mean_positive_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.mean_positive_similarity, out);
    out << "\n";
  }

  // member: mean_negative_similarity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mean_negative_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.mean_negative_similarity, out);
    out << "\n";
  }

  // member: mean_margin
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mean_margin: ";
    rosidl_generator_traits::value_to_yaml(msg.mean_margin, out);
    out << "\n";
  }

  // member: min_margin_in_window
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "min_margin_in_window: ";
    rosidl_generator_traits::value_to_yaml(msg.min_margin_in_window, out);
    out << "\n";
  }

  // member: mean_objectness_score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mean_objectness_score: ";
    rosidl_generator_traits::value_to_yaml(msg.mean_objectness_score, out);
    out << "\n";
  }

  // member: roi
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "roi:\n";
    to_block_style_yaml(msg.roi, out, indentation + 2);
  }

  // member: center_x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "center_x: ";
    rosidl_generator_traits::value_to_yaml(msg.center_x, out);
    out << "\n";
  }

  // member: center_y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "center_y: ";
    rosidl_generator_traits::value_to_yaml(msg.center_y, out);
    out << "\n";
  }

  // member: depth_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "depth_m: ";
    rosidl_generator_traits::value_to_yaml(msg.depth_m, out);
    out << "\n";
  }

  // member: center_std_px
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "center_std_px: ";
    rosidl_generator_traits::value_to_yaml(msg.center_std_px, out);
    out << "\n";
  }

  // member: depth_std_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "depth_std_m: ";
    rosidl_generator_traits::value_to_yaml(msg.depth_std_m, out);
    out << "\n";
  }

  // member: horizontal_error_norm
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "horizontal_error_norm: ";
    rosidl_generator_traits::value_to_yaml(msg.horizontal_error_norm, out);
    out << "\n";
  }

  // member: suggested_turn
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "suggested_turn: ";
    rosidl_generator_traits::value_to_yaml(msg.suggested_turn, out);
    out << "\n";
  }

  // member: latest_result
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "latest_result:\n";
    to_block_style_yaml(msg.latest_result, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TemporalConfirmationResult & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace macrobot_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use macrobot_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const macrobot_interfaces::msg::TemporalConfirmationResult & msg,
  std::ostream & out, size_t indentation = 0)
{
  macrobot_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use macrobot_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const macrobot_interfaces::msg::TemporalConfirmationResult & msg)
{
  return macrobot_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<macrobot_interfaces::msg::TemporalConfirmationResult>()
{
  return "macrobot_interfaces::msg::TemporalConfirmationResult";
}

template<>
inline const char * name<macrobot_interfaces::msg::TemporalConfirmationResult>()
{
  return "macrobot_interfaces/msg/TemporalConfirmationResult";
}

template<>
struct has_fixed_size<macrobot_interfaces::msg::TemporalConfirmationResult>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<macrobot_interfaces::msg::TemporalConfirmationResult>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<macrobot_interfaces::msg::TemporalConfirmationResult>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__TEMPORAL_CONFIRMATION_RESULT__TRAITS_HPP_
