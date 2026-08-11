// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from macrobot_interfaces:msg/TemporalConfirmationResult.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/temporal_confirmation_result__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `target_object`
// Member `state`
// Member `event`
// Member `suggested_turn`
#include "rosidl_runtime_c/string_functions.h"
// Member `roi`
#include "sensor_msgs/msg/detail/region_of_interest__functions.h"
// Member `latest_result`
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__functions.h"

bool
macrobot_interfaces__msg__TemporalConfirmationResult__init(macrobot_interfaces__msg__TemporalConfirmationResult * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    macrobot_interfaces__msg__TemporalConfirmationResult__fini(msg);
    return false;
  }
  // target_object
  if (!rosidl_runtime_c__String__init(&msg->target_object)) {
    macrobot_interfaces__msg__TemporalConfirmationResult__fini(msg);
    return false;
  }
  // track_id
  // frame_index
  // state
  if (!rosidl_runtime_c__String__init(&msg->state)) {
    macrobot_interfaces__msg__TemporalConfirmationResult__fini(msg);
    return false;
  }
  // event
  if (!rosidl_runtime_c__String__init(&msg->event)) {
    macrobot_interfaces__msg__TemporalConfirmationResult__fini(msg);
    return false;
  }
  // confirmed
  // track_age_frames
  // window_size
  // required_hits
  // samples_in_window
  // matched_frames_in_window
  // hits_in_window
  // misses_in_window
  // consecutive_hits
  // consecutive_misses
  // hit_ratio
  // temporal_score
  // stability_score
  // mean_positive_similarity
  // mean_negative_similarity
  // mean_margin
  // min_margin_in_window
  // mean_objectness_score
  // roi
  if (!sensor_msgs__msg__RegionOfInterest__init(&msg->roi)) {
    macrobot_interfaces__msg__TemporalConfirmationResult__fini(msg);
    return false;
  }
  // center_x
  // center_y
  // depth_m
  // center_std_px
  // depth_std_m
  // horizontal_error_norm
  // suggested_turn
  if (!rosidl_runtime_c__String__init(&msg->suggested_turn)) {
    macrobot_interfaces__msg__TemporalConfirmationResult__fini(msg);
    return false;
  }
  // latest_result
  if (!macrobot_interfaces__msg__EmbeddingRetrievalResult__init(&msg->latest_result)) {
    macrobot_interfaces__msg__TemporalConfirmationResult__fini(msg);
    return false;
  }
  return true;
}

void
macrobot_interfaces__msg__TemporalConfirmationResult__fini(macrobot_interfaces__msg__TemporalConfirmationResult * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // target_object
  rosidl_runtime_c__String__fini(&msg->target_object);
  // track_id
  // frame_index
  // state
  rosidl_runtime_c__String__fini(&msg->state);
  // event
  rosidl_runtime_c__String__fini(&msg->event);
  // confirmed
  // track_age_frames
  // window_size
  // required_hits
  // samples_in_window
  // matched_frames_in_window
  // hits_in_window
  // misses_in_window
  // consecutive_hits
  // consecutive_misses
  // hit_ratio
  // temporal_score
  // stability_score
  // mean_positive_similarity
  // mean_negative_similarity
  // mean_margin
  // min_margin_in_window
  // mean_objectness_score
  // roi
  sensor_msgs__msg__RegionOfInterest__fini(&msg->roi);
  // center_x
  // center_y
  // depth_m
  // center_std_px
  // depth_std_m
  // horizontal_error_norm
  // suggested_turn
  rosidl_runtime_c__String__fini(&msg->suggested_turn);
  // latest_result
  macrobot_interfaces__msg__EmbeddingRetrievalResult__fini(&msg->latest_result);
}

bool
macrobot_interfaces__msg__TemporalConfirmationResult__are_equal(const macrobot_interfaces__msg__TemporalConfirmationResult * lhs, const macrobot_interfaces__msg__TemporalConfirmationResult * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // target_object
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->target_object), &(rhs->target_object)))
  {
    return false;
  }
  // track_id
  if (lhs->track_id != rhs->track_id) {
    return false;
  }
  // frame_index
  if (lhs->frame_index != rhs->frame_index) {
    return false;
  }
  // state
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->state), &(rhs->state)))
  {
    return false;
  }
  // event
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->event), &(rhs->event)))
  {
    return false;
  }
  // confirmed
  if (lhs->confirmed != rhs->confirmed) {
    return false;
  }
  // track_age_frames
  if (lhs->track_age_frames != rhs->track_age_frames) {
    return false;
  }
  // window_size
  if (lhs->window_size != rhs->window_size) {
    return false;
  }
  // required_hits
  if (lhs->required_hits != rhs->required_hits) {
    return false;
  }
  // samples_in_window
  if (lhs->samples_in_window != rhs->samples_in_window) {
    return false;
  }
  // matched_frames_in_window
  if (lhs->matched_frames_in_window != rhs->matched_frames_in_window) {
    return false;
  }
  // hits_in_window
  if (lhs->hits_in_window != rhs->hits_in_window) {
    return false;
  }
  // misses_in_window
  if (lhs->misses_in_window != rhs->misses_in_window) {
    return false;
  }
  // consecutive_hits
  if (lhs->consecutive_hits != rhs->consecutive_hits) {
    return false;
  }
  // consecutive_misses
  if (lhs->consecutive_misses != rhs->consecutive_misses) {
    return false;
  }
  // hit_ratio
  if (lhs->hit_ratio != rhs->hit_ratio) {
    return false;
  }
  // temporal_score
  if (lhs->temporal_score != rhs->temporal_score) {
    return false;
  }
  // stability_score
  if (lhs->stability_score != rhs->stability_score) {
    return false;
  }
  // mean_positive_similarity
  if (lhs->mean_positive_similarity != rhs->mean_positive_similarity) {
    return false;
  }
  // mean_negative_similarity
  if (lhs->mean_negative_similarity != rhs->mean_negative_similarity) {
    return false;
  }
  // mean_margin
  if (lhs->mean_margin != rhs->mean_margin) {
    return false;
  }
  // min_margin_in_window
  if (lhs->min_margin_in_window != rhs->min_margin_in_window) {
    return false;
  }
  // mean_objectness_score
  if (lhs->mean_objectness_score != rhs->mean_objectness_score) {
    return false;
  }
  // roi
  if (!sensor_msgs__msg__RegionOfInterest__are_equal(
      &(lhs->roi), &(rhs->roi)))
  {
    return false;
  }
  // center_x
  if (lhs->center_x != rhs->center_x) {
    return false;
  }
  // center_y
  if (lhs->center_y != rhs->center_y) {
    return false;
  }
  // depth_m
  if (lhs->depth_m != rhs->depth_m) {
    return false;
  }
  // center_std_px
  if (lhs->center_std_px != rhs->center_std_px) {
    return false;
  }
  // depth_std_m
  if (lhs->depth_std_m != rhs->depth_std_m) {
    return false;
  }
  // horizontal_error_norm
  if (lhs->horizontal_error_norm != rhs->horizontal_error_norm) {
    return false;
  }
  // suggested_turn
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->suggested_turn), &(rhs->suggested_turn)))
  {
    return false;
  }
  // latest_result
  if (!macrobot_interfaces__msg__EmbeddingRetrievalResult__are_equal(
      &(lhs->latest_result), &(rhs->latest_result)))
  {
    return false;
  }
  return true;
}

bool
macrobot_interfaces__msg__TemporalConfirmationResult__copy(
  const macrobot_interfaces__msg__TemporalConfirmationResult * input,
  macrobot_interfaces__msg__TemporalConfirmationResult * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // target_object
  if (!rosidl_runtime_c__String__copy(
      &(input->target_object), &(output->target_object)))
  {
    return false;
  }
  // track_id
  output->track_id = input->track_id;
  // frame_index
  output->frame_index = input->frame_index;
  // state
  if (!rosidl_runtime_c__String__copy(
      &(input->state), &(output->state)))
  {
    return false;
  }
  // event
  if (!rosidl_runtime_c__String__copy(
      &(input->event), &(output->event)))
  {
    return false;
  }
  // confirmed
  output->confirmed = input->confirmed;
  // track_age_frames
  output->track_age_frames = input->track_age_frames;
  // window_size
  output->window_size = input->window_size;
  // required_hits
  output->required_hits = input->required_hits;
  // samples_in_window
  output->samples_in_window = input->samples_in_window;
  // matched_frames_in_window
  output->matched_frames_in_window = input->matched_frames_in_window;
  // hits_in_window
  output->hits_in_window = input->hits_in_window;
  // misses_in_window
  output->misses_in_window = input->misses_in_window;
  // consecutive_hits
  output->consecutive_hits = input->consecutive_hits;
  // consecutive_misses
  output->consecutive_misses = input->consecutive_misses;
  // hit_ratio
  output->hit_ratio = input->hit_ratio;
  // temporal_score
  output->temporal_score = input->temporal_score;
  // stability_score
  output->stability_score = input->stability_score;
  // mean_positive_similarity
  output->mean_positive_similarity = input->mean_positive_similarity;
  // mean_negative_similarity
  output->mean_negative_similarity = input->mean_negative_similarity;
  // mean_margin
  output->mean_margin = input->mean_margin;
  // min_margin_in_window
  output->min_margin_in_window = input->min_margin_in_window;
  // mean_objectness_score
  output->mean_objectness_score = input->mean_objectness_score;
  // roi
  if (!sensor_msgs__msg__RegionOfInterest__copy(
      &(input->roi), &(output->roi)))
  {
    return false;
  }
  // center_x
  output->center_x = input->center_x;
  // center_y
  output->center_y = input->center_y;
  // depth_m
  output->depth_m = input->depth_m;
  // center_std_px
  output->center_std_px = input->center_std_px;
  // depth_std_m
  output->depth_std_m = input->depth_std_m;
  // horizontal_error_norm
  output->horizontal_error_norm = input->horizontal_error_norm;
  // suggested_turn
  if (!rosidl_runtime_c__String__copy(
      &(input->suggested_turn), &(output->suggested_turn)))
  {
    return false;
  }
  // latest_result
  if (!macrobot_interfaces__msg__EmbeddingRetrievalResult__copy(
      &(input->latest_result), &(output->latest_result)))
  {
    return false;
  }
  return true;
}

macrobot_interfaces__msg__TemporalConfirmationResult *
macrobot_interfaces__msg__TemporalConfirmationResult__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__TemporalConfirmationResult * msg = (macrobot_interfaces__msg__TemporalConfirmationResult *)allocator.allocate(sizeof(macrobot_interfaces__msg__TemporalConfirmationResult), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(macrobot_interfaces__msg__TemporalConfirmationResult));
  bool success = macrobot_interfaces__msg__TemporalConfirmationResult__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
macrobot_interfaces__msg__TemporalConfirmationResult__destroy(macrobot_interfaces__msg__TemporalConfirmationResult * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    macrobot_interfaces__msg__TemporalConfirmationResult__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__init(macrobot_interfaces__msg__TemporalConfirmationResult__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__TemporalConfirmationResult * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(macrobot_interfaces__msg__TemporalConfirmationResult)) {
      return false;
    }
    data = (macrobot_interfaces__msg__TemporalConfirmationResult *)allocator.zero_allocate(size, sizeof(macrobot_interfaces__msg__TemporalConfirmationResult), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = macrobot_interfaces__msg__TemporalConfirmationResult__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        macrobot_interfaces__msg__TemporalConfirmationResult__fini(&data[i - 1]);
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
macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__fini(macrobot_interfaces__msg__TemporalConfirmationResult__Sequence * array)
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
      macrobot_interfaces__msg__TemporalConfirmationResult__fini(&array->data[i]);
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

macrobot_interfaces__msg__TemporalConfirmationResult__Sequence *
macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__TemporalConfirmationResult__Sequence * array = (macrobot_interfaces__msg__TemporalConfirmationResult__Sequence *)allocator.allocate(sizeof(macrobot_interfaces__msg__TemporalConfirmationResult__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__destroy(macrobot_interfaces__msg__TemporalConfirmationResult__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__are_equal(const macrobot_interfaces__msg__TemporalConfirmationResult__Sequence * lhs, const macrobot_interfaces__msg__TemporalConfirmationResult__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!macrobot_interfaces__msg__TemporalConfirmationResult__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__copy(
  const macrobot_interfaces__msg__TemporalConfirmationResult__Sequence * input,
  macrobot_interfaces__msg__TemporalConfirmationResult__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(macrobot_interfaces__msg__TemporalConfirmationResult)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(macrobot_interfaces__msg__TemporalConfirmationResult);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    macrobot_interfaces__msg__TemporalConfirmationResult * data =
      (macrobot_interfaces__msg__TemporalConfirmationResult *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!macrobot_interfaces__msg__TemporalConfirmationResult__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          macrobot_interfaces__msg__TemporalConfirmationResult__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!macrobot_interfaces__msg__TemporalConfirmationResult__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
