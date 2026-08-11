// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from macrobot_interfaces:msg/DepthCandidate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/depth_candidate.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE__STRUCT_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'roi'
#include "sensor_msgs/msg/detail/region_of_interest__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__macrobot_interfaces__msg__DepthCandidate __attribute__((deprecated))
#else
# define DEPRECATED__macrobot_interfaces__msg__DepthCandidate __declspec(deprecated)
#endif

namespace macrobot_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct DepthCandidate_
{
  using Type = DepthCandidate_<ContainerAllocator>;

  explicit DepthCandidate_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : roi(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->id = 0ul;
      this->center_x = 0.0f;
      this->center_y = 0.0f;
      this->median_depth_m = 0.0f;
      this->near_depth_m = 0.0f;
      this->far_depth_m = 0.0f;
      this->depth_std_m = 0.0f;
      this->valid_depth_ratio = 0.0f;
      this->fill_ratio = 0.0f;
      this->area_ratio = 0.0f;
      this->foreground_height_m = 0.0f;
      this->foreground_height_valid = false;
      this->proposal_score = 0.0f;
      this->touches_border = false;
    }
  }

  explicit DepthCandidate_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : roi(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->id = 0ul;
      this->center_x = 0.0f;
      this->center_y = 0.0f;
      this->median_depth_m = 0.0f;
      this->near_depth_m = 0.0f;
      this->far_depth_m = 0.0f;
      this->depth_std_m = 0.0f;
      this->valid_depth_ratio = 0.0f;
      this->fill_ratio = 0.0f;
      this->area_ratio = 0.0f;
      this->foreground_height_m = 0.0f;
      this->foreground_height_valid = false;
      this->proposal_score = 0.0f;
      this->touches_border = false;
    }
  }

  // field types and members
  using _id_type =
    uint32_t;
  _id_type id;
  using _roi_type =
    sensor_msgs::msg::RegionOfInterest_<ContainerAllocator>;
  _roi_type roi;
  using _center_x_type =
    float;
  _center_x_type center_x;
  using _center_y_type =
    float;
  _center_y_type center_y;
  using _median_depth_m_type =
    float;
  _median_depth_m_type median_depth_m;
  using _near_depth_m_type =
    float;
  _near_depth_m_type near_depth_m;
  using _far_depth_m_type =
    float;
  _far_depth_m_type far_depth_m;
  using _depth_std_m_type =
    float;
  _depth_std_m_type depth_std_m;
  using _valid_depth_ratio_type =
    float;
  _valid_depth_ratio_type valid_depth_ratio;
  using _fill_ratio_type =
    float;
  _fill_ratio_type fill_ratio;
  using _area_ratio_type =
    float;
  _area_ratio_type area_ratio;
  using _foreground_height_m_type =
    float;
  _foreground_height_m_type foreground_height_m;
  using _foreground_height_valid_type =
    bool;
  _foreground_height_valid_type foreground_height_valid;
  using _proposal_score_type =
    float;
  _proposal_score_type proposal_score;
  using _touches_border_type =
    bool;
  _touches_border_type touches_border;

  // setters for named parameter idiom
  Type & set__id(
    const uint32_t & _arg)
  {
    this->id = _arg;
    return *this;
  }
  Type & set__roi(
    const sensor_msgs::msg::RegionOfInterest_<ContainerAllocator> & _arg)
  {
    this->roi = _arg;
    return *this;
  }
  Type & set__center_x(
    const float & _arg)
  {
    this->center_x = _arg;
    return *this;
  }
  Type & set__center_y(
    const float & _arg)
  {
    this->center_y = _arg;
    return *this;
  }
  Type & set__median_depth_m(
    const float & _arg)
  {
    this->median_depth_m = _arg;
    return *this;
  }
  Type & set__near_depth_m(
    const float & _arg)
  {
    this->near_depth_m = _arg;
    return *this;
  }
  Type & set__far_depth_m(
    const float & _arg)
  {
    this->far_depth_m = _arg;
    return *this;
  }
  Type & set__depth_std_m(
    const float & _arg)
  {
    this->depth_std_m = _arg;
    return *this;
  }
  Type & set__valid_depth_ratio(
    const float & _arg)
  {
    this->valid_depth_ratio = _arg;
    return *this;
  }
  Type & set__fill_ratio(
    const float & _arg)
  {
    this->fill_ratio = _arg;
    return *this;
  }
  Type & set__area_ratio(
    const float & _arg)
  {
    this->area_ratio = _arg;
    return *this;
  }
  Type & set__foreground_height_m(
    const float & _arg)
  {
    this->foreground_height_m = _arg;
    return *this;
  }
  Type & set__foreground_height_valid(
    const bool & _arg)
  {
    this->foreground_height_valid = _arg;
    return *this;
  }
  Type & set__proposal_score(
    const float & _arg)
  {
    this->proposal_score = _arg;
    return *this;
  }
  Type & set__touches_border(
    const bool & _arg)
  {
    this->touches_border = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator> *;
  using ConstRawPtr =
    const macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__macrobot_interfaces__msg__DepthCandidate
    std::shared_ptr<macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__macrobot_interfaces__msg__DepthCandidate
    std::shared_ptr<macrobot_interfaces::msg::DepthCandidate_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DepthCandidate_ & other) const
  {
    if (this->id != other.id) {
      return false;
    }
    if (this->roi != other.roi) {
      return false;
    }
    if (this->center_x != other.center_x) {
      return false;
    }
    if (this->center_y != other.center_y) {
      return false;
    }
    if (this->median_depth_m != other.median_depth_m) {
      return false;
    }
    if (this->near_depth_m != other.near_depth_m) {
      return false;
    }
    if (this->far_depth_m != other.far_depth_m) {
      return false;
    }
    if (this->depth_std_m != other.depth_std_m) {
      return false;
    }
    if (this->valid_depth_ratio != other.valid_depth_ratio) {
      return false;
    }
    if (this->fill_ratio != other.fill_ratio) {
      return false;
    }
    if (this->area_ratio != other.area_ratio) {
      return false;
    }
    if (this->foreground_height_m != other.foreground_height_m) {
      return false;
    }
    if (this->foreground_height_valid != other.foreground_height_valid) {
      return false;
    }
    if (this->proposal_score != other.proposal_score) {
      return false;
    }
    if (this->touches_border != other.touches_border) {
      return false;
    }
    return true;
  }
  bool operator!=(const DepthCandidate_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DepthCandidate_

// alias to use template instance with default allocator
using DepthCandidate =
  macrobot_interfaces::msg::DepthCandidate_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__DEPTH_CANDIDATE__STRUCT_HPP_
