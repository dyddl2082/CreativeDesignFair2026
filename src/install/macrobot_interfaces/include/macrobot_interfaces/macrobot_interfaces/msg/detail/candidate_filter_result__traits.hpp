// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from macrobot_interfaces:msg/CandidateFilterResult.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/candidate_filter_result.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__CANDIDATE_FILTER_RESULT__TRAITS_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__CANDIDATE_FILTER_RESULT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "macrobot_interfaces/msg/detail/candidate_filter_result__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'proposal_header'
// Member 'image_header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'candidate'
#include "macrobot_interfaces/msg/detail/depth_candidate__traits.hpp"
// Member 'crop_roi'
#include "sensor_msgs/msg/detail/region_of_interest__traits.hpp"

namespace macrobot_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const CandidateFilterResult & msg,
  std::ostream & out)
{
  out << "{";
  // member: proposal_header
  {
    out << "proposal_header: ";
    to_flow_style_yaml(msg.proposal_header, out);
    out << ", ";
  }

  // member: image_header
  {
    out << "image_header: ";
    to_flow_style_yaml(msg.image_header, out);
    out << ", ";
  }

  // member: candidate_id
  {
    out << "candidate_id: ";
    rosidl_generator_traits::value_to_yaml(msg.candidate_id, out);
    out << ", ";
  }

  // member: crop_index
  {
    out << "crop_index: ";
    rosidl_generator_traits::value_to_yaml(msg.crop_index, out);
    out << ", ";
  }

  // member: frame_crop_count
  {
    out << "frame_crop_count: ";
    rosidl_generator_traits::value_to_yaml(msg.frame_crop_count, out);
    out << ", ";
  }

  // member: target_object
  {
    out << "target_object: ";
    rosidl_generator_traits::value_to_yaml(msg.target_object, out);
    out << ", ";
  }

  // member: reference_profile_available
  {
    out << "reference_profile_available: ";
    rosidl_generator_traits::value_to_yaml(msg.reference_profile_available, out);
    out << ", ";
  }

  // member: reference_image_count
  {
    out << "reference_image_count: ";
    rosidl_generator_traits::value_to_yaml(msg.reference_image_count, out);
    out << ", ";
  }

  // member: camera_info_available
  {
    out << "camera_info_available: ";
    rosidl_generator_traits::value_to_yaml(msg.camera_info_available, out);
    out << ", ";
  }

  // member: plane_found
  {
    out << "plane_found: ";
    rosidl_generator_traits::value_to_yaml(msg.plane_found, out);
    out << ", ";
  }

  // member: foreground_height_valid
  {
    out << "foreground_height_valid: ";
    rosidl_generator_traits::value_to_yaml(msg.foreground_height_valid, out);
    out << ", ";
  }

  // member: foreground_mask_available
  {
    out << "foreground_mask_available: ";
    rosidl_generator_traits::value_to_yaml(msg.foreground_mask_available, out);
    out << ", ";
  }

  // member: accepted
  {
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << ", ";
  }

  // member: reject_stage
  {
    out << "reject_stage: ";
    rosidl_generator_traits::value_to_yaml(msg.reject_stage, out);
    out << ", ";
  }

  // member: reject_reason
  {
    out << "reject_reason: ";
    rosidl_generator_traits::value_to_yaml(msg.reject_reason, out);
    out << ", ";
  }

  // member: objectness_score
  {
    out << "objectness_score: ";
    rosidl_generator_traits::value_to_yaml(msg.objectness_score, out);
    out << ", ";
  }

  // member: target_hint_score
  {
    out << "target_hint_score: ";
    rosidl_generator_traits::value_to_yaml(msg.target_hint_score, out);
    out << ", ";
  }

  // member: filter_score
  {
    out << "filter_score: ";
    rosidl_generator_traits::value_to_yaml(msg.filter_score, out);
    out << ", ";
  }

  // member: depth_score
  {
    out << "depth_score: ";
    rosidl_generator_traits::value_to_yaml(msg.depth_score, out);
    out << ", ";
  }

  // member: quality_score
  {
    out << "quality_score: ";
    rosidl_generator_traits::value_to_yaml(msg.quality_score, out);
    out << ", ";
  }

  // member: color_score
  {
    out << "color_score: ";
    rosidl_generator_traits::value_to_yaml(msg.color_score, out);
    out << ", ";
  }

  // member: shape_score
  {
    out << "shape_score: ";
    rosidl_generator_traits::value_to_yaml(msg.shape_score, out);
    out << ", ";
  }

  // member: physical_size_score
  {
    out << "physical_size_score: ";
    rosidl_generator_traits::value_to_yaml(msg.physical_size_score, out);
    out << ", ";
  }

  // member: sharpness
  {
    out << "sharpness: ";
    rosidl_generator_traits::value_to_yaml(msg.sharpness, out);
    out << ", ";
  }

  // member: mean_brightness
  {
    out << "mean_brightness: ";
    rosidl_generator_traits::value_to_yaml(msg.mean_brightness, out);
    out << ", ";
  }

  // member: dark_ratio
  {
    out << "dark_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.dark_ratio, out);
    out << ", ";
  }

  // member: bright_clip_ratio
  {
    out << "bright_clip_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.bright_clip_ratio, out);
    out << ", ";
  }

  // member: edge_density
  {
    out << "edge_density: ";
    rosidl_generator_traits::value_to_yaml(msg.edge_density, out);
    out << ", ";
  }

  // member: mask_fill_ratio
  {
    out << "mask_fill_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.mask_fill_ratio, out);
    out << ", ";
  }

  // member: mask_solidity
  {
    out << "mask_solidity: ";
    rosidl_generator_traits::value_to_yaml(msg.mask_solidity, out);
    out << ", ";
  }

  // member: color_similarity
  {
    out << "color_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.color_similarity, out);
    out << ", ";
  }

  // member: aspect_ratio
  {
    out << "aspect_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.aspect_ratio, out);
    out << ", ";
  }

  // member: estimated_width_m
  {
    out << "estimated_width_m: ";
    rosidl_generator_traits::value_to_yaml(msg.estimated_width_m, out);
    out << ", ";
  }

  // member: estimated_height_m
  {
    out << "estimated_height_m: ";
    rosidl_generator_traits::value_to_yaml(msg.estimated_height_m, out);
    out << ", ";
  }

  // member: sync_offset_abs_sec
  {
    out << "sync_offset_abs_sec: ";
    rosidl_generator_traits::value_to_yaml(msg.sync_offset_abs_sec, out);
    out << ", ";
  }

  // member: candidate
  {
    out << "candidate: ";
    to_flow_style_yaml(msg.candidate, out);
    out << ", ";
  }

  // member: crop_roi
  {
    out << "crop_roi: ";
    to_flow_style_yaml(msg.crop_roi, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CandidateFilterResult & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: proposal_header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "proposal_header:\n";
    to_block_style_yaml(msg.proposal_header, out, indentation + 2);
  }

  // member: image_header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "image_header:\n";
    to_block_style_yaml(msg.image_header, out, indentation + 2);
  }

  // member: candidate_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "candidate_id: ";
    rosidl_generator_traits::value_to_yaml(msg.candidate_id, out);
    out << "\n";
  }

  // member: crop_index
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "crop_index: ";
    rosidl_generator_traits::value_to_yaml(msg.crop_index, out);
    out << "\n";
  }

  // member: frame_crop_count
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "frame_crop_count: ";
    rosidl_generator_traits::value_to_yaml(msg.frame_crop_count, out);
    out << "\n";
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

  // member: reference_profile_available
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "reference_profile_available: ";
    rosidl_generator_traits::value_to_yaml(msg.reference_profile_available, out);
    out << "\n";
  }

  // member: reference_image_count
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "reference_image_count: ";
    rosidl_generator_traits::value_to_yaml(msg.reference_image_count, out);
    out << "\n";
  }

  // member: camera_info_available
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "camera_info_available: ";
    rosidl_generator_traits::value_to_yaml(msg.camera_info_available, out);
    out << "\n";
  }

  // member: plane_found
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "plane_found: ";
    rosidl_generator_traits::value_to_yaml(msg.plane_found, out);
    out << "\n";
  }

  // member: foreground_height_valid
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "foreground_height_valid: ";
    rosidl_generator_traits::value_to_yaml(msg.foreground_height_valid, out);
    out << "\n";
  }

  // member: foreground_mask_available
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "foreground_mask_available: ";
    rosidl_generator_traits::value_to_yaml(msg.foreground_mask_available, out);
    out << "\n";
  }

  // member: accepted
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << "\n";
  }

  // member: reject_stage
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "reject_stage: ";
    rosidl_generator_traits::value_to_yaml(msg.reject_stage, out);
    out << "\n";
  }

  // member: reject_reason
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "reject_reason: ";
    rosidl_generator_traits::value_to_yaml(msg.reject_reason, out);
    out << "\n";
  }

  // member: objectness_score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "objectness_score: ";
    rosidl_generator_traits::value_to_yaml(msg.objectness_score, out);
    out << "\n";
  }

  // member: target_hint_score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "target_hint_score: ";
    rosidl_generator_traits::value_to_yaml(msg.target_hint_score, out);
    out << "\n";
  }

  // member: filter_score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "filter_score: ";
    rosidl_generator_traits::value_to_yaml(msg.filter_score, out);
    out << "\n";
  }

  // member: depth_score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "depth_score: ";
    rosidl_generator_traits::value_to_yaml(msg.depth_score, out);
    out << "\n";
  }

  // member: quality_score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "quality_score: ";
    rosidl_generator_traits::value_to_yaml(msg.quality_score, out);
    out << "\n";
  }

  // member: color_score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "color_score: ";
    rosidl_generator_traits::value_to_yaml(msg.color_score, out);
    out << "\n";
  }

  // member: shape_score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "shape_score: ";
    rosidl_generator_traits::value_to_yaml(msg.shape_score, out);
    out << "\n";
  }

  // member: physical_size_score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "physical_size_score: ";
    rosidl_generator_traits::value_to_yaml(msg.physical_size_score, out);
    out << "\n";
  }

  // member: sharpness
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "sharpness: ";
    rosidl_generator_traits::value_to_yaml(msg.sharpness, out);
    out << "\n";
  }

  // member: mean_brightness
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mean_brightness: ";
    rosidl_generator_traits::value_to_yaml(msg.mean_brightness, out);
    out << "\n";
  }

  // member: dark_ratio
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "dark_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.dark_ratio, out);
    out << "\n";
  }

  // member: bright_clip_ratio
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "bright_clip_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.bright_clip_ratio, out);
    out << "\n";
  }

  // member: edge_density
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "edge_density: ";
    rosidl_generator_traits::value_to_yaml(msg.edge_density, out);
    out << "\n";
  }

  // member: mask_fill_ratio
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mask_fill_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.mask_fill_ratio, out);
    out << "\n";
  }

  // member: mask_solidity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mask_solidity: ";
    rosidl_generator_traits::value_to_yaml(msg.mask_solidity, out);
    out << "\n";
  }

  // member: color_similarity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "color_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.color_similarity, out);
    out << "\n";
  }

  // member: aspect_ratio
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "aspect_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.aspect_ratio, out);
    out << "\n";
  }

  // member: estimated_width_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "estimated_width_m: ";
    rosidl_generator_traits::value_to_yaml(msg.estimated_width_m, out);
    out << "\n";
  }

  // member: estimated_height_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "estimated_height_m: ";
    rosidl_generator_traits::value_to_yaml(msg.estimated_height_m, out);
    out << "\n";
  }

  // member: sync_offset_abs_sec
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "sync_offset_abs_sec: ";
    rosidl_generator_traits::value_to_yaml(msg.sync_offset_abs_sec, out);
    out << "\n";
  }

  // member: candidate
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "candidate:\n";
    to_block_style_yaml(msg.candidate, out, indentation + 2);
  }

  // member: crop_roi
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "crop_roi:\n";
    to_block_style_yaml(msg.crop_roi, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CandidateFilterResult & msg, bool use_flow_style = false)
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
  const macrobot_interfaces::msg::CandidateFilterResult & msg,
  std::ostream & out, size_t indentation = 0)
{
  macrobot_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use macrobot_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const macrobot_interfaces::msg::CandidateFilterResult & msg)
{
  return macrobot_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<macrobot_interfaces::msg::CandidateFilterResult>()
{
  return "macrobot_interfaces::msg::CandidateFilterResult";
}

template<>
inline const char * name<macrobot_interfaces::msg::CandidateFilterResult>()
{
  return "macrobot_interfaces/msg/CandidateFilterResult";
}

template<>
struct has_fixed_size<macrobot_interfaces::msg::CandidateFilterResult>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<macrobot_interfaces::msg::CandidateFilterResult>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<macrobot_interfaces::msg::CandidateFilterResult>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__CANDIDATE_FILTER_RESULT__TRAITS_HPP_
