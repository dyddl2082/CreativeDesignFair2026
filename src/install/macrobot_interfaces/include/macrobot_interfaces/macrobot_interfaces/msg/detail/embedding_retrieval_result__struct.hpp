// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from macrobot_interfaces:msg/EmbeddingRetrievalResult.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/embedding_retrieval_result.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_RETRIEVAL_RESULT__STRUCT_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_RETRIEVAL_RESULT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'proposal_header'
// Member 'image_header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'candidate'
#include "macrobot_interfaces/msg/detail/depth_candidate__struct.hpp"
// Member 'crop_roi'
#include "sensor_msgs/msg/detail/region_of_interest__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__macrobot_interfaces__msg__EmbeddingRetrievalResult __attribute__((deprecated))
#else
# define DEPRECATED__macrobot_interfaces__msg__EmbeddingRetrievalResult __declspec(deprecated)
#endif

namespace macrobot_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct EmbeddingRetrievalResult_
{
  using Type = EmbeddingRetrievalResult_<ContainerAllocator>;

  explicit EmbeddingRetrievalResult_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : proposal_header(_init),
    image_header(_init),
    candidate(_init),
    crop_roi(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->candidate_id = 0ul;
      this->crop_index = 0ul;
      this->frame_crop_count = 0ul;
      this->target_object = "";
      this->model_id = "";
      this->pooling = "";
      this->device = "";
      this->embedding_dim = 0ul;
      this->positive_bank_available = false;
      this->positive_reference_count = 0ul;
      this->negative_bank_available = false;
      this->negative_reference_count = 0ul;
      this->foreground_mask_used = false;
      this->objectness_score = 0.0f;
      this->target_hint_score = 0.0f;
      this->positive_similarity = 0.0f;
      this->best_positive_similarity = 0.0f;
      this->negative_similarity = 0.0f;
      this->best_negative_similarity = 0.0f;
      this->margin = 0.0f;
      this->best_positive_path = "";
      this->best_negative_path = "";
      this->thresholds_enforced = false;
      this->passed_positive_threshold = false;
      this->passed_margin_threshold = false;
      this->accepted = false;
      this->reject_reason = "";
      this->preprocessing_ms = 0.0f;
      this->inference_ms = 0.0f;
      this->matching_ms = 0.0f;
    }
  }

  explicit EmbeddingRetrievalResult_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : proposal_header(_alloc, _init),
    image_header(_alloc, _init),
    target_object(_alloc),
    model_id(_alloc),
    pooling(_alloc),
    device(_alloc),
    best_positive_path(_alloc),
    best_negative_path(_alloc),
    reject_reason(_alloc),
    candidate(_alloc, _init),
    crop_roi(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->candidate_id = 0ul;
      this->crop_index = 0ul;
      this->frame_crop_count = 0ul;
      this->target_object = "";
      this->model_id = "";
      this->pooling = "";
      this->device = "";
      this->embedding_dim = 0ul;
      this->positive_bank_available = false;
      this->positive_reference_count = 0ul;
      this->negative_bank_available = false;
      this->negative_reference_count = 0ul;
      this->foreground_mask_used = false;
      this->objectness_score = 0.0f;
      this->target_hint_score = 0.0f;
      this->positive_similarity = 0.0f;
      this->best_positive_similarity = 0.0f;
      this->negative_similarity = 0.0f;
      this->best_negative_similarity = 0.0f;
      this->margin = 0.0f;
      this->best_positive_path = "";
      this->best_negative_path = "";
      this->thresholds_enforced = false;
      this->passed_positive_threshold = false;
      this->passed_margin_threshold = false;
      this->accepted = false;
      this->reject_reason = "";
      this->preprocessing_ms = 0.0f;
      this->inference_ms = 0.0f;
      this->matching_ms = 0.0f;
    }
  }

  // field types and members
  using _proposal_header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _proposal_header_type proposal_header;
  using _image_header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _image_header_type image_header;
  using _candidate_id_type =
    uint32_t;
  _candidate_id_type candidate_id;
  using _crop_index_type =
    uint32_t;
  _crop_index_type crop_index;
  using _frame_crop_count_type =
    uint32_t;
  _frame_crop_count_type frame_crop_count;
  using _target_object_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _target_object_type target_object;
  using _model_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _model_id_type model_id;
  using _pooling_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _pooling_type pooling;
  using _device_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _device_type device;
  using _embedding_dim_type =
    uint32_t;
  _embedding_dim_type embedding_dim;
  using _positive_bank_available_type =
    bool;
  _positive_bank_available_type positive_bank_available;
  using _positive_reference_count_type =
    uint32_t;
  _positive_reference_count_type positive_reference_count;
  using _negative_bank_available_type =
    bool;
  _negative_bank_available_type negative_bank_available;
  using _negative_reference_count_type =
    uint32_t;
  _negative_reference_count_type negative_reference_count;
  using _foreground_mask_used_type =
    bool;
  _foreground_mask_used_type foreground_mask_used;
  using _objectness_score_type =
    float;
  _objectness_score_type objectness_score;
  using _target_hint_score_type =
    float;
  _target_hint_score_type target_hint_score;
  using _positive_similarity_type =
    float;
  _positive_similarity_type positive_similarity;
  using _best_positive_similarity_type =
    float;
  _best_positive_similarity_type best_positive_similarity;
  using _negative_similarity_type =
    float;
  _negative_similarity_type negative_similarity;
  using _best_negative_similarity_type =
    float;
  _best_negative_similarity_type best_negative_similarity;
  using _margin_type =
    float;
  _margin_type margin;
  using _best_positive_path_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _best_positive_path_type best_positive_path;
  using _best_negative_path_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _best_negative_path_type best_negative_path;
  using _top_positive_paths_type =
    std::vector<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>>;
  _top_positive_paths_type top_positive_paths;
  using _top_positive_scores_type =
    std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>>;
  _top_positive_scores_type top_positive_scores;
  using _top_negative_paths_type =
    std::vector<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>>;
  _top_negative_paths_type top_negative_paths;
  using _top_negative_scores_type =
    std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>>;
  _top_negative_scores_type top_negative_scores;
  using _thresholds_enforced_type =
    bool;
  _thresholds_enforced_type thresholds_enforced;
  using _passed_positive_threshold_type =
    bool;
  _passed_positive_threshold_type passed_positive_threshold;
  using _passed_margin_threshold_type =
    bool;
  _passed_margin_threshold_type passed_margin_threshold;
  using _accepted_type =
    bool;
  _accepted_type accepted;
  using _reject_reason_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _reject_reason_type reject_reason;
  using _preprocessing_ms_type =
    float;
  _preprocessing_ms_type preprocessing_ms;
  using _inference_ms_type =
    float;
  _inference_ms_type inference_ms;
  using _matching_ms_type =
    float;
  _matching_ms_type matching_ms;
  using _candidate_type =
    macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator>;
  _candidate_type candidate;
  using _crop_roi_type =
    sensor_msgs::msg::RegionOfInterest_<ContainerAllocator>;
  _crop_roi_type crop_roi;

  // setters for named parameter idiom
  Type & set__proposal_header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->proposal_header = _arg;
    return *this;
  }
  Type & set__image_header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->image_header = _arg;
    return *this;
  }
  Type & set__candidate_id(
    const uint32_t & _arg)
  {
    this->candidate_id = _arg;
    return *this;
  }
  Type & set__crop_index(
    const uint32_t & _arg)
  {
    this->crop_index = _arg;
    return *this;
  }
  Type & set__frame_crop_count(
    const uint32_t & _arg)
  {
    this->frame_crop_count = _arg;
    return *this;
  }
  Type & set__target_object(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->target_object = _arg;
    return *this;
  }
  Type & set__model_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->model_id = _arg;
    return *this;
  }
  Type & set__pooling(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->pooling = _arg;
    return *this;
  }
  Type & set__device(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->device = _arg;
    return *this;
  }
  Type & set__embedding_dim(
    const uint32_t & _arg)
  {
    this->embedding_dim = _arg;
    return *this;
  }
  Type & set__positive_bank_available(
    const bool & _arg)
  {
    this->positive_bank_available = _arg;
    return *this;
  }
  Type & set__positive_reference_count(
    const uint32_t & _arg)
  {
    this->positive_reference_count = _arg;
    return *this;
  }
  Type & set__negative_bank_available(
    const bool & _arg)
  {
    this->negative_bank_available = _arg;
    return *this;
  }
  Type & set__negative_reference_count(
    const uint32_t & _arg)
  {
    this->negative_reference_count = _arg;
    return *this;
  }
  Type & set__foreground_mask_used(
    const bool & _arg)
  {
    this->foreground_mask_used = _arg;
    return *this;
  }
  Type & set__objectness_score(
    const float & _arg)
  {
    this->objectness_score = _arg;
    return *this;
  }
  Type & set__target_hint_score(
    const float & _arg)
  {
    this->target_hint_score = _arg;
    return *this;
  }
  Type & set__positive_similarity(
    const float & _arg)
  {
    this->positive_similarity = _arg;
    return *this;
  }
  Type & set__best_positive_similarity(
    const float & _arg)
  {
    this->best_positive_similarity = _arg;
    return *this;
  }
  Type & set__negative_similarity(
    const float & _arg)
  {
    this->negative_similarity = _arg;
    return *this;
  }
  Type & set__best_negative_similarity(
    const float & _arg)
  {
    this->best_negative_similarity = _arg;
    return *this;
  }
  Type & set__margin(
    const float & _arg)
  {
    this->margin = _arg;
    return *this;
  }
  Type & set__best_positive_path(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->best_positive_path = _arg;
    return *this;
  }
  Type & set__best_negative_path(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->best_negative_path = _arg;
    return *this;
  }
  Type & set__top_positive_paths(
    const std::vector<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>> & _arg)
  {
    this->top_positive_paths = _arg;
    return *this;
  }
  Type & set__top_positive_scores(
    const std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>> & _arg)
  {
    this->top_positive_scores = _arg;
    return *this;
  }
  Type & set__top_negative_paths(
    const std::vector<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>> & _arg)
  {
    this->top_negative_paths = _arg;
    return *this;
  }
  Type & set__top_negative_scores(
    const std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>> & _arg)
  {
    this->top_negative_scores = _arg;
    return *this;
  }
  Type & set__thresholds_enforced(
    const bool & _arg)
  {
    this->thresholds_enforced = _arg;
    return *this;
  }
  Type & set__passed_positive_threshold(
    const bool & _arg)
  {
    this->passed_positive_threshold = _arg;
    return *this;
  }
  Type & set__passed_margin_threshold(
    const bool & _arg)
  {
    this->passed_margin_threshold = _arg;
    return *this;
  }
  Type & set__accepted(
    const bool & _arg)
  {
    this->accepted = _arg;
    return *this;
  }
  Type & set__reject_reason(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->reject_reason = _arg;
    return *this;
  }
  Type & set__preprocessing_ms(
    const float & _arg)
  {
    this->preprocessing_ms = _arg;
    return *this;
  }
  Type & set__inference_ms(
    const float & _arg)
  {
    this->inference_ms = _arg;
    return *this;
  }
  Type & set__matching_ms(
    const float & _arg)
  {
    this->matching_ms = _arg;
    return *this;
  }
  Type & set__candidate(
    const macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator> & _arg)
  {
    this->candidate = _arg;
    return *this;
  }
  Type & set__crop_roi(
    const sensor_msgs::msg::RegionOfInterest_<ContainerAllocator> & _arg)
  {
    this->crop_roi = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator> *;
  using ConstRawPtr =
    const macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__macrobot_interfaces__msg__EmbeddingRetrievalResult
    std::shared_ptr<macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__macrobot_interfaces__msg__EmbeddingRetrievalResult
    std::shared_ptr<macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const EmbeddingRetrievalResult_ & other) const
  {
    if (this->proposal_header != other.proposal_header) {
      return false;
    }
    if (this->image_header != other.image_header) {
      return false;
    }
    if (this->candidate_id != other.candidate_id) {
      return false;
    }
    if (this->crop_index != other.crop_index) {
      return false;
    }
    if (this->frame_crop_count != other.frame_crop_count) {
      return false;
    }
    if (this->target_object != other.target_object) {
      return false;
    }
    if (this->model_id != other.model_id) {
      return false;
    }
    if (this->pooling != other.pooling) {
      return false;
    }
    if (this->device != other.device) {
      return false;
    }
    if (this->embedding_dim != other.embedding_dim) {
      return false;
    }
    if (this->positive_bank_available != other.positive_bank_available) {
      return false;
    }
    if (this->positive_reference_count != other.positive_reference_count) {
      return false;
    }
    if (this->negative_bank_available != other.negative_bank_available) {
      return false;
    }
    if (this->negative_reference_count != other.negative_reference_count) {
      return false;
    }
    if (this->foreground_mask_used != other.foreground_mask_used) {
      return false;
    }
    if (this->objectness_score != other.objectness_score) {
      return false;
    }
    if (this->target_hint_score != other.target_hint_score) {
      return false;
    }
    if (this->positive_similarity != other.positive_similarity) {
      return false;
    }
    if (this->best_positive_similarity != other.best_positive_similarity) {
      return false;
    }
    if (this->negative_similarity != other.negative_similarity) {
      return false;
    }
    if (this->best_negative_similarity != other.best_negative_similarity) {
      return false;
    }
    if (this->margin != other.margin) {
      return false;
    }
    if (this->best_positive_path != other.best_positive_path) {
      return false;
    }
    if (this->best_negative_path != other.best_negative_path) {
      return false;
    }
    if (this->top_positive_paths != other.top_positive_paths) {
      return false;
    }
    if (this->top_positive_scores != other.top_positive_scores) {
      return false;
    }
    if (this->top_negative_paths != other.top_negative_paths) {
      return false;
    }
    if (this->top_negative_scores != other.top_negative_scores) {
      return false;
    }
    if (this->thresholds_enforced != other.thresholds_enforced) {
      return false;
    }
    if (this->passed_positive_threshold != other.passed_positive_threshold) {
      return false;
    }
    if (this->passed_margin_threshold != other.passed_margin_threshold) {
      return false;
    }
    if (this->accepted != other.accepted) {
      return false;
    }
    if (this->reject_reason != other.reject_reason) {
      return false;
    }
    if (this->preprocessing_ms != other.preprocessing_ms) {
      return false;
    }
    if (this->inference_ms != other.inference_ms) {
      return false;
    }
    if (this->matching_ms != other.matching_ms) {
      return false;
    }
    if (this->candidate != other.candidate) {
      return false;
    }
    if (this->crop_roi != other.crop_roi) {
      return false;
    }
    return true;
  }
  bool operator!=(const EmbeddingRetrievalResult_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct EmbeddingRetrievalResult_

// alias to use template instance with default allocator
using EmbeddingRetrievalResult =
  macrobot_interfaces::msg::EmbeddingRetrievalResult_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_RETRIEVAL_RESULT__STRUCT_HPP_
