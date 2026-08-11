// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from macrobot_interfaces:msg/EmbeddingRetrievalResult.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/embedding_retrieval_result.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_RETRIEVAL_RESULT__BUILDER_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_RETRIEVAL_RESULT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace macrobot_interfaces
{

namespace msg
{

namespace builder
{

class Init_EmbeddingRetrievalResult_crop_roi
{
public:
  explicit Init_EmbeddingRetrievalResult_crop_roi(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult crop_roi(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_crop_roi_type arg)
  {
    msg_.crop_roi = std::move(arg);
    return std::move(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_candidate
{
public:
  explicit Init_EmbeddingRetrievalResult_candidate(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_crop_roi candidate(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_candidate_type arg)
  {
    msg_.candidate = std::move(arg);
    return Init_EmbeddingRetrievalResult_crop_roi(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_matching_ms
{
public:
  explicit Init_EmbeddingRetrievalResult_matching_ms(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_candidate matching_ms(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_matching_ms_type arg)
  {
    msg_.matching_ms = std::move(arg);
    return Init_EmbeddingRetrievalResult_candidate(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_inference_ms
{
public:
  explicit Init_EmbeddingRetrievalResult_inference_ms(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_matching_ms inference_ms(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_inference_ms_type arg)
  {
    msg_.inference_ms = std::move(arg);
    return Init_EmbeddingRetrievalResult_matching_ms(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_preprocessing_ms
{
public:
  explicit Init_EmbeddingRetrievalResult_preprocessing_ms(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_inference_ms preprocessing_ms(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_preprocessing_ms_type arg)
  {
    msg_.preprocessing_ms = std::move(arg);
    return Init_EmbeddingRetrievalResult_inference_ms(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_reject_reason
{
public:
  explicit Init_EmbeddingRetrievalResult_reject_reason(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_preprocessing_ms reject_reason(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_reject_reason_type arg)
  {
    msg_.reject_reason = std::move(arg);
    return Init_EmbeddingRetrievalResult_preprocessing_ms(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_accepted
{
public:
  explicit Init_EmbeddingRetrievalResult_accepted(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_reject_reason accepted(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_EmbeddingRetrievalResult_reject_reason(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_passed_margin_threshold
{
public:
  explicit Init_EmbeddingRetrievalResult_passed_margin_threshold(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_accepted passed_margin_threshold(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_passed_margin_threshold_type arg)
  {
    msg_.passed_margin_threshold = std::move(arg);
    return Init_EmbeddingRetrievalResult_accepted(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_passed_positive_threshold
{
public:
  explicit Init_EmbeddingRetrievalResult_passed_positive_threshold(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_passed_margin_threshold passed_positive_threshold(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_passed_positive_threshold_type arg)
  {
    msg_.passed_positive_threshold = std::move(arg);
    return Init_EmbeddingRetrievalResult_passed_margin_threshold(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_thresholds_enforced
{
public:
  explicit Init_EmbeddingRetrievalResult_thresholds_enforced(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_passed_positive_threshold thresholds_enforced(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_thresholds_enforced_type arg)
  {
    msg_.thresholds_enforced = std::move(arg);
    return Init_EmbeddingRetrievalResult_passed_positive_threshold(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_top_negative_scores
{
public:
  explicit Init_EmbeddingRetrievalResult_top_negative_scores(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_thresholds_enforced top_negative_scores(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_top_negative_scores_type arg)
  {
    msg_.top_negative_scores = std::move(arg);
    return Init_EmbeddingRetrievalResult_thresholds_enforced(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_top_negative_paths
{
public:
  explicit Init_EmbeddingRetrievalResult_top_negative_paths(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_top_negative_scores top_negative_paths(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_top_negative_paths_type arg)
  {
    msg_.top_negative_paths = std::move(arg);
    return Init_EmbeddingRetrievalResult_top_negative_scores(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_top_positive_scores
{
public:
  explicit Init_EmbeddingRetrievalResult_top_positive_scores(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_top_negative_paths top_positive_scores(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_top_positive_scores_type arg)
  {
    msg_.top_positive_scores = std::move(arg);
    return Init_EmbeddingRetrievalResult_top_negative_paths(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_top_positive_paths
{
public:
  explicit Init_EmbeddingRetrievalResult_top_positive_paths(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_top_positive_scores top_positive_paths(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_top_positive_paths_type arg)
  {
    msg_.top_positive_paths = std::move(arg);
    return Init_EmbeddingRetrievalResult_top_positive_scores(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_best_negative_path
{
public:
  explicit Init_EmbeddingRetrievalResult_best_negative_path(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_top_positive_paths best_negative_path(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_best_negative_path_type arg)
  {
    msg_.best_negative_path = std::move(arg);
    return Init_EmbeddingRetrievalResult_top_positive_paths(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_best_positive_path
{
public:
  explicit Init_EmbeddingRetrievalResult_best_positive_path(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_best_negative_path best_positive_path(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_best_positive_path_type arg)
  {
    msg_.best_positive_path = std::move(arg);
    return Init_EmbeddingRetrievalResult_best_negative_path(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_margin
{
public:
  explicit Init_EmbeddingRetrievalResult_margin(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_best_positive_path margin(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_margin_type arg)
  {
    msg_.margin = std::move(arg);
    return Init_EmbeddingRetrievalResult_best_positive_path(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_best_negative_similarity
{
public:
  explicit Init_EmbeddingRetrievalResult_best_negative_similarity(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_margin best_negative_similarity(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_best_negative_similarity_type arg)
  {
    msg_.best_negative_similarity = std::move(arg);
    return Init_EmbeddingRetrievalResult_margin(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_negative_similarity
{
public:
  explicit Init_EmbeddingRetrievalResult_negative_similarity(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_best_negative_similarity negative_similarity(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_negative_similarity_type arg)
  {
    msg_.negative_similarity = std::move(arg);
    return Init_EmbeddingRetrievalResult_best_negative_similarity(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_best_positive_similarity
{
public:
  explicit Init_EmbeddingRetrievalResult_best_positive_similarity(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_negative_similarity best_positive_similarity(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_best_positive_similarity_type arg)
  {
    msg_.best_positive_similarity = std::move(arg);
    return Init_EmbeddingRetrievalResult_negative_similarity(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_positive_similarity
{
public:
  explicit Init_EmbeddingRetrievalResult_positive_similarity(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_best_positive_similarity positive_similarity(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_positive_similarity_type arg)
  {
    msg_.positive_similarity = std::move(arg);
    return Init_EmbeddingRetrievalResult_best_positive_similarity(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_target_hint_score
{
public:
  explicit Init_EmbeddingRetrievalResult_target_hint_score(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_positive_similarity target_hint_score(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_target_hint_score_type arg)
  {
    msg_.target_hint_score = std::move(arg);
    return Init_EmbeddingRetrievalResult_positive_similarity(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_objectness_score
{
public:
  explicit Init_EmbeddingRetrievalResult_objectness_score(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_target_hint_score objectness_score(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_objectness_score_type arg)
  {
    msg_.objectness_score = std::move(arg);
    return Init_EmbeddingRetrievalResult_target_hint_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_foreground_mask_used
{
public:
  explicit Init_EmbeddingRetrievalResult_foreground_mask_used(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_objectness_score foreground_mask_used(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_foreground_mask_used_type arg)
  {
    msg_.foreground_mask_used = std::move(arg);
    return Init_EmbeddingRetrievalResult_objectness_score(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_negative_reference_count
{
public:
  explicit Init_EmbeddingRetrievalResult_negative_reference_count(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_foreground_mask_used negative_reference_count(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_negative_reference_count_type arg)
  {
    msg_.negative_reference_count = std::move(arg);
    return Init_EmbeddingRetrievalResult_foreground_mask_used(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_negative_bank_available
{
public:
  explicit Init_EmbeddingRetrievalResult_negative_bank_available(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_negative_reference_count negative_bank_available(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_negative_bank_available_type arg)
  {
    msg_.negative_bank_available = std::move(arg);
    return Init_EmbeddingRetrievalResult_negative_reference_count(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_positive_reference_count
{
public:
  explicit Init_EmbeddingRetrievalResult_positive_reference_count(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_negative_bank_available positive_reference_count(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_positive_reference_count_type arg)
  {
    msg_.positive_reference_count = std::move(arg);
    return Init_EmbeddingRetrievalResult_negative_bank_available(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_positive_bank_available
{
public:
  explicit Init_EmbeddingRetrievalResult_positive_bank_available(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_positive_reference_count positive_bank_available(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_positive_bank_available_type arg)
  {
    msg_.positive_bank_available = std::move(arg);
    return Init_EmbeddingRetrievalResult_positive_reference_count(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_embedding_dim
{
public:
  explicit Init_EmbeddingRetrievalResult_embedding_dim(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_positive_bank_available embedding_dim(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_embedding_dim_type arg)
  {
    msg_.embedding_dim = std::move(arg);
    return Init_EmbeddingRetrievalResult_positive_bank_available(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_device
{
public:
  explicit Init_EmbeddingRetrievalResult_device(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_embedding_dim device(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_device_type arg)
  {
    msg_.device = std::move(arg);
    return Init_EmbeddingRetrievalResult_embedding_dim(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_pooling
{
public:
  explicit Init_EmbeddingRetrievalResult_pooling(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_device pooling(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_pooling_type arg)
  {
    msg_.pooling = std::move(arg);
    return Init_EmbeddingRetrievalResult_device(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_model_id
{
public:
  explicit Init_EmbeddingRetrievalResult_model_id(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_pooling model_id(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_model_id_type arg)
  {
    msg_.model_id = std::move(arg);
    return Init_EmbeddingRetrievalResult_pooling(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_target_object
{
public:
  explicit Init_EmbeddingRetrievalResult_target_object(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_model_id target_object(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_target_object_type arg)
  {
    msg_.target_object = std::move(arg);
    return Init_EmbeddingRetrievalResult_model_id(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_frame_crop_count
{
public:
  explicit Init_EmbeddingRetrievalResult_frame_crop_count(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_target_object frame_crop_count(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_frame_crop_count_type arg)
  {
    msg_.frame_crop_count = std::move(arg);
    return Init_EmbeddingRetrievalResult_target_object(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_crop_index
{
public:
  explicit Init_EmbeddingRetrievalResult_crop_index(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_frame_crop_count crop_index(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_crop_index_type arg)
  {
    msg_.crop_index = std::move(arg);
    return Init_EmbeddingRetrievalResult_frame_crop_count(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_candidate_id
{
public:
  explicit Init_EmbeddingRetrievalResult_candidate_id(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_crop_index candidate_id(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_candidate_id_type arg)
  {
    msg_.candidate_id = std::move(arg);
    return Init_EmbeddingRetrievalResult_crop_index(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_image_header
{
public:
  explicit Init_EmbeddingRetrievalResult_image_header(::macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
  : msg_(msg)
  {}
  Init_EmbeddingRetrievalResult_candidate_id image_header(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_image_header_type arg)
  {
    msg_.image_header = std::move(arg);
    return Init_EmbeddingRetrievalResult_candidate_id(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

class Init_EmbeddingRetrievalResult_proposal_header
{
public:
  Init_EmbeddingRetrievalResult_proposal_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_EmbeddingRetrievalResult_image_header proposal_header(::macrobot_interfaces::msg::EmbeddingRetrievalResult::_proposal_header_type arg)
  {
    msg_.proposal_header = std::move(arg);
    return Init_EmbeddingRetrievalResult_image_header(msg_);
  }

private:
  ::macrobot_interfaces::msg::EmbeddingRetrievalResult msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::macrobot_interfaces::msg::EmbeddingRetrievalResult>()
{
  return macrobot_interfaces::msg::builder::Init_EmbeddingRetrievalResult_proposal_header();
}

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_RETRIEVAL_RESULT__BUILDER_HPP_
