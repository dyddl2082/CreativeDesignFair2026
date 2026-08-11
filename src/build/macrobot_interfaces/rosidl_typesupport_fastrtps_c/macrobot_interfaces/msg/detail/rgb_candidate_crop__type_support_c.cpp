// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from macrobot_interfaces:msg/RgbCandidateCrop.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "macrobot_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__struct.h"
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"  // candidate
#include "sensor_msgs/msg/detail/compressed_image__functions.h"  // foreground_mask, image
#include "sensor_msgs/msg/detail/region_of_interest__functions.h"  // crop_roi
#include "std_msgs/msg/detail/header__functions.h"  // proposal_header

// forward declare type support functions

bool cdr_serialize_macrobot_interfaces__msg__DepthCandidate(
  const macrobot_interfaces__msg__DepthCandidate * ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool cdr_deserialize_macrobot_interfaces__msg__DepthCandidate(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces__msg__DepthCandidate * ros_message);

size_t get_serialized_size_macrobot_interfaces__msg__DepthCandidate(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_macrobot_interfaces__msg__DepthCandidate(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

bool cdr_serialize_key_macrobot_interfaces__msg__DepthCandidate(
  const macrobot_interfaces__msg__DepthCandidate * ros_message,
  eprosima::fastcdr::Cdr & cdr);

size_t get_serialized_size_key_macrobot_interfaces__msg__DepthCandidate(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_key_macrobot_interfaces__msg__DepthCandidate(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, macrobot_interfaces, msg, DepthCandidate)();

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
bool cdr_serialize_sensor_msgs__msg__CompressedImage(
  const sensor_msgs__msg__CompressedImage * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
bool cdr_deserialize_sensor_msgs__msg__CompressedImage(
  eprosima::fastcdr::Cdr & cdr,
  sensor_msgs__msg__CompressedImage * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t get_serialized_size_sensor_msgs__msg__CompressedImage(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t max_serialized_size_sensor_msgs__msg__CompressedImage(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
bool cdr_serialize_key_sensor_msgs__msg__CompressedImage(
  const sensor_msgs__msg__CompressedImage * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t get_serialized_size_key_sensor_msgs__msg__CompressedImage(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t max_serialized_size_key_sensor_msgs__msg__CompressedImage(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, sensor_msgs, msg, CompressedImage)();

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
bool cdr_serialize_sensor_msgs__msg__RegionOfInterest(
  const sensor_msgs__msg__RegionOfInterest * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
bool cdr_deserialize_sensor_msgs__msg__RegionOfInterest(
  eprosima::fastcdr::Cdr & cdr,
  sensor_msgs__msg__RegionOfInterest * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t get_serialized_size_sensor_msgs__msg__RegionOfInterest(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t max_serialized_size_sensor_msgs__msg__RegionOfInterest(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
bool cdr_serialize_key_sensor_msgs__msg__RegionOfInterest(
  const sensor_msgs__msg__RegionOfInterest * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t get_serialized_size_key_sensor_msgs__msg__RegionOfInterest(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t max_serialized_size_key_sensor_msgs__msg__RegionOfInterest(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, sensor_msgs, msg, RegionOfInterest)();

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
bool cdr_serialize_std_msgs__msg__Header(
  const std_msgs__msg__Header * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
bool cdr_deserialize_std_msgs__msg__Header(
  eprosima::fastcdr::Cdr & cdr,
  std_msgs__msg__Header * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t get_serialized_size_std_msgs__msg__Header(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t max_serialized_size_std_msgs__msg__Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
bool cdr_serialize_key_std_msgs__msg__Header(
  const std_msgs__msg__Header * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t get_serialized_size_key_std_msgs__msg__Header(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
size_t max_serialized_size_key_std_msgs__msg__Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_macrobot_interfaces
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, std_msgs, msg, Header)();


using _RgbCandidateCrop__ros_msg_type = macrobot_interfaces__msg__RgbCandidateCrop;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_macrobot_interfaces__msg__RgbCandidateCrop(
  const macrobot_interfaces__msg__RgbCandidateCrop * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: proposal_header
  {
    cdr_serialize_std_msgs__msg__Header(
      &ros_message->proposal_header, cdr);
  }

  // Field name: proposal_image_width
  {
    cdr << ros_message->proposal_image_width;
  }

  // Field name: proposal_image_height
  {
    cdr << ros_message->proposal_image_height;
  }

  // Field name: color_image_width
  {
    cdr << ros_message->color_image_width;
  }

  // Field name: color_image_height
  {
    cdr << ros_message->color_image_height;
  }

  // Field name: source_candidate_count
  {
    cdr << ros_message->source_candidate_count;
  }

  // Field name: frame_crop_count
  {
    cdr << ros_message->frame_crop_count;
  }

  // Field name: crop_index
  {
    cdr << ros_message->crop_index;
  }

  // Field name: candidate
  {
    cdr_serialize_macrobot_interfaces__msg__DepthCandidate(
      &ros_message->candidate, cdr);
  }

  // Field name: crop_roi
  {
    cdr_serialize_sensor_msgs__msg__RegionOfInterest(
      &ros_message->crop_roi, cdr);
  }

  // Field name: color_time_offset_sec
  {
    cdr << ros_message->color_time_offset_sec;
  }

  // Field name: plane_found
  {
    cdr << (ros_message->plane_found ? true : false);
  }

  // Field name: foreground_mask_available
  {
    cdr << (ros_message->foreground_mask_available ? true : false);
  }

  // Field name: mask_fill_ratio
  {
    cdr << ros_message->mask_fill_ratio;
  }

  // Field name: foreground_mask
  {
    cdr_serialize_sensor_msgs__msg__CompressedImage(
      &ros_message->foreground_mask, cdr);
  }

  // Field name: encoded_width
  {
    cdr << ros_message->encoded_width;
  }

  // Field name: encoded_height
  {
    cdr << ros_message->encoded_height;
  }

  // Field name: jpeg_size_bytes
  {
    cdr << ros_message->jpeg_size_bytes;
  }

  // Field name: jpeg_quality
  {
    cdr << ros_message->jpeg_quality;
  }

  // Field name: size_limit_met
  {
    cdr << (ros_message->size_limit_met ? true : false);
  }

  // Field name: image
  {
    cdr_serialize_sensor_msgs__msg__CompressedImage(
      &ros_message->image, cdr);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_deserialize_macrobot_interfaces__msg__RgbCandidateCrop(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces__msg__RgbCandidateCrop * ros_message)
{
  // Field name: proposal_header
  {
    cdr_deserialize_std_msgs__msg__Header(cdr, &ros_message->proposal_header);
  }

  // Field name: proposal_image_width
  {
    cdr >> ros_message->proposal_image_width;
  }

  // Field name: proposal_image_height
  {
    cdr >> ros_message->proposal_image_height;
  }

  // Field name: color_image_width
  {
    cdr >> ros_message->color_image_width;
  }

  // Field name: color_image_height
  {
    cdr >> ros_message->color_image_height;
  }

  // Field name: source_candidate_count
  {
    cdr >> ros_message->source_candidate_count;
  }

  // Field name: frame_crop_count
  {
    cdr >> ros_message->frame_crop_count;
  }

  // Field name: crop_index
  {
    cdr >> ros_message->crop_index;
  }

  // Field name: candidate
  {
    cdr_deserialize_macrobot_interfaces__msg__DepthCandidate(cdr, &ros_message->candidate);
  }

  // Field name: crop_roi
  {
    cdr_deserialize_sensor_msgs__msg__RegionOfInterest(cdr, &ros_message->crop_roi);
  }

  // Field name: color_time_offset_sec
  {
    cdr >> ros_message->color_time_offset_sec;
  }

  // Field name: plane_found
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->plane_found = tmp ? true : false;
  }

  // Field name: foreground_mask_available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->foreground_mask_available = tmp ? true : false;
  }

  // Field name: mask_fill_ratio
  {
    cdr >> ros_message->mask_fill_ratio;
  }

  // Field name: foreground_mask
  {
    cdr_deserialize_sensor_msgs__msg__CompressedImage(cdr, &ros_message->foreground_mask);
  }

  // Field name: encoded_width
  {
    cdr >> ros_message->encoded_width;
  }

  // Field name: encoded_height
  {
    cdr >> ros_message->encoded_height;
  }

  // Field name: jpeg_size_bytes
  {
    cdr >> ros_message->jpeg_size_bytes;
  }

  // Field name: jpeg_quality
  {
    cdr >> ros_message->jpeg_quality;
  }

  // Field name: size_limit_met
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->size_limit_met = tmp ? true : false;
  }

  // Field name: image
  {
    cdr_deserialize_sensor_msgs__msg__CompressedImage(cdr, &ros_message->image);
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t get_serialized_size_macrobot_interfaces__msg__RgbCandidateCrop(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _RgbCandidateCrop__ros_msg_type * ros_message = static_cast<const _RgbCandidateCrop__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: proposal_header
  current_alignment += get_serialized_size_std_msgs__msg__Header(
    &(ros_message->proposal_header), current_alignment);

  // Field name: proposal_image_width
  {
    size_t item_size = sizeof(ros_message->proposal_image_width);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: proposal_image_height
  {
    size_t item_size = sizeof(ros_message->proposal_image_height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: color_image_width
  {
    size_t item_size = sizeof(ros_message->color_image_width);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: color_image_height
  {
    size_t item_size = sizeof(ros_message->color_image_height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: source_candidate_count
  {
    size_t item_size = sizeof(ros_message->source_candidate_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: frame_crop_count
  {
    size_t item_size = sizeof(ros_message->frame_crop_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: crop_index
  {
    size_t item_size = sizeof(ros_message->crop_index);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: candidate
  current_alignment += get_serialized_size_macrobot_interfaces__msg__DepthCandidate(
    &(ros_message->candidate), current_alignment);

  // Field name: crop_roi
  current_alignment += get_serialized_size_sensor_msgs__msg__RegionOfInterest(
    &(ros_message->crop_roi), current_alignment);

  // Field name: color_time_offset_sec
  {
    size_t item_size = sizeof(ros_message->color_time_offset_sec);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: plane_found
  {
    size_t item_size = sizeof(ros_message->plane_found);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_mask_available
  {
    size_t item_size = sizeof(ros_message->foreground_mask_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mask_fill_ratio
  {
    size_t item_size = sizeof(ros_message->mask_fill_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_mask
  current_alignment += get_serialized_size_sensor_msgs__msg__CompressedImage(
    &(ros_message->foreground_mask), current_alignment);

  // Field name: encoded_width
  {
    size_t item_size = sizeof(ros_message->encoded_width);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: encoded_height
  {
    size_t item_size = sizeof(ros_message->encoded_height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: jpeg_size_bytes
  {
    size_t item_size = sizeof(ros_message->jpeg_size_bytes);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: jpeg_quality
  {
    size_t item_size = sizeof(ros_message->jpeg_quality);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: size_limit_met
  {
    size_t item_size = sizeof(ros_message->size_limit_met);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: image
  current_alignment += get_serialized_size_sensor_msgs__msg__CompressedImage(
    &(ros_message->image), current_alignment);

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t max_serialized_size_macrobot_interfaces__msg__RgbCandidateCrop(
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

  // Field name: proposal_header
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_std_msgs__msg__Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: proposal_image_width
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: proposal_image_height
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: color_image_width
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: color_image_height
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: source_candidate_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: frame_crop_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: crop_index
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: candidate
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_macrobot_interfaces__msg__DepthCandidate(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: crop_roi
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_sensor_msgs__msg__RegionOfInterest(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: color_time_offset_sec
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: plane_found
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: foreground_mask_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: mask_fill_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: foreground_mask
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_sensor_msgs__msg__CompressedImage(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: encoded_width
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: encoded_height
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: jpeg_size_bytes
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: jpeg_quality
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: size_limit_met
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: image
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_sensor_msgs__msg__CompressedImage(
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
    using DataType = macrobot_interfaces__msg__RgbCandidateCrop;
    is_plain =
      (
      offsetof(DataType, image) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_key_macrobot_interfaces__msg__RgbCandidateCrop(
  const macrobot_interfaces__msg__RgbCandidateCrop * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: proposal_header
  {
    cdr_serialize_key_std_msgs__msg__Header(
      &ros_message->proposal_header, cdr);
  }

  // Field name: proposal_image_width
  {
    cdr << ros_message->proposal_image_width;
  }

  // Field name: proposal_image_height
  {
    cdr << ros_message->proposal_image_height;
  }

  // Field name: color_image_width
  {
    cdr << ros_message->color_image_width;
  }

  // Field name: color_image_height
  {
    cdr << ros_message->color_image_height;
  }

  // Field name: source_candidate_count
  {
    cdr << ros_message->source_candidate_count;
  }

  // Field name: frame_crop_count
  {
    cdr << ros_message->frame_crop_count;
  }

  // Field name: crop_index
  {
    cdr << ros_message->crop_index;
  }

  // Field name: candidate
  {
    cdr_serialize_key_macrobot_interfaces__msg__DepthCandidate(
      &ros_message->candidate, cdr);
  }

  // Field name: crop_roi
  {
    cdr_serialize_key_sensor_msgs__msg__RegionOfInterest(
      &ros_message->crop_roi, cdr);
  }

  // Field name: color_time_offset_sec
  {
    cdr << ros_message->color_time_offset_sec;
  }

  // Field name: plane_found
  {
    cdr << (ros_message->plane_found ? true : false);
  }

  // Field name: foreground_mask_available
  {
    cdr << (ros_message->foreground_mask_available ? true : false);
  }

  // Field name: mask_fill_ratio
  {
    cdr << ros_message->mask_fill_ratio;
  }

  // Field name: foreground_mask
  {
    cdr_serialize_key_sensor_msgs__msg__CompressedImage(
      &ros_message->foreground_mask, cdr);
  }

  // Field name: encoded_width
  {
    cdr << ros_message->encoded_width;
  }

  // Field name: encoded_height
  {
    cdr << ros_message->encoded_height;
  }

  // Field name: jpeg_size_bytes
  {
    cdr << ros_message->jpeg_size_bytes;
  }

  // Field name: jpeg_quality
  {
    cdr << ros_message->jpeg_quality;
  }

  // Field name: size_limit_met
  {
    cdr << (ros_message->size_limit_met ? true : false);
  }

  // Field name: image
  {
    cdr_serialize_key_sensor_msgs__msg__CompressedImage(
      &ros_message->image, cdr);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t get_serialized_size_key_macrobot_interfaces__msg__RgbCandidateCrop(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _RgbCandidateCrop__ros_msg_type * ros_message = static_cast<const _RgbCandidateCrop__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: proposal_header
  current_alignment += get_serialized_size_key_std_msgs__msg__Header(
    &(ros_message->proposal_header), current_alignment);

  // Field name: proposal_image_width
  {
    size_t item_size = sizeof(ros_message->proposal_image_width);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: proposal_image_height
  {
    size_t item_size = sizeof(ros_message->proposal_image_height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: color_image_width
  {
    size_t item_size = sizeof(ros_message->color_image_width);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: color_image_height
  {
    size_t item_size = sizeof(ros_message->color_image_height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: source_candidate_count
  {
    size_t item_size = sizeof(ros_message->source_candidate_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: frame_crop_count
  {
    size_t item_size = sizeof(ros_message->frame_crop_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: crop_index
  {
    size_t item_size = sizeof(ros_message->crop_index);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: candidate
  current_alignment += get_serialized_size_key_macrobot_interfaces__msg__DepthCandidate(
    &(ros_message->candidate), current_alignment);

  // Field name: crop_roi
  current_alignment += get_serialized_size_key_sensor_msgs__msg__RegionOfInterest(
    &(ros_message->crop_roi), current_alignment);

  // Field name: color_time_offset_sec
  {
    size_t item_size = sizeof(ros_message->color_time_offset_sec);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: plane_found
  {
    size_t item_size = sizeof(ros_message->plane_found);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_mask_available
  {
    size_t item_size = sizeof(ros_message->foreground_mask_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mask_fill_ratio
  {
    size_t item_size = sizeof(ros_message->mask_fill_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_mask
  current_alignment += get_serialized_size_key_sensor_msgs__msg__CompressedImage(
    &(ros_message->foreground_mask), current_alignment);

  // Field name: encoded_width
  {
    size_t item_size = sizeof(ros_message->encoded_width);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: encoded_height
  {
    size_t item_size = sizeof(ros_message->encoded_height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: jpeg_size_bytes
  {
    size_t item_size = sizeof(ros_message->jpeg_size_bytes);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: jpeg_quality
  {
    size_t item_size = sizeof(ros_message->jpeg_quality);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: size_limit_met
  {
    size_t item_size = sizeof(ros_message->size_limit_met);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: image
  current_alignment += get_serialized_size_key_sensor_msgs__msg__CompressedImage(
    &(ros_message->image), current_alignment);

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t max_serialized_size_key_macrobot_interfaces__msg__RgbCandidateCrop(
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
  // Field name: proposal_header
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_std_msgs__msg__Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: proposal_image_width
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: proposal_image_height
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: color_image_width
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: color_image_height
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: source_candidate_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: frame_crop_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: crop_index
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: candidate
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_macrobot_interfaces__msg__DepthCandidate(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: crop_roi
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_sensor_msgs__msg__RegionOfInterest(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: color_time_offset_sec
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: plane_found
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: foreground_mask_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: mask_fill_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: foreground_mask
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_sensor_msgs__msg__CompressedImage(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: encoded_width
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: encoded_height
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: jpeg_size_bytes
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: jpeg_quality
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: size_limit_met
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: image
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_sensor_msgs__msg__CompressedImage(
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
    using DataType = macrobot_interfaces__msg__RgbCandidateCrop;
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
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const macrobot_interfaces__msg__RgbCandidateCrop * ros_message = static_cast<const macrobot_interfaces__msg__RgbCandidateCrop *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_macrobot_interfaces__msg__RgbCandidateCrop(ros_message, cdr);
}

static bool _RgbCandidateCrop__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  macrobot_interfaces__msg__RgbCandidateCrop * ros_message = static_cast<macrobot_interfaces__msg__RgbCandidateCrop *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_macrobot_interfaces__msg__RgbCandidateCrop(cdr, ros_message);
}

static uint32_t _RgbCandidateCrop__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_macrobot_interfaces__msg__RgbCandidateCrop(
      untyped_ros_message, 0));
}

static size_t _RgbCandidateCrop__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_macrobot_interfaces__msg__RgbCandidateCrop(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_RgbCandidateCrop = {
  "macrobot_interfaces::msg",
  "RgbCandidateCrop",
  _RgbCandidateCrop__cdr_serialize,
  _RgbCandidateCrop__cdr_deserialize,
  _RgbCandidateCrop__get_serialized_size,
  _RgbCandidateCrop__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _RgbCandidateCrop__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_RgbCandidateCrop,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__RgbCandidateCrop__get_type_hash,
  &macrobot_interfaces__msg__RgbCandidateCrop__get_type_description,
  &macrobot_interfaces__msg__RgbCandidateCrop__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, macrobot_interfaces, msg, RgbCandidateCrop)() {
  return &_RgbCandidateCrop__type_support;
}

#if defined(__cplusplus)
}
#endif
