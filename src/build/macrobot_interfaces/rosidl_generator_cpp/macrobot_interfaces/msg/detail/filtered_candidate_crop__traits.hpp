// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from macrobot_interfaces:msg/FilteredCandidateCrop.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/filtered_candidate_crop.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__TRAITS_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'result'
#include "macrobot_interfaces/msg/detail/candidate_filter_result__traits.hpp"
// Member 'crop'
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__traits.hpp"

namespace macrobot_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const FilteredCandidateCrop & msg,
  std::ostream & out)
{
  out << "{";
  // member: result
  {
    out << "result: ";
    to_flow_style_yaml(msg.result, out);
    out << ", ";
  }

  // member: crop
  {
    out << "crop: ";
    to_flow_style_yaml(msg.crop, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const FilteredCandidateCrop & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: result
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "result:\n";
    to_block_style_yaml(msg.result, out, indentation + 2);
  }

  // member: crop
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "crop:\n";
    to_block_style_yaml(msg.crop, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const FilteredCandidateCrop & msg, bool use_flow_style = false)
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
  const macrobot_interfaces::msg::FilteredCandidateCrop & msg,
  std::ostream & out, size_t indentation = 0)
{
  macrobot_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use macrobot_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const macrobot_interfaces::msg::FilteredCandidateCrop & msg)
{
  return macrobot_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<macrobot_interfaces::msg::FilteredCandidateCrop>()
{
  return "macrobot_interfaces::msg::FilteredCandidateCrop";
}

template<>
inline const char * name<macrobot_interfaces::msg::FilteredCandidateCrop>()
{
  return "macrobot_interfaces/msg/FilteredCandidateCrop";
}

template<>
struct has_fixed_size<macrobot_interfaces::msg::FilteredCandidateCrop>
  : std::integral_constant<bool, has_fixed_size<macrobot_interfaces::msg::CandidateFilterResult>::value && has_fixed_size<macrobot_interfaces::msg::RgbCandidateCrop>::value> {};

template<>
struct has_bounded_size<macrobot_interfaces::msg::FilteredCandidateCrop>
  : std::integral_constant<bool, has_bounded_size<macrobot_interfaces::msg::CandidateFilterResult>::value && has_bounded_size<macrobot_interfaces::msg::RgbCandidateCrop>::value> {};

template<>
struct is_message<macrobot_interfaces::msg::FilteredCandidateCrop>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__TRAITS_HPP_
