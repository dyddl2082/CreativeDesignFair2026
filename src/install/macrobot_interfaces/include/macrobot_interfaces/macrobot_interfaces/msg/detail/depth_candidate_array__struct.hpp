// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from macrobot_interfaces:msg/DepthCandidateArray.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/depth_candidate_array.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE_ARRAY__STRUCT_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE_ARRAY__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'foreground_mask'
#include "sensor_msgs/msg/detail/compressed_image__struct.hpp"
// Member 'candidates'
#include "macrobot_interfaces/msg/detail/depth_candidate__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__macrobot_interfaces__msg__DepthCandidateArray __attribute__((deprecated))
#else
# define DEPRECATED__macrobot_interfaces__msg__DepthCandidateArray __declspec(deprecated)
#endif

namespace macrobot_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct DepthCandidateArray_
{
  using Type = DepthCandidateArray_<ContainerAllocator>;

  explicit DepthCandidateArray_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    foreground_mask(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->image_width = 0ul;
      this->image_height = 0ul;
      this->plane_found = false;
      this->plane_inlier_ratio = 0.0f;
      std::fill<typename std::array<float, 4>::iterator, float>(this->plane_coefficients.begin(), this->plane_coefficients.end(), 0.0f);
      this->foreground_mask_available = false;
    }
  }

  explicit DepthCandidateArray_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    plane_coefficients(_alloc),
    foreground_mask(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->image_width = 0ul;
      this->image_height = 0ul;
      this->plane_found = false;
      this->plane_inlier_ratio = 0.0f;
      std::fill<typename std::array<float, 4>::iterator, float>(this->plane_coefficients.begin(), this->plane_coefficients.end(), 0.0f);
      this->foreground_mask_available = false;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _image_width_type =
    uint32_t;
  _image_width_type image_width;
  using _image_height_type =
    uint32_t;
  _image_height_type image_height;
  using _plane_found_type =
    bool;
  _plane_found_type plane_found;
  using _plane_inlier_ratio_type =
    float;
  _plane_inlier_ratio_type plane_inlier_ratio;
  using _plane_coefficients_type =
    std::array<float, 4>;
  _plane_coefficients_type plane_coefficients;
  using _foreground_mask_available_type =
    bool;
  _foreground_mask_available_type foreground_mask_available;
  using _foreground_mask_type =
    sensor_msgs::msg::CompressedImage_<ContainerAllocator>;
  _foreground_mask_type foreground_mask;
  using _candidates_type =
    std::vector<macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator>>>;
  _candidates_type candidates;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__image_width(
    const uint32_t & _arg)
  {
    this->image_width = _arg;
    return *this;
  }
  Type & set__image_height(
    const uint32_t & _arg)
  {
    this->image_height = _arg;
    return *this;
  }
  Type & set__plane_found(
    const bool & _arg)
  {
    this->plane_found = _arg;
    return *this;
  }
  Type & set__plane_inlier_ratio(
    const float & _arg)
  {
    this->plane_inlier_ratio = _arg;
    return *this;
  }
  Type & set__plane_coefficients(
    const std::array<float, 4> & _arg)
  {
    this->plane_coefficients = _arg;
    return *this;
  }
  Type & set__foreground_mask_available(
    const bool & _arg)
  {
    this->foreground_mask_available = _arg;
    return *this;
  }
  Type & set__foreground_mask(
    const sensor_msgs::msg::CompressedImage_<ContainerAllocator> & _arg)
  {
    this->foreground_mask = _arg;
    return *this;
  }
  Type & set__candidates(
    const std::vector<macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator>>> & _arg)
  {
    this->candidates = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    macrobot_interfaces::msg::DepthCandidateArray_<ContainerAllocator> *;
  using ConstRawPtr =
    const macrobot_interfaces::msg::DepthCandidateArray_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::DepthCandidateArray_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::DepthCandidateArray_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::DepthCandidateArray_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::DepthCandidateArray_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::DepthCandidateArray_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::DepthCandidateArray_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::DepthCandidateArray_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::DepthCandidateArray_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__macrobot_interfaces__msg__DepthCandidateArray
    std::shared_ptr<macrobot_interfaces::msg::DepthCandidateArray_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__macrobot_interfaces__msg__DepthCandidateArray
    std::shared_ptr<macrobot_interfaces::msg::DepthCandidateArray_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DepthCandidateArray_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->image_width != other.image_width) {
      return false;
    }
    if (this->image_height != other.image_height) {
      return false;
    }
    if (this->plane_found != other.plane_found) {
      return false;
    }
    if (this->plane_inlier_ratio != other.plane_inlier_ratio) {
      return false;
    }
    if (this->plane_coefficients != other.plane_coefficients) {
      return false;
    }
    if (this->foreground_mask_available != other.foreground_mask_available) {
      return false;
    }
    if (this->foreground_mask != other.foreground_mask) {
      return false;
    }
    if (this->candidates != other.candidates) {
      return false;
    }
    return true;
  }
  bool operator!=(const DepthCandidateArray_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DepthCandidateArray_

// alias to use template instance with default allocator
using DepthCandidateArray =
  macrobot_interfaces::msg::DepthCandidateArray_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE_ARRAY__STRUCT_HPP_
