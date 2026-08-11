// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from macrobot_interfaces:msg/RgbCandidateCrop.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/rgb_candidate_crop.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__RGB_CANDIDATE_CROP__STRUCT_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__RGB_CANDIDATE_CROP__STRUCT_HPP_

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
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'candidate'
#include "macrobot_interfaces/msg/detail/depth_candidate__struct.hpp"
// Member 'crop_roi'
#include "sensor_msgs/msg/detail/region_of_interest__struct.hpp"
// Member 'foreground_mask'
// Member 'image'
#include "sensor_msgs/msg/detail/compressed_image__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__macrobot_interfaces__msg__RgbCandidateCrop __attribute__((deprecated))
#else
# define DEPRECATED__macrobot_interfaces__msg__RgbCandidateCrop __declspec(deprecated)
#endif

namespace macrobot_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct RgbCandidateCrop_
{
  using Type = RgbCandidateCrop_<ContainerAllocator>;

  explicit RgbCandidateCrop_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : proposal_header(_init),
    candidate(_init),
    crop_roi(_init),
    foreground_mask(_init),
    image(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->proposal_image_width = 0ul;
      this->proposal_image_height = 0ul;
      this->color_image_width = 0ul;
      this->color_image_height = 0ul;
      this->source_candidate_count = 0ul;
      this->frame_crop_count = 0ul;
      this->crop_index = 0ul;
      this->color_time_offset_sec = 0.0f;
      this->plane_found = false;
      this->foreground_mask_available = false;
      this->mask_fill_ratio = 0.0f;
      this->encoded_width = 0ul;
      this->encoded_height = 0ul;
      this->jpeg_size_bytes = 0ul;
      this->jpeg_quality = 0;
      this->size_limit_met = false;
    }
  }

  explicit RgbCandidateCrop_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : proposal_header(_alloc, _init),
    candidate(_alloc, _init),
    crop_roi(_alloc, _init),
    foreground_mask(_alloc, _init),
    image(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->proposal_image_width = 0ul;
      this->proposal_image_height = 0ul;
      this->color_image_width = 0ul;
      this->color_image_height = 0ul;
      this->source_candidate_count = 0ul;
      this->frame_crop_count = 0ul;
      this->crop_index = 0ul;
      this->color_time_offset_sec = 0.0f;
      this->plane_found = false;
      this->foreground_mask_available = false;
      this->mask_fill_ratio = 0.0f;
      this->encoded_width = 0ul;
      this->encoded_height = 0ul;
      this->jpeg_size_bytes = 0ul;
      this->jpeg_quality = 0;
      this->size_limit_met = false;
    }
  }

  // field types and members
  using _proposal_header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _proposal_header_type proposal_header;
  using _proposal_image_width_type =
    uint32_t;
  _proposal_image_width_type proposal_image_width;
  using _proposal_image_height_type =
    uint32_t;
  _proposal_image_height_type proposal_image_height;
  using _color_image_width_type =
    uint32_t;
  _color_image_width_type color_image_width;
  using _color_image_height_type =
    uint32_t;
  _color_image_height_type color_image_height;
  using _source_candidate_count_type =
    uint32_t;
  _source_candidate_count_type source_candidate_count;
  using _frame_crop_count_type =
    uint32_t;
  _frame_crop_count_type frame_crop_count;
  using _crop_index_type =
    uint32_t;
  _crop_index_type crop_index;
  using _candidate_type =
    macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator>;
  _candidate_type candidate;
  using _crop_roi_type =
    sensor_msgs::msg::RegionOfInterest_<ContainerAllocator>;
  _crop_roi_type crop_roi;
  using _color_time_offset_sec_type =
    float;
  _color_time_offset_sec_type color_time_offset_sec;
  using _plane_found_type =
    bool;
  _plane_found_type plane_found;
  using _foreground_mask_available_type =
    bool;
  _foreground_mask_available_type foreground_mask_available;
  using _mask_fill_ratio_type =
    float;
  _mask_fill_ratio_type mask_fill_ratio;
  using _foreground_mask_type =
    sensor_msgs::msg::CompressedImage_<ContainerAllocator>;
  _foreground_mask_type foreground_mask;
  using _encoded_width_type =
    uint32_t;
  _encoded_width_type encoded_width;
  using _encoded_height_type =
    uint32_t;
  _encoded_height_type encoded_height;
  using _jpeg_size_bytes_type =
    uint32_t;
  _jpeg_size_bytes_type jpeg_size_bytes;
  using _jpeg_quality_type =
    uint8_t;
  _jpeg_quality_type jpeg_quality;
  using _size_limit_met_type =
    bool;
  _size_limit_met_type size_limit_met;
  using _image_type =
    sensor_msgs::msg::CompressedImage_<ContainerAllocator>;
  _image_type image;

  // setters for named parameter idiom
  Type & set__proposal_header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->proposal_header = _arg;
    return *this;
  }
  Type & set__proposal_image_width(
    const uint32_t & _arg)
  {
    this->proposal_image_width = _arg;
    return *this;
  }
  Type & set__proposal_image_height(
    const uint32_t & _arg)
  {
    this->proposal_image_height = _arg;
    return *this;
  }
  Type & set__color_image_width(
    const uint32_t & _arg)
  {
    this->color_image_width = _arg;
    return *this;
  }
  Type & set__color_image_height(
    const uint32_t & _arg)
  {
    this->color_image_height = _arg;
    return *this;
  }
  Type & set__source_candidate_count(
    const uint32_t & _arg)
  {
    this->source_candidate_count = _arg;
    return *this;
  }
  Type & set__frame_crop_count(
    const uint32_t & _arg)
  {
    this->frame_crop_count = _arg;
    return *this;
  }
  Type & set__crop_index(
    const uint32_t & _arg)
  {
    this->crop_index = _arg;
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
  Type & set__color_time_offset_sec(
    const float & _arg)
  {
    this->color_time_offset_sec = _arg;
    return *this;
  }
  Type & set__plane_found(
    const bool & _arg)
  {
    this->plane_found = _arg;
    return *this;
  }
  Type & set__foreground_mask_available(
    const bool & _arg)
  {
    this->foreground_mask_available = _arg;
    return *this;
  }
  Type & set__mask_fill_ratio(
    const float & _arg)
  {
    this->mask_fill_ratio = _arg;
    return *this;
  }
  Type & set__foreground_mask(
    const sensor_msgs::msg::CompressedImage_<ContainerAllocator> & _arg)
  {
    this->foreground_mask = _arg;
    return *this;
  }
  Type & set__encoded_width(
    const uint32_t & _arg)
  {
    this->encoded_width = _arg;
    return *this;
  }
  Type & set__encoded_height(
    const uint32_t & _arg)
  {
    this->encoded_height = _arg;
    return *this;
  }
  Type & set__jpeg_size_bytes(
    const uint32_t & _arg)
  {
    this->jpeg_size_bytes = _arg;
    return *this;
  }
  Type & set__jpeg_quality(
    const uint8_t & _arg)
  {
    this->jpeg_quality = _arg;
    return *this;
  }
  Type & set__size_limit_met(
    const bool & _arg)
  {
    this->size_limit_met = _arg;
    return *this;
  }
  Type & set__image(
    const sensor_msgs::msg::CompressedImage_<ContainerAllocator> & _arg)
  {
    this->image = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator> *;
  using ConstRawPtr =
    const macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__macrobot_interfaces__msg__RgbCandidateCrop
    std::shared_ptr<macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__macrobot_interfaces__msg__RgbCandidateCrop
    std::shared_ptr<macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RgbCandidateCrop_ & other) const
  {
    if (this->proposal_header != other.proposal_header) {
      return false;
    }
    if (this->proposal_image_width != other.proposal_image_width) {
      return false;
    }
    if (this->proposal_image_height != other.proposal_image_height) {
      return false;
    }
    if (this->color_image_width != other.color_image_width) {
      return false;
    }
    if (this->color_image_height != other.color_image_height) {
      return false;
    }
    if (this->source_candidate_count != other.source_candidate_count) {
      return false;
    }
    if (this->frame_crop_count != other.frame_crop_count) {
      return false;
    }
    if (this->crop_index != other.crop_index) {
      return false;
    }
    if (this->candidate != other.candidate) {
      return false;
    }
    if (this->crop_roi != other.crop_roi) {
      return false;
    }
    if (this->color_time_offset_sec != other.color_time_offset_sec) {
      return false;
    }
    if (this->plane_found != other.plane_found) {
      return false;
    }
    if (this->foreground_mask_available != other.foreground_mask_available) {
      return false;
    }
    if (this->mask_fill_ratio != other.mask_fill_ratio) {
      return false;
    }
    if (this->foreground_mask != other.foreground_mask) {
      return false;
    }
    if (this->encoded_width != other.encoded_width) {
      return false;
    }
    if (this->encoded_height != other.encoded_height) {
      return false;
    }
    if (this->jpeg_size_bytes != other.jpeg_size_bytes) {
      return false;
    }
    if (this->jpeg_quality != other.jpeg_quality) {
      return false;
    }
    if (this->size_limit_met != other.size_limit_met) {
      return false;
    }
    if (this->image != other.image) {
      return false;
    }
    return true;
  }
  bool operator!=(const RgbCandidateCrop_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RgbCandidateCrop_

// alias to use template instance with default allocator
using RgbCandidateCrop =
  macrobot_interfaces::msg::RgbCandidateCrop_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__RGB_CANDIDATE_CROP__STRUCT_HPP_
