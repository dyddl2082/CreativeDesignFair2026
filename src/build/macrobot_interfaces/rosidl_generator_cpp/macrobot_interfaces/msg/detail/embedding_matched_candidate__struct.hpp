// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from macrobot_interfaces:msg/EmbeddingMatchedCandidate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/embedding_matched_candidate.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__STRUCT_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__STRUCT_HPP_

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
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__struct.hpp"
// Member 'filtered_crop'
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__macrobot_interfaces__msg__EmbeddingMatchedCandidate __attribute__((deprecated))
#else
# define DEPRECATED__macrobot_interfaces__msg__EmbeddingMatchedCandidate __declspec(deprecated)
#endif

namespace macrobot_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct EmbeddingMatchedCandidate_
{
  using Type = EmbeddingMatchedCandidate_<ContainerAllocator>;

  explicit EmbeddingMatchedCandidate_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : result(_init),
    filtered_crop(_init)
  {
    (void)_init;
  }

  explicit EmbeddingMatchedCandidate_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : result(_alloc, _init),
    filtered_crop(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _result_type =
    macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator>;
  _result_type result;
  using _filtered_crop_type =
    macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator>;
  _filtered_crop_type filtered_crop;

  // setters for named parameter idiom
  Type & set__result(
    const macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator> & _arg)
  {
    this->result = _arg;
    return *this;
  }
  Type & set__filtered_crop(
    const macrobot_interfaces::msg::FilteredCandidateCrop_<ContainerAllocator> & _arg)
  {
    this->filtered_crop = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    macrobot_interfaces::msg::EmbeddingMatchedCandidate_<ContainerAllocator> *;
  using ConstRawPtr =
    const macrobot_interfaces::msg::EmbeddingMatchedCandidate_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::EmbeddingMatchedCandidate_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::EmbeddingMatchedCandidate_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::EmbeddingMatchedCandidate_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::EmbeddingMatchedCandidate_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::EmbeddingMatchedCandidate_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::EmbeddingMatchedCandidate_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::EmbeddingMatchedCandidate_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::EmbeddingMatchedCandidate_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__macrobot_interfaces__msg__EmbeddingMatchedCandidate
    std::shared_ptr<macrobot_interfaces::msg::EmbeddingMatchedCandidate_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__macrobot_interfaces__msg__EmbeddingMatchedCandidate
    std::shared_ptr<macrobot_interfaces::msg::EmbeddingMatchedCandidate_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const EmbeddingMatchedCandidate_ & other) const
  {
    if (this->result != other.result) {
      return false;
    }
    if (this->filtered_crop != other.filtered_crop) {
      return false;
    }
    return true;
  }
  bool operator!=(const EmbeddingMatchedCandidate_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct EmbeddingMatchedCandidate_

// alias to use template instance with default allocator
using EmbeddingMatchedCandidate =
  macrobot_interfaces::msg::EmbeddingMatchedCandidate_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__EMBEDDING_MATCHED_CANDIDATE__STRUCT_HPP_
