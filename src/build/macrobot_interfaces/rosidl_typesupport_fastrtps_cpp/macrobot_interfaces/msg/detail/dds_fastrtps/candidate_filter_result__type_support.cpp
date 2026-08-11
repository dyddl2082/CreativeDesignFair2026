// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from macrobot_interfaces:msg/CandidateFilterResult.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/candidate_filter_result__rosidl_typesupport_fastrtps_cpp.hpp"
#include "macrobot_interfaces/msg/detail/candidate_filter_result__functions.h"
#include "macrobot_interfaces/msg/detail/candidate_filter_result__struct.hpp"

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
  const macrobot_interfaces::msg::CandidateFilterResult & ros_message,
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

  // Member: reference_profile_available
  cdr << (ros_message.reference_profile_available ? true : false);

  // Member: reference_image_count
  cdr << ros_message.reference_image_count;

  // Member: camera_info_available
  cdr << (ros_message.camera_info_available ? true : false);

  // Member: plane_found
  cdr << (ros_message.plane_found ? true : false);

  // Member: foreground_height_valid
  cdr << (ros_message.foreground_height_valid ? true : false);

  // Member: foreground_mask_available
  cdr << (ros_message.foreground_mask_available ? true : false);

  // Member: accepted
  cdr << (ros_message.accepted ? true : false);

  // Member: reject_stage
  cdr << ros_message.reject_stage;

  // Member: reject_reason
  cdr << ros_message.reject_reason;

  // Member: objectness_score
  cdr << ros_message.objectness_score;

  // Member: target_hint_score
  cdr << ros_message.target_hint_score;

  // Member: filter_score
  cdr << ros_message.filter_score;

  // Member: depth_score
  cdr << ros_message.depth_score;

  // Member: quality_score
  cdr << ros_message.quality_score;

  // Member: color_score
  cdr << ros_message.color_score;

  // Member: shape_score
  cdr << ros_message.shape_score;

  // Member: physical_size_score
  cdr << ros_message.physical_size_score;

  // Member: sharpness
  cdr << ros_message.sharpness;

  // Member: mean_brightness
  cdr << ros_message.mean_brightness;

  // Member: dark_ratio
  cdr << ros_message.dark_ratio;

  // Member: bright_clip_ratio
  cdr << ros_message.bright_clip_ratio;

  // Member: edge_density
  cdr << ros_message.edge_density;

  // Member: mask_fill_ratio
  cdr << ros_message.mask_fill_ratio;

  // Member: mask_solidity
  cdr << ros_message.mask_solidity;

  // Member: color_similarity
  cdr << ros_message.color_similarity;

  // Member: aspect_ratio
  cdr << ros_message.aspect_ratio;

  // Member: estimated_width_m
  cdr << ros_message.estimated_width_m;

  // Member: estimated_height_m
  cdr << ros_message.estimated_height_m;

  // Member: sync_offset_abs_sec
  cdr << ros_message.sync_offset_abs_sec;

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
  macrobot_interfaces::msg::CandidateFilterResult & ros_message)
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

  // Member: reference_profile_available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.reference_profile_available = tmp ? true : false;
  }

  // Member: reference_image_count
  cdr >> ros_message.reference_image_count;

  // Member: camera_info_available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.camera_info_available = tmp ? true : false;
  }

  // Member: plane_found
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.plane_found = tmp ? true : false;
  }

  // Member: foreground_height_valid
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.foreground_height_valid = tmp ? true : false;
  }

  // Member: foreground_mask_available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.foreground_mask_available = tmp ? true : false;
  }

  // Member: accepted
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.accepted = tmp ? true : false;
  }

  // Member: reject_stage
  cdr >> ros_message.reject_stage;

  // Member: reject_reason
  cdr >> ros_message.reject_reason;

  // Member: objectness_score
  cdr >> ros_message.objectness_score;

  // Member: target_hint_score
  cdr >> ros_message.target_hint_score;

  // Member: filter_score
  cdr >> ros_message.filter_score;

  // Member: depth_score
  cdr >> ros_message.depth_score;

  // Member: quality_score
  cdr >> ros_message.quality_score;

  // Member: color_score
  cdr >> ros_message.color_score;

  // Member: shape_score
  cdr >> ros_message.shape_score;

  // Member: physical_size_score
  cdr >> ros_message.physical_size_score;

  // Member: sharpness
  cdr >> ros_message.sharpness;

  // Member: mean_brightness
  cdr >> ros_message.mean_brightness;

  // Member: dark_ratio
  cdr >> ros_message.dark_ratio;

  // Member: bright_clip_ratio
  cdr >> ros_message.bright_clip_ratio;

  // Member: edge_density
  cdr >> ros_message.edge_density;

  // Member: mask_fill_ratio
  cdr >> ros_message.mask_fill_ratio;

  // Member: mask_solidity
  cdr >> ros_message.mask_solidity;

  // Member: color_similarity
  cdr >> ros_message.color_similarity;

  // Member: aspect_ratio
  cdr >> ros_message.aspect_ratio;

  // Member: estimated_width_m
  cdr >> ros_message.estimated_width_m;

  // Member: estimated_height_m
  cdr >> ros_message.estimated_height_m;

  // Member: sync_offset_abs_sec
  cdr >> ros_message.sync_offset_abs_sec;

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
  const macrobot_interfaces::msg::CandidateFilterResult & ros_message,
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

  // Member: reference_profile_available
  {
    size_t item_size = sizeof(ros_message.reference_profile_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: reference_image_count
  {
    size_t item_size = sizeof(ros_message.reference_image_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: camera_info_available
  {
    size_t item_size = sizeof(ros_message.camera_info_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: plane_found
  {
    size_t item_size = sizeof(ros_message.plane_found);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: foreground_height_valid
  {
    size_t item_size = sizeof(ros_message.foreground_height_valid);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: foreground_mask_available
  {
    size_t item_size = sizeof(ros_message.foreground_mask_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: accepted
  {
    size_t item_size = sizeof(ros_message.accepted);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: reject_stage
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.reject_stage.size() + 1);

  // Member: reject_reason
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.reject_reason.size() + 1);

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

  // Member: filter_score
  {
    size_t item_size = sizeof(ros_message.filter_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: depth_score
  {
    size_t item_size = sizeof(ros_message.depth_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: quality_score
  {
    size_t item_size = sizeof(ros_message.quality_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: color_score
  {
    size_t item_size = sizeof(ros_message.color_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: shape_score
  {
    size_t item_size = sizeof(ros_message.shape_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: physical_size_score
  {
    size_t item_size = sizeof(ros_message.physical_size_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: sharpness
  {
    size_t item_size = sizeof(ros_message.sharpness);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: mean_brightness
  {
    size_t item_size = sizeof(ros_message.mean_brightness);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: dark_ratio
  {
    size_t item_size = sizeof(ros_message.dark_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: bright_clip_ratio
  {
    size_t item_size = sizeof(ros_message.bright_clip_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: edge_density
  {
    size_t item_size = sizeof(ros_message.edge_density);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: mask_fill_ratio
  {
    size_t item_size = sizeof(ros_message.mask_fill_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: mask_solidity
  {
    size_t item_size = sizeof(ros_message.mask_solidity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: color_similarity
  {
    size_t item_size = sizeof(ros_message.color_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: aspect_ratio
  {
    size_t item_size = sizeof(ros_message.aspect_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: estimated_width_m
  {
    size_t item_size = sizeof(ros_message.estimated_width_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: estimated_height_m
  {
    size_t item_size = sizeof(ros_message.estimated_height_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: sync_offset_abs_sec
  {
    size_t item_size = sizeof(ros_message.sync_offset_abs_sec);
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
max_serialized_size_CandidateFilterResult(
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
  // Member: reference_profile_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: reference_image_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: camera_info_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: plane_found
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: foreground_height_valid
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: foreground_mask_available
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
  // Member: reject_stage
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
  // Member: filter_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: depth_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: quality_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: color_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: shape_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: physical_size_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: sharpness
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: mean_brightness
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: dark_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: bright_clip_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: edge_density
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: mask_fill_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: mask_solidity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: color_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: aspect_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: estimated_width_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: estimated_height_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: sync_offset_abs_sec
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
    using DataType = macrobot_interfaces::msg::CandidateFilterResult;
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
  const macrobot_interfaces::msg::CandidateFilterResult & ros_message,
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

  // Member: reference_profile_available
  cdr << (ros_message.reference_profile_available ? true : false);

  // Member: reference_image_count
  cdr << ros_message.reference_image_count;

  // Member: camera_info_available
  cdr << (ros_message.camera_info_available ? true : false);

  // Member: plane_found
  cdr << (ros_message.plane_found ? true : false);

  // Member: foreground_height_valid
  cdr << (ros_message.foreground_height_valid ? true : false);

  // Member: foreground_mask_available
  cdr << (ros_message.foreground_mask_available ? true : false);

  // Member: accepted
  cdr << (ros_message.accepted ? true : false);

  // Member: reject_stage
  cdr << ros_message.reject_stage;

  // Member: reject_reason
  cdr << ros_message.reject_reason;

  // Member: objectness_score
  cdr << ros_message.objectness_score;

  // Member: target_hint_score
  cdr << ros_message.target_hint_score;

  // Member: filter_score
  cdr << ros_message.filter_score;

  // Member: depth_score
  cdr << ros_message.depth_score;

  // Member: quality_score
  cdr << ros_message.quality_score;

  // Member: color_score
  cdr << ros_message.color_score;

  // Member: shape_score
  cdr << ros_message.shape_score;

  // Member: physical_size_score
  cdr << ros_message.physical_size_score;

  // Member: sharpness
  cdr << ros_message.sharpness;

  // Member: mean_brightness
  cdr << ros_message.mean_brightness;

  // Member: dark_ratio
  cdr << ros_message.dark_ratio;

  // Member: bright_clip_ratio
  cdr << ros_message.bright_clip_ratio;

  // Member: edge_density
  cdr << ros_message.edge_density;

  // Member: mask_fill_ratio
  cdr << ros_message.mask_fill_ratio;

  // Member: mask_solidity
  cdr << ros_message.mask_solidity;

  // Member: color_similarity
  cdr << ros_message.color_similarity;

  // Member: aspect_ratio
  cdr << ros_message.aspect_ratio;

  // Member: estimated_width_m
  cdr << ros_message.estimated_width_m;

  // Member: estimated_height_m
  cdr << ros_message.estimated_height_m;

  // Member: sync_offset_abs_sec
  cdr << ros_message.sync_offset_abs_sec;

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
  const macrobot_interfaces::msg::CandidateFilterResult & ros_message,
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

  // Member: reference_profile_available
  {
    size_t item_size = sizeof(ros_message.reference_profile_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: reference_image_count
  {
    size_t item_size = sizeof(ros_message.reference_image_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: camera_info_available
  {
    size_t item_size = sizeof(ros_message.camera_info_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: plane_found
  {
    size_t item_size = sizeof(ros_message.plane_found);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: foreground_height_valid
  {
    size_t item_size = sizeof(ros_message.foreground_height_valid);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: foreground_mask_available
  {
    size_t item_size = sizeof(ros_message.foreground_mask_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: accepted
  {
    size_t item_size = sizeof(ros_message.accepted);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: reject_stage
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.reject_stage.size() + 1);

  // Member: reject_reason
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.reject_reason.size() + 1);

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

  // Member: filter_score
  {
    size_t item_size = sizeof(ros_message.filter_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: depth_score
  {
    size_t item_size = sizeof(ros_message.depth_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: quality_score
  {
    size_t item_size = sizeof(ros_message.quality_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: color_score
  {
    size_t item_size = sizeof(ros_message.color_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: shape_score
  {
    size_t item_size = sizeof(ros_message.shape_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: physical_size_score
  {
    size_t item_size = sizeof(ros_message.physical_size_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: sharpness
  {
    size_t item_size = sizeof(ros_message.sharpness);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: mean_brightness
  {
    size_t item_size = sizeof(ros_message.mean_brightness);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: dark_ratio
  {
    size_t item_size = sizeof(ros_message.dark_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: bright_clip_ratio
  {
    size_t item_size = sizeof(ros_message.bright_clip_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: edge_density
  {
    size_t item_size = sizeof(ros_message.edge_density);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: mask_fill_ratio
  {
    size_t item_size = sizeof(ros_message.mask_fill_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: mask_solidity
  {
    size_t item_size = sizeof(ros_message.mask_solidity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: color_similarity
  {
    size_t item_size = sizeof(ros_message.color_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: aspect_ratio
  {
    size_t item_size = sizeof(ros_message.aspect_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: estimated_width_m
  {
    size_t item_size = sizeof(ros_message.estimated_width_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: estimated_height_m
  {
    size_t item_size = sizeof(ros_message.estimated_height_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: sync_offset_abs_sec
  {
    size_t item_size = sizeof(ros_message.sync_offset_abs_sec);
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
max_serialized_size_key_CandidateFilterResult(
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

  // Member: reference_profile_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: reference_image_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: camera_info_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: plane_found
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: foreground_height_valid
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: foreground_mask_available
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

  // Member: reject_stage
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

  // Member: filter_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: depth_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: quality_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: color_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: shape_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: physical_size_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: sharpness
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: mean_brightness
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: dark_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: bright_clip_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: edge_density
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: mask_fill_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: mask_solidity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: color_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: aspect_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: estimated_width_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: estimated_height_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: sync_offset_abs_sec
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
    using DataType = macrobot_interfaces::msg::CandidateFilterResult;
    is_plain =
      (
      offsetof(DataType, crop_roi) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}


static bool _CandidateFilterResult__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const macrobot_interfaces::msg::CandidateFilterResult *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _CandidateFilterResult__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<macrobot_interfaces::msg::CandidateFilterResult *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _CandidateFilterResult__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const macrobot_interfaces::msg::CandidateFilterResult *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _CandidateFilterResult__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_CandidateFilterResult(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _CandidateFilterResult__callbacks = {
  "macrobot_interfaces::msg",
  "CandidateFilterResult",
  _CandidateFilterResult__cdr_serialize,
  _CandidateFilterResult__cdr_deserialize,
  _CandidateFilterResult__get_serialized_size,
  _CandidateFilterResult__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _CandidateFilterResult__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_CandidateFilterResult__callbacks,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__CandidateFilterResult__get_type_hash,
  &macrobot_interfaces__msg__CandidateFilterResult__get_type_description,
  &macrobot_interfaces__msg__CandidateFilterResult__get_type_description_sources,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace macrobot_interfaces

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_macrobot_interfaces
const rosidl_message_type_support_t *
get_message_type_support_handle<macrobot_interfaces::msg::CandidateFilterResult>()
{
  return &macrobot_interfaces::msg::typesupport_fastrtps_cpp::_CandidateFilterResult__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, macrobot_interfaces, msg, CandidateFilterResult)() {
  return &macrobot_interfaces::msg::typesupport_fastrtps_cpp::_CandidateFilterResult__handle;
}

#ifdef __cplusplus
}
#endif
