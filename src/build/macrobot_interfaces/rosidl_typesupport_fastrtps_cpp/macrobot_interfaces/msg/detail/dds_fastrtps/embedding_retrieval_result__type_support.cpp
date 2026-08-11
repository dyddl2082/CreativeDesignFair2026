// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from macrobot_interfaces:msg/EmbeddingRetrievalResult.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__rosidl_typesupport_fastrtps_cpp.hpp"
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__functions.h"
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__struct.hpp"

#include <cstddef>
#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions
namespace std_msgs
{
namespace msg
{
namespace typesupport_fastrtps_cpp
{
bool cdr_serialize(
  const std_msgs::msg::Header &,
  eprosima::fastcdr::Cdr &);
bool cdr_deserialize(
  eprosima::fastcdr::Cdr &,
  std_msgs::msg::Header &);
size_t get_serialized_size(
  const std_msgs::msg::Header &,
  size_t current_alignment);
size_t
max_serialized_size_Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
bool cdr_serialize_key(
  const std_msgs::msg::Header &,
  eprosima::fastcdr::Cdr &);
size_t get_serialized_size_key(
  const std_msgs::msg::Header &,
  size_t current_alignment);
size_t
max_serialized_size_key_Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
}  // namespace typesupport_fastrtps_cpp
}  // namespace msg
}  // namespace std_msgs

// functions for std_msgs::msg::Header already declared above

namespace macrobot_interfaces
{
namespace msg
{
namespace typesupport_fastrtps_cpp
{
bool cdr_serialize(
  const macrobot_interfaces::msg::DepthCandidate &,
  eprosima::fastcdr::Cdr &);
bool cdr_deserialize(
  eprosima::fastcdr::Cdr &,
  macrobot_interfaces::msg::DepthCandidate &);
size_t get_serialized_size(
  const macrobot_interfaces::msg::DepthCandidate &,
  size_t current_alignment);
size_t
max_serialized_size_DepthCandidate(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
bool cdr_serialize_key(
  const macrobot_interfaces::msg::DepthCandidate &,
  eprosima::fastcdr::Cdr &);
size_t get_serialized_size_key(
  const macrobot_interfaces::msg::DepthCandidate &,
  size_t current_alignment);
size_t
max_serialized_size_key_DepthCandidate(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
}  // namespace typesupport_fastrtps_cpp
}  // namespace msg
}  // namespace macrobot_interfaces

namespace sensor_msgs
{
namespace msg
{
namespace typesupport_fastrtps_cpp
{
bool cdr_serialize(
  const sensor_msgs::msg::RegionOfInterest &,
  eprosima::fastcdr::Cdr &);
bool cdr_deserialize(
  eprosima::fastcdr::Cdr &,
  sensor_msgs::msg::RegionOfInterest &);
size_t get_serialized_size(
  const sensor_msgs::msg::RegionOfInterest &,
  size_t current_alignment);
size_t
max_serialized_size_RegionOfInterest(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
bool cdr_serialize_key(
  const sensor_msgs::msg::RegionOfInterest &,
  eprosima::fastcdr::Cdr &);
size_t get_serialized_size_key(
  const sensor_msgs::msg::RegionOfInterest &,
  size_t current_alignment);
size_t
max_serialized_size_key_RegionOfInterest(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
}  // namespace typesupport_fastrtps_cpp
}  // namespace msg
}  // namespace sensor_msgs


namespace macrobot_interfaces
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{


bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
cdr_serialize(
  const macrobot_interfaces::msg::EmbeddingRetrievalResult & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: proposal_header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.proposal_header,
    cdr);

  // Member: image_header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.image_header,
    cdr);

  // Member: candidate_id
  cdr << ros_message.candidate_id;

  // Member: crop_index
  cdr << ros_message.crop_index;

  // Member: frame_crop_count
  cdr << ros_message.frame_crop_count;

  // Member: target_object
  cdr << ros_message.target_object;

  // Member: model_id
  cdr << ros_message.model_id;

  // Member: pooling
  cdr << ros_message.pooling;

  // Member: device
  cdr << ros_message.device;

  // Member: embedding_dim
  cdr << ros_message.embedding_dim;

  // Member: positive_bank_available
  cdr << (ros_message.positive_bank_available ? true : false);

  // Member: positive_reference_count
  cdr << ros_message.positive_reference_count;

  // Member: negative_bank_available
  cdr << (ros_message.negative_bank_available ? true : false);

  // Member: negative_reference_count
  cdr << ros_message.negative_reference_count;

  // Member: foreground_mask_used
  cdr << (ros_message.foreground_mask_used ? true : false);

  // Member: objectness_score
  cdr << ros_message.objectness_score;

  // Member: target_hint_score
  cdr << ros_message.target_hint_score;

  // Member: positive_similarity
  cdr << ros_message.positive_similarity;

  // Member: best_positive_similarity
  cdr << ros_message.best_positive_similarity;

  // Member: negative_similarity
  cdr << ros_message.negative_similarity;

  // Member: best_negative_similarity
  cdr << ros_message.best_negative_similarity;

  // Member: margin
  cdr << ros_message.margin;

  // Member: best_positive_path
  cdr << ros_message.best_positive_path;

  // Member: best_negative_path
  cdr << ros_message.best_negative_path;

  // Member: top_positive_paths
  {
    cdr << ros_message.top_positive_paths;
  }

  // Member: top_positive_scores
  {
    cdr << ros_message.top_positive_scores;
  }

  // Member: top_negative_paths
  {
    cdr << ros_message.top_negative_paths;
  }

  // Member: top_negative_scores
  {
    cdr << ros_message.top_negative_scores;
  }

  // Member: thresholds_enforced
  cdr << (ros_message.thresholds_enforced ? true : false);

  // Member: passed_positive_threshold
  cdr << (ros_message.passed_positive_threshold ? true : false);

  // Member: passed_margin_threshold
  cdr << (ros_message.passed_margin_threshold ? true : false);

  // Member: accepted
  cdr << (ros_message.accepted ? true : false);

  // Member: reject_reason
  cdr << ros_message.reject_reason;

  // Member: preprocessing_ms
  cdr << ros_message.preprocessing_ms;

  // Member: inference_ms
  cdr << ros_message.inference_ms;

  // Member: matching_ms
  cdr << ros_message.matching_ms;

  // Member: candidate
  macrobot_interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.candidate,
    cdr);

  // Member: crop_roi
  sensor_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.crop_roi,
    cdr);

  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces::msg::EmbeddingRetrievalResult & ros_message)
{
  // Member: proposal_header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.proposal_header);

  // Member: image_header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.image_header);

  // Member: candidate_id
  cdr >> ros_message.candidate_id;

  // Member: crop_index
  cdr >> ros_message.crop_index;

  // Member: frame_crop_count
  cdr >> ros_message.frame_crop_count;

  // Member: target_object
  cdr >> ros_message.target_object;

  // Member: model_id
  cdr >> ros_message.model_id;

  // Member: pooling
  cdr >> ros_message.pooling;

  // Member: device
  cdr >> ros_message.device;

  // Member: embedding_dim
  cdr >> ros_message.embedding_dim;

  // Member: positive_bank_available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.positive_bank_available = tmp ? true : false;
  }

  // Member: positive_reference_count
  cdr >> ros_message.positive_reference_count;

  // Member: negative_bank_available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.negative_bank_available = tmp ? true : false;
  }

  // Member: negative_reference_count
  cdr >> ros_message.negative_reference_count;

  // Member: foreground_mask_used
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.foreground_mask_used = tmp ? true : false;
  }

  // Member: objectness_score
  cdr >> ros_message.objectness_score;

  // Member: target_hint_score
  cdr >> ros_message.target_hint_score;

  // Member: positive_similarity
  cdr >> ros_message.positive_similarity;

  // Member: best_positive_similarity
  cdr >> ros_message.best_positive_similarity;

  // Member: negative_similarity
  cdr >> ros_message.negative_similarity;

  // Member: best_negative_similarity
  cdr >> ros_message.best_negative_similarity;

  // Member: margin
  cdr >> ros_message.margin;

  // Member: best_positive_path
  cdr >> ros_message.best_positive_path;

  // Member: best_negative_path
  cdr >> ros_message.best_negative_path;

  // Member: top_positive_paths
  {
    cdr >> ros_message.top_positive_paths;
  }

  // Member: top_positive_scores
  {
    cdr >> ros_message.top_positive_scores;
  }

  // Member: top_negative_paths
  {
    cdr >> ros_message.top_negative_paths;
  }

  // Member: top_negative_scores
  {
    cdr >> ros_message.top_negative_scores;
  }

  // Member: thresholds_enforced
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.thresholds_enforced = tmp ? true : false;
  }

  // Member: passed_positive_threshold
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.passed_positive_threshold = tmp ? true : false;
  }

  // Member: passed_margin_threshold
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.passed_margin_threshold = tmp ? true : false;
  }

  // Member: accepted
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.accepted = tmp ? true : false;
  }

  // Member: reject_reason
  cdr >> ros_message.reject_reason;

  // Member: preprocessing_ms
  cdr >> ros_message.preprocessing_ms;

  // Member: inference_ms
  cdr >> ros_message.inference_ms;

  // Member: matching_ms
  cdr >> ros_message.matching_ms;

  // Member: candidate
  macrobot_interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.candidate);

  // Member: crop_roi
  sensor_msgs::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.crop_roi);

  return true;
}  // NOLINT(readability/fn_size)


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
get_serialized_size(
  const macrobot_interfaces::msg::EmbeddingRetrievalResult & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: proposal_header
  current_alignment +=
    std_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.proposal_header, current_alignment);

  // Member: image_header
  current_alignment +=
    std_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.image_header, current_alignment);

  // Member: candidate_id
  {
    size_t item_size = sizeof(ros_message.candidate_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: crop_index
  {
    size_t item_size = sizeof(ros_message.crop_index);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: frame_crop_count
  {
    size_t item_size = sizeof(ros_message.frame_crop_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: target_object
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.target_object.size() + 1);

  // Member: model_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.model_id.size() + 1);

  // Member: pooling
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.pooling.size() + 1);

  // Member: device
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.device.size() + 1);

  // Member: embedding_dim
  {
    size_t item_size = sizeof(ros_message.embedding_dim);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: positive_bank_available
  {
    size_t item_size = sizeof(ros_message.positive_bank_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: positive_reference_count
  {
    size_t item_size = sizeof(ros_message.positive_reference_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: negative_bank_available
  {
    size_t item_size = sizeof(ros_message.negative_bank_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: negative_reference_count
  {
    size_t item_size = sizeof(ros_message.negative_reference_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: foreground_mask_used
  {
    size_t item_size = sizeof(ros_message.foreground_mask_used);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: objectness_score
  {
    size_t item_size = sizeof(ros_message.objectness_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: target_hint_score
  {
    size_t item_size = sizeof(ros_message.target_hint_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: positive_similarity
  {
    size_t item_size = sizeof(ros_message.positive_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: best_positive_similarity
  {
    size_t item_size = sizeof(ros_message.best_positive_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: negative_similarity
  {
    size_t item_size = sizeof(ros_message.negative_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: best_negative_similarity
  {
    size_t item_size = sizeof(ros_message.best_negative_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: margin
  {
    size_t item_size = sizeof(ros_message.margin);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: best_positive_path
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.best_positive_path.size() + 1);

  // Member: best_negative_path
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.best_negative_path.size() + 1);

  // Member: top_positive_paths
  {
    size_t array_size = ros_message.top_positive_paths.size();
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        (ros_message.top_positive_paths[index].size() + 1);
    }
  }

  // Member: top_positive_scores
  {
    size_t array_size = ros_message.top_positive_scores.size();
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    size_t item_size = sizeof(ros_message.top_positive_scores[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: top_negative_paths
  {
    size_t array_size = ros_message.top_negative_paths.size();
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        (ros_message.top_negative_paths[index].size() + 1);
    }
  }

  // Member: top_negative_scores
  {
    size_t array_size = ros_message.top_negative_scores.size();
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    size_t item_size = sizeof(ros_message.top_negative_scores[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: thresholds_enforced
  {
    size_t item_size = sizeof(ros_message.thresholds_enforced);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: passed_positive_threshold
  {
    size_t item_size = sizeof(ros_message.passed_positive_threshold);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: passed_margin_threshold
  {
    size_t item_size = sizeof(ros_message.passed_margin_threshold);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: accepted
  {
    size_t item_size = sizeof(ros_message.accepted);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: reject_reason
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.reject_reason.size() + 1);

  // Member: preprocessing_ms
  {
    size_t item_size = sizeof(ros_message.preprocessing_ms);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: inference_ms
  {
    size_t item_size = sizeof(ros_message.inference_ms);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: matching_ms
  {
    size_t item_size = sizeof(ros_message.matching_ms);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: candidate
  current_alignment +=
    macrobot_interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.candidate, current_alignment);

  // Member: crop_roi
  current_alignment +=
    sensor_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.crop_roi, current_alignment);

  return current_alignment - initial_alignment;
}


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
max_serialized_size_EmbeddingRetrievalResult(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // Member: proposal_header
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        std_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // Member: image_header
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        std_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // Member: candidate_id
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: crop_index
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: frame_crop_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: target_object
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // Member: model_id
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // Member: pooling
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // Member: device
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // Member: embedding_dim
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: positive_bank_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: positive_reference_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: negative_bank_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: negative_reference_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: foreground_mask_used
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: objectness_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: target_hint_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: positive_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: best_positive_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: negative_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: best_negative_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: margin
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: best_positive_path
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // Member: best_negative_path
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // Member: top_positive_paths
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // Member: top_positive_scores
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: top_negative_paths
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // Member: top_negative_scores
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: thresholds_enforced
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: passed_positive_threshold
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: passed_margin_threshold
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: accepted
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: reject_reason
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // Member: preprocessing_ms
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: inference_ms
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: matching_ms
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: candidate
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        macrobot_interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_DepthCandidate(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // Member: crop_roi
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        sensor_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_RegionOfInterest(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = macrobot_interfaces::msg::EmbeddingRetrievalResult;
    is_plain =
      (
      offsetof(DataType, crop_roi) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
cdr_serialize_key(
  const macrobot_interfaces::msg::EmbeddingRetrievalResult & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: proposal_header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize_key(
    ros_message.proposal_header,
    cdr);

  // Member: image_header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize_key(
    ros_message.image_header,
    cdr);

  // Member: candidate_id
  cdr << ros_message.candidate_id;

  // Member: crop_index
  cdr << ros_message.crop_index;

  // Member: frame_crop_count
  cdr << ros_message.frame_crop_count;

  // Member: target_object
  cdr << ros_message.target_object;

  // Member: model_id
  cdr << ros_message.model_id;

  // Member: pooling
  cdr << ros_message.pooling;

  // Member: device
  cdr << ros_message.device;

  // Member: embedding_dim
  cdr << ros_message.embedding_dim;

  // Member: positive_bank_available
  cdr << (ros_message.positive_bank_available ? true : false);

  // Member: positive_reference_count
  cdr << ros_message.positive_reference_count;

  // Member: negative_bank_available
  cdr << (ros_message.negative_bank_available ? true : false);

  // Member: negative_reference_count
  cdr << ros_message.negative_reference_count;

  // Member: foreground_mask_used
  cdr << (ros_message.foreground_mask_used ? true : false);

  // Member: objectness_score
  cdr << ros_message.objectness_score;

  // Member: target_hint_score
  cdr << ros_message.target_hint_score;

  // Member: positive_similarity
  cdr << ros_message.positive_similarity;

  // Member: best_positive_similarity
  cdr << ros_message.best_positive_similarity;

  // Member: negative_similarity
  cdr << ros_message.negative_similarity;

  // Member: best_negative_similarity
  cdr << ros_message.best_negative_similarity;

  // Member: margin
  cdr << ros_message.margin;

  // Member: best_positive_path
  cdr << ros_message.best_positive_path;

  // Member: best_negative_path
  cdr << ros_message.best_negative_path;

  // Member: top_positive_paths
  {
    cdr << ros_message.top_positive_paths;
  }

  // Member: top_positive_scores
  {
    cdr << ros_message.top_positive_scores;
  }

  // Member: top_negative_paths
  {
    cdr << ros_message.top_negative_paths;
  }

  // Member: top_negative_scores
  {
    cdr << ros_message.top_negative_scores;
  }

  // Member: thresholds_enforced
  cdr << (ros_message.thresholds_enforced ? true : false);

  // Member: passed_positive_threshold
  cdr << (ros_message.passed_positive_threshold ? true : false);

  // Member: passed_margin_threshold
  cdr << (ros_message.passed_margin_threshold ? true : false);

  // Member: accepted
  cdr << (ros_message.accepted ? true : false);

  // Member: reject_reason
  cdr << ros_message.reject_reason;

  // Member: preprocessing_ms
  cdr << ros_message.preprocessing_ms;

  // Member: inference_ms
  cdr << ros_message.inference_ms;

  // Member: matching_ms
  cdr << ros_message.matching_ms;

  // Member: candidate
  macrobot_interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize_key(
    ros_message.candidate,
    cdr);

  // Member: crop_roi
  sensor_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize_key(
    ros_message.crop_roi,
    cdr);

  return true;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
get_serialized_size_key(
  const macrobot_interfaces::msg::EmbeddingRetrievalResult & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: proposal_header
  current_alignment +=
    std_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size_key(
    ros_message.proposal_header, current_alignment);

  // Member: image_header
  current_alignment +=
    std_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size_key(
    ros_message.image_header, current_alignment);

  // Member: candidate_id
  {
    size_t item_size = sizeof(ros_message.candidate_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: crop_index
  {
    size_t item_size = sizeof(ros_message.crop_index);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: frame_crop_count
  {
    size_t item_size = sizeof(ros_message.frame_crop_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: target_object
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.target_object.size() + 1);

  // Member: model_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.model_id.size() + 1);

  // Member: pooling
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.pooling.size() + 1);

  // Member: device
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.device.size() + 1);

  // Member: embedding_dim
  {
    size_t item_size = sizeof(ros_message.embedding_dim);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: positive_bank_available
  {
    size_t item_size = sizeof(ros_message.positive_bank_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: positive_reference_count
  {
    size_t item_size = sizeof(ros_message.positive_reference_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: negative_bank_available
  {
    size_t item_size = sizeof(ros_message.negative_bank_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: negative_reference_count
  {
    size_t item_size = sizeof(ros_message.negative_reference_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: foreground_mask_used
  {
    size_t item_size = sizeof(ros_message.foreground_mask_used);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: objectness_score
  {
    size_t item_size = sizeof(ros_message.objectness_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: target_hint_score
  {
    size_t item_size = sizeof(ros_message.target_hint_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: positive_similarity
  {
    size_t item_size = sizeof(ros_message.positive_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: best_positive_similarity
  {
    size_t item_size = sizeof(ros_message.best_positive_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: negative_similarity
  {
    size_t item_size = sizeof(ros_message.negative_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: best_negative_similarity
  {
    size_t item_size = sizeof(ros_message.best_negative_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: margin
  {
    size_t item_size = sizeof(ros_message.margin);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: best_positive_path
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.best_positive_path.size() + 1);

  // Member: best_negative_path
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.best_negative_path.size() + 1);

  // Member: top_positive_paths
  {
    size_t array_size = ros_message.top_positive_paths.size();
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        (ros_message.top_positive_paths[index].size() + 1);
    }
  }

  // Member: top_positive_scores
  {
    size_t array_size = ros_message.top_positive_scores.size();
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    size_t item_size = sizeof(ros_message.top_positive_scores[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: top_negative_paths
  {
    size_t array_size = ros_message.top_negative_paths.size();
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        (ros_message.top_negative_paths[index].size() + 1);
    }
  }

  // Member: top_negative_scores
  {
    size_t array_size = ros_message.top_negative_scores.size();
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    size_t item_size = sizeof(ros_message.top_negative_scores[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: thresholds_enforced
  {
    size_t item_size = sizeof(ros_message.thresholds_enforced);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: passed_positive_threshold
  {
    size_t item_size = sizeof(ros_message.passed_positive_threshold);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: passed_margin_threshold
  {
    size_t item_size = sizeof(ros_message.passed_margin_threshold);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: accepted
  {
    size_t item_size = sizeof(ros_message.accepted);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: reject_reason
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.reject_reason.size() + 1);

  // Member: preprocessing_ms
  {
    size_t item_size = sizeof(ros_message.preprocessing_ms);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: inference_ms
  {
    size_t item_size = sizeof(ros_message.inference_ms);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: matching_ms
  {
    size_t item_size = sizeof(ros_message.matching_ms);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: candidate
  current_alignment +=
    macrobot_interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size_key(
    ros_message.candidate, current_alignment);

  // Member: crop_roi
  current_alignment +=
    sensor_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size_key(
    ros_message.crop_roi, current_alignment);

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
max_serialized_size_key_EmbeddingRetrievalResult(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // Member: proposal_header
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        std_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_key_Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: image_header
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        std_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_key_Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: candidate_id
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: crop_index
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: frame_crop_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: target_object
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Member: model_id
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Member: pooling
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Member: device
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Member: embedding_dim
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: positive_bank_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: positive_reference_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: negative_bank_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: negative_reference_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: foreground_mask_used
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: objectness_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: target_hint_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: positive_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: best_positive_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: negative_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: best_negative_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: margin
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: best_positive_path
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Member: best_negative_path
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Member: top_positive_paths
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Member: top_positive_scores
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: top_negative_paths
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Member: top_negative_scores
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: thresholds_enforced
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: passed_positive_threshold
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: passed_margin_threshold
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: accepted
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: reject_reason
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Member: preprocessing_ms
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: inference_ms
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: matching_ms
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: candidate
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        macrobot_interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_key_DepthCandidate(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: crop_roi
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        sensor_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_key_RegionOfInterest(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = macrobot_interfaces::msg::EmbeddingRetrievalResult;
    is_plain =
      (
      offsetof(DataType, crop_roi) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}


static bool _EmbeddingRetrievalResult__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const macrobot_interfaces::msg::EmbeddingRetrievalResult *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _EmbeddingRetrievalResult__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<macrobot_interfaces::msg::EmbeddingRetrievalResult *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _EmbeddingRetrievalResult__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const macrobot_interfaces::msg::EmbeddingRetrievalResult *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _EmbeddingRetrievalResult__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_EmbeddingRetrievalResult(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _EmbeddingRetrievalResult__callbacks = {
  "macrobot_interfaces::msg",
  "EmbeddingRetrievalResult",
  _EmbeddingRetrievalResult__cdr_serialize,
  _EmbeddingRetrievalResult__cdr_deserialize,
  _EmbeddingRetrievalResult__get_serialized_size,
  _EmbeddingRetrievalResult__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _EmbeddingRetrievalResult__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_EmbeddingRetrievalResult__callbacks,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_hash,
  &macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_description,
  &macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_description_sources,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace macrobot_interfaces

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_macrobot_interfaces
const rosidl_message_type_support_t *
get_message_type_support_handle<macrobot_interfaces::msg::EmbeddingRetrievalResult>()
{
  return &macrobot_interfaces::msg::typesupport_fastrtps_cpp::_EmbeddingRetrievalResult__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, macrobot_interfaces, msg, EmbeddingRetrievalResult)() {
  return &macrobot_interfaces::msg::typesupport_fastrtps_cpp::_EmbeddingRetrievalResult__handle;
}

#ifdef __cplusplus
}
#endif
