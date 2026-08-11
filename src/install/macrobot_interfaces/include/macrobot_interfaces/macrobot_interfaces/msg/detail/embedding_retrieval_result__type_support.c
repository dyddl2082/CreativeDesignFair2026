// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from macrobot_interfaces:msg/EmbeddingRetrievalResult.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__rosidl_typesupport_introspection_c.h"
#include "macrobot_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__functions.h"
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__struct.h"


// Include directives for member types
// Member `proposal_header`
// Member `image_header`
#include "std_msgs/msg/header.h"
// Member `proposal_header`
// Member `image_header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `target_object`
// Member `model_id`
// Member `pooling`
// Member `device`
// Member `best_positive_path`
// Member `best_negative_path`
// Member `top_positive_paths`
// Member `top_negative_paths`
// Member `reject_reason`
#include "rosidl_runtime_c/string_functions.h"
// Member `top_positive_scores`
// Member `top_negative_scores`
#include "rosidl_runtime_c/primitives_sequence_functions.h"
// Member `candidate`
#include "macrobot_interfaces/msg/depth_candidate.h"
// Member `candidate`
#include "macrobot_interfaces/msg/detail/depth_candidate__rosidl_typesupport_introspection_c.h"
// Member `crop_roi`
#include "sensor_msgs/msg/region_of_interest.h"
// Member `crop_roi`
#include "sensor_msgs/msg/detail/region_of_interest__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  macrobot_interfaces__msg__EmbeddingRetrievalResult__init(message_memory);
}

void macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_fini_function(void * message_memory)
{
  macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(message_memory);
}

size_t macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__size_function__EmbeddingRetrievalResult__top_positive_paths(
  const void * untyped_member)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return member->size;
}

const void * macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_const_function__EmbeddingRetrievalResult__top_positive_paths(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void * macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_function__EmbeddingRetrievalResult__top_positive_paths(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__fetch_function__EmbeddingRetrievalResult__top_positive_paths(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const rosidl_runtime_c__String * item =
    ((const rosidl_runtime_c__String *)
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_const_function__EmbeddingRetrievalResult__top_positive_paths(untyped_member, index));
  rosidl_runtime_c__String * value =
    (rosidl_runtime_c__String *)(untyped_value);
  *value = *item;
}

void macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__assign_function__EmbeddingRetrievalResult__top_positive_paths(
  void * untyped_member, size_t index, const void * untyped_value)
{
  rosidl_runtime_c__String * item =
    ((rosidl_runtime_c__String *)
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_function__EmbeddingRetrievalResult__top_positive_paths(untyped_member, index));
  const rosidl_runtime_c__String * value =
    (const rosidl_runtime_c__String *)(untyped_value);
  *item = *value;
}

bool macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__resize_function__EmbeddingRetrievalResult__top_positive_paths(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  rosidl_runtime_c__String__Sequence__fini(member);
  return rosidl_runtime_c__String__Sequence__init(member, size);
}

size_t macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__size_function__EmbeddingRetrievalResult__top_positive_scores(
  const void * untyped_member)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return member->size;
}

const void * macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_const_function__EmbeddingRetrievalResult__top_positive_scores(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void * macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_function__EmbeddingRetrievalResult__top_positive_scores(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__fetch_function__EmbeddingRetrievalResult__top_positive_scores(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_const_function__EmbeddingRetrievalResult__top_positive_scores(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__assign_function__EmbeddingRetrievalResult__top_positive_scores(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_function__EmbeddingRetrievalResult__top_positive_scores(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

bool macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__resize_function__EmbeddingRetrievalResult__top_positive_scores(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  rosidl_runtime_c__float__Sequence__fini(member);
  return rosidl_runtime_c__float__Sequence__init(member, size);
}

size_t macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__size_function__EmbeddingRetrievalResult__top_negative_paths(
  const void * untyped_member)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return member->size;
}

const void * macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_const_function__EmbeddingRetrievalResult__top_negative_paths(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void * macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_function__EmbeddingRetrievalResult__top_negative_paths(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__fetch_function__EmbeddingRetrievalResult__top_negative_paths(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const rosidl_runtime_c__String * item =
    ((const rosidl_runtime_c__String *)
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_const_function__EmbeddingRetrievalResult__top_negative_paths(untyped_member, index));
  rosidl_runtime_c__String * value =
    (rosidl_runtime_c__String *)(untyped_value);
  *value = *item;
}

void macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__assign_function__EmbeddingRetrievalResult__top_negative_paths(
  void * untyped_member, size_t index, const void * untyped_value)
{
  rosidl_runtime_c__String * item =
    ((rosidl_runtime_c__String *)
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_function__EmbeddingRetrievalResult__top_negative_paths(untyped_member, index));
  const rosidl_runtime_c__String * value =
    (const rosidl_runtime_c__String *)(untyped_value);
  *item = *value;
}

bool macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__resize_function__EmbeddingRetrievalResult__top_negative_paths(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  rosidl_runtime_c__String__Sequence__fini(member);
  return rosidl_runtime_c__String__Sequence__init(member, size);
}

size_t macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__size_function__EmbeddingRetrievalResult__top_negative_scores(
  const void * untyped_member)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return member->size;
}

const void * macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_const_function__EmbeddingRetrievalResult__top_negative_scores(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void * macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_function__EmbeddingRetrievalResult__top_negative_scores(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__fetch_function__EmbeddingRetrievalResult__top_negative_scores(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_const_function__EmbeddingRetrievalResult__top_negative_scores(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__assign_function__EmbeddingRetrievalResult__top_negative_scores(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_function__EmbeddingRetrievalResult__top_negative_scores(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

bool macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__resize_function__EmbeddingRetrievalResult__top_negative_scores(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  rosidl_runtime_c__float__Sequence__fini(member);
  return rosidl_runtime_c__float__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_message_member_array[38] = {
  {
    "proposal_header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, proposal_header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "image_header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, image_header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "candidate_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, candidate_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "crop_index",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, crop_index),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "frame_crop_count",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, frame_crop_count),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "target_object",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, target_object),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "model_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, model_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "pooling",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, pooling),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "device",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, device),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "embedding_dim",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, embedding_dim),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "positive_bank_available",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, positive_bank_available),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "positive_reference_count",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, positive_reference_count),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "negative_bank_available",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, negative_bank_available),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "negative_reference_count",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, negative_reference_count),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "foreground_mask_used",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, foreground_mask_used),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "objectness_score",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, objectness_score),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "target_hint_score",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, target_hint_score),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "positive_similarity",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, positive_similarity),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "best_positive_similarity",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, best_positive_similarity),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "negative_similarity",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, negative_similarity),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "best_negative_similarity",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, best_negative_similarity),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "margin",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, margin),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "best_positive_path",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, best_positive_path),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "best_negative_path",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, best_negative_path),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "top_positive_paths",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, top_positive_paths),  // bytes offset in struct
    NULL,  // default value
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__size_function__EmbeddingRetrievalResult__top_positive_paths,  // size() function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_const_function__EmbeddingRetrievalResult__top_positive_paths,  // get_const(index) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_function__EmbeddingRetrievalResult__top_positive_paths,  // get(index) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__fetch_function__EmbeddingRetrievalResult__top_positive_paths,  // fetch(index, &value) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__assign_function__EmbeddingRetrievalResult__top_positive_paths,  // assign(index, value) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__resize_function__EmbeddingRetrievalResult__top_positive_paths  // resize(index) function pointer
  },
  {
    "top_positive_scores",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, top_positive_scores),  // bytes offset in struct
    NULL,  // default value
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__size_function__EmbeddingRetrievalResult__top_positive_scores,  // size() function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_const_function__EmbeddingRetrievalResult__top_positive_scores,  // get_const(index) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_function__EmbeddingRetrievalResult__top_positive_scores,  // get(index) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__fetch_function__EmbeddingRetrievalResult__top_positive_scores,  // fetch(index, &value) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__assign_function__EmbeddingRetrievalResult__top_positive_scores,  // assign(index, value) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__resize_function__EmbeddingRetrievalResult__top_positive_scores  // resize(index) function pointer
  },
  {
    "top_negative_paths",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, top_negative_paths),  // bytes offset in struct
    NULL,  // default value
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__size_function__EmbeddingRetrievalResult__top_negative_paths,  // size() function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_const_function__EmbeddingRetrievalResult__top_negative_paths,  // get_const(index) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_function__EmbeddingRetrievalResult__top_negative_paths,  // get(index) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__fetch_function__EmbeddingRetrievalResult__top_negative_paths,  // fetch(index, &value) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__assign_function__EmbeddingRetrievalResult__top_negative_paths,  // assign(index, value) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__resize_function__EmbeddingRetrievalResult__top_negative_paths  // resize(index) function pointer
  },
  {
    "top_negative_scores",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, top_negative_scores),  // bytes offset in struct
    NULL,  // default value
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__size_function__EmbeddingRetrievalResult__top_negative_scores,  // size() function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_const_function__EmbeddingRetrievalResult__top_negative_scores,  // get_const(index) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__get_function__EmbeddingRetrievalResult__top_negative_scores,  // get(index) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__fetch_function__EmbeddingRetrievalResult__top_negative_scores,  // fetch(index, &value) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__assign_function__EmbeddingRetrievalResult__top_negative_scores,  // assign(index, value) function pointer
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__resize_function__EmbeddingRetrievalResult__top_negative_scores  // resize(index) function pointer
  },
  {
    "thresholds_enforced",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, thresholds_enforced),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "passed_positive_threshold",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, passed_positive_threshold),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "passed_margin_threshold",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, passed_margin_threshold),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "accepted",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, accepted),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "reject_reason",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, reject_reason),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "preprocessing_ms",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, preprocessing_ms),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "inference_ms",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, inference_ms),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "matching_ms",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, matching_ms),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "candidate",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, candidate),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "crop_roi",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(macrobot_interfaces__msg__EmbeddingRetrievalResult, crop_roi),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_message_members = {
  "macrobot_interfaces__msg",  // message namespace
  "EmbeddingRetrievalResult",  // message name
  38,  // number of fields
  sizeof(macrobot_interfaces__msg__EmbeddingRetrievalResult),
  false,  // has_any_key_member_
  macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_message_member_array,  // message members
  macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_init_function,  // function to initialize message memory (memory has to be allocated)
  macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_message_type_support_handle = {
  0,
  &macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_message_members,
  get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_hash,
  &macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_description,
  &macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_macrobot_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, macrobot_interfaces, msg, EmbeddingRetrievalResult)() {
  macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_message_member_array[36].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, macrobot_interfaces, msg, DepthCandidate)();
  macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_message_member_array[37].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, sensor_msgs, msg, RegionOfInterest)();
  if (!macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_message_type_support_handle.typesupport_identifier) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &macrobot_interfaces__msg__EmbeddingRetrievalResult__rosidl_typesupport_introspection_c__EmbeddingRetrievalResult_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
