// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from macrobot_interfaces:msg/EmbeddingRetrievalResult.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "macrobot_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__struct.h"
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__functions.h"
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
#include "rosidl_runtime_c/primitives_sequence.h"  // top_negative_scores, top_positive_scores
#include "rosidl_runtime_c/primitives_sequence_functions.h"  // top_negative_scores, top_positive_scores
#include "rosidl_runtime_c/string.h"  // best_negative_path, best_positive_path, device, model_id, pooling, reject_reason, target_object, top_negative_paths, top_positive_paths
#include "rosidl_runtime_c/string_functions.h"  // best_negative_path, best_positive_path, device, model_id, pooling, reject_reason, target_object, top_negative_paths, top_positive_paths
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


using _EmbeddingRetrievalResult__ros_msg_type = macrobot_interfaces__msg__EmbeddingRetrievalResult;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  const macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message,
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

  // Field name: model_id
  {
    const rosidl_runtime_c__String * str = &ros_message->model_id;
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

  // Field name: pooling
  {
    const rosidl_runtime_c__String * str = &ros_message->pooling;
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

  // Field name: device
  {
    const rosidl_runtime_c__String * str = &ros_message->device;
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

  // Field name: embedding_dim
  {
    cdr << ros_message->embedding_dim;
  }

  // Field name: positive_bank_available
  {
    cdr << (ros_message->positive_bank_available ? true : false);
  }

  // Field name: positive_reference_count
  {
    cdr << ros_message->positive_reference_count;
  }

  // Field name: negative_bank_available
  {
    cdr << (ros_message->negative_bank_available ? true : false);
  }

  // Field name: negative_reference_count
  {
    cdr << ros_message->negative_reference_count;
  }

  // Field name: foreground_mask_used
  {
    cdr << (ros_message->foreground_mask_used ? true : false);
  }

  // Field name: objectness_score
  {
    cdr << ros_message->objectness_score;
  }

  // Field name: target_hint_score
  {
    cdr << ros_message->target_hint_score;
  }

  // Field name: positive_similarity
  {
    cdr << ros_message->positive_similarity;
  }

  // Field name: best_positive_similarity
  {
    cdr << ros_message->best_positive_similarity;
  }

  // Field name: negative_similarity
  {
    cdr << ros_message->negative_similarity;
  }

  // Field name: best_negative_similarity
  {
    cdr << ros_message->best_negative_similarity;
  }

  // Field name: margin
  {
    cdr << ros_message->margin;
  }

  // Field name: best_positive_path
  {
    const rosidl_runtime_c__String * str = &ros_message->best_positive_path;
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

  // Field name: best_negative_path
  {
    const rosidl_runtime_c__String * str = &ros_message->best_negative_path;
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

  // Field name: top_positive_paths
  {
    size_t size = ros_message->top_positive_paths.size;
    auto array_ptr = ros_message->top_positive_paths.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      const rosidl_runtime_c__String * str = &array_ptr[i];
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
  }

  // Field name: top_positive_scores
  {
    size_t size = ros_message->top_positive_scores.size;
    auto array_ptr = ros_message->top_positive_scores.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: top_negative_paths
  {
    size_t size = ros_message->top_negative_paths.size;
    auto array_ptr = ros_message->top_negative_paths.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      const rosidl_runtime_c__String * str = &array_ptr[i];
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
  }

  // Field name: top_negative_scores
  {
    size_t size = ros_message->top_negative_scores.size;
    auto array_ptr = ros_message->top_negative_scores.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: thresholds_enforced
  {
    cdr << (ros_message->thresholds_enforced ? true : false);
  }

  // Field name: passed_positive_threshold
  {
    cdr << (ros_message->passed_positive_threshold ? true : false);
  }

  // Field name: passed_margin_threshold
  {
    cdr << (ros_message->passed_margin_threshold ? true : false);
  }

  // Field name: accepted
  {
    cdr << (ros_message->accepted ? true : false);
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

  // Field name: preprocessing_ms
  {
    cdr << ros_message->preprocessing_ms;
  }

  // Field name: inference_ms
  {
    cdr << ros_message->inference_ms;
  }

  // Field name: matching_ms
  {
    cdr << ros_message->matching_ms;
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
bool cdr_deserialize_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  eprosima::fastcdr::Cdr & cdr,
  macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message)
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

  // Field name: model_id
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->model_id.data) {
      rosidl_runtime_c__String__init(&ros_message->model_id);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->model_id,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'model_id'\n");
      return false;
    }
  }

  // Field name: pooling
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->pooling.data) {
      rosidl_runtime_c__String__init(&ros_message->pooling);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->pooling,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'pooling'\n");
      return false;
    }
  }

  // Field name: device
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->device.data) {
      rosidl_runtime_c__String__init(&ros_message->device);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->device,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'device'\n");
      return false;
    }
  }

  // Field name: embedding_dim
  {
    cdr >> ros_message->embedding_dim;
  }

  // Field name: positive_bank_available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->positive_bank_available = tmp ? true : false;
  }

  // Field name: positive_reference_count
  {
    cdr >> ros_message->positive_reference_count;
  }

  // Field name: negative_bank_available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->negative_bank_available = tmp ? true : false;
  }

  // Field name: negative_reference_count
  {
    cdr >> ros_message->negative_reference_count;
  }

  // Field name: foreground_mask_used
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->foreground_mask_used = tmp ? true : false;
  }

  // Field name: objectness_score
  {
    cdr >> ros_message->objectness_score;
  }

  // Field name: target_hint_score
  {
    cdr >> ros_message->target_hint_score;
  }

  // Field name: positive_similarity
  {
    cdr >> ros_message->positive_similarity;
  }

  // Field name: best_positive_similarity
  {
    cdr >> ros_message->best_positive_similarity;
  }

  // Field name: negative_similarity
  {
    cdr >> ros_message->negative_similarity;
  }

  // Field name: best_negative_similarity
  {
    cdr >> ros_message->best_negative_similarity;
  }

  // Field name: margin
  {
    cdr >> ros_message->margin;
  }

  // Field name: best_positive_path
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->best_positive_path.data) {
      rosidl_runtime_c__String__init(&ros_message->best_positive_path);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->best_positive_path,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'best_positive_path'\n");
      return false;
    }
  }

  // Field name: best_negative_path
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->best_negative_path.data) {
      rosidl_runtime_c__String__init(&ros_message->best_negative_path);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->best_negative_path,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'best_negative_path'\n");
      return false;
    }
  }

  // Field name: top_positive_paths
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);

    // Check there are at least 'size' remaining bytes in the CDR stream before resizing
    auto old_state = cdr.get_state();
    bool correct_size = cdr.jump(size);
    cdr.set_state(old_state);
    if (!correct_size) {
      fprintf(stderr, "sequence size exceeds remaining buffer\n");
      return false;
    }

    if (ros_message->top_positive_paths.data) {
      rosidl_runtime_c__String__Sequence__fini(&ros_message->top_positive_paths);
    }
    if (!rosidl_runtime_c__String__Sequence__init(&ros_message->top_positive_paths, size)) {
      fprintf(stderr, "failed to create array for field 'top_positive_paths'");
      return false;
    }
    auto array_ptr = ros_message->top_positive_paths.data;
    for (size_t i = 0; i < size; ++i) {
      std::string tmp;
      cdr >> tmp;
      auto & ros_i = array_ptr[i];
      if (!ros_i.data) {
        rosidl_runtime_c__String__init(&ros_i);
      }
      bool succeeded = rosidl_runtime_c__String__assign(
        &ros_i,
        tmp.c_str());
      if (!succeeded) {
        fprintf(stderr, "failed to assign string into field 'top_positive_paths'\n");
        return false;
      }
    }
  }

  // Field name: top_positive_scores
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);

    // Check there are at least 'size' remaining bytes in the CDR stream before resizing
    auto old_state = cdr.get_state();
    bool correct_size = cdr.jump(size);
    cdr.set_state(old_state);
    if (!correct_size) {
      fprintf(stderr, "sequence size exceeds remaining buffer\n");
      return false;
    }

    if (ros_message->top_positive_scores.data) {
      rosidl_runtime_c__float__Sequence__fini(&ros_message->top_positive_scores);
    }
    if (!rosidl_runtime_c__float__Sequence__init(&ros_message->top_positive_scores, size)) {
      fprintf(stderr, "failed to create array for field 'top_positive_scores'");
      return false;
    }
    auto array_ptr = ros_message->top_positive_scores.data;
    cdr.deserialize_array(array_ptr, size);
  }

  // Field name: top_negative_paths
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);

    // Check there are at least 'size' remaining bytes in the CDR stream before resizing
    auto old_state = cdr.get_state();
    bool correct_size = cdr.jump(size);
    cdr.set_state(old_state);
    if (!correct_size) {
      fprintf(stderr, "sequence size exceeds remaining buffer\n");
      return false;
    }

    if (ros_message->top_negative_paths.data) {
      rosidl_runtime_c__String__Sequence__fini(&ros_message->top_negative_paths);
    }
    if (!rosidl_runtime_c__String__Sequence__init(&ros_message->top_negative_paths, size)) {
      fprintf(stderr, "failed to create array for field 'top_negative_paths'");
      return false;
    }
    auto array_ptr = ros_message->top_negative_paths.data;
    for (size_t i = 0; i < size; ++i) {
      std::string tmp;
      cdr >> tmp;
      auto & ros_i = array_ptr[i];
      if (!ros_i.data) {
        rosidl_runtime_c__String__init(&ros_i);
      }
      bool succeeded = rosidl_runtime_c__String__assign(
        &ros_i,
        tmp.c_str());
      if (!succeeded) {
        fprintf(stderr, "failed to assign string into field 'top_negative_paths'\n");
        return false;
      }
    }
  }

  // Field name: top_negative_scores
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);

    // Check there are at least 'size' remaining bytes in the CDR stream before resizing
    auto old_state = cdr.get_state();
    bool correct_size = cdr.jump(size);
    cdr.set_state(old_state);
    if (!correct_size) {
      fprintf(stderr, "sequence size exceeds remaining buffer\n");
      return false;
    }

    if (ros_message->top_negative_scores.data) {
      rosidl_runtime_c__float__Sequence__fini(&ros_message->top_negative_scores);
    }
    if (!rosidl_runtime_c__float__Sequence__init(&ros_message->top_negative_scores, size)) {
      fprintf(stderr, "failed to create array for field 'top_negative_scores'");
      return false;
    }
    auto array_ptr = ros_message->top_negative_scores.data;
    cdr.deserialize_array(array_ptr, size);
  }

  // Field name: thresholds_enforced
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->thresholds_enforced = tmp ? true : false;
  }

  // Field name: passed_positive_threshold
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->passed_positive_threshold = tmp ? true : false;
  }

  // Field name: passed_margin_threshold
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->passed_margin_threshold = tmp ? true : false;
  }

  // Field name: accepted
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->accepted = tmp ? true : false;
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

  // Field name: preprocessing_ms
  {
    cdr >> ros_message->preprocessing_ms;
  }

  // Field name: inference_ms
  {
    cdr >> ros_message->inference_ms;
  }

  // Field name: matching_ms
  {
    cdr >> ros_message->matching_ms;
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
size_t get_serialized_size_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _EmbeddingRetrievalResult__ros_msg_type * ros_message = static_cast<const _EmbeddingRetrievalResult__ros_msg_type *>(untyped_ros_message);
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

  // Field name: model_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->model_id.size + 1);

  // Field name: pooling
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->pooling.size + 1);

  // Field name: device
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->device.size + 1);

  // Field name: embedding_dim
  {
    size_t item_size = sizeof(ros_message->embedding_dim);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: positive_bank_available
  {
    size_t item_size = sizeof(ros_message->positive_bank_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: positive_reference_count
  {
    size_t item_size = sizeof(ros_message->positive_reference_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: negative_bank_available
  {
    size_t item_size = sizeof(ros_message->negative_bank_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: negative_reference_count
  {
    size_t item_size = sizeof(ros_message->negative_reference_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_mask_used
  {
    size_t item_size = sizeof(ros_message->foreground_mask_used);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

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

  // Field name: positive_similarity
  {
    size_t item_size = sizeof(ros_message->positive_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: best_positive_similarity
  {
    size_t item_size = sizeof(ros_message->best_positive_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: negative_similarity
  {
    size_t item_size = sizeof(ros_message->negative_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: best_negative_similarity
  {
    size_t item_size = sizeof(ros_message->best_negative_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: margin
  {
    size_t item_size = sizeof(ros_message->margin);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: best_positive_path
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->best_positive_path.size + 1);

  // Field name: best_negative_path
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->best_negative_path.size + 1);

  // Field name: top_positive_paths
  {
    size_t array_size = ros_message->top_positive_paths.size;
    auto array_ptr = ros_message->top_positive_paths.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        (array_ptr[index].size + 1);
    }
  }

  // Field name: top_positive_scores
  {
    size_t array_size = ros_message->top_positive_scores.size;
    auto array_ptr = ros_message->top_positive_scores.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: top_negative_paths
  {
    size_t array_size = ros_message->top_negative_paths.size;
    auto array_ptr = ros_message->top_negative_paths.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        (array_ptr[index].size + 1);
    }
  }

  // Field name: top_negative_scores
  {
    size_t array_size = ros_message->top_negative_scores.size;
    auto array_ptr = ros_message->top_negative_scores.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: thresholds_enforced
  {
    size_t item_size = sizeof(ros_message->thresholds_enforced);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: passed_positive_threshold
  {
    size_t item_size = sizeof(ros_message->passed_positive_threshold);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: passed_margin_threshold
  {
    size_t item_size = sizeof(ros_message->passed_margin_threshold);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: accepted
  {
    size_t item_size = sizeof(ros_message->accepted);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: reject_reason
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->reject_reason.size + 1);

  // Field name: preprocessing_ms
  {
    size_t item_size = sizeof(ros_message->preprocessing_ms);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: inference_ms
  {
    size_t item_size = sizeof(ros_message->inference_ms);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: matching_ms
  {
    size_t item_size = sizeof(ros_message->matching_ms);
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
size_t max_serialized_size_macrobot_interfaces__msg__EmbeddingRetrievalResult(
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

  // Field name: model_id
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

  // Field name: pooling
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

  // Field name: device
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

  // Field name: embedding_dim
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: positive_bank_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: positive_reference_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: negative_bank_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: negative_reference_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: foreground_mask_used
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
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

  // Field name: positive_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: best_positive_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: negative_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: best_negative_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: margin
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: best_positive_path
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

  // Field name: best_negative_path
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

  // Field name: top_positive_paths
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: top_positive_scores
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: top_negative_paths
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: top_negative_scores
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: thresholds_enforced
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: passed_positive_threshold
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: passed_margin_threshold
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

  // Field name: preprocessing_ms
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: inference_ms
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: matching_ms
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
    using DataType = macrobot_interfaces__msg__EmbeddingRetrievalResult;
    is_plain =
      (
      offsetof(DataType, crop_roi) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_macrobot_interfaces
bool cdr_serialize_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  const macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message,
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

  // Field name: model_id
  {
    const rosidl_runtime_c__String * str = &ros_message->model_id;
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

  // Field name: pooling
  {
    const rosidl_runtime_c__String * str = &ros_message->pooling;
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

  // Field name: device
  {
    const rosidl_runtime_c__String * str = &ros_message->device;
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

  // Field name: embedding_dim
  {
    cdr << ros_message->embedding_dim;
  }

  // Field name: positive_bank_available
  {
    cdr << (ros_message->positive_bank_available ? true : false);
  }

  // Field name: positive_reference_count
  {
    cdr << ros_message->positive_reference_count;
  }

  // Field name: negative_bank_available
  {
    cdr << (ros_message->negative_bank_available ? true : false);
  }

  // Field name: negative_reference_count
  {
    cdr << ros_message->negative_reference_count;
  }

  // Field name: foreground_mask_used
  {
    cdr << (ros_message->foreground_mask_used ? true : false);
  }

  // Field name: objectness_score
  {
    cdr << ros_message->objectness_score;
  }

  // Field name: target_hint_score
  {
    cdr << ros_message->target_hint_score;
  }

  // Field name: positive_similarity
  {
    cdr << ros_message->positive_similarity;
  }

  // Field name: best_positive_similarity
  {
    cdr << ros_message->best_positive_similarity;
  }

  // Field name: negative_similarity
  {
    cdr << ros_message->negative_similarity;
  }

  // Field name: best_negative_similarity
  {
    cdr << ros_message->best_negative_similarity;
  }

  // Field name: margin
  {
    cdr << ros_message->margin;
  }

  // Field name: best_positive_path
  {
    const rosidl_runtime_c__String * str = &ros_message->best_positive_path;
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

  // Field name: best_negative_path
  {
    const rosidl_runtime_c__String * str = &ros_message->best_negative_path;
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

  // Field name: top_positive_paths
  {
    size_t size = ros_message->top_positive_paths.size;
    auto array_ptr = ros_message->top_positive_paths.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      const rosidl_runtime_c__String * str = &array_ptr[i];
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
  }

  // Field name: top_positive_scores
  {
    size_t size = ros_message->top_positive_scores.size;
    auto array_ptr = ros_message->top_positive_scores.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: top_negative_paths
  {
    size_t size = ros_message->top_negative_paths.size;
    auto array_ptr = ros_message->top_negative_paths.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      const rosidl_runtime_c__String * str = &array_ptr[i];
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
  }

  // Field name: top_negative_scores
  {
    size_t size = ros_message->top_negative_scores.size;
    auto array_ptr = ros_message->top_negative_scores.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: thresholds_enforced
  {
    cdr << (ros_message->thresholds_enforced ? true : false);
  }

  // Field name: passed_positive_threshold
  {
    cdr << (ros_message->passed_positive_threshold ? true : false);
  }

  // Field name: passed_margin_threshold
  {
    cdr << (ros_message->passed_margin_threshold ? true : false);
  }

  // Field name: accepted
  {
    cdr << (ros_message->accepted ? true : false);
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

  // Field name: preprocessing_ms
  {
    cdr << ros_message->preprocessing_ms;
  }

  // Field name: inference_ms
  {
    cdr << ros_message->inference_ms;
  }

  // Field name: matching_ms
  {
    cdr << ros_message->matching_ms;
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
size_t get_serialized_size_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _EmbeddingRetrievalResult__ros_msg_type * ros_message = static_cast<const _EmbeddingRetrievalResult__ros_msg_type *>(untyped_ros_message);
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

  // Field name: model_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->model_id.size + 1);

  // Field name: pooling
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->pooling.size + 1);

  // Field name: device
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->device.size + 1);

  // Field name: embedding_dim
  {
    size_t item_size = sizeof(ros_message->embedding_dim);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: positive_bank_available
  {
    size_t item_size = sizeof(ros_message->positive_bank_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: positive_reference_count
  {
    size_t item_size = sizeof(ros_message->positive_reference_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: negative_bank_available
  {
    size_t item_size = sizeof(ros_message->negative_bank_available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: negative_reference_count
  {
    size_t item_size = sizeof(ros_message->negative_reference_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: foreground_mask_used
  {
    size_t item_size = sizeof(ros_message->foreground_mask_used);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

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

  // Field name: positive_similarity
  {
    size_t item_size = sizeof(ros_message->positive_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: best_positive_similarity
  {
    size_t item_size = sizeof(ros_message->best_positive_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: negative_similarity
  {
    size_t item_size = sizeof(ros_message->negative_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: best_negative_similarity
  {
    size_t item_size = sizeof(ros_message->best_negative_similarity);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: margin
  {
    size_t item_size = sizeof(ros_message->margin);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: best_positive_path
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->best_positive_path.size + 1);

  // Field name: best_negative_path
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->best_negative_path.size + 1);

  // Field name: top_positive_paths
  {
    size_t array_size = ros_message->top_positive_paths.size;
    auto array_ptr = ros_message->top_positive_paths.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        (array_ptr[index].size + 1);
    }
  }

  // Field name: top_positive_scores
  {
    size_t array_size = ros_message->top_positive_scores.size;
    auto array_ptr = ros_message->top_positive_scores.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: top_negative_paths
  {
    size_t array_size = ros_message->top_negative_paths.size;
    auto array_ptr = ros_message->top_negative_paths.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        (array_ptr[index].size + 1);
    }
  }

  // Field name: top_negative_scores
  {
    size_t array_size = ros_message->top_negative_scores.size;
    auto array_ptr = ros_message->top_negative_scores.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: thresholds_enforced
  {
    size_t item_size = sizeof(ros_message->thresholds_enforced);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: passed_positive_threshold
  {
    size_t item_size = sizeof(ros_message->passed_positive_threshold);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: passed_margin_threshold
  {
    size_t item_size = sizeof(ros_message->passed_margin_threshold);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: accepted
  {
    size_t item_size = sizeof(ros_message->accepted);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: reject_reason
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->reject_reason.size + 1);

  // Field name: preprocessing_ms
  {
    size_t item_size = sizeof(ros_message->preprocessing_ms);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: inference_ms
  {
    size_t item_size = sizeof(ros_message->inference_ms);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: matching_ms
  {
    size_t item_size = sizeof(ros_message->matching_ms);
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
size_t max_serialized_size_key_macrobot_interfaces__msg__EmbeddingRetrievalResult(
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

  // Field name: model_id
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

  // Field name: pooling
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

  // Field name: device
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

  // Field name: embedding_dim
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: positive_bank_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: positive_reference_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: negative_bank_available
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: negative_reference_count
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: foreground_mask_used
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
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

  // Field name: positive_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: best_positive_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: negative_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: best_negative_similarity
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: margin
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: best_positive_path
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

  // Field name: best_negative_path
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

  // Field name: top_positive_paths
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: top_positive_scores
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: top_negative_paths
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: top_negative_scores
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: thresholds_enforced
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: passed_positive_threshold
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: passed_margin_threshold
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

  // Field name: preprocessing_ms
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: inference_ms
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: matching_ms
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
    using DataType = macrobot_interfaces__msg__EmbeddingRetrievalResult;
    is_plain =
      (
      offsetof(DataType, crop_roi) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _EmbeddingRetrievalResult__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message = static_cast<const macrobot_interfaces__msg__EmbeddingRetrievalResult *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_macrobot_interfaces__msg__EmbeddingRetrievalResult(ros_message, cdr);
}

static bool _EmbeddingRetrievalResult__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message = static_cast<macrobot_interfaces__msg__EmbeddingRetrievalResult *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_macrobot_interfaces__msg__EmbeddingRetrievalResult(cdr, ros_message);
}

static uint32_t _EmbeddingRetrievalResult__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_macrobot_interfaces__msg__EmbeddingRetrievalResult(
      untyped_ros_message, 0));
}

static size_t _EmbeddingRetrievalResult__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_macrobot_interfaces__msg__EmbeddingRetrievalResult(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_EmbeddingRetrievalResult = {
  "macrobot_interfaces::msg",
  "EmbeddingRetrievalResult",
  _EmbeddingRetrievalResult__cdr_serialize,
  _EmbeddingRetrievalResult__cdr_deserialize,
  _EmbeddingRetrievalResult__get_serialized_size,
  _EmbeddingRetrievalResult__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _EmbeddingRetrievalResult__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_EmbeddingRetrievalResult,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_hash,
  &macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_description,
  &macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, macrobot_interfaces, msg, EmbeddingRetrievalResult)() {
  return &_EmbeddingRetrievalResult__type_support;
}

#if defined(__cplusplus)
}
#endif
