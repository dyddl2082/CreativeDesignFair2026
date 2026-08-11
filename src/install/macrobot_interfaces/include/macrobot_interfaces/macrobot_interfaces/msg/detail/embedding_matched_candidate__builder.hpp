// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from macrobot_interfaces:msg/EmbeddingMatchedCandidate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/embedding_matched_candidate.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__BUILDER_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "macrobot_interfaces/msg/detail/embedding_matched_candidate__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace macrobot_interfaces
{

namespace msg
{

namespace builder
{

class Init_EmbeddingMatchedCandidate_filtered_crop
{
public:
  explicit Init_EmbeddingMatchedCandidate_filtered_crop(::macrobot_interfaces::msg::EmbeddingMatchedCandidate & msg)
  : msg_(msg)
  {}
  ::macrobot_interfaces::msg::EmbeddingMatchedCandidate filtered_crop(::macrobot_interfaces::msg::EmbeddingMatchedCandidate::_filtered_crop_type arg)
  {
    msg_.filtered_crop = std::move(arg);
    return std::move(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingMatchedCandidate msg_;
};

class Init_EmbeddingMatchedCandidate_result
{
public:
  Init_EmbeddingMatchedCandidate_result()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_EmbeddingMatchedCandidate_filtered_crop result(::macrobot_interfaces::msg::EmbeddingMatchedCandidate::_result_type arg)
  {
    msg_.result = std::move(arg);
    return Init_EmbeddingMatchedCandidate_filtered_crop(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingMatchedCandidate msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::macrobot_interfaces::msg::EmbeddingMatchedCandidate>()
{
  return macrobot_interfaces::msg::builder::Init_EmbeddingMatchedCandidate_result();
}

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__BUILDER_HPP_
