// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from macrobot_interfaces:msg/FilteredCandidateCrop.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/filtered_candidate_crop.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__STRUCT_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'result'
#include "macrobot_interfaces/msg/detail/candidate_filter_result__struct.hpp"
// Member 'crop'
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__macrobot_interfaces__msg__FilteredCandidateCrop __attribute__((deprecated))
#else
# define DEPRECATED__macrobot_interfaces__msg__FilteredCandidateCrop __declspec(deprecated)
#endif

namespace macrobot_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct FilteredCandidateCrop_
{
  using Type = FilteredCandidateCrop_<ContainerAllocator>;

  explicit FilteredCandidateCrop_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : result(_init),
    crop(_init)
  {
    (void)_init;
  }

  explicit FilteredCandidateCrop_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : result(_alloc, _init),
    crop(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _result_type =
    macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator>;
  _result_type result;
  using _crop_type =
    macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator>;
  _crop_type crop;

  // setters for named parameter idiom
  Type & set__result(
    const macrobot_interfaces::msg::CandidateFilterResult_<ContainerAllocator> & _arg)
  {
    this->result = _arg;
    return *this;
  }
  Type & set__crop(
    const macrobot_interfaces::msg::RgbCandidateCrop_<ContainerAllocator> & _arg)
  {
    this->crop = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator> *;
  using ConstRawPtr =
    const macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__macrobot_interfaces__msg__FilteredCandidateCrop
    std::shared_ptr<macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__macrobot_interfaces__msg__FilteredCandidateCrop
    std::shared_ptr<macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const FilteredCandidateCrop_ & other) const
  {
    if (this->result != other.result) {
      return false;
    }
    if (this->crop != other.crop) {
      return false;
    }
    return true;
  }
  bool operator!=(const FilteredCandidateCrop_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct FilteredCandidateCrop_

// alias to use template instance with default allocator
using FilteredCandidateCrop =
  macrobot_interfaces::msg::FilteredCandidateCrop_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__FILTERED_CANDIDATE_CROP__STRUCT_HPP_
