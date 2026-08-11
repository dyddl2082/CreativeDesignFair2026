// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from macrobot_interfaces:msg/RgbCandidateCrop.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__rosidl_typesupport_fastrtps_cpp.hpp"
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__functions.h"
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__struct.hpp"

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

namespace sensor_msgs
{
namespace msg
{
namespace typesupport_fastrtps_cpp
{
bool cdr_serialize(
  const sensor_msgs::msg::CompressedImage &,
  eprosima::fastcdr::Cdr &);
bool cdr_deserialize(
  eprosima::fastcdr::Cdr &,
  sensor_msgs::msg::CompressedImage &);
size_t get_serialized_size(
  const sensor_msgs::msg::CompressedImage &,
  size_t current_alignment);
size_t
max_serialized_size_CompressedImage(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
bool cdr_serialize_key(
  const sensor_msgs::msg::CompressedImage &,
  eprosima::fastcdr::Cdr &);
size_t get_serialized_size_key(
  const sensor_msgs::msg::CompressedImage &,
  size_t current_alignment);
size_t
max_serialized_size_key_CompressedImage(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
}  // namespace typesupport_fastrtps_cpp
}  // namespace msg
}  // namespace sensor_msgs

// functions for sensor_msgs::msg::CompressedImage already declared above


namespace macrobot_interfaces
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{


bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
cdr_serialize(
  const macrobot_interfaces::msg::RgbCandidateCrop & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: proposal_header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.proposal_header,
    cdr);

  // Member: proposal_image_width
  cdr << ros_message.proposal_image_width;

  // Member: proposal_image_height
  cdr << ros_message.proposal_image_height;

  // Member: color_image_width
  cdr << ros_message.color_image_width;

  // Member: color_image_height
  cdr << ros_message.color_image_height;

  // Member: source_candidate_count
  cdr << ros_message.source_candidate_count;

  // Member: frame_crop_count
  cdr << ros_message.frame_crop_count;

  // Member: crop_index
  cdr << ros_message.crop_index;

  // Member: candidate
  macrobot_interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.candidate,
    cdr);

  // Member: crop_roi
  sensor_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.crop_roi,
    cdr);

  // Member: color_time_offset_sec
  cdr << ros_message.color_time_offset_sec;

  // Member: plane_found
  cdr << (ros_message.plane_found ? true : false);

  // Member: foreground_mask_available
  cdr << (ros_message.foreground_mask_available ? true : false);

  // Member: mask_fill_ratio
  cdr << ros_message.mask_fill_ratio;

  // Member: foreground_mask
  sensor_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.foreground_mask,
    cdr);

  // Member: encoded_width
  cdr << ros_message.encoded_width;

  // Member: encoded_height
  cdr << ros_message.encoded_height;

  // Member: jpeg_size_bytes
  cdr << ros_message.jpeg_size_bytes;

  // Member: jpeg_quality
  cdr << ros_message.jpeg_quality;

  // Member: size_limit_met
  cdr << (ros_message.size_limit_met ? true : false);

  // Member: image
  sensor_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.image,
    cdr);

  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces::msg::RgbCandidateCrop & ros_message)
{
  // Member: proposal_header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.proposal_header);

  // Member: proposal_image_width
  cdr >> ros_message.proposal_image_width;

  // Member: proposal_image_height
  cdr >> ros_message.proposal_image_height;

  // Member: color_image_width
  cdr >> ros_message.color_image_width;

  // Member: color_image_height
  cdr >> ros_message.color_image_height;

  // Member: source_candidate_count
  cdr >> ros_message.source_candidate_count;

  // Member: frame_crop_count
  cdr >> ros_message.frame_crop_count;

  // Member: crop_index
  cdr >> ros_message.crop_index;

  // Member: candidate
  macrobot_interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.candidate);

  // Member: crop_roi
  sensor_msgs::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.crop_roi);

  // Member: color_time_offset_sec
  cdr >> ros_message.color_time_offset_sec;

  // Member: plane_found
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.plane_found = tmp ? true : false;
  }

  // Member: foreground_mask_available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.foreground_mask_available = tmp ? true : false;
  }

  // Member: mask_fill_ratio
  cdr >> ros_message.mask_fill_ratio;

  // Member: foreground_mask
  sensor_msgs::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.foreground_mask);

  // Member: encoded_width
  cdr >> ros_message.encoded_width;

  // Member: encoded_height
  cdr >> ros_message.encoded_height;

  // Member: jpeg_size_bytes
  cdr >> ros_message.jpeg_size_bytes;

  // Member: jpeg_quality
  cdr >> ros_message.jpeg_quality;

  // Member: size_limit_met
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.size_limit_met = tmp ? true : false;
  }

  // Member: image
  sensor_msgs::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.image);

  return true;
}  // NOLINT(readability/fn_size)


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
get_serialized_size(
  const macrobot_interfaces::msg::RgbCandidateCrop & ros_message,
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

  // Member: proposal_image_width
  {
    size_t item_size = sizeof(ros_message.proposal_image_width);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: proposal_image_height
  {
    size_t item_size = sizeof(ros_message.proposal_image_height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: color_image_width
  {
    size_t item_size = sizeof(ros_message.color_image_width);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: color_image_height
  {
    size_t item_size = sizeof(ros_message.color_image_height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: source_candidate_count
  {
    size_t item_size = sizeof(ros_message.source_candidate_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: frame_crop_count
  {
    size_t item_size = sizeof(ros_message.frame_crop_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: crop_index
  {
    size_t item_size = sizeof(ros_message.crop_index);
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

  // Member: color_time_offset_sec
  {
    size_t item_size = sizeof(ros_message.color_time_offset_sec);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: plane_found
  {
    size_t item_size = sizeof(ros_message.plane_found);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: foreground_mask_available
  {
    size_t item_size = sizeof(ros_message.foreground_mask_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: mask_fill_ratio
  {
    size_t item_size = sizeof(ros_message.mask_fill_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: foreground_mask
  current_alignment +=
    sensor_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.foreground_mask, current_alignment);

  // Member: encoded_width
  {
    size_t item_size = sizeof(ros_message.encoded_width);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: encoded_height
  {
    size_t item_size = sizeof(ros_message.encoded_height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: jpeg_size_bytes
  {
    size_t item_size = sizeof(ros_message.jpeg_size_bytes);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: jpeg_quality
  {
    size_t item_size = sizeof(ros_message.jpeg_quality);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: size_limit_met
  {
    size_t item_size = sizeof(ros_message.size_limit_met);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: image
  current_alignment +=
    sensor_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.image, current_alignment);

  return current_alignment - initial_alignment;
}


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
max_serialized_size_RgbCandidateCrop(
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
  // Member: proposal_image_width
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: proposal_image_height
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: color_image_width
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: color_image_height
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: source_candidate_count
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
  // Member: crop_index
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
  // Member: color_time_offset_sec
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: plane_found
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
  // Member: mask_fill_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: foreground_mask
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        sensor_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_CompressedImage(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // Member: encoded_width
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: encoded_height
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: jpeg_size_bytes
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: jpeg_quality
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: size_limit_met
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: image
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        sensor_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_CompressedImage(
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
    using DataType = macrobot_interfaces::msg::RgbCandidateCrop;
    is_plain =
      (
      offsetof(DataType, image) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
cdr_serialize_key(
  const macrobot_interfaces::msg::RgbCandidateCrop & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: proposal_header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize_key(
    ros_message.proposal_header,
    cdr);

  // Member: proposal_image_width
  cdr << ros_message.proposal_image_width;

  // Member: proposal_image_height
  cdr << ros_message.proposal_image_height;

  // Member: color_image_width
  cdr << ros_message.color_image_width;

  // Member: color_image_height
  cdr << ros_message.color_image_height;

  // Member: source_candidate_count
  cdr << ros_message.source_candidate_count;

  // Member: frame_crop_count
  cdr << ros_message.frame_crop_count;

  // Member: crop_index
  cdr << ros_message.crop_index;

  // Member: candidate
  macrobot_interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize_key(
    ros_message.candidate,
    cdr);

  // Member: crop_roi
  sensor_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize_key(
    ros_message.crop_roi,
    cdr);

  // Member: color_time_offset_sec
  cdr << ros_message.color_time_offset_sec;

  // Member: plane_found
  cdr << (ros_message.plane_found ? true : false);

  // Member: foreground_mask_available
  cdr << (ros_message.foreground_mask_available ? true : false);

  // Member: mask_fill_ratio
  cdr << ros_message.mask_fill_ratio;

  // Member: foreground_mask
  sensor_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize_key(
    ros_message.foreground_mask,
    cdr);

  // Member: encoded_width
  cdr << ros_message.encoded_width;

  // Member: encoded_height
  cdr << ros_message.encoded_height;

  // Member: jpeg_size_bytes
  cdr << ros_message.jpeg_size_bytes;

  // Member: jpeg_quality
  cdr << ros_message.jpeg_quality;

  // Member: size_limit_met
  cdr << (ros_message.size_limit_met ? true : false);

  // Member: image
  sensor_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize_key(
    ros_message.image,
    cdr);

  return true;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
get_serialized_size_key(
  const macrobot_interfaces::msg::RgbCandidateCrop & ros_message,
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

  // Member: proposal_image_width
  {
    size_t item_size = sizeof(ros_message.proposal_image_width);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: proposal_image_height
  {
    size_t item_size = sizeof(ros_message.proposal_image_height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: color_image_width
  {
    size_t item_size = sizeof(ros_message.color_image_width);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: color_image_height
  {
    size_t item_size = sizeof(ros_message.color_image_height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: source_candidate_count
  {
    size_t item_size = sizeof(ros_message.source_candidate_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: frame_crop_count
  {
    size_t item_size = sizeof(ros_message.frame_crop_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: crop_index
  {
    size_t item_size = sizeof(ros_message.crop_index);
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

  // Member: color_time_offset_sec
  {
    size_t item_size = sizeof(ros_message.color_time_offset_sec);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: plane_found
  {
    size_t item_size = sizeof(ros_message.plane_found);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: foreground_mask_available
  {
    size_t item_size = sizeof(ros_message.foreground_mask_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: mask_fill_ratio
  {
    size_t item_size = sizeof(ros_message.mask_fill_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: foreground_mask
  current_alignment +=
    sensor_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size_key(
    ros_message.foreground_mask, current_alignment);

  // Member: encoded_width
  {
    size_t item_size = sizeof(ros_message.encoded_width);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: encoded_height
  {
    size_t item_size = sizeof(ros_message.encoded_height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: jpeg_size_bytes
  {
    size_t item_size = sizeof(ros_message.jpeg_size_bytes);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: jpeg_quality
  {
    size_t item_size = sizeof(ros_message.jpeg_quality);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: size_limit_met
  {
    size_t item_size = sizeof(ros_message.size_limit_met);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: image
  current_alignment +=
    sensor_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size_key(
    ros_message.image, current_alignment);

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_macrobot_interfaces
max_serialized_size_key_RgbCandidateCrop(
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

  // Member: proposal_image_width
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: proposal_image_height
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: color_image_width
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: color_image_height
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: source_candidate_count
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

  // Member: crop_index
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

  // Member: color_time_offset_sec
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: plane_found
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

  // Member: mask_fill_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: foreground_mask
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        sensor_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_key_CompressedImage(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: encoded_width
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: encoded_height
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: jpeg_size_bytes
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: jpeg_quality
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: size_limit_met
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: image
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        sensor_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_key_CompressedImage(
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
    using DataType = macrobot_interfaces::msg::RgbCandidateCrop;
    is_plain =
      (
      offsetof(DataType, image) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}


static bool _RgbCandidateCrop__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const macrobot_interfaces::msg::RgbCandidateCrop *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _RgbCandidateCrop__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<macrobot_interfaces::msg::RgbCandidateCrop *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _RgbCandidateCrop__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const macrobot_interfaces::msg::RgbCandidateCrop *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _RgbCandidateCrop__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_RgbCandidateCrop(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _RgbCandidateCrop__callbacks = {
  "macrobot_interfaces::msg",
  "RgbCandidateCrop",
  _RgbCandidateCrop__cdr_serialize,
  _RgbCandidateCrop__cdr_deserialize,
  _RgbCandidateCrop__get_serialized_size,
  _RgbCandidateCrop__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _RgbCandidateCrop__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_RgbCandidateCrop__callbacks,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__RgbCandidateCrop__get_type_hash,
  &macrobot_interfaces__msg__RgbCandidateCrop__get_type_description,
  &macrobot_interfaces__msg__RgbCandidateCrop__get_type_description_sources,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace macrobot_interfaces

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_macrobot_interfaces
const rosidl_message_type_support_t *
get_message_type_support_handle<macrobot_interfaces::msg::RgbCandidateCrop>()
{
  return &macrobot_interfaces::msg::typesupport_fastrtps_cpp::_RgbCandidateCrop__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, macrobot_interfaces, msg, RgbCandidateCrop)() {
  return &macrobot_interfaces::msg::typesupport_fastrtps_cpp::_RgbCandidateCrop__handle;
}

#ifdef __cplusplus
}
#endif
