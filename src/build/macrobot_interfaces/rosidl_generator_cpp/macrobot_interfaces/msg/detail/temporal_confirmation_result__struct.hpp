// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from macrobot_interfaces:msg/TemporalConfirmationResult.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "macrobot_interfaces/msg/temporal_confirmation_result.hpp"


#ifndef MACROBOT_INTERFACES__MSG__DETAIL__TEMPORAL_CONFIRMATION_RESULT__STRUCT_HPP_
#define MACROBOT_INTERFACES__MSG__DETAIL__TEMPORAL_CONFIRMATION_RESULT__STRUCT_HPP_

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
// Member 'roi'
#include "sensor_msgs/msg/detail/region_of_interest__struct.hpp"
// Member 'latest_result'
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__macrobot_interfaces__msg__TemporalConfirmationResult __attribute__((deprecated))
#else
# define DEPRECATED__macrobot_interfaces__msg__TemporalConfirmationResult __declspec(deprecated)
#endif

namespace macrobot_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct TemporalConfirmationResult_
{
  using Type = TemporalConfirmationResult_<ContainerAllocator>;

  explicit TemporalConfirmationResult_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    roi(_init),
    latest_result(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->target_object = "";
      this->track_id = 0ul;
      this->frame_index = 0ull;
      this->state = "";
      this->event = "";
      this->confirmed = false;
      this->track_age_frames = 0ul;
      this->window_size = 0ul;
      this->required_hits = 0ul;
      this->samples_in_window = 0ul;
      this->matched_frames_in_window = 0ul;
      this->hits_in_window = 0ul;
      this->misses_in_window = 0ul;
      this->consecutive_hits = 0ul;
      this->consecutive_misses = 0ul;
      this->hit_ratio = 0.0f;
      this->temporal_score = 0.0f;
      this->stability_score = 0.0f;
      this->mean_positive_similarity = 0.0f;
      this->mean_negative_similarity = 0.0f;
      this->mean_margin = 0.0f;
      this->min_margin_in_window = 0.0f;
      this->mean_objectness_score = 0.0f;
      this->center_x = 0.0f;
      this->center_y = 0.0f;
      this->depth_m = 0.0f;
      this->center_std_px = 0.0f;
      this->depth_std_m = 0.0f;
      this->horizontal_error_norm = 0.0f;
      this->suggested_turn = "";
    }
  }

  explicit TemporalConfirmationResult_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    target_object(_alloc),
    state(_alloc),
    event(_alloc),
    roi(_alloc, _init),
    suggested_turn(_alloc),
    latest_result(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->target_object = "";
      this->track_id = 0ul;
      this->frame_index = 0ull;
      this->state = "";
      this->event = "";
      this->confirmed = false;
      this->track_age_frames = 0ul;
      this->window_size = 0ul;
      this->required_hits = 0ul;
      this->samples_in_window = 0ul;
      this->matched_frames_in_window = 0ul;
      this->hits_in_window = 0ul;
      this->misses_in_window = 0ul;
      this->consecutive_hits = 0ul;
      this->consecutive_misses = 0ul;
      this->hit_ratio = 0.0f;
      this->temporal_score = 0.0f;
      this->stability_score = 0.0f;
      this->mean_positive_similarity = 0.0f;
      this->mean_negative_similarity = 0.0f;
      this->mean_margin = 0.0f;
      this->min_margin_in_window = 0.0f;
      this->mean_objectness_score = 0.0f;
      this->center_x = 0.0f;
      this->center_y = 0.0f;
      this->depth_m = 0.0f;
      this->center_std_px = 0.0f;
      this->depth_std_m = 0.0f;
      this->horizontal_error_norm = 0.0f;
      this->suggested_turn = "";
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _target_object_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _target_object_type target_object;
  using _track_id_type =
    uint32_t;
  _track_id_type track_id;
  using _frame_index_type =
    uint64_t;
  _frame_index_type frame_index;
  using _state_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _state_type state;
  using _event_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _event_type event;
  using _confirmed_type =
    bool;
  _confirmed_type confirmed;
  using _track_age_frames_type =
    uint32_t;
  _track_age_frames_type track_age_frames;
  using _window_size_type =
    uint32_t;
  _window_size_type window_size;
  using _required_hits_type =
    uint32_t;
  _required_hits_type required_hits;
  using _samples_in_window_type =
    uint32_t;
  _samples_in_window_type samples_in_window;
  using _matched_frames_in_window_type =
    uint32_t;
  _matched_frames_in_window_type matched_frames_in_window;
  using _hits_in_window_type =
    uint32_t;
  _hits_in_window_type hits_in_window;
  using _misses_in_window_type =
    uint32_t;
  _misses_in_window_type misses_in_window;
  using _consecutive_hits_type =
    uint32_t;
  _consecutive_hits_type consecutive_hits;
  using _consecutive_misses_type =
    uint32_t;
  _consecutive_misses_type consecutive_misses;
  using _hit_ratio_type =
    float;
  _hit_ratio_type hit_ratio;
  using _temporal_score_type =
    float;
  _temporal_score_type temporal_score;
  using _stability_score_type =
    float;
  _stability_score_type stability_score;
  using _mean_positive_similarity_type =
    float;
  _mean_positive_similarity_type mean_positive_similarity;
  using _mean_negative_similarity_type =
    float;
  _mean_negative_similarity_type mean_negative_similarity;
  using _mean_margin_type =
    float;
  _mean_margin_type mean_margin;
  using _min_margin_in_window_type =
    float;
  _min_margin_in_window_type min_margin_in_window;
  using _mean_objectness_score_type =
    float;
  _mean_objectness_score_type mean_objectness_score;
  using _roi_type =
    sensor_msgs::msg::RegionOfInterest_<ContainerAllocator>;
  _roi_type roi;
  using _center_x_type =
    float;
  _center_x_type center_x;
  using _center_y_type =
    float;
  _center_y_type center_y;
  using _depth_m_type =
    float;
  _depth_m_type depth_m;
  using _center_std_px_type =
    float;
  _center_std_px_type center_std_px;
  using _depth_std_m_type =
    float;
  _depth_std_m_type depth_std_m;
  using _horizontal_error_norm_type =
    float;
  _horizontal_error_norm_type horizontal_error_norm;
  using _suggested_turn_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _suggested_turn_type suggested_turn;
  using _latest_result_type =
    macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator>;
  _latest_result_type latest_result;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__target_object(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->target_object = _arg;
    return *this;
  }
  Type & set__track_id(
    const uint32_t & _arg)
  {
    this->track_id = _arg;
    return *this;
  }
  Type & set__frame_index(
    const uint64_t & _arg)
  {
    this->frame_index = _arg;
    return *this;
  }
  Type & set__state(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->state = _arg;
    return *this;
  }
  Type & set__event(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->event = _arg;
    return *this;
  }
  Type & set__confirmed(
    const bool & _arg)
  {
    this->confirmed = _arg;
    return *this;
  }
  Type & set__track_age_frames(
    const uint32_t & _arg)
  {
    this->track_age_frames = _arg;
    return *this;
  }
  Type & set__window_size(
    const uint32_t & _arg)
  {
    this->window_size = _arg;
    return *this;
  }
  Type & set__required_hits(
    const uint32_t & _arg)
  {
    this->required_hits = _arg;
    return *this;
  }
  Type & set__samples_in_window(
    const uint32_t & _arg)
  {
    this->samples_in_window = _arg;
    return *this;
  }
  Type & set__matched_frames_in_window(
    const uint32_t & _arg)
  {
    this->matched_frames_in_window = _arg;
    return *this;
  }
  Type & set__hits_in_window(
    const uint32_t & _arg)
  {
    this->hits_in_window = _arg;
    return *this;
  }
  Type & set__misses_in_window(
    const uint32_t & _arg)
  {
    this->misses_in_window = _arg;
    return *this;
  }
  Type & set__consecutive_hits(
    const uint32_t & _arg)
  {
    this->consecutive_hits = _arg;
    return *this;
  }
  Type & set__consecutive_misses(
    const uint32_t & _arg)
  {
    this->consecutive_misses = _arg;
    return *this;
  }
  Type & set__hit_ratio(
    const float & _arg)
  {
    this->hit_ratio = _arg;
    return *this;
  }
  Type & set__temporal_score(
    const float & _arg)
  {
    this->temporal_score = _arg;
    return *this;
  }
  Type & set__stability_score(
    const float & _arg)
  {
    this->stability_score = _arg;
    return *this;
  }
  Type & set__mean_positive_similarity(
    const float & _arg)
  {
    this->mean_positive_similarity = _arg;
    return *this;
  }
  Type & set__mean_negative_similarity(
    const float & _arg)
  {
    this->mean_negative_similarity = _arg;
    return *this;
  }
  Type & set__mean_margin(
    const float & _arg)
  {
    this->mean_margin = _arg;
    return *this;
  }
  Type & set__min_margin_in_window(
    const float & _arg)
  {
    this->min_margin_in_window = _arg;
    return *this;
  }
  Type & set__mean_objectness_score(
    const float & _arg)
  {
    this->mean_objectness_score = _arg;
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
  Type & set__depth_m(
    const float & _arg)
  {
    this->depth_m = _arg;
    return *this;
  }
  Type & set__center_std_px(
    const float & _arg)
  {
    this->center_std_px = _arg;
    return *this;
  }
  Type & set__depth_std_m(
    const float & _arg)
  {
    this->depth_std_m = _arg;
    return *this;
  }
  Type & set__horizontal_error_norm(
    const float & _arg)
  {
    this->horizontal_error_norm = _arg;
    return *this;
  }
  Type & set__suggested_turn(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->suggested_turn = _arg;
    return *this;
  }
  Type & set__latest_result(
    const macrobot_interfaces::msg::EmbeddingRetrievalResult_<ContainerAllocator> & _arg)
  {
    this->latest_result = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    macrobot_interfaces::msg::TemporalConfirmationResult_<ContainerAllocator> *;
  using ConstRawPtr =
    const macrobot_interfaces::msg::TemporalConfirmationResult_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::TemporalConfirmationResult_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<macrobot_interfaces::msg::TemporalConfirmationResult_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::TemporalConfirmationResult_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::TemporalConfirmationResult_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      macrobot_interfaces::msg::TemporalConfirmationResult_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<macrobot_interfaces::msg::TemporalConfirmationResult_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::TemporalConfirmationResult_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<macrobot_interfaces::msg::TemporalConfirmationResult_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__macrobot_interfaces__msg__TemporalConfirmationResult
    std::shared_ptr<macrobot_interfaces::msg::TemporalConfirmationResult_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__macrobot_interfaces__msg__TemporalConfirmationResult
    std::shared_ptr<macrobot_interfaces::msg::TemporalConfirmationResult_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const TemporalConfirmationResult_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->target_object != other.target_object) {
      return false;
    }
    if (this->track_id != other.track_id) {
      return false;
    }
    if (this->frame_index != other.frame_index) {
      return false;
    }
    if (this->state != other.state) {
      return false;
    }
    if (this->event != other.event) {
      return false;
    }
    if (this->confirmed != other.confirmed) {
      return false;
    }
    if (this->track_age_frames != other.track_age_frames) {
      return false;
    }
    if (this->window_size != other.window_size) {
      return false;
    }
    if (this->required_hits != other.required_hits) {
      return false;
    }
    if (this->samples_in_window != other.samples_in_window) {
      return false;
    }
    if (this->matched_frames_in_window != other.matched_frames_in_window) {
      return false;
    }
    if (this->hits_in_window != other.hits_in_window) {
      return false;
    }
    if (this->misses_in_window != other.misses_in_window) {
      return false;
    }
    if (this->consecutive_hits != other.consecutive_hits) {
      return false;
    }
    if (this->consecutive_misses != other.consecutive_misses) {
      return false;
    }
    if (this->hit_ratio != other.hit_ratio) {
      return false;
    }
    if (this->temporal_score != other.temporal_score) {
      return false;
    }
    if (this->stability_score != other.stability_score) {
      return false;
    }
    if (this->mean_positive_similarity != other.mean_positive_similarity) {
      return false;
    }
    if (this->mean_negative_similarity != other.mean_negative_similarity) {
      return false;
    }
    if (this->mean_margin != other.mean_margin) {
      return false;
    }
    if (this->min_margin_in_window != other.min_margin_in_window) {
      return false;
    }
    if (this->mean_objectness_score != other.mean_objectness_score) {
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
    if (this->depth_m != other.depth_m) {
      return false;
    }
    if (this->center_std_px != other.center_std_px) {
      return false;
    }
    if (this->depth_std_m != other.depth_std_m) {
      return false;
    }
    if (this->horizontal_error_norm != other.horizontal_error_norm) {
      return false;
    }
    if (this->suggested_turn != other.suggested_turn) {
      return false;
    }
    if (this->latest_result != other.latest_result) {
      return false;
    }
    return true;
  }
  bool operator!=(const TemporalConfirmationResult_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct TemporalConfirmationResult_

// alias to use template instance with default allocator
using TemporalConfirmationResult =
  macrobot_interfaces::msg::TemporalConfirmationResult_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace macrobot_interfaces

#endif  // MACROBOT_INTERFACES__MSG__DETAIL__TEMPORAL_CONFIRMATION_RESULT__STRUCT_HPP_
