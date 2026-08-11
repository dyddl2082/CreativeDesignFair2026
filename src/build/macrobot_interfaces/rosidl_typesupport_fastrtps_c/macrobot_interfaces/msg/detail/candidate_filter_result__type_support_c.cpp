// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from macrobot_interfaces:msg/CandidateFilterResult.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/candidate_filter_result__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "macrobot_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "macrobot_interfaces/msg/detail/candidate_filter_result__struct.h"
#include "macrobot_interfaces/msg/detail/candidate_filter_result__functions.h"
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
#include "rosidl_runtime_c/string.h"  // reject_reason, reject_stage, target_object
#include "rosidl_runtime_c/string_functions.h"  // reject_reason, reject_stage, target_object
#include "sensor_msgs/msg/detail/region_of_interest__functions.h"  // crop_roi
#include "std_msgs/msg/detail/header__functions.h"  // image_header, proposal_header

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


using _CandidateFilterResult__ros_msg_type = macrobot_interfaces__msg__CandidateFilterResult;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_macrobot_interfaces__msg__CandidateFilterResult(
  const macrobot_interfaces__msg__CandidateFilterResult * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: proposal_header
  {
    cdr_serialize_std_msgs__msg__Header(
      &ros_message->proposal_header, cdr);
  }

  // Field name: image_header
  {
    cdr_serialize_std_msgs__msg__Header(
      &ros_message->image_header, cdr);
  }

  // Field name: candidate_id
  {
    cdr << ros_message->candidate_id;
  }

  // Field name: crop_index
  {
    cdr << ros_message->crop_index;
  }

  // Field name: frame_crop_count
  {
    cdr << ros_message->frame_crop_count;
  }

  // Field name: target_object
  {
    const rosidl_runtime_c__String * str = &ros_message->target_object;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: reference_profile_available
  {
    cdr << (ros_message->reference_profile_available ? true : false);
  }

  // Field name: reference_image_count
  {
    cdr << ros_message->reference_image_count;
  }

  // Field name: camera_info_available
  {
    cdr << (ros_message->camera_info_available ? true : false);
  }

  // Field name: plane_found
  {
    cdr << (ros_message->plane_found ? true : false);
  }

  // Field name: foreground_height_valid
  {
    cdr << (ros_message->foreground_height_valid ? true : false);
  }

  // Field name: foreground_mask_available
  {
    cdr << (ros_message->foreground_mask_available ? true : false);
  }

  // Field name: accepted
  {
    cdr << (ros_message->accepted ? true : false);
  }

  // Field name: reject_stage
  {
    const rosidl_runtime_c__String * str = &ros_message->reject_stage;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: reject_reason
  {
    const rosidl_runtime_c__String * str = &ros_message->reject_reason;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: objectness_score
  {
    cdr << ros_message->objectness_score;
  }

  // Field name: target_hint_score
  {
    cdr << ros_message->target_hint_score;
  }

  // Field name: filter_score
  {
    cdr << ros_message->filter_score;
  }

  // Field name: depth_score
  {
    cdr << ros_message->depth_score;
  }

  // Field name: quality_score
  {
    cdr << ros_message->quality_score;
  }

  // Field name: color_score
  {
    cdr << ros_message->color_score;
  }

  // Field name: shape_score
  {
    cdr << ros_message->shape_score;
  }

  // Field name: physical_size_score
  {
    cdr << ros_message->physical_size_score;
  }

  // Field name: sharpness
  {
    cdr << ros_message->sharpness;
  }

  // Field name: mean_brightness
  {
    cdr << ros_message->mean_brightness;
  }

  // Field name: dark_ratio
  {
    cdr << ros_message->dark_ratio;
  }

  // Field name: bright_clip_ratio
  {
    cdr << ros_message->bright_clip_ratio;
  }

  // Field name: edge_density
  {
    cdr << ros_message->edge_density;
  }

  // Field name: mask_fill_ratio
  {
    cdr << ros_message->mask_fill_ratio;
  }

  // Field name: mask_solidity
  {
    cdr << ros_message->mask_solidity;
  }

  // Field name: color_similarity
  {
    cdr << ros_message->color_similarity;
  }

  // Field name: aspect_ratio
  {
    cdr << ros_message->aspect_ratio;
  }

  // Field name: estimated_width_m
  {
    cdr << ros_message->estimated_width_m;
  }

  // Field name: estimated_height_m
  {
    cdr << ros_message->estimated_height_m;
  }

  // Field name: sync_offset_abs_sec
  {
    cdr << ros_message->sync_offset_abs_sec;
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

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_deserialize_macrobot_interfaces__msg__CandidateFilterResult(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces__msg__CandidateFilterResult * ros_message)
{
  // Field name: proposal_header
  {
    cdr_deserialize_std_msgs__msg__Header(cdr, &ros_message->proposal_header);
  }

  // Field name: image_header
  {
    cdr_deserialize_std_msgs__msg__Header(cdr, &ros_message->image_header);
  }

  // Field name: candidate_id
  {
    cdr >> ros_message->candidate_id;
  }

  // Field name: crop_index
  {
    cdr >> ros_message->crop_index;
  }

  // Field name: frame_crop_count
  {
    cdr >> ros_message->frame_crop_count;
  }

  // Field name: target_object
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->target_object.data) {
      rosidl_runtime_c__String__init(&ros_message->target_object);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->target_object,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'target_object'\n");
      return false;
    }
  }

  // Field name: reference_profile_available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->reference_profile_available = tmp ? true : false;
  }

  // Field name: reference_image_count
  {
    cdr >> ros_message->reference_image_count;
  }

  // Field name: camera_info_available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->camera_info_available = tmp ? true : false;
  }

  // Field name: plane_found
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->plane_found = tmp ? true : false;
  }

  // Field name: foreground_height_valid
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->foreground_height_valid = tmp ? true : false;
  }

  // Field name: foreground_mask_available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->foreground_mask_available = tmp ? true : false;
  }

  // Field name: accepted
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->accepted = tmp ? true : false;
  }

  // Field name: reject_stage
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->reject_stage.data) {
      rosidl_runtime_c__String__init(&ros_message->reject_stage);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->reject_stage,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'reject_stage'\n");
      return false;
    }
  }

  // Field name: reject_reason
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->reject_reason.data) {
      rosidl_runtime_c__String__init(&ros_message->reject_reason);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->reject_reason,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'reject_reason'\n");
      return false;
    }
  }

  // Field name: objectness_score
  {
    cdr >> ros_message->objectness_score;
  }

  // Field name: target_hint_score
  {
    cdr >> ros_message->target_hint_score;
  }

  // Field name: filter_score
  {
    cdr >> ros_message->filter_score;
  }

  // Field name: depth_score
  {
    cdr >> ros_message->depth_score;
  }

  // Field name: quality_score
  {
    cdr >> ros_message->quality_score;
  }

  // Field name: color_score
  {
    cdr >> ros_message->color_score;
  }

  // Field name: shape_score
  {
    cdr >> ros_message->shape_score;
  }

  // Field name: physical_size_score
  {
    cdr >> ros_message->physical_size_score;
  }

  // Field name: sharpness
  {
    cdr >> ros_message->sharpness;
  }

  // Field name: mean_brightness
  {
    cdr >> ros_message->mean_brightness;
  }

  // Field name: dark_ratio
  {
    cdr >> ros_message->dark_ratio;
  }

  // Field name: bright_clip_ratio
  {
    cdr >> ros_message->bright_clip_ratio;
  }

  // Field name: edge_density
  {
    cdr >> ros_message->edge_density;
  }

  // Field name: mask_fill_ratio
  {
    cdr >> ros_message->mask_fill_ratio;
  }

  // Field name: mask_solidity
  {
    cdr >> ros_message->mask_solidity;
  }

  // Field name: color_similarity
  {
    cdr >> ros_message->color_similarity;
  }

  // Field name: aspect_ratio
  {
    cdr >> ros_message->aspect_ratio;
  }

  // Field name: estimated_width_m
  {
    cdr >> ros_message->estimated_width_m;
  }

  // Field name: estimated_height_m
  {
    cdr >> ros_message->estimated_height_m;
  }

  // Field name: sync_offset_abs_sec
  {
    cdr >> ros_message->sync_offset_abs_sec;
  }

  // Field name: candidate
  {
    cdr_deserialize_macrobot_interfaces__msg__DepthCandidate(cdr, &ros_message->candidate);
  }

  // Field name: crop_roi
  {
    cdr_deserialize_sensor_msgs__msg__RegionOfInterest(cdr, &ros_message->crop_roi);
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t get_serialized_size_macrobot_interfaces__msg__CandidateFilterResult(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _CandidateFilterResult__ros_msg_type * ros_message = static_cast<const _CandidateFilterResult__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: proposal_header
  current_alignment += get_serialized_size_std_msgs__msg__Header(
    &(ros_message->proposal_header), current_alignment);

  // Field name: image_header
  current_alignment += get_serialized_size_std_msgs__msg__Header(
    &(ros_message->image_header), current_alignment);

  // Field name: candidate_id
  {
    size_t item_size = sizeof(ros_message->candidate_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: crop_index
  {
    size_t item_size = sizeof(ros_message->crop_index);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: frame_crop_count
  {
    size_t item_size = sizeof(ros_message->frame_crop_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: target_object
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->target_object.size + 1);

  // Field name: reference_profile_available
  {
    size_t item_size = sizeof(ros_message->reference_profile_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: reference_image_count
  {
    size_t item_size = sizeof(ros_message->reference_image_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: camera_info_available
  {
    size_t item_size = sizeof(ros_message->camera_info_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: plane_found
  {
    size_t item_size = sizeof(ros_message->plane_found);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_height_valid
  {
    size_t item_size = sizeof(ros_message->foreground_height_valid);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_mask_available
  {
    size_t item_size = sizeof(ros_message->foreground_mask_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: accepted
  {
    size_t item_size = sizeof(ros_message->accepted);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: reject_stage
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->reject_stage.size + 1);

  // Field name: reject_reason
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->reject_reason.size + 1);

  // Field name: objectness_score
  {
    size_t item_size = sizeof(ros_message->objectness_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: target_hint_score
  {
    size_t item_size = sizeof(ros_message->target_hint_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: filter_score
  {
    size_t item_size = sizeof(ros_message->filter_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: depth_score
  {
    size_t item_size = sizeof(ros_message->depth_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: quality_score
  {
    size_t item_size = sizeof(ros_message->quality_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: color_score
  {
    size_t item_size = sizeof(ros_message->color_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: shape_score
  {
    size_t item_size = sizeof(ros_message->shape_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: physical_size_score
  {
    size_t item_size = sizeof(ros_message->physical_size_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: sharpness
  {
    size_t item_size = sizeof(ros_message->sharpness);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mean_brightness
  {
    size_t item_size = sizeof(ros_message->mean_brightness);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: dark_ratio
  {
    size_t item_size = sizeof(ros_message->dark_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: bright_clip_ratio
  {
    size_t item_size = sizeof(ros_message->bright_clip_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: edge_density
  {
    size_t item_size = sizeof(ros_message->edge_density);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mask_fill_ratio
  {
    size_t item_size = sizeof(ros_message->mask_fill_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mask_solidity
  {
    size_t item_size = sizeof(ros_message->mask_solidity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: color_similarity
  {
    size_t item_size = sizeof(ros_message->color_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: aspect_ratio
  {
    size_t item_size = sizeof(ros_message->aspect_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: estimated_width_m
  {
    size_t item_size = sizeof(ros_message->estimated_width_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: estimated_height_m
  {
    size_t item_size = sizeof(ros_message->estimated_height_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: sync_offset_abs_sec
  {
    size_t item_size = sizeof(ros_message->sync_offset_abs_sec);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: candidate
  current_alignment += get_serialized_size_macrobot_interfaces__msg__DepthCandidate(
    &(ros_message->candidate), current_alignment);

  // Field name: crop_roi
  current_alignment += get_serialized_size_sensor_msgs__msg__RegionOfInterest(
    &(ros_message->crop_roi), current_alignment);

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t max_serialized_size_macrobot_interfaces__msg__CandidateFilterResult(
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

  // Field name: image_header
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

  // Field name: candidate_id
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

  // Field name: frame_crop_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: target_object
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

  // Field name: reference_profile_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: reference_image_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: camera_info_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: plane_found
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: foreground_height_valid
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

  // Field name: accepted
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: reject_stage
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

  // Field name: reject_reason
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

  // Field name: objectness_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: target_hint_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: filter_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: depth_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: quality_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: color_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: shape_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: physical_size_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: sharpness
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mean_brightness
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: dark_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: bright_clip_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: edge_density
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mask_fill_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mask_solidity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: color_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: aspect_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: estimated_width_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: estimated_height_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: sync_offset_abs_sec
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


  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = macrobot_interfaces__msg__CandidateFilterResult;
    is_plain =
      (
      offsetof(DataType, crop_roi) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_key_macrobot_interfaces__msg__CandidateFilterResult(
  const macrobot_interfaces__msg__CandidateFilterResult * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: proposal_header
  {
    cdr_serialize_key_std_msgs__msg__Header(
      &ros_message->proposal_header, cdr);
  }

  // Field name: image_header
  {
    cdr_serialize_key_std_msgs__msg__Header(
      &ros_message->image_header, cdr);
  }

  // Field name: candidate_id
  {
    cdr << ros_message->candidate_id;
  }

  // Field name: crop_index
  {
    cdr << ros_message->crop_index;
  }

  // Field name: frame_crop_count
  {
    cdr << ros_message->frame_crop_count;
  }

  // Field name: target_object
  {
    const rosidl_runtime_c__String * str = &ros_message->target_object;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: reference_profile_available
  {
    cdr << (ros_message->reference_profile_available ? true : false);
  }

  // Field name: reference_image_count
  {
    cdr << ros_message->reference_image_count;
  }

  // Field name: camera_info_available
  {
    cdr << (ros_message->camera_info_available ? true : false);
  }

  // Field name: plane_found
  {
    cdr << (ros_message->plane_found ? true : false);
  }

  // Field name: foreground_height_valid
  {
    cdr << (ros_message->foreground_height_valid ? true : false);
  }

  // Field name: foreground_mask_available
  {
    cdr << (ros_message->foreground_mask_available ? true : false);
  }

  // Field name: accepted
  {
    cdr << (ros_message->accepted ? true : false);
  }

  // Field name: reject_stage
  {
    const rosidl_runtime_c__String * str = &ros_message->reject_stage;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: reject_reason
  {
    const rosidl_runtime_c__String * str = &ros_message->reject_reason;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: objectness_score
  {
    cdr << ros_message->objectness_score;
  }

  // Field name: target_hint_score
  {
    cdr << ros_message->target_hint_score;
  }

  // Field name: filter_score
  {
    cdr << ros_message->filter_score;
  }

  // Field name: depth_score
  {
    cdr << ros_message->depth_score;
  }

  // Field name: quality_score
  {
    cdr << ros_message->quality_score;
  }

  // Field name: color_score
  {
    cdr << ros_message->color_score;
  }

  // Field name: shape_score
  {
    cdr << ros_message->shape_score;
  }

  // Field name: physical_size_score
  {
    cdr << ros_message->physical_size_score;
  }

  // Field name: sharpness
  {
    cdr << ros_message->sharpness;
  }

  // Field name: mean_brightness
  {
    cdr << ros_message->mean_brightness;
  }

  // Field name: dark_ratio
  {
    cdr << ros_message->dark_ratio;
  }

  // Field name: bright_clip_ratio
  {
    cdr << ros_message->bright_clip_ratio;
  }

  // Field name: edge_density
  {
    cdr << ros_message->edge_density;
  }

  // Field name: mask_fill_ratio
  {
    cdr << ros_message->mask_fill_ratio;
  }

  // Field name: mask_solidity
  {
    cdr << ros_message->mask_solidity;
  }

  // Field name: color_similarity
  {
    cdr << ros_message->color_similarity;
  }

  // Field name: aspect_ratio
  {
    cdr << ros_message->aspect_ratio;
  }

  // Field name: estimated_width_m
  {
    cdr << ros_message->estimated_width_m;
  }

  // Field name: estimated_height_m
  {
    cdr << ros_message->estimated_height_m;
  }

  // Field name: sync_offset_abs_sec
  {
    cdr << ros_message->sync_offset_abs_sec;
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

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t get_serialized_size_key_macrobot_interfaces__msg__CandidateFilterResult(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _CandidateFilterResult__ros_msg_type * ros_message = static_cast<const _CandidateFilterResult__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: proposal_header
  current_alignment += get_serialized_size_key_std_msgs__msg__Header(
    &(ros_message->proposal_header), current_alignment);

  // Field name: image_header
  current_alignment += get_serialized_size_key_std_msgs__msg__Header(
    &(ros_message->image_header), current_alignment);

  // Field name: candidate_id
  {
    size_t item_size = sizeof(ros_message->candidate_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: crop_index
  {
    size_t item_size = sizeof(ros_message->crop_index);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: frame_crop_count
  {
    size_t item_size = sizeof(ros_message->frame_crop_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: target_object
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->target_object.size + 1);

  // Field name: reference_profile_available
  {
    size_t item_size = sizeof(ros_message->reference_profile_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: reference_image_count
  {
    size_t item_size = sizeof(ros_message->reference_image_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: camera_info_available
  {
    size_t item_size = sizeof(ros_message->camera_info_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: plane_found
  {
    size_t item_size = sizeof(ros_message->plane_found);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_height_valid
  {
    size_t item_size = sizeof(ros_message->foreground_height_valid);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_mask_available
  {
    size_t item_size = sizeof(ros_message->foreground_mask_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: accepted
  {
    size_t item_size = sizeof(ros_message->accepted);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: reject_stage
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->reject_stage.size + 1);

  // Field name: reject_reason
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->reject_reason.size + 1);

  // Field name: objectness_score
  {
    size_t item_size = sizeof(ros_message->objectness_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: target_hint_score
  {
    size_t item_size = sizeof(ros_message->target_hint_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: filter_score
  {
    size_t item_size = sizeof(ros_message->filter_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: depth_score
  {
    size_t item_size = sizeof(ros_message->depth_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: quality_score
  {
    size_t item_size = sizeof(ros_message->quality_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: color_score
  {
    size_t item_size = sizeof(ros_message->color_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: shape_score
  {
    size_t item_size = sizeof(ros_message->shape_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: physical_size_score
  {
    size_t item_size = sizeof(ros_message->physical_size_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: sharpness
  {
    size_t item_size = sizeof(ros_message->sharpness);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mean_brightness
  {
    size_t item_size = sizeof(ros_message->mean_brightness);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: dark_ratio
  {
    size_t item_size = sizeof(ros_message->dark_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: bright_clip_ratio
  {
    size_t item_size = sizeof(ros_message->bright_clip_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: edge_density
  {
    size_t item_size = sizeof(ros_message->edge_density);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mask_fill_ratio
  {
    size_t item_size = sizeof(ros_message->mask_fill_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mask_solidity
  {
    size_t item_size = sizeof(ros_message->mask_solidity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: color_similarity
  {
    size_t item_size = sizeof(ros_message->color_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: aspect_ratio
  {
    size_t item_size = sizeof(ros_message->aspect_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: estimated_width_m
  {
    size_t item_size = sizeof(ros_message->estimated_width_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: estimated_height_m
  {
    size_t item_size = sizeof(ros_message->estimated_height_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: sync_offset_abs_sec
  {
    size_t item_size = sizeof(ros_message->sync_offset_abs_sec);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: candidate
  current_alignment += get_serialized_size_key_macrobot_interfaces__msg__DepthCandidate(
    &(ros_message->candidate), current_alignment);

  // Field name: crop_roi
  current_alignment += get_serialized_size_key_sensor_msgs__msg__RegionOfInterest(
    &(ros_message->crop_roi), current_alignment);

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t max_serialized_size_key_macrobot_interfaces__msg__CandidateFilterResult(
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

  // Field name: image_header
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

  // Field name: candidate_id
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

  // Field name: frame_crop_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: target_object
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

  // Field name: reference_profile_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: reference_image_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: camera_info_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: plane_found
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: foreground_height_valid
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

  // Field name: accepted
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: reject_stage
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

  // Field name: reject_reason
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

  // Field name: objectness_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: target_hint_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: filter_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: depth_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: quality_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: color_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: shape_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: physical_size_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: sharpness
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mean_brightness
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: dark_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: bright_clip_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: edge_density
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mask_fill_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mask_solidity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: color_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: aspect_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: estimated_width_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: estimated_height_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: sync_offset_abs_sec
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

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = macrobot_interfaces__msg__CandidateFilterResult;
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
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const macrobot_interfaces__msg__CandidateFilterResult * ros_message = static_cast<const macrobot_interfaces__msg__CandidateFilterResult *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_macrobot_interfaces__msg__CandidateFilterResult(ros_message, cdr);
}

static bool _CandidateFilterResult__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  macrobot_interfaces__msg__CandidateFilterResult * ros_message = static_cast<macrobot_interfaces__msg__CandidateFilterResult *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_macrobot_interfaces__msg__CandidateFilterResult(cdr, ros_message);
}

static uint32_t _CandidateFilterResult__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_macrobot_interfaces__msg__CandidateFilterResult(
      untyped_ros_message, 0));
}

static size_t _CandidateFilterResult__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_macrobot_interfaces__msg__CandidateFilterResult(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_CandidateFilterResult = {
  "macrobot_interfaces::msg",
  "CandidateFilterResult",
  _CandidateFilterResult__cdr_serialize,
  _CandidateFilterResult__cdr_deserialize,
  _CandidateFilterResult__get_serialized_size,
  _CandidateFilterResult__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _CandidateFilterResult__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_CandidateFilterResult,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__CandidateFilterResult__get_type_hash,
  &macrobot_interfaces__msg__CandidateFilterResult__get_type_description,
  &macrobot_interfaces__msg__CandidateFilterResult__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, macrobot_interfaces, msg, CandidateFilterResult)() {
  return &_CandidateFilterResult__type_support;
}

#if defined(__cplusplus)
}
#endif
