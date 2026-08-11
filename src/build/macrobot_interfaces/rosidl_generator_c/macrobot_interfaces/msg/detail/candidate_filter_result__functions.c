// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from macrobot_interfaces:msg/CandidateFilterResult.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/candidate_filter_result__functions.h"

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
// Member `reject_stage`
// Member `reject_reason`
#include "rosidl_runtime_c/string_functions.h"
// Member `candidate`
#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"
// Member `crop_roi`
#include "sensor_msgs/msg/detail/region_of_interest__functions.h"

bool
macrobot_interfaces__msg__CandidateFilterResult__init(macrobot_interfaces__msg__CandidateFilterResult * msg)
{
  if (!msg) {
    return false;
  }
  // proposal_header
  if (!std_msgs__msg__Header__init(&msg->proposal_header)) {
    macrobot_interfaces__msg__CandidateFilterResult__fini(msg);
    return false;
  }
  // image_header
  if (!std_msgs__msg__Header__init(&msg->image_header)) {
    macrobot_interfaces__msg__CandidateFilterResult__fini(msg);
    return false;
  }
  // candidate_id
  // crop_index
  // frame_crop_count
  // target_object
  if (!rosidl_runtime_c__String__init(&msg->target_object)) {
    macrobot_interfaces__msg__CandidateFilterResult__fini(msg);
    return false;
  }
  // reference_profile_available
  // reference_image_count
  // camera_info_available
  // plane_found
  // foreground_height_valid
  // foreground_mask_available
  // accepted
  // reject_stage
  if (!rosidl_runtime_c__String__init(&msg->reject_stage)) {
    macrobot_interfaces__msg__CandidateFilterResult__fini(msg);
    return false;
  }
  // reject_reason
  if (!rosidl_runtime_c__String__init(&msg->reject_reason)) {
    macrobot_interfaces__msg__CandidateFilterResult__fini(msg);
    return false;
  }
  // objectness_score
  // target_hint_score
  // filter_score
  // depth_score
  // quality_score
  // color_score
  // shape_score
  // physical_size_score
  // sharpness
  // mean_brightness
  // dark_ratio
  // bright_clip_ratio
  // edge_density
  // mask_fill_ratio
  // mask_solidity
  // color_similarity
  // aspect_ratio
  // estimated_width_m
  // estimated_height_m
  // sync_offset_abs_sec
  // candidate
  if (!macrobot_interfaces__msg__DepthCandidate__init(&msg->candidate)) {
    macrobot_interfaces__msg__CandidateFilterResult__fini(msg);
    return false;
  }
  // crop_roi
  if (!sensor_msgs__msg__RegionOfInterest__init(&msg->crop_roi)) {
    macrobot_interfaces__msg__CandidateFilterResult__fini(msg);
    return false;
  }
  return true;
}

void
macrobot_interfaces__msg__CandidateFilterResult__fini(macrobot_interfaces__msg__CandidateFilterResult * msg)
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
  // reference_profile_available
  // reference_image_count
  // camera_info_available
  // plane_found
  // foreground_height_valid
  // foreground_mask_available
  // accepted
  // reject_stage
  rosidl_runtime_c__String__fini(&msg->reject_stage);
  // reject_reason
  rosidl_runtime_c__String__fini(&msg->reject_reason);
  // objectness_score
  // target_hint_score
  // filter_score
  // depth_score
  // quality_score
  // color_score
  // shape_score
  // physical_size_score
  // sharpness
  // mean_brightness
  // dark_ratio
  // bright_clip_ratio
  // edge_density
  // mask_fill_ratio
  // mask_solidity
  // color_similarity
  // aspect_ratio
  // estimated_width_m
  // estimated_height_m
  // sync_offset_abs_sec
  // candidate
  macrobot_interfaces__msg__DepthCandidate__fini(&msg->candidate);
  // crop_roi
  sensor_msgs__msg__RegionOfInterest__fini(&msg->crop_roi);
}

bool
macrobot_interfaces__msg__CandidateFilterResult__are_equal(const macrobot_interfaces__msg__CandidateFilterResult * lhs, const macrobot_interfaces__msg__CandidateFilterResult * rhs)
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
  // reference_profile_available
  if (lhs->reference_profile_available != rhs->reference_profile_available) {
    return false;
  }
  // reference_image_count
  if (lhs->reference_image_count != rhs->reference_image_count) {
    return false;
  }
  // camera_info_available
  if (lhs->camera_info_available != rhs->camera_info_available) {
    return false;
  }
  // plane_found
  if (lhs->plane_found != rhs->plane_found) {
    return false;
  }
  // foreground_height_valid
  if (lhs->foreground_height_valid != rhs->foreground_height_valid) {
    return false;
  }
  // foreground_mask_available
  if (lhs->foreground_mask_available != rhs->foreground_mask_available) {
    return false;
  }
  // accepted
  if (lhs->accepted != rhs->accepted) {
    return false;
  }
  // reject_stage
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->reject_stage), &(rhs->reject_stage)))
  {
    return false;
  }
  // reject_reason
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->reject_reason), &(rhs->reject_reason)))
  {
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
  // filter_score
  if (lhs->filter_score != rhs->filter_score) {
    return false;
  }
  // depth_score
  if (lhs->depth_score != rhs->depth_score) {
    return false;
  }
  // quality_score
  if (lhs->quality_score != rhs->quality_score) {
    return false;
  }
  // color_score
  if (lhs->color_score != rhs->color_score) {
    return false;
  }
  // shape_score
  if (lhs->shape_score != rhs->shape_score) {
    return false;
  }
  // physical_size_score
  if (lhs->physical_size_score != rhs->physical_size_score) {
    return false;
  }
  // sharpness
  if (lhs->sharpness != rhs->sharpness) {
    return false;
  }
  // mean_brightness
  if (lhs->mean_brightness != rhs->mean_brightness) {
    return false;
  }
  // dark_ratio
  if (lhs->dark_ratio != rhs->dark_ratio) {
    return false;
  }
  // bright_clip_ratio
  if (lhs->bright_clip_ratio != rhs->bright_clip_ratio) {
    return false;
  }
  // edge_density
  if (lhs->edge_density != rhs->edge_density) {
    return false;
  }
  // mask_fill_ratio
  if (lhs->mask_fill_ratio != rhs->mask_fill_ratio) {
    return false;
  }
  // mask_solidity
  if (lhs->mask_solidity != rhs->mask_solidity) {
    return false;
  }
  // color_similarity
  if (lhs->color_similarity != rhs->color_similarity) {
    return false;
  }
  // aspect_ratio
  if (lhs->aspect_ratio != rhs->aspect_ratio) {
    return false;
  }
  // estimated_width_m
  if (lhs->estimated_width_m != rhs->estimated_width_m) {
    return false;
  }
  // estimated_height_m
  if (lhs->estimated_height_m != rhs->estimated_height_m) {
    return false;
  }
  // sync_offset_abs_sec
  if (lhs->sync_offset_abs_sec != rhs->sync_offset_abs_sec) {
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
macrobot_interfaces__msg__CandidateFilterResult__copy(
  const macrobot_interfaces__msg__CandidateFilterResult * input,
  macrobot_interfaces__msg__CandidateFilterResult * output)
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
  // reference_profile_available
  output->reference_profile_available = input->reference_profile_available;
  // reference_image_count
  output->reference_image_count = input->reference_image_count;
  // camera_info_available
  output->camera_info_available = input->camera_info_available;
  // plane_found
  output->plane_found = input->plane_found;
  // foreground_height_valid
  output->foreground_height_valid = input->foreground_height_valid;
  // foreground_mask_available
  output->foreground_mask_available = input->foreground_mask_available;
  // accepted
  output->accepted = input->accepted;
  // reject_stage
  if (!rosidl_runtime_c__String__copy(
      &(input->reject_stage), &(output->reject_stage)))
  {
    return false;
  }
  // reject_reason
  if (!rosidl_runtime_c__String__copy(
      &(input->reject_reason), &(output->reject_reason)))
  {
    return false;
  }
  // objectness_score
  output->objectness_score = input->objectness_score;
  // target_hint_score
  output->target_hint_score = input->target_hint_score;
  // filter_score
  output->filter_score = input->filter_score;
  // depth_score
  output->depth_score = input->depth_score;
  // quality_score
  output->quality_score = input->quality_score;
  // color_score
  output->color_score = input->color_score;
  // shape_score
  output->shape_score = input->shape_score;
  // physical_size_score
  output->physical_size_score = input->physical_size_score;
  // sharpness
  output->sharpness = input->sharpness;
  // mean_brightness
  output->mean_brightness = input->mean_brightness;
  // dark_ratio
  output->dark_ratio = input->dark_ratio;
  // bright_clip_ratio
  output->bright_clip_ratio = input->bright_clip_ratio;
  // edge_density
  output->edge_density = input->edge_density;
  // mask_fill_ratio
  output->mask_fill_ratio = input->mask_fill_ratio;
  // mask_solidity
  output->mask_solidity = input->mask_solidity;
  // color_similarity
  output->color_similarity = input->color_similarity;
  // aspect_ratio
  output->aspect_ratio = input->aspect_ratio;
  // estimated_width_m
  output->estimated_width_m = input->estimated_width_m;
  // estimated_height_m
  output->estimated_height_m = input->estimated_height_m;
  // sync_offset_abs_sec
  output->sync_offset_abs_sec = input->sync_offset_abs_sec;
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

macrobot_interfaces__msg__CandidateFilterResult *
macrobot_interfaces__msg__CandidateFilterResult__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__CandidateFilterResult * msg = (macrobot_interfaces__msg__CandidateFilterResult *)allocator.allocate(sizeof(macrobot_interfaces__msg__CandidateFilterResult), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(macrobot_interfaces__msg__CandidateFilterResult));
  bool success = macrobot_interfaces__msg__CandidateFilterResult__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
macrobot_interfaces__msg__CandidateFilterResult__destroy(macrobot_interfaces__msg__CandidateFilterResult * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    macrobot_interfaces__msg__CandidateFilterResult__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
macrobot_interfaces__msg__CandidateFilterResult__Sequence__init(macrobot_interfaces__msg__CandidateFilterResult__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__CandidateFilterResult * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(macrobot_interfaces__msg__CandidateFilterResult)) {
      return false;
    }
    data = (macrobot_interfaces__msg__CandidateFilterResult *)allocator.zero_allocate(size, sizeof(macrobot_interfaces__msg__CandidateFilterResult), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = macrobot_interfaces__msg__CandidateFilterResult__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        macrobot_interfaces__msg__CandidateFilterResult__fini(&data[i - 1]);
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
macrobot_interfaces__msg__CandidateFilterResult__Sequence__fini(macrobot_interfaces__msg__CandidateFilterResult__Sequence * array)
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
      macrobot_interfaces__msg__CandidateFilterResult__fini(&array->data[i]);
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

macrobot_interfaces__msg__CandidateFilterResult__Sequence *
macrobot_interfaces__msg__CandidateFilterResult__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__CandidateFilterResult__Sequence * array = (macrobot_interfaces__msg__CandidateFilterResult__Sequence *)allocator.allocate(sizeof(macrobot_interfaces__msg__CandidateFilterResult__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = macrobot_interfaces__msg__CandidateFilterResult__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
macrobot_interfaces__msg__CandidateFilterResult__Sequence__destroy(macrobot_interfaces__msg__CandidateFilterResult__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    macrobot_interfaces__msg__CandidateFilterResult__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
macrobot_interfaces__msg__CandidateFilterResult__Sequence__are_equal(const macrobot_interfaces__msg__CandidateFilterResult__Sequence * lhs, const macrobot_interfaces__msg__CandidateFilterResult__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!macrobot_interfaces__msg__CandidateFilterResult__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
macrobot_interfaces__msg__CandidateFilterResult__Sequence__copy(
  const macrobot_interfaces__msg__CandidateFilterResult__Sequence * input,
  macrobot_interfaces__msg__CandidateFilterResult__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(macrobot_interfaces__msg__CandidateFilterResult)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(macrobot_interfaces__msg__CandidateFilterResult);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    macrobot_interfaces__msg__CandidateFilterResult * data =
      (macrobot_interfaces__msg__CandidateFilterResult *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!macrobot_interfaces__msg__CandidateFilterResult__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          macrobot_interfaces__msg__CandidateFilterResult__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!macrobot_interfaces__msg__CandidateFilterResult__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
