// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from macrobot_interfaces:msg/CandidateFilterResult.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/candidate_filter_result.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__CANDIDATE_FILTER_RESULT__STRUCT_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__CANDIDATE_FILTER_RESULT__STRUCT_HPP_

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
# define DEPRECATED__macrobot_interfaces__msg__CandidateFilterResult __attribute__((deprecated))
#else
# define DEPRECATED__macrobot_interfaces__msg__CandidateFilterResult __declspec(deprecated)
#endif

namespace macrobot_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct CandidateFilterResult_
{
  using Type = CandidateFilterResult_<ContainerAllocator>;

  explicit CandidateFilterResult_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
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
      this->reference_profile_available = false;
      this->reference_image_count = 0ul;
      this->camera_info_available = false;
      this->plane_found = false;
      this->foreground_height_valid = false;
      this->foreground_mask_available = false;
      this->accepted = false;
      this->reject_stage = "";
      this->reject_reason = "";
      this->objectness_score = 0.0f;
      this->target_hint_score = 0.0f;
      this->filter_score = 0.0f;
      this->depth_score = 0.0f;
      this->quality_score = 0.0f;
      this->color_score = 0.0f;
      this->shape_score = 0.0f;
      this->physical_size_score = 0.0f;
      this->sharpness = 0.0f;
      this->mean_brightness = 0.0f;
      this->dark_ratio = 0.0f;
      this->bright_clip_ratio = 0.0f;
      this->edge_density = 0.0f;
      this->mask_fill_ratio = 0.0f;
      this->mask_solidity = 0.0f;
      this->color_similarity = 0.0f;
      this->aspect_ratio = 0.0f;
      this->estimated_width_m = 0.0f;
      this->estimated_height_m = 0.0f;
      this->sync_offset_abs_sec = 0.0f;
    }
  }

  explicit CandidateFilterResult_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : proposal_header(_alloc, _init),
    image_header(_alloc, _init),
    target_object(_alloc),
    reject_stage(_alloc),
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
      this->reference_profile_available = false;
      this->reference_image_count = 0ul;
      this->camera_info_available = false;
      this->plane_found = false;
      this->foreground_height_valid = false;
      this->foreground_mask_available = false;
      this->accepted = false;
      this->reject_stage = "";
      this->reject_reason = "";
      this->objectness_score = 0.0f;
      this->target_hint_score = 0.0f;
      this->filter_score = 0.0f;
      this->depth_score = 0.0f;
      this->quality_score = 0.0f;
      this->color_score = 0.0f;
      this->shape_score = 0.0f;
      this->physical_size_score = 0.0f;
      this->sharpness = 0.0f;
      this->mean_brightness = 0.0f;
      this->dark_ratio = 0.0f;
      this->bright_clip_ratio = 0.0f;
      this->edge_density = 0.0f;
      this->mask_fill_ratio = 0.0f;
      this->mask_solidity = 0.0f;
      this->color_similarity = 0.0f;
      this->aspect_ratio = 0.0f;
      this->estimated_width_m = 0.0f;
      this->estimated_height_m = 0.0f;
      this->sync_offset_abs_sec = 0.0f;
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
  using _reference_profile_available_type =
    bool;
  _reference_profile_available_type reference_profile_available;
  using _reference_image_count_type =
    uint32_t;
  _reference_image_count_type reference_image_count;
  using _camera_info_available_type =
    bool;
  _camera_info_available_type camera_info_available;
  using _plane_found_type =
    bool;
  _plane_found_type plane_found;
  using _foreground_height_valid_type =
    bool;
  _foreground_height_valid_type foreground_height_valid;
  using _foreground_mask_available_type =
    bool;
  _foreground_mask_available_type foreground_mask_available;
  using _accepted_type =
    bool;
  _accepted_type accepted;
  using _reject_stage_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _reject_stage_type reject_stage;
  using _reject_reason_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _reject_reason_type reject_reason;
  using _objectness_score_type =
    float;
  _objectness_score_type objectness_score;
  using _target_hint_score_type =
    float;
  _target_hint_score_type target_hint_score;
  using _filter_score_type =
    float;
  _filter_score_type filter_score;
  using _depth_score_type =
    float;
  _depth_score_type depth_score;
  using _quality_score_type =
    float;
  _quality_score_type quality_score;
  using _color_score_type =
    float;
  _color_score_type color_score;
  using _shape_score_type =
    float;
  _shape_score_type shape_score;
  using _physical_size_score_type =
    float;
  _physical_size_score_type physical_size_score;
  using _sharpness_type =
    float;
  _sharpness_type sharpness;
  using _mean_brightness_type =
    float;
  _mean_brightness_type mean_brightness;
  using _dark_ratio_type =
    float;
  _dark_ratio_type dark_ratio;
  using _bright_clip_ratio_type =
    float;
  _bright_clip_ratio_type bright_clip_ratio;
  using _edge_density_type =
    float;
  _edge_density_type edge_density;
  using _mask_fill_ratio_type =
    float;
  _mask_fill_ratio_type mask_fill_ratio;
  using _mask_solidity_type =
    float;
  _mask_solidity_type mask_solidity;
  using _color_similarity_type =
    float;
  _color_similarity_type color_similarity;
  using _aspect_ratio_type =
    float;
  _aspect_ratio_type aspect_ratio;
  using _estimated_width_m_type =
    float;
  _estimated_width_m_type estimated_width_m;
  using _estimated_height_m_type =
    float;
  _estimated_height_m_type estimated_height_m;
  using _sync_offset_abs_sec_type =
    float;
  _sync_offset_abs_sec_type sync_offset_abs_sec;
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
  Type & set__reference_profile_available(
    const bool & _arg)
  {
    this->reference_profile_available = _arg;
    return *this;
  }
  Type & set__reference_image_count(
    const uint32_t & _arg)
  {
    this->reference_image_count = _arg;
    return *this;
  }
  Type & set__camera_info_available(
    const bool & _arg)
  {
    this->camera_info_available = _arg;
    return *this;
  }
  Type & set__plane_found(
    const bool & _arg)
  {
    this->plane_found = _arg;
    return *this;
  }
  Type & set__foreground_height_valid(
    const bool & _arg)
  {
    this->foreground_height_valid = _arg;
    return *this;
  }
  Type & set__foreground_mask_available(
    const bool & _arg)
  {
    this->foreground_mask_available = _arg;
    return *this;
  }
  Type & set__accepted(
    const bool & _arg)
  {
    this->accepted = _arg;
    return *this;
  }
  Type & set__reject_stage(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->reject_stage = _arg;
    return *this;
  }
  Type & set__reject_reason(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->reject_reason = _arg;
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
  Type & set__filter_score(
    const float & _arg)
  {
    this->filter_score = _arg;
    return *this;
  }
  Type & set__depth_score(
    const float & _arg)
  {
    this->depth_score = _arg;
    return *this;
  }
  Type & set__quality_score(
    const float & _arg)
  {
    this->quality_score = _arg;
    return *this;
  }
  Type & set__color_score(
    const float & _arg)
  {
    this->color_score = _arg;
    return *this;
  }
  Type & set__shape_score(
    const float & _arg)
  {
    this->shape_score = _arg;
    return *this;
  }
  Type & set__physical_size_score(
    const float & _arg)
  {
    this->physical_size_score = _arg;
    return *this;
  }
  Type & set__sharpness(
    const float & _arg)
  {
    this->sharpness = _arg;
    return *this;
  }
  Type & set__mean_brightness(
    const float & _arg)
  {
    this->mean_brightness = _arg;
    return *this;
  }
  Type & set__dark_ratio(
    const float & _arg)
  {
    this->dark_ratio = _arg;
    return *this;
  }
  Type & set__bright_clip_ratio(
    const float & _arg)
  {
    this->bright_clip_ratio = _arg;
    return *this;
  }
  Type & set__edge_density(
    const float & _arg)
  {
    this->edge_density = _arg;
    return *this;
  }
  Type & set__mask_fill_ratio(
    const float & _arg)
  {
    this->mask_fill_ratio = _arg;
    return *this;
  }
  Type & set__mask_solidity(
    const float & _arg)
  {
    this->mask_solidity = _arg;
    return *this;
  }
  Type & set__color_similarity(
    const float & _arg)
  {
    this->color_similarity = _arg;
    return *this;
  }
  Type & set__aspect_ratio(
    const float & _arg)
  {
    this->aspect_ratio = _arg;
    return *this;
  }
  Type & set__estimated_width_m(
    const float & _arg)
  {
    this->estimated_width_m = _arg;
    return *this;
  }
  Type & set__estimated_height_m(
    const float & _arg)
  {
    this->estimated_height_m = _arg;
    return *this;
  }
  Type & set__sync_offset_abs_sec(
    const float & _arg)
  {
    this->sync_offset_abs_sec = _arg;
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
    macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator> *;
  using ConstRawPtr =
    const macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__macrobot_interfaces__msg__CandidateFilterResult
    std::shared_ptr<macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__macrobot_interfaces__msg__CandidateFilterResult
    std::shared_ptr<macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CandidateFilterResult_ & other) const
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
    if (this->reference_profile_available != other.reference_profile_available) {
      return false;
    }
    if (this->reference_image_count != other.reference_image_count) {
      return false;
    }
    if (this->camera_info_available != other.camera_info_available) {
      return false;
    }
    if (this->plane_found != other.plane_found) {
      return false;
    }
    if (this->foreground_height_valid != other.foreground_height_valid) {
      return false;
    }
    if (this->foreground_mask_available != other.foreground_mask_available) {
      return false;
    }
    if (this->accepted != other.accepted) {
      return false;
    }
    if (this->reject_stage != other.reject_stage) {
      return false;
    }
    if (this->reject_reason != other.reject_reason) {
      return false;
    }
    if (this->objectness_score != other.objectness_score) {
      return false;
    }
    if (this->target_hint_score != other.target_hint_score) {
      return false;
    }
    if (this->filter_score != other.filter_score) {
      return false;
    }
    if (this->depth_score != other.depth_score) {
      return false;
    }
    if (this->quality_score != other.quality_score) {
      return false;
    }
    if (this->color_score != other.color_score) {
      return false;
    }
    if (this->shape_score != other.shape_score) {
      return false;
    }
    if (this->physical_size_score != other.physical_size_score) {
      return false;
    }
    if (this->sharpness != other.sharpness) {
      return false;
    }
    if (this->mean_brightness != other.mean_brightness) {
      return false;
    }
    if (this->dark_ratio != other.dark_ratio) {
      return false;
    }
    if (this->bright_clip_ratio != other.bright_clip_ratio) {
      return false;
    }
    if (this->edge_density != other.edge_density) {
      return false;
    }
    if (this->mask_fill_ratio != other.mask_fill_ratio) {
      return false;
    }
    if (this->mask_solidity != other.mask_solidity) {
      return false;
    }
    if (this->color_similarity != other.color_similarity) {
      return false;
    }
    if (this->aspect_ratio != other.aspect_ratio) {
      return false;
    }
    if (this->estimated_width_m != other.estimated_width_m) {
      return false;
    }
    if (this->estimated_height_m != other.estimated_height_m) {
      return false;
    }
    if (this->sync_offset_abs_sec != other.sync_offset_abs_sec) {
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
  bool operator!=(const CandidateFilterResult_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CandidateFilterResult_

// alias to use template instance with default allocator
using CandidateFilterResult =
  macrobot_interfaces::msg::CandidateFilterResult_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__CANDIDATE_FILTER_RESULT__STRUCT_HPP_
