// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from macrobot_interfaces:msg/TemporalConfirmationResult.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/temporal_confirmation_result__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "macrobot_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "macrobot_interfaces/msg/detail/temporal_confirmation_result__struct.h"
#include "macrobot_interfaces/msg/detail/temporal_confirmation_result__functions.h"
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

#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__functions.h"  // latest_result
#include "rosidl_runtime_c/string.h"  // event, state, suggested_turn, target_object
#include "rosidl_runtime_c/string_functions.h"  // event, state, suggested_turn, target_object
#include "sensor_msgs/msg/detail/region_of_interest__functions.h"  // roi
#include "std_msgs/msg/detail/header__functions.h"  // header

// forward declare type support functions

bool cdr_serialize_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  const macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool cdr_deserialize_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message);

size_t get_serialized_size_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

bool cdr_serialize_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  const macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message,
  eprosima::fastcdr::Cdr & cdr);

size_t get_serialized_size_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, macrobot_interfaces, msg, EmbeddingRetrievalResult)();

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


using _TemporalConfirmationResult__ros_msg_type = macrobot_interfaces__msg__TemporalConfirmationResult;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_macrobot_interfaces__msg__TemporalConfirmationResult(
  const macrobot_interfaces__msg__TemporalConfirmationResult * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: header
  {
    cdr_serialize_std_msgs__msg__Header(
      &ros_message->header, cdr);
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

  // Field name: track_id
  {
    cdr << ros_message->track_id;
  }

  // Field name: frame_index
  {
    cdr << ros_message->frame_index;
  }

  // Field name: state
  {
    const rosidl_runtime_c__String * str = &ros_message->state;
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

  // Field name: event
  {
    const rosidl_runtime_c__String * str = &ros_message->event;
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

  // Field name: confirmed
  {
    cdr << (ros_message->confirmed ? true : false);
  }

  // Field name: track_age_frames
  {
    cdr << ros_message->track_age_frames;
  }

  // Field name: window_size
  {
    cdr << ros_message->window_size;
  }

  // Field name: required_hits
  {
    cdr << ros_message->required_hits;
  }

  // Field name: samples_in_window
  {
    cdr << ros_message->samples_in_window;
  }

  // Field name: matched_frames_in_window
  {
    cdr << ros_message->matched_frames_in_window;
  }

  // Field name: hits_in_window
  {
    cdr << ros_message->hits_in_window;
  }

  // Field name: misses_in_window
  {
    cdr << ros_message->misses_in_window;
  }

  // Field name: consecutive_hits
  {
    cdr << ros_message->consecutive_hits;
  }

  // Field name: consecutive_misses
  {
    cdr << ros_message->consecutive_misses;
  }

  // Field name: hit_ratio
  {
    cdr << ros_message->hit_ratio;
  }

  // Field name: temporal_score
  {
    cdr << ros_message->temporal_score;
  }

  // Field name: stability_score
  {
    cdr << ros_message->stability_score;
  }

  // Field name: mean_positive_similarity
  {
    cdr << ros_message->mean_positive_similarity;
  }

  // Field name: mean_negative_similarity
  {
    cdr << ros_message->mean_negative_similarity;
  }

  // Field name: mean_margin
  {
    cdr << ros_message->mean_margin;
  }

  // Field name: min_margin_in_window
  {
    cdr << ros_message->min_margin_in_window;
  }

  // Field name: mean_objectness_score
  {
    cdr << ros_message->mean_objectness_score;
  }

  // Field name: roi
  {
    cdr_serialize_sensor_msgs__msg__RegionOfInterest(
      &ros_message->roi, cdr);
  }

  // Field name: center_x
  {
    cdr << ros_message->center_x;
  }

  // Field name: center_y
  {
    cdr << ros_message->center_y;
  }

  // Field name: depth_m
  {
    cdr << ros_message->depth_m;
  }

  // Field name: center_std_px
  {
    cdr << ros_message->center_std_px;
  }

  // Field name: depth_std_m
  {
    cdr << ros_message->depth_std_m;
  }

  // Field name: horizontal_error_norm
  {
    cdr << ros_message->horizontal_error_norm;
  }

  // Field name: suggested_turn
  {
    const rosidl_runtime_c__String * str = &ros_message->suggested_turn;
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

  // Field name: latest_result
  {
    cdr_serialize_macrobot_interfaces__msg__EmbeddingRetrievalResult(
      &ros_message->latest_result, cdr);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_deserialize_macrobot_interfaces__msg__TemporalConfirmationResult(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces__msg__TemporalConfirmationResult * ros_message)
{
  // Field name: header
  {
    cdr_deserialize_std_msgs__msg__Header(cdr, &ros_message->header);
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

  // Field name: track_id
  {
    cdr >> ros_message->track_id;
  }

  // Field name: frame_index
  {
    cdr >> ros_message->frame_index;
  }

  // Field name: state
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->state.data) {
      rosidl_runtime_c__String__init(&ros_message->state);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->state,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'state'\n");
      return false;
    }
  }

  // Field name: event
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->event.data) {
      rosidl_runtime_c__String__init(&ros_message->event);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->event,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'event'\n");
      return false;
    }
  }

  // Field name: confirmed
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->confirmed = tmp ? true : false;
  }

  // Field name: track_age_frames
  {
    cdr >> ros_message->track_age_frames;
  }

  // Field name: window_size
  {
    cdr >> ros_message->window_size;
  }

  // Field name: required_hits
  {
    cdr >> ros_message->required_hits;
  }

  // Field name: samples_in_window
  {
    cdr >> ros_message->samples_in_window;
  }

  // Field name: matched_frames_in_window
  {
    cdr >> ros_message->matched_frames_in_window;
  }

  // Field name: hits_in_window
  {
    cdr >> ros_message->hits_in_window;
  }

  // Field name: misses_in_window
  {
    cdr >> ros_message->misses_in_window;
  }

  // Field name: consecutive_hits
  {
    cdr >> ros_message->consecutive_hits;
  }

  // Field name: consecutive_misses
  {
    cdr >> ros_message->consecutive_misses;
  }

  // Field name: hit_ratio
  {
    cdr >> ros_message->hit_ratio;
  }

  // Field name: temporal_score
  {
    cdr >> ros_message->temporal_score;
  }

  // Field name: stability_score
  {
    cdr >> ros_message->stability_score;
  }

  // Field name: mean_positive_similarity
  {
    cdr >> ros_message->mean_positive_similarity;
  }

  // Field name: mean_negative_similarity
  {
    cdr >> ros_message->mean_negative_similarity;
  }

  // Field name: mean_margin
  {
    cdr >> ros_message->mean_margin;
  }

  // Field name: min_margin_in_window
  {
    cdr >> ros_message->min_margin_in_window;
  }

  // Field name: mean_objectness_score
  {
    cdr >> ros_message->mean_objectness_score;
  }

  // Field name: roi
  {
    cdr_deserialize_sensor_msgs__msg__RegionOfInterest(cdr, &ros_message->roi);
  }

  // Field name: center_x
  {
    cdr >> ros_message->center_x;
  }

  // Field name: center_y
  {
    cdr >> ros_message->center_y;
  }

  // Field name: depth_m
  {
    cdr >> ros_message->depth_m;
  }

  // Field name: center_std_px
  {
    cdr >> ros_message->center_std_px;
  }

  // Field name: depth_std_m
  {
    cdr >> ros_message->depth_std_m;
  }

  // Field name: horizontal_error_norm
  {
    cdr >> ros_message->horizontal_error_norm;
  }

  // Field name: suggested_turn
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->suggested_turn.data) {
      rosidl_runtime_c__String__init(&ros_message->suggested_turn);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->suggested_turn,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'suggested_turn'\n");
      return false;
    }
  }

  // Field name: latest_result
  {
    cdr_deserialize_macrobot_interfaces__msg__EmbeddingRetrievalResult(cdr, &ros_message->latest_result);
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t get_serialized_size_macrobot_interfaces__msg__TemporalConfirmationResult(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _TemporalConfirmationResult__ros_msg_type * ros_message = static_cast<const _TemporalConfirmationResult__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: header
  current_alignment += get_serialized_size_std_msgs__msg__Header(
    &(ros_message->header), current_alignment);

  // Field name: target_object
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->target_object.size + 1);

  // Field name: track_id
  {
    size_t item_size = sizeof(ros_message->track_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: frame_index
  {
    size_t item_size = sizeof(ros_message->frame_index);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: state
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->state.size + 1);

  // Field name: event
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->event.size + 1);

  // Field name: confirmed
  {
    size_t item_size = sizeof(ros_message->confirmed);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: track_age_frames
  {
    size_t item_size = sizeof(ros_message->track_age_frames);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: window_size
  {
    size_t item_size = sizeof(ros_message->window_size);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: required_hits
  {
    size_t item_size = sizeof(ros_message->required_hits);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: samples_in_window
  {
    size_t item_size = sizeof(ros_message->samples_in_window);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: matched_frames_in_window
  {
    size_t item_size = sizeof(ros_message->matched_frames_in_window);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: hits_in_window
  {
    size_t item_size = sizeof(ros_message->hits_in_window);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: misses_in_window
  {
    size_t item_size = sizeof(ros_message->misses_in_window);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: consecutive_hits
  {
    size_t item_size = sizeof(ros_message->consecutive_hits);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: consecutive_misses
  {
    size_t item_size = sizeof(ros_message->consecutive_misses);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: hit_ratio
  {
    size_t item_size = sizeof(ros_message->hit_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: temporal_score
  {
    size_t item_size = sizeof(ros_message->temporal_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: stability_score
  {
    size_t item_size = sizeof(ros_message->stability_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mean_positive_similarity
  {
    size_t item_size = sizeof(ros_message->mean_positive_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mean_negative_similarity
  {
    size_t item_size = sizeof(ros_message->mean_negative_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mean_margin
  {
    size_t item_size = sizeof(ros_message->mean_margin);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: min_margin_in_window
  {
    size_t item_size = sizeof(ros_message->min_margin_in_window);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mean_objectness_score
  {
    size_t item_size = sizeof(ros_message->mean_objectness_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: roi
  current_alignment += get_serialized_size_sensor_msgs__msg__RegionOfInterest(
    &(ros_message->roi), current_alignment);

  // Field name: center_x
  {
    size_t item_size = sizeof(ros_message->center_x);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: center_y
  {
    size_t item_size = sizeof(ros_message->center_y);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: depth_m
  {
    size_t item_size = sizeof(ros_message->depth_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: center_std_px
  {
    size_t item_size = sizeof(ros_message->center_std_px);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: depth_std_m
  {
    size_t item_size = sizeof(ros_message->depth_std_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: horizontal_error_norm
  {
    size_t item_size = sizeof(ros_message->horizontal_error_norm);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: suggested_turn
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->suggested_turn.size + 1);

  // Field name: latest_result
  current_alignment += get_serialized_size_macrobot_interfaces__msg__EmbeddingRetrievalResult(
    &(ros_message->latest_result), current_alignment);

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t max_serialized_size_macrobot_interfaces__msg__TemporalConfirmationResult(
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

  // Field name: header
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

  // Field name: track_id
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: frame_index
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint64_t);
    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }

  // Field name: state
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

  // Field name: event
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

  // Field name: confirmed
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: track_age_frames
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: window_size
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: required_hits
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: samples_in_window
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: matched_frames_in_window
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: hits_in_window
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: misses_in_window
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: consecutive_hits
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: consecutive_misses
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: hit_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: temporal_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: stability_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mean_positive_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mean_negative_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mean_margin
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: min_margin_in_window
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mean_objectness_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: roi
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

  // Field name: center_x
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: center_y
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: depth_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: center_std_px
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: depth_std_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: horizontal_error_norm
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: suggested_turn
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

  // Field name: latest_result
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_macrobot_interfaces__msg__EmbeddingRetrievalResult(
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
    using DataType = macrobot_interfaces__msg__TemporalConfirmationResult;
    is_plain =
      (
      offsetof(DataType, latest_result) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_key_macrobot_interfaces__msg__TemporalConfirmationResult(
  const macrobot_interfaces__msg__TemporalConfirmationResult * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: header
  {
    cdr_serialize_key_std_msgs__msg__Header(
      &ros_message->header, cdr);
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

  // Field name: track_id
  {
    cdr << ros_message->track_id;
  }

  // Field name: frame_index
  {
    cdr << ros_message->frame_index;
  }

  // Field name: state
  {
    const rosidl_runtime_c__String * str = &ros_message->state;
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

  // Field name: event
  {
    const rosidl_runtime_c__String * str = &ros_message->event;
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

  // Field name: confirmed
  {
    cdr << (ros_message->confirmed ? true : false);
  }

  // Field name: track_age_frames
  {
    cdr << ros_message->track_age_frames;
  }

  // Field name: window_size
  {
    cdr << ros_message->window_size;
  }

  // Field name: required_hits
  {
    cdr << ros_message->required_hits;
  }

  // Field name: samples_in_window
  {
    cdr << ros_message->samples_in_window;
  }

  // Field name: matched_frames_in_window
  {
    cdr << ros_message->matched_frames_in_window;
  }

  // Field name: hits_in_window
  {
    cdr << ros_message->hits_in_window;
  }

  // Field name: misses_in_window
  {
    cdr << ros_message->misses_in_window;
  }

  // Field name: consecutive_hits
  {
    cdr << ros_message->consecutive_hits;
  }

  // Field name: consecutive_misses
  {
    cdr << ros_message->consecutive_misses;
  }

  // Field name: hit_ratio
  {
    cdr << ros_message->hit_ratio;
  }

  // Field name: temporal_score
  {
    cdr << ros_message->temporal_score;
  }

  // Field name: stability_score
  {
    cdr << ros_message->stability_score;
  }

  // Field name: mean_positive_similarity
  {
    cdr << ros_message->mean_positive_similarity;
  }

  // Field name: mean_negative_similarity
  {
    cdr << ros_message->mean_negative_similarity;
  }

  // Field name: mean_margin
  {
    cdr << ros_message->mean_margin;
  }

  // Field name: min_margin_in_window
  {
    cdr << ros_message->min_margin_in_window;
  }

  // Field name: mean_objectness_score
  {
    cdr << ros_message->mean_objectness_score;
  }

  // Field name: roi
  {
    cdr_serialize_key_sensor_msgs__msg__RegionOfInterest(
      &ros_message->roi, cdr);
  }

  // Field name: center_x
  {
    cdr << ros_message->center_x;
  }

  // Field name: center_y
  {
    cdr << ros_message->center_y;
  }

  // Field name: depth_m
  {
    cdr << ros_message->depth_m;
  }

  // Field name: center_std_px
  {
    cdr << ros_message->center_std_px;
  }

  // Field name: depth_std_m
  {
    cdr << ros_message->depth_std_m;
  }

  // Field name: horizontal_error_norm
  {
    cdr << ros_message->horizontal_error_norm;
  }

  // Field name: suggested_turn
  {
    const rosidl_runtime_c__String * str = &ros_message->suggested_turn;
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

  // Field name: latest_result
  {
    cdr_serialize_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
      &ros_message->latest_result, cdr);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t get_serialized_size_key_macrobot_interfaces__msg__TemporalConfirmationResult(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _TemporalConfirmationResult__ros_msg_type * ros_message = static_cast<const _TemporalConfirmationResult__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: header
  current_alignment += get_serialized_size_key_std_msgs__msg__Header(
    &(ros_message->header), current_alignment);

  // Field name: target_object
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->target_object.size + 1);

  // Field name: track_id
  {
    size_t item_size = sizeof(ros_message->track_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: frame_index
  {
    size_t item_size = sizeof(ros_message->frame_index);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: state
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->state.size + 1);

  // Field name: event
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->event.size + 1);

  // Field name: confirmed
  {
    size_t item_size = sizeof(ros_message->confirmed);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: track_age_frames
  {
    size_t item_size = sizeof(ros_message->track_age_frames);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: window_size
  {
    size_t item_size = sizeof(ros_message->window_size);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: required_hits
  {
    size_t item_size = sizeof(ros_message->required_hits);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: samples_in_window
  {
    size_t item_size = sizeof(ros_message->samples_in_window);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: matched_frames_in_window
  {
    size_t item_size = sizeof(ros_message->matched_frames_in_window);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: hits_in_window
  {
    size_t item_size = sizeof(ros_message->hits_in_window);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: misses_in_window
  {
    size_t item_size = sizeof(ros_message->misses_in_window);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: consecutive_hits
  {
    size_t item_size = sizeof(ros_message->consecutive_hits);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: consecutive_misses
  {
    size_t item_size = sizeof(ros_message->consecutive_misses);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: hit_ratio
  {
    size_t item_size = sizeof(ros_message->hit_ratio);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: temporal_score
  {
    size_t item_size = sizeof(ros_message->temporal_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: stability_score
  {
    size_t item_size = sizeof(ros_message->stability_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mean_positive_similarity
  {
    size_t item_size = sizeof(ros_message->mean_positive_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mean_negative_similarity
  {
    size_t item_size = sizeof(ros_message->mean_negative_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mean_margin
  {
    size_t item_size = sizeof(ros_message->mean_margin);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: min_margin_in_window
  {
    size_t item_size = sizeof(ros_message->min_margin_in_window);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: mean_objectness_score
  {
    size_t item_size = sizeof(ros_message->mean_objectness_score);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: roi
  current_alignment += get_serialized_size_key_sensor_msgs__msg__RegionOfInterest(
    &(ros_message->roi), current_alignment);

  // Field name: center_x
  {
    size_t item_size = sizeof(ros_message->center_x);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: center_y
  {
    size_t item_size = sizeof(ros_message->center_y);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: depth_m
  {
    size_t item_size = sizeof(ros_message->depth_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: center_std_px
  {
    size_t item_size = sizeof(ros_message->center_std_px);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: depth_std_m
  {
    size_t item_size = sizeof(ros_message->depth_std_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: horizontal_error_norm
  {
    size_t item_size = sizeof(ros_message->horizontal_error_norm);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: suggested_turn
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->suggested_turn.size + 1);

  // Field name: latest_result
  current_alignment += get_serialized_size_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
    &(ros_message->latest_result), current_alignment);

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
size_t max_serialized_size_key_macrobot_interfaces__msg__TemporalConfirmationResult(
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
  // Field name: header
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

  // Field name: track_id
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: frame_index
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint64_t);
    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }

  // Field name: state
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

  // Field name: event
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

  // Field name: confirmed
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: track_age_frames
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: window_size
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: required_hits
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: samples_in_window
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: matched_frames_in_window
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: hits_in_window
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: misses_in_window
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: consecutive_hits
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: consecutive_misses
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: hit_ratio
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: temporal_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: stability_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mean_positive_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mean_negative_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mean_margin
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: min_margin_in_window
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: mean_objectness_score
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: roi
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

  // Field name: center_x
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: center_y
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: depth_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: center_std_px
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: depth_std_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: horizontal_error_norm
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: suggested_turn
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

  // Field name: latest_result
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
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
    using DataType = macrobot_interfaces__msg__TemporalConfirmationResult;
    is_plain =
      (
      offsetof(DataType, latest_result) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _TemporalConfirmationResult__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const macrobot_interfaces__msg__TemporalConfirmationResult * ros_message = static_cast<const macrobot_interfaces__msg__TemporalConfirmationResult *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_macrobot_interfaces__msg__TemporalConfirmationResult(ros_message, cdr);
}

static bool _TemporalConfirmationResult__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  macrobot_interfaces__msg__TemporalConfirmationResult * ros_message = static_cast<macrobot_interfaces__msg__TemporalConfirmationResult *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_macrobot_interfaces__msg__TemporalConfirmationResult(cdr, ros_message);
}

static uint32_t _TemporalConfirmationResult__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_macrobot_interfaces__msg__TemporalConfirmationResult(
      untyped_ros_message, 0));
}

static size_t _TemporalConfirmationResult__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_macrobot_interfaces__msg__TemporalConfirmationResult(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_TemporalConfirmationResult = {
  "macrobot_interfaces::msg",
  "TemporalConfirmationResult",
  _TemporalConfirmationResult__cdr_serialize,
  _TemporalConfirmationResult__cdr_deserialize,
  _TemporalConfirmationResult__get_serialized_size,
  _TemporalConfirmationResult__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _TemporalConfirmationResult__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_TemporalConfirmationResult,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__TemporalConfirmationResult__get_type_hash,
  &macrobot_interfaces__msg__TemporalConfirmationResult__get_type_description,
  &macrobot_interfaces__msg__TemporalConfirmationResult__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, macrobot_interfaces, msg, TemporalConfirmationResult)() {
  return &_TemporalConfirmationResult__type_support;
}

#if defined(__cplusplus)
}
#endif
