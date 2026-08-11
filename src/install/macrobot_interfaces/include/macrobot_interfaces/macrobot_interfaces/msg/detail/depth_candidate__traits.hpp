// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from macrobot_interfaces:msg/DepthCandidate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/depth_candidate.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE__TRAITS_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "macrobot_interfaces/msg/detail/depth_candidate__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'roi'
#include "sensor_msgs/msg/detail/region_of_interest__traits.hpp"

namespace macrobot_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const DepthCandidate & msg,
  std::ostream & out)
{
  out << "{";
  // member: id
  {
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
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

  // member: median_depth_m
  {
    out << "median_depth_m: ";
    rosidl_generator_traits::value_to_yaml(msg.median_depth_m, out);
    out << ", ";
  }

  // member: near_depth_m
  {
    out << "near_depth_m: ";
    rosidl_generator_traits::value_to_yaml(msg.near_depth_m, out);
    out << ", ";
  }

  // member: far_depth_m
  {
    out << "far_depth_m: ";
    rosidl_generator_traits::value_to_yaml(msg.far_depth_m, out);
    out << ", ";
  }

  // member: depth_std_m
  {
    out << "depth_std_m: ";
    rosidl_generator_traits::value_to_yaml(msg.depth_std_m, out);
    out << ", ";
  }

  // member: valid_depth_ratio
  {
    out << "valid_depth_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.valid_depth_ratio, out);
    out << ", ";
  }

  // member: fill_ratio
  {
    out << "fill_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.fill_ratio, out);
    out << ", ";
  }

  // member: area_ratio
  {
    out << "area_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.area_ratio, out);
    out << ", ";
  }

  // member: foreground_height_m
  {
    out << "foreground_height_m: ";
    rosidl_generator_traits::value_to_yaml(msg.foreground_height_m, out);
    out << ", ";
  }

  // member: foreground_height_valid
  {
    out << "foreground_height_valid: ";
    rosidl_generator_traits::value_to_yaml(msg.foreground_height_valid, out);
    out << ", ";
  }

  // member: proposal_score
  {
    out << "proposal_score: ";
    rosidl_generator_traits::value_to_yaml(msg.proposal_score, out);
    out << ", ";
  }

  // member: touches_border
  {
    out << "touches_border: ";
    rosidl_generator_traits::value_to_yaml(msg.touches_border, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const DepthCandidate & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
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

  // member: median_depth_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "median_depth_m: ";
    rosidl_generator_traits::value_to_yaml(msg.median_depth_m, out);
    out << "\n";
  }

  // member: near_depth_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "near_depth_m: ";
    rosidl_generator_traits::value_to_yaml(msg.near_depth_m, out);
    out << "\n";
  }

  // member: far_depth_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "far_depth_m: ";
    rosidl_generator_traits::value_to_yaml(msg.far_depth_m, out);
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

  // member: valid_depth_ratio
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "valid_depth_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.valid_depth_ratio, out);
    out << "\n";
  }

  // member: fill_ratio
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fill_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.fill_ratio, out);
    out << "\n";
  }

  // member: area_ratio
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "area_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.area_ratio, out);
    out << "\n";
  }

  // member: foreground_height_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "foreground_height_m: ";
    rosidl_generator_traits::value_to_yaml(msg.foreground_height_m, out);
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

  // member: proposal_score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "proposal_score: ";
    rosidl_generator_traits::value_to_yaml(msg.proposal_score, out);
    out << "\n";
  }

  // member: touches_border
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "touches_border: ";
    rosidl_generator_traits::value_to_yaml(msg.touches_border, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DepthCandidate & msg, bool use_flow_style = false)
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
  const macrobot_interfaces::msg::DepthCandidate & msg,
  std::ostream & out, size_t indentation = 0)
{
  macrobot_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use macrobot_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const macrobot_interfaces::msg::DepthCandidate & msg)
{
  return macrobot_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<macrobot_interfaces::msg::DepthCandidate>()
{
  return "macrobot_interfaces::msg::DepthCandidate";
}

template<>
inline const char * name<macrobot_interfaces::msg::DepthCandidate>()
{
  return "macrobot_interfaces/msg/DepthCandidate";
}

template<>
struct has_fixed_size<macrobot_interfaces::msg::DepthCandidate>
  : std::integral_constant<bool, has_fixed_size<sensor_msgs::msg::RegionOfInterest>::value> {};

template<>
struct has_bounded_size<macrobot_interfaces::msg::DepthCandidate>
  : std::integral_constant<bool, has_bounded_size<sensor_msgs::msg::RegionOfInterest>::value> {};

template<>
struct is_message<macrobot_interfaces::msg::DepthCandidate>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE__TRAITS_HPP_
