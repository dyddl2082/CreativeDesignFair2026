// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from macrobot_interfaces:msg/EmbeddingMatchedCandidate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/embedding_matched_candidate.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__TRAITS_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "macrobot_interfaces/msg/detail/embedding_matched_candidate__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'result'
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__traits.hpp"
// Member 'filtered_crop'
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__traits.hpp"

namespace macrobot_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const EmbeddingMatchedCandidate & msg,
  std::ostream & out)
{
  out << "{";
  // member: result
  {
    out << "result: ";
    to_flow_style_yaml(msg.result, out);
    out << ", ";
  }

  // member: filtered_crop
  {
    out << "filtered_crop: ";
    to_flow_style_yaml(msg.filtered_crop, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const EmbeddingMatchedCandidate & msg,
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

  // member: filtered_crop
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "filtered_crop:\n";
    to_block_style_yaml(msg.filtered_crop, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const EmbeddingMatchedCandidate & msg, bool use_flow_style = false)
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
  const macrobot_interfaces::msg::EmbeddingMatchedCandidate & msg,
  std::ostream & out, size_t indentation = 0)
{
  macrobot_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use macrobot_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const macrobot_interfaces::msg::EmbeddingMatchedCandidate & msg)
{
  return macrobot_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<macrobot_interfaces::msg::EmbeddingMatchedCandidate>()
{
  return "macrobot_interfaces::msg::EmbeddingMatchedCandidate";
}

template<>
inline const char * name<macrobot_interfaces::msg::EmbeddingMatchedCandidate>()
{
  return "macrobot_interfaces/msg/EmbeddingMatchedCandidate";
}

template<>
struct has_fixed_size<macrobot_interfaces::msg::EmbeddingMatchedCandidate>
  : std::integral_constant<bool, has_fixed_size<macrobot_interfaces::msg::EmbeddingRetrievalResult>::value && has_fixed_size<macrobot_interfaces::msg::FilteredCandidateCrop>::value> {};

template<>
struct has_bounded_size<macrobot_interfaces::msg::EmbeddingMatchedCandidate>
  : std::integral_constant<bool, has_bounded_size<macrobot_interfaces::msg::EmbeddingRetrievalResult>::value && has_bounded_size<macrobot_interfaces::msg::FilteredCandidateCrop>::value> {};

template<>
struct is_message<macrobot_interfaces::msg::EmbeddingMatchedCandidate>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__TRAITS_HPP_
