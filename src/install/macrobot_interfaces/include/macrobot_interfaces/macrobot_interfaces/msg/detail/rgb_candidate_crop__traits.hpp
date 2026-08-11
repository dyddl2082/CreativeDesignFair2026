// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from macrobot_interfaces:msg/RgbCandidateCrop.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/rgb_candidate_crop.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__RGB_CANDIDATE_CROP__TRAITS_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__RGB_CANDIDATE_CROP__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'proposal_header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'candidate'
#include "macrobot_interfaces/msg/detail/depth_candidate__traits.hpp"
// Member 'crop_roi'
#include "sensor_msgs/msg/detail/region_of_interest__traits.hpp"
// Member 'foreground_mask'
// Member 'image'
#include "sensor_msgs/msg/detail/compressed_image__traits.hpp"

namespace macrobot_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const RgbCandidateCrop & msg,
  std::ostream & out)
{
  out << "{";
  // member: proposal_header
  {
    out << "proposal_header: ";
    to_flow_style_yaml(msg.proposal_header, out);
    out << ", ";
  }

  // member: proposal_image_width
  {
    out << "proposal_image_width: ";
    rosidl_generator_traits::value_to_yaml(msg.proposal_image_width, out);
    out << ", ";
  }

  // member: proposal_image_height
  {
    out << "proposal_image_height: ";
    rosidl_generator_traits::value_to_yaml(msg.proposal_image_height, out);
    out << ", ";
  }

  // member: color_image_width
  {
    out << "color_image_width: ";
    rosidl_generator_traits::value_to_yaml(msg.color_image_width, out);
    out << ", ";
  }

  // member: color_image_height
  {
    out << "color_image_height: ";
    rosidl_generator_traits::value_to_yaml(msg.color_image_height, out);
    out << ", ";
  }

  // member: source_candidate_count
  {
    out << "source_candidate_count: ";
    rosidl_generator_traits::value_to_yaml(msg.source_candidate_count, out);
    out << ", ";
  }

  // member: frame_crop_count
  {
    out << "frame_crop_count: ";
    rosidl_generator_traits::value_to_yaml(msg.frame_crop_count, out);
    out << ", ";
  }

  // member: crop_index
  {
    out << "crop_index: ";
    rosidl_generator_traits::value_to_yaml(msg.crop_index, out);
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
    out << ", ";
  }

  // member: color_time_offset_sec
  {
    out << "color_time_offset_sec: ";
    rosidl_generator_traits::value_to_yaml(msg.color_time_offset_sec, out);
    out << ", ";
  }

  // member: plane_found
  {
    out << "plane_found: ";
    rosidl_generator_traits::value_to_yaml(msg.plane_found, out);
    out << ", ";
  }

  // member: foreground_mask_available
  {
    out << "foreground_mask_available: ";
    rosidl_generator_traits::value_to_yaml(msg.foreground_mask_available, out);
    out << ", ";
  }

  // member: mask_fill_ratio
  {
    out << "mask_fill_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.mask_fill_ratio, out);
    out << ", ";
  }

  // member: foreground_mask
  {
    out << "foreground_mask: ";
    to_flow_style_yaml(msg.foreground_mask, out);
    out << ", ";
  }

  // member: encoded_width
  {
    out << "encoded_width: ";
    rosidl_generator_traits::value_to_yaml(msg.encoded_width, out);
    out << ", ";
  }

  // member: encoded_height
  {
    out << "encoded_height: ";
    rosidl_generator_traits::value_to_yaml(msg.encoded_height, out);
    out << ", ";
  }

  // member: jpeg_size_bytes
  {
    out << "jpeg_size_bytes: ";
    rosidl_generator_traits::value_to_yaml(msg.jpeg_size_bytes, out);
    out << ", ";
  }

  // member: jpeg_quality
  {
    out << "jpeg_quality: ";
    rosidl_generator_traits::value_to_yaml(msg.jpeg_quality, out);
    out << ", ";
  }

  // member: size_limit_met
  {
    out << "size_limit_met: ";
    rosidl_generator_traits::value_to_yaml(msg.size_limit_met, out);
    out << ", ";
  }

  // member: image
  {
    out << "image: ";
    to_flow_style_yaml(msg.image, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const RgbCandidateCrop & msg,
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

  // member: proposal_image_width
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "proposal_image_width: ";
    rosidl_generator_traits::value_to_yaml(msg.proposal_image_width, out);
    out << "\n";
  }

  // member: proposal_image_height
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "proposal_image_height: ";
    rosidl_generator_traits::value_to_yaml(msg.proposal_image_height, out);
    out << "\n";
  }

  // member: color_image_width
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "color_image_width: ";
    rosidl_generator_traits::value_to_yaml(msg.color_image_width, out);
    out << "\n";
  }

  // member: color_image_height
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "color_image_height: ";
    rosidl_generator_traits::value_to_yaml(msg.color_image_height, out);
    out << "\n";
  }

  // member: source_candidate_count
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "source_candidate_count: ";
    rosidl_generator_traits::value_to_yaml(msg.source_candidate_count, out);
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

  // member: crop_index
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "crop_index: ";
    rosidl_generator_traits::value_to_yaml(msg.crop_index, out);
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

  // member: color_time_offset_sec
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "color_time_offset_sec: ";
    rosidl_generator_traits::value_to_yaml(msg.color_time_offset_sec, out);
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

  // member: foreground_mask_available
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "foreground_mask_available: ";
    rosidl_generator_traits::value_to_yaml(msg.foreground_mask_available, out);
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

  // member: foreground_mask
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "foreground_mask:\n";
    to_block_style_yaml(msg.foreground_mask, out, indentation + 2);
  }

  // member: encoded_width
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "encoded_width: ";
    rosidl_generator_traits::value_to_yaml(msg.encoded_width, out);
    out << "\n";
  }

  // member: encoded_height
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "encoded_height: ";
    rosidl_generator_traits::value_to_yaml(msg.encoded_height, out);
    out << "\n";
  }

  // member: jpeg_size_bytes
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "jpeg_size_bytes: ";
    rosidl_generator_traits::value_to_yaml(msg.jpeg_size_bytes, out);
    out << "\n";
  }

  // member: jpeg_quality
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "jpeg_quality: ";
    rosidl_generator_traits::value_to_yaml(msg.jpeg_quality, out);
    out << "\n";
  }

  // member: size_limit_met
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "size_limit_met: ";
    rosidl_generator_traits::value_to_yaml(msg.size_limit_met, out);
    out << "\n";
  }

  // member: image
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "image:\n";
    to_block_style_yaml(msg.image, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const RgbCandidateCrop & msg, bool use_flow_style = false)
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
  const macrobot_interfaces::msg::RgbCandidateCrop & msg,
  std::ostream & out, size_t indentation = 0)
{
  macrobot_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use macrobot_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const macrobot_interfaces::msg::RgbCandidateCrop & msg)
{
  return macrobot_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<macrobot_interfaces::msg::RgbCandidateCrop>()
{
  return "macrobot_interfaces::msg::RgbCandidateCrop";
}

template<>
inline const char * name<macrobot_interfaces::msg::RgbCandidateCrop>()
{
  return "macrobot_interfaces/msg/RgbCandidateCrop";
}

template<>
struct has_fixed_size<macrobot_interfaces::msg::RgbCandidateCrop>
  : std::integral_constant<bool, has_fixed_size<macrobot_interfaces::msg::DepthCandidate>::value && has_fixed_size<sensor_msgs::msg::CompressedImage>::value && has_fixed_size<sensor_msgs::msg::RegionOfInterest>::value && has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<macrobot_interfaces::msg::RgbCandidateCrop>
  : std::integral_constant<bool, has_bounded_size<macrobot_interfaces::msg::DepthCandidate>::value && has_bounded_size<sensor_msgs::msg::CompressedImage>::value && has_bounded_size<sensor_msgs::msg::RegionOfInterest>::value && has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<macrobot_interfaces::msg::RgbCandidateCrop>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__RGB_CANDIDATE_CROP__TRAITS_HPP_
