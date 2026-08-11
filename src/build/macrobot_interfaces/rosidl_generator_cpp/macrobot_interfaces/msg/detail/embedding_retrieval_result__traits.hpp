// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from macrobot_interfaces:msg/EmbeddingRetrievalResult.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/embedding_retrieval_result.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_RETRIEVAL_RESULT__TRAITS_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_RETRIEVAL_RESULT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__struct.hpp"
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
  const EmbeddingRetrievalResult & msg,
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

  // member: model_id
  {
    out << "model_id: ";
    rosidl_generator_traits::value_to_yaml(msg.model_id, out);
    out << ", ";
  }

  // member: pooling
  {
    out << "pooling: ";
    rosidl_generator_traits::value_to_yaml(msg.pooling, out);
    out << ", ";
  }

  // member: device
  {
    out << "device: ";
    rosidl_generator_traits::value_to_yaml(msg.device, out);
    out << ", ";
  }

  // member: embedding_dim
  {
    out << "embedding_dim: ";
    rosidl_generator_traits::value_to_yaml(msg.embedding_dim, out);
    out << ", ";
  }

  // member: positive_bank_available
  {
    out << "positive_bank_available: ";
    rosidl_generator_traits::value_to_yaml(msg.positive_bank_available, out);
    out << ", ";
  }

  // member: positive_reference_count
  {
    out << "positive_reference_count: ";
    rosidl_generator_traits::value_to_yaml(msg.positive_reference_count, out);
    out << ", ";
  }

  // member: negative_bank_available
  {
    out << "negative_bank_available: ";
    rosidl_generator_traits::value_to_yaml(msg.negative_bank_available, out);
    out << ", ";
  }

  // member: negative_reference_count
  {
    out << "negative_reference_count: ";
    rosidl_generator_traits::value_to_yaml(msg.negative_reference_count, out);
    out << ", ";
  }

  // member: foreground_mask_used
  {
    out << "foreground_mask_used: ";
    rosidl_generator_traits::value_to_yaml(msg.foreground_mask_used, out);
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

  // member: positive_similarity
  {
    out << "positive_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.positive_similarity, out);
    out << ", ";
  }

  // member: best_positive_similarity
  {
    out << "best_positive_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.best_positive_similarity, out);
    out << ", ";
  }

  // member: negative_similarity
  {
    out << "negative_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.negative_similarity, out);
    out << ", ";
  }

  // member: best_negative_similarity
  {
    out << "best_negative_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.best_negative_similarity, out);
    out << ", ";
  }

  // member: margin
  {
    out << "margin: ";
    rosidl_generator_traits::value_to_yaml(msg.margin, out);
    out << ", ";
  }

  // member: best_positive_path
  {
    out << "best_positive_path: ";
    rosidl_generator_traits::value_to_yaml(msg.best_positive_path, out);
    out << ", ";
  }

  // member: best_negative_path
  {
    out << "best_negative_path: ";
    rosidl_generator_traits::value_to_yaml(msg.best_negative_path, out);
    out << ", ";
  }

  // member: top_positive_paths
  {
    if (msg.top_positive_paths.size() == 0) {
      out << "top_positive_paths: []";
    } else {
      out << "top_positive_paths: [";
      size_t pending_items = msg.top_positive_paths.size();
      for (auto item : msg.top_positive_paths) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: top_positive_scores
  {
    if (msg.top_positive_scores.size() == 0) {
      out << "top_positive_scores: []";
    } else {
      out << "top_positive_scores: [";
      size_t pending_items = msg.top_positive_scores.size();
      for (auto item : msg.top_positive_scores) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: top_negative_paths
  {
    if (msg.top_negative_paths.size() == 0) {
      out << "top_negative_paths: []";
    } else {
      out << "top_negative_paths: [";
      size_t pending_items = msg.top_negative_paths.size();
      for (auto item : msg.top_negative_paths) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: top_negative_scores
  {
    if (msg.top_negative_scores.size() == 0) {
      out << "top_negative_scores: []";
    } else {
      out << "top_negative_scores: [";
      size_t pending_items = msg.top_negative_scores.size();
      for (auto item : msg.top_negative_scores) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: thresholds_enforced
  {
    out << "thresholds_enforced: ";
    rosidl_generator_traits::value_to_yaml(msg.thresholds_enforced, out);
    out << ", ";
  }

  // member: passed_positive_threshold
  {
    out << "passed_positive_threshold: ";
    rosidl_generator_traits::value_to_yaml(msg.passed_positive_threshold, out);
    out << ", ";
  }

  // member: passed_margin_threshold
  {
    out << "passed_margin_threshold: ";
    rosidl_generator_traits::value_to_yaml(msg.passed_margin_threshold, out);
    out << ", ";
  }

  // member: accepted
  {
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << ", ";
  }

  // member: reject_reason
  {
    out << "reject_reason: ";
    rosidl_generator_traits::value_to_yaml(msg.reject_reason, out);
    out << ", ";
  }

  // member: preprocessing_ms
  {
    out << "preprocessing_ms: ";
    rosidl_generator_traits::value_to_yaml(msg.preprocessing_ms, out);
    out << ", ";
  }

  // member: inference_ms
  {
    out << "inference_ms: ";
    rosidl_generator_traits::value_to_yaml(msg.inference_ms, out);
    out << ", ";
  }

  // member: matching_ms
  {
    out << "matching_ms: ";
    rosidl_generator_traits::value_to_yaml(msg.matching_ms, out);
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
  const EmbeddingRetrievalResult & msg,
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

  // member: model_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "model_id: ";
    rosidl_generator_traits::value_to_yaml(msg.model_id, out);
    out << "\n";
  }

  // member: pooling
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pooling: ";
    rosidl_generator_traits::value_to_yaml(msg.pooling, out);
    out << "\n";
  }

  // member: device
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "device: ";
    rosidl_generator_traits::value_to_yaml(msg.device, out);
    out << "\n";
  }

  // member: embedding_dim
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "embedding_dim: ";
    rosidl_generator_traits::value_to_yaml(msg.embedding_dim, out);
    out << "\n";
  }

  // member: positive_bank_available
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "positive_bank_available: ";
    rosidl_generator_traits::value_to_yaml(msg.positive_bank_available, out);
    out << "\n";
  }

  // member: positive_reference_count
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "positive_reference_count: ";
    rosidl_generator_traits::value_to_yaml(msg.positive_reference_count, out);
    out << "\n";
  }

  // member: negative_bank_available
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "negative_bank_available: ";
    rosidl_generator_traits::value_to_yaml(msg.negative_bank_available, out);
    out << "\n";
  }

  // member: negative_reference_count
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "negative_reference_count: ";
    rosidl_generator_traits::value_to_yaml(msg.negative_reference_count, out);
    out << "\n";
  }

  // member: foreground_mask_used
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "foreground_mask_used: ";
    rosidl_generator_traits::value_to_yaml(msg.foreground_mask_used, out);
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

  // member: positive_similarity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "positive_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.positive_similarity, out);
    out << "\n";
  }

  // member: best_positive_similarity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "best_positive_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.best_positive_similarity, out);
    out << "\n";
  }

  // member: negative_similarity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "negative_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.negative_similarity, out);
    out << "\n";
  }

  // member: best_negative_similarity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "best_negative_similarity: ";
    rosidl_generator_traits::value_to_yaml(msg.best_negative_similarity, out);
    out << "\n";
  }

  // member: margin
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "margin: ";
    rosidl_generator_traits::value_to_yaml(msg.margin, out);
    out << "\n";
  }

  // member: best_positive_path
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "best_positive_path: ";
    rosidl_generator_traits::value_to_yaml(msg.best_positive_path, out);
    out << "\n";
  }

  // member: best_negative_path
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "best_negative_path: ";
    rosidl_generator_traits::value_to_yaml(msg.best_negative_path, out);
    out << "\n";
  }

  // member: top_positive_paths
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.top_positive_paths.size() == 0) {
      out << "top_positive_paths: []\n";
    } else {
      out << "top_positive_paths:\n";
      for (auto item : msg.top_positive_paths) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: top_positive_scores
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.top_positive_scores.size() == 0) {
      out << "top_positive_scores: []\n";
    } else {
      out << "top_positive_scores:\n";
      for (auto item : msg.top_positive_scores) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: top_negative_paths
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.top_negative_paths.size() == 0) {
      out << "top_negative_paths: []\n";
    } else {
      out << "top_negative_paths:\n";
      for (auto item : msg.top_negative_paths) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: top_negative_scores
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.top_negative_scores.size() == 0) {
      out << "top_negative_scores: []\n";
    } else {
      out << "top_negative_scores:\n";
      for (auto item : msg.top_negative_scores) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: thresholds_enforced
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "thresholds_enforced: ";
    rosidl_generator_traits::value_to_yaml(msg.thresholds_enforced, out);
    out << "\n";
  }

  // member: passed_positive_threshold
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "passed_positive_threshold: ";
    rosidl_generator_traits::value_to_yaml(msg.passed_positive_threshold, out);
    out << "\n";
  }

  // member: passed_margin_threshold
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "passed_margin_threshold: ";
    rosidl_generator_traits::value_to_yaml(msg.passed_margin_threshold, out);
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

  // member: reject_reason
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "reject_reason: ";
    rosidl_generator_traits::value_to_yaml(msg.reject_reason, out);
    out << "\n";
  }

  // member: preprocessing_ms
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "preprocessing_ms: ";
    rosidl_generator_traits::value_to_yaml(msg.preprocessing_ms, out);
    out << "\n";
  }

  // member: inference_ms
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "inference_ms: ";
    rosidl_generator_traits::value_to_yaml(msg.inference_ms, out);
    out << "\n";
  }

  // member: matching_ms
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "matching_ms: ";
    rosidl_generator_traits::value_to_yaml(msg.matching_ms, out);
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

inline std::string to_yaml(const EmbeddingRetrievalResult & msg, bool use_flow_style = false)
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
  const macrobot_interfaces::msg::EmbeddingRetrievalResult & msg,
  std::ostream & out, size_t indentation = 0)
{
  macrobot_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use macrobot_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const macrobot_interfaces::msg::EmbeddingRetrievalResult & msg)
{
  return macrobot_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<macrobot_interfaces::msg::EmbeddingRetrievalResult>()
{
  return "macrobot_interfaces::msg::EmbeddingRetrievalResult";
}

template<>
inline const char * name<macrobot_interfaces::msg::EmbeddingRetrievalResult>()
{
  return "macrobot_interfaces/msg/EmbeddingRetrievalResult";
}

template<>
struct has_fixed_size<macrobot_interfaces::msg::EmbeddingRetrievalResult>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<macrobot_interfaces::msg::EmbeddingRetrievalResult>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<macrobot_interfaces::msg::EmbeddingRetrievalResult>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_RETRIEVAL_RESULT__TRAITS_HPP_
