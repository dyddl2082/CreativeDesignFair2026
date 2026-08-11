// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from macrobot_interfaces:msg/EmbeddingRetrievalResult.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `proposal_header`
// Member `image_header`
#include "std_msgs/msg/detail/header__functions.h"
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
#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"
// Member `crop_roi`
#include "sensor_msgs/msg/detail/region_of_interest__functions.h"

bool
macrobot_interfaces__msg__EmbeddingRetrievalResult__init(macrobot_interfaces__msg__EmbeddingRetrievalResult * msg)
{
  if (!msg) {
    return false;
  }
  // proposal_header
  if (!std_msgs__msg__Header__init(&msg->proposal_header)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // image_header
  if (!std_msgs__msg__Header__init(&msg->image_header)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // candidate_id
  // crop_index
  // frame_crop_count
  // target_object
  if (!rosidl_runtime_c__String__init(&msg->target_object)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // model_id
  if (!rosidl_runtime_c__String__init(&msg->model_id)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // pooling
  if (!rosidl_runtime_c__String__init(&msg->pooling)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // device
  if (!rosidl_runtime_c__String__init(&msg->device)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // embedding_dim
  // positive_bank_available
  // positive_reference_count
  // negative_bank_available
  // negative_reference_count
  // foreground_mask_used
  // objectness_score
  // target_hint_score
  // positive_similarity
  // best_positive_similarity
  // negative_similarity
  // best_negative_similarity
  // margin
  // best_positive_path
  if (!rosidl_runtime_c__String__init(&msg->best_positive_path)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // best_negative_path
  if (!rosidl_runtime_c__String__init(&msg->best_negative_path)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // top_positive_paths
  if (!rosidl_runtime_c__String__Sequence__init(&msg->top_positive_paths, 0)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // top_positive_scores
  if (!rosidl_runtime_c__float__Sequence__init(&msg->top_positive_scores, 0)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // top_negative_paths
  if (!rosidl_runtime_c__String__Sequence__init(&msg->top_negative_paths, 0)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // top_negative_scores
  if (!rosidl_runtime_c__float__Sequence__init(&msg->top_negative_scores, 0)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // thresholds_enforced
  // passed_positive_threshold
  // passed_margin_threshold
  // accepted
  // reject_reason
  if (!rosidl_runtime_c__String__init(&msg->reject_reason)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // preprocessing_ms
  // inference_ms
  // matching_ms
  // candidate
  if (!macrobot_interfaces__msg__DepthCandidate__init(&msg->candidate)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  // crop_roi
  if (!sensor_msgs__msg__RegionOfInterest__init(&msg->crop_roi)) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
    return false;
  }
  return true;
}

void
macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(macrobot_interfaces__msg__EmbeddingRetrievalResult * msg)
{
  if (!msg) {
    return;
  }
  // proposal_header
  std_msgs__msg__Header__fini(&msg->proposal_header);
  // image_header
  std_msgs__msg__Header__fini(&msg->image_header);
  // candidate_id
  // crop_index
  // frame_crop_count
  // target_object
  rosidl_runtime_c__String__fini(&msg->target_object);
  // model_id
  rosidl_runtime_c__String__fini(&msg->model_id);
  // pooling
  rosidl_runtime_c__String__fini(&msg->pooling);
  // device
  rosidl_runtime_c__String__fini(&msg->device);
  // embedding_dim
  // positive_bank_available
  // positive_reference_count
  // negative_bank_available
  // negative_reference_count
  // foreground_mask_used
  // objectness_score
  // target_hint_score
  // positive_similarity
  // best_positive_similarity
  // negative_similarity
  // best_negative_similarity
  // margin
  // best_positive_path
  rosidl_runtime_c__String__fini(&msg->best_positive_path);
  // best_negative_path
  rosidl_runtime_c__String__fini(&msg->best_negative_path);
  // top_positive_paths
  rosidl_runtime_c__String__Sequence__fini(&msg->top_positive_paths);
  // top_positive_scores
  rosidl_runtime_c__float__Sequence__fini(&msg->top_positive_scores);
  // top_negative_paths
  rosidl_runtime_c__String__Sequence__fini(&msg->top_negative_paths);
  // top_negative_scores
  rosidl_runtime_c__float__Sequence__fini(&msg->top_negative_scores);
  // thresholds_enforced
  // passed_positive_threshold
  // passed_margin_threshold
  // accepted
  // reject_reason
  rosidl_runtime_c__String__fini(&msg->reject_reason);
  // preprocessing_ms
  // inference_ms
  // matching_ms
  // candidate
  macrobot_interfaces__msg__DepthCandidate__fini(&msg->candidate);
  // crop_roi
  sensor_msgs__msg__RegionOfInterest__fini(&msg->crop_roi);
}

bool
macrobot_interfaces__msg__EmbeddingRetrievalResult__are_equal(const macrobot_interfaces__msg__EmbeddingRetrievalResult * lhs, const macrobot_interfaces__msg__EmbeddingRetrievalResult * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // proposal_header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->proposal_header), &(rhs->proposal_header)))
  {
    return false;
  }
  // image_header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->image_header), &(rhs->image_header)))
  {
    return false;
  }
  // candidate_id
  if (lhs->candidate_id != rhs->candidate_id) {
    return false;
  }
  // crop_index
  if (lhs->crop_index != rhs->crop_index) {
    return false;
  }
  // frame_crop_count
  if (lhs->frame_crop_count != rhs->frame_crop_count) {
    return false;
  }
  // target_object
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->target_object), &(rhs->target_object)))
  {
    return false;
  }
  // model_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->model_id), &(rhs->model_id)))
  {
    return false;
  }
  // pooling
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->pooling), &(rhs->pooling)))
  {
    return false;
  }
  // device
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->device), &(rhs->device)))
  {
    return false;
  }
  // embedding_dim
  if (lhs->embedding_dim != rhs->embedding_dim) {
    return false;
  }
  // positive_bank_available
  if (lhs->positive_bank_available != rhs->positive_bank_available) {
    return false;
  }
  // positive_reference_count
  if (lhs->positive_reference_count != rhs->positive_reference_count) {
    return false;
  }
  // negative_bank_available
  if (lhs->negative_bank_available != rhs->negative_bank_available) {
    return false;
  }
  // negative_reference_count
  if (lhs->negative_reference_count != rhs->negative_reference_count) {
    return false;
  }
  // foreground_mask_used
  if (lhs->foreground_mask_used != rhs->foreground_mask_used) {
    return false;
  }
  // objectness_score
  if (lhs->objectness_score != rhs->objectness_score) {
    return false;
  }
  // target_hint_score
  if (lhs->target_hint_score != rhs->target_hint_score) {
    return false;
  }
  // positive_similarity
  if (lhs->positive_similarity != rhs->positive_similarity) {
    return false;
  }
  // best_positive_similarity
  if (lhs->best_positive_similarity != rhs->best_positive_similarity) {
    return false;
  }
  // negative_similarity
  if (lhs->negative_similarity != rhs->negative_similarity) {
    return false;
  }
  // best_negative_similarity
  if (lhs->best_negative_similarity != rhs->best_negative_similarity) {
    return false;
  }
  // margin
  if (lhs->margin != rhs->margin) {
    return false;
  }
  // best_positive_path
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->best_positive_path), &(rhs->best_positive_path)))
  {
    return false;
  }
  // best_negative_path
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->best_negative_path), &(rhs->best_negative_path)))
  {
    return false;
  }
  // top_positive_paths
  if (!rosidl_runtime_c__String__Sequence__are_equal(
      &(lhs->top_positive_paths), &(rhs->top_positive_paths)))
  {
    return false;
  }
  // top_positive_scores
  if (!rosidl_runtime_c__float__Sequence__are_equal(
      &(lhs->top_positive_scores), &(rhs->top_positive_scores)))
  {
    return false;
  }
  // top_negative_paths
  if (!rosidl_runtime_c__String__Sequence__are_equal(
      &(lhs->top_negative_paths), &(rhs->top_negative_paths)))
  {
    return false;
  }
  // top_negative_scores
  if (!rosidl_runtime_c__float__Sequence__are_equal(
      &(lhs->top_negative_scores), &(rhs->top_negative_scores)))
  {
    return false;
  }
  // thresholds_enforced
  if (lhs->thresholds_enforced != rhs->thresholds_enforced) {
    return false;
  }
  // passed_positive_threshold
  if (lhs->passed_positive_threshold != rhs->passed_positive_threshold) {
    return false;
  }
  // passed_margin_threshold
  if (lhs->passed_margin_threshold != rhs->passed_margin_threshold) {
    return false;
  }
  // accepted
  if (lhs->accepted != rhs->accepted) {
    return false;
  }
  // reject_reason
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->reject_reason), &(rhs->reject_reason)))
  {
    return false;
  }
  // preprocessing_ms
  if (lhs->preprocessing_ms != rhs->preprocessing_ms) {
    return false;
  }
  // inference_ms
  if (lhs->inference_ms != rhs->inference_ms) {
    return false;
  }
  // matching_ms
  if (lhs->matching_ms != rhs->matching_ms) {
    return false;
  }
  // candidate
  if (!macrobot_interfaces__msg__DepthCandidate__are_equal(
      &(lhs->candidate), &(rhs->candidate)))
  {
    return false;
  }
  // crop_roi
  if (!sensor_msgs__msg__RegionOfInterest__are_equal(
      &(lhs->crop_roi), &(rhs->crop_roi)))
  {
    return false;
  }
  return true;
}

bool
macrobot_interfaces__msg__EmbeddingRetrievalResult__copy(
  const macrobot_interfaces__msg__EmbeddingRetrievalResult * input,
  macrobot_interfaces__msg__EmbeddingRetrievalResult * output)
{
  if (!input || !output) {
    return false;
  }
  // proposal_header
  if (!std_msgs__msg__Header__copy(
      &(input->proposal_header), &(output->proposal_header)))
  {
    return false;
  }
  // image_header
  if (!std_msgs__msg__Header__copy(
      &(input->image_header), &(output->image_header)))
  {
    return false;
  }
  // candidate_id
  output->candidate_id = input->candidate_id;
  // crop_index
  output->crop_index = input->crop_index;
  // frame_crop_count
  output->frame_crop_count = input->frame_crop_count;
  // target_object
  if (!rosidl_runtime_c__String__copy(
      &(input->target_object), &(output->target_object)))
  {
    return false;
  }
  // model_id
  if (!rosidl_runtime_c__String__copy(
      &(input->model_id), &(output->model_id)))
  {
    return false;
  }
  // pooling
  if (!rosidl_runtime_c__String__copy(
      &(input->pooling), &(output->pooling)))
  {
    return false;
  }
  // device
  if (!rosidl_runtime_c__String__copy(
      &(input->device), &(output->device)))
  {
    return false;
  }
  // embedding_dim
  output->embedding_dim = input->embedding_dim;
  // positive_bank_available
  output->positive_bank_available = input->positive_bank_available;
  // positive_reference_count
  output->positive_reference_count = input->positive_reference_count;
  // negative_bank_available
  output->negative_bank_available = input->negative_bank_available;
  // negative_reference_count
  output->negative_reference_count = input->negative_reference_count;
  // foreground_mask_used
  output->foreground_mask_used = input->foreground_mask_used;
  // objectness_score
  output->objectness_score = input->objectness_score;
  // target_hint_score
  output->target_hint_score = input->target_hint_score;
  // positive_similarity
  output->positive_similarity = input->positive_similarity;
  // best_positive_similarity
  output->best_positive_similarity = input->best_positive_similarity;
  // negative_similarity
  output->negative_similarity = input->negative_similarity;
  // best_negative_similarity
  output->best_negative_similarity = input->best_negative_similarity;
  // margin
  output->margin = input->margin;
  // best_positive_path
  if (!rosidl_runtime_c__String__copy(
      &(input->best_positive_path), &(output->best_positive_path)))
  {
    return false;
  }
  // best_negative_path
  if (!rosidl_runtime_c__String__copy(
      &(input->best_negative_path), &(output->best_negative_path)))
  {
    return false;
  }
  // top_positive_paths
  if (!rosidl_runtime_c__String__Sequence__copy(
      &(input->top_positive_paths), &(output->top_positive_paths)))
  {
    return false;
  }
  // top_positive_scores
  if (!rosidl_runtime_c__float__Sequence__copy(
      &(input->top_positive_scores), &(output->top_positive_scores)))
  {
    return false;
  }
  // top_negative_paths
  if (!rosidl_runtime_c__String__Sequence__copy(
      &(input->top_negative_paths), &(output->top_negative_paths)))
  {
    return false;
  }
  // top_negative_scores
  if (!rosidl_runtime_c__float__Sequence__copy(
      &(input->top_negative_scores), &(output->top_negative_scores)))
  {
    return false;
  }
  // thresholds_enforced
  output->thresholds_enforced = input->thresholds_enforced;
  // passed_positive_threshold
  output->passed_positive_threshold = input->passed_positive_threshold;
  // passed_margin_threshold
  output->passed_margin_threshold = input->passed_margin_threshold;
  // accepted
  output->accepted = input->accepted;
  // reject_reason
  if (!rosidl_runtime_c__String__copy(
      &(input->reject_reason), &(output->reject_reason)))
  {
    return false;
  }
  // preprocessing_ms
  output->preprocessing_ms = input->preprocessing_ms;
  // inference_ms
  output->inference_ms = input->inference_ms;
  // matching_ms
  output->matching_ms = input->matching_ms;
  // candidate
  if (!macrobot_interfaces__msg__DepthCandidate__copy(
      &(input->candidate), &(output->candidate)))
  {
    return false;
  }
  // crop_roi
  if (!sensor_msgs__msg__RegionOfInterest__copy(
      &(input->crop_roi), &(output->crop_roi)))
  {
    return false;
  }
  return true;
}

macrobot_interfaces__msg__EmbeddingRetrievalResult *
macrobot_interfaces__msg__EmbeddingRetrievalResult__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__EmbeddingRetrievalResult * msg = (macrobot_interfaces__msg__EmbeddingRetrievalResult *)allocator.allocate(sizeof(macrobot_interfaces__msg__EmbeddingRetrievalResult), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(macrobot_interfaces__msg__EmbeddingRetrievalResult));
  bool success = macrobot_interfaces__msg__EmbeddingRetrievalResult__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
macrobot_interfaces__msg__EmbeddingRetrievalResult__destroy(macrobot_interfaces__msg__EmbeddingRetrievalResult * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__init(macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__EmbeddingRetrievalResult * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(macrobot_interfaces__msg__EmbeddingRetrievalResult)) {
      return false;
    }
    data = (macrobot_interfaces__msg__EmbeddingRetrievalResult *)allocator.zero_allocate(size, sizeof(macrobot_interfaces__msg__EmbeddingRetrievalResult), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = macrobot_interfaces__msg__EmbeddingRetrievalResult__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__fini(macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence *
macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence * array = (macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence *)allocator.allocate(sizeof(macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__destroy(macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__are_equal(const macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence * lhs, const macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!macrobot_interfaces__msg__EmbeddingRetrievalResult__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__copy(
  const macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence * input,
  macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(macrobot_interfaces__msg__EmbeddingRetrievalResult)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(macrobot_interfaces__msg__EmbeddingRetrievalResult);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    macrobot_interfaces__msg__EmbeddingRetrievalResult * data =
      (macrobot_interfaces__msg__EmbeddingRetrievalResult *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!macrobot_interfaces__msg__EmbeddingRetrievalResult__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!macrobot_interfaces__msg__EmbeddingRetrievalResult__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
