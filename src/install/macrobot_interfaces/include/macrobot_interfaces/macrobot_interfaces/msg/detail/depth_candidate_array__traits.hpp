// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from macrobot_interfaces:msg/DepthCandidateArray.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/depth_candidate_array.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE_ARRAY__TRAITS_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE_ARRAY__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "macrobot_interfaces/msg/detail/depth_candidate_array__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'foreground_mask'
#include "sensor_msgs/msg/detail/compressed_image__traits.hpp"
// Member 'candidates'
#include "macrobot_interfaces/msg/detail/depth_candidate__traits.hpp"

namespace macrobot_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const DepthCandidateArray & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: image_width
  {
    out << "image_width: ";
    rosidl_generator_traits::value_to_yaml(msg.image_width, out);
    out << ", ";
  }

  // member: image_height
  {
    out << "image_height: ";
    rosidl_generator_traits::value_to_yaml(msg.image_height, out);
    out << ", ";
  }

  // member: plane_found
  {
    out << "plane_found: ";
    rosidl_generator_traits::value_to_yaml(msg.plane_found, out);
    out << ", ";
  }

  // member: plane_inlier_ratio
  {
    out << "plane_inlier_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.plane_inlier_ratio, out);
    out << ", ";
  }

  // member: plane_coefficients
  {
    if (msg.plane_coefficients.size() == 0) {
      out << "plane_coefficients: []";
    } else {
      out << "plane_coefficients: [";
      size_t pending_items = msg.plane_coefficients.size();
      for (auto item : msg.plane_coefficients) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: foreground_mask_available
  {
    out << "foreground_mask_available: ";
    rosidl_generator_traits::value_to_yaml(msg.foreground_mask_available, out);
    out << ", ";
  }

  // member: foreground_mask
  {
    out << "foreground_mask: ";
    to_flow_style_yaml(msg.foreground_mask, out);
    out << ", ";
  }

  // member: candidates
  {
    if (msg.candidates.size() == 0) {
      out << "candidates: []";
    } else {
      out << "candidates: [";
      size_t pending_items = msg.candidates.size();
      for (auto item : msg.candidates) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const DepthCandidateArray & msg,
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

  // member: image_width
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "image_width: ";
    rosidl_generator_traits::value_to_yaml(msg.image_width, out);
    out << "\n";
  }

  // member: image_height
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "image_height: ";
    rosidl_generator_traits::value_to_yaml(msg.image_height, out);
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

  // member: plane_inlier_ratio
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "plane_inlier_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.plane_inlier_ratio, out);
    out << "\n";
  }

  // member: plane_coefficients
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.plane_coefficients.size() == 0) {
      out << "plane_coefficients: []\n";
    } else {
      out << "plane_coefficients:\n";
      for (auto item : msg.plane_coefficients) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
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

  // member: foreground_mask
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "foreground_mask:\n";
    to_block_style_yaml(msg.foreground_mask, out, indentation + 2);
  }

  // member: candidates
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.candidates.size() == 0) {
      out << "candidates: []\n";
    } else {
      out << "candidates:\n";
      for (auto item : msg.candidates) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DepthCandidateArray & msg, bool use_flow_style = false)
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
  const macrobot_interfaces::msg::DepthCandidateArray & msg,
  std::ostream & out, size_t indentation = 0)
{
  macrobot_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use macrobot_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const macrobot_interfaces::msg::DepthCandidateArray & msg)
{
  return macrobot_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<macrobot_interfaces::msg::DepthCandidateArray>()
{
  return "macrobot_interfaces::msg::DepthCandidateArray";
}

template<>
inline const char * name<macrobot_interfaces::msg::DepthCandidateArray>()
{
  return "macrobot_interfaces/msg/DepthCandidateArray";
}

template<>
struct has_fixed_size<macrobot_interfaces::msg::DepthCandidateArray>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<macrobot_interfaces::msg::DepthCandidateArray>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<macrobot_interfaces::msg::DepthCandidateArray>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE_ARRAY__TRAITS_HPP_
