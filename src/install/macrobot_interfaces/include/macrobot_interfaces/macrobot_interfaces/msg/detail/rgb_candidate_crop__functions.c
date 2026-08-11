// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from macrobot_interfaces:msg/RgbCandidateCrop.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `proposal_header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `candidate`
#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"
// Member `crop_roi`
#include "sensor_msgs/msg/detail/region_of_interest__functions.h"
// Member `foreground_mask`
// Member `image`
#include "sensor_msgs/msg/detail/compressed_image__functions.h"

bool
macrobot_interfaces__msg__RgbCandidateCrop__init(macrobot_interfaces__msg__RgbCandidateCrop * msg)
{
  if (!msg) {
    return false;
  }
  // proposal_header
  if (!std_msgs__msg__Header__init(&msg->proposal_header)) {
    macrobot_interfaces__msg__RgbCandidateCrop__fini(msg);
    return false;
  }
  // proposal_image_width
  // proposal_image_height
  // color_image_width
  // color_image_height
  // source_candidate_count
  // frame_crop_count
  // crop_index
  // candidate
  if (!macrobot_interfaces__msg__DepthCandidate__init(&msg->candidate)) {
    macrobot_interfaces__msg__RgbCandidateCrop__fini(msg);
    return false;
  }
  // crop_roi
  if (!sensor_msgs__msg__RegionOfInterest__init(&msg->crop_roi)) {
    macrobot_interfaces__msg__RgbCandidateCrop__fini(msg);
    return false;
  }
  // color_time_offset_sec
  // plane_found
  // foreground_mask_available
  // mask_fill_ratio
  // foreground_mask
  if (!sensor_msgs__msg__CompressedImage__init(&msg->foreground_mask)) {
    macrobot_interfaces__msg__RgbCandidateCrop__fini(msg);
    return false;
  }
  // encoded_width
  // encoded_height
  // jpeg_size_bytes
  // jpeg_quality
  // size_limit_met
  // image
  if (!sensor_msgs__msg__CompressedImage__init(&msg->image)) {
    macrobot_interfaces__msg__RgbCandidateCrop__fini(msg);
    return false;
  }
  return true;
}

void
macrobot_interfaces__msg__RgbCandidateCrop__fini(macrobot_interfaces__msg__RgbCandidateCrop * msg)
{
  if (!msg) {
    return;
  }
  // proposal_header
  std_msgs__msg__Header__fini(&msg->proposal_header);
  // proposal_image_width
  // proposal_image_height
  // color_image_width
  // color_image_height
  // source_candidate_count
  // frame_crop_count
  // crop_index
  // candidate
  macrobot_interfaces__msg__DepthCandidate__fini(&msg->candidate);
  // crop_roi
  sensor_msgs__msg__RegionOfInterest__fini(&msg->crop_roi);
  // color_time_offset_sec
  // plane_found
  // foreground_mask_available
  // mask_fill_ratio
  // foreground_mask
  sensor_msgs__msg__CompressedImage__fini(&msg->foreground_mask);
  // encoded_width
  // encoded_height
  // jpeg_size_bytes
  // jpeg_quality
  // size_limit_met
  // image
  sensor_msgs__msg__CompressedImage__fini(&msg->image);
}

bool
macrobot_interfaces__msg__RgbCandidateCrop__are_equal(const macrobot_interfaces__msg__RgbCandidateCrop * lhs, const macrobot_interfaces__msg__RgbCandidateCrop * rhs)
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
  // proposal_image_width
  if (lhs->proposal_image_width != rhs->proposal_image_width) {
    return false;
  }
  // proposal_image_height
  if (lhs->proposal_image_height != rhs->proposal_image_height) {
    return false;
  }
  // color_image_width
  if (lhs->color_image_width != rhs->color_image_width) {
    return false;
  }
  // color_image_height
  if (lhs->color_image_height != rhs->color_image_height) {
    return false;
  }
  // source_candidate_count
  if (lhs->source_candidate_count != rhs->source_candidate_count) {
    return false;
  }
  // frame_crop_count
  if (lhs->frame_crop_count != rhs->frame_crop_count) {
    return false;
  }
  // crop_index
  if (lhs->crop_index != rhs->crop_index) {
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
  // color_time_offset_sec
  if (lhs->color_time_offset_sec != rhs->color_time_offset_sec) {
    return false;
  }
  // plane_found
  if (lhs->plane_found != rhs->plane_found) {
    return false;
  }
  // foreground_mask_available
  if (lhs->foreground_mask_available != rhs->foreground_mask_available) {
    return false;
  }
  // mask_fill_ratio
  if (lhs->mask_fill_ratio != rhs->mask_fill_ratio) {
    return false;
  }
  // foreground_mask
  if (!sensor_msgs__msg__CompressedImage__are_equal(
      &(lhs->foreground_mask), &(rhs->foreground_mask)))
  {
    return false;
  }
  // encoded_width
  if (lhs->encoded_width != rhs->encoded_width) {
    return false;
  }
  // encoded_height
  if (lhs->encoded_height != rhs->encoded_height) {
    return false;
  }
  // jpeg_size_bytes
  if (lhs->jpeg_size_bytes != rhs->jpeg_size_bytes) {
    return false;
  }
  // jpeg_quality
  if (lhs->jpeg_quality != rhs->jpeg_quality) {
    return false;
  }
  // size_limit_met
  if (lhs->size_limit_met != rhs->size_limit_met) {
    return false;
  }
  // image
  if (!sensor_msgs__msg__CompressedImage__are_equal(
      &(lhs->image), &(rhs->image)))
  {
    return false;
  }
  return true;
}

bool
macrobot_interfaces__msg__RgbCandidateCrop__copy(
  const macrobot_interfaces__msg__RgbCandidateCrop * input,
  macrobot_interfaces__msg__RgbCandidateCrop * output)
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
  // proposal_image_width
  output->proposal_image_width = input->proposal_image_width;
  // proposal_image_height
  output->proposal_image_height = input->proposal_image_height;
  // color_image_width
  output->color_image_width = input->color_image_width;
  // color_image_height
  output->color_image_height = input->color_image_height;
  // source_candidate_count
  output->source_candidate_count = input->source_candidate_count;
  // frame_crop_count
  output->frame_crop_count = input->frame_crop_count;
  // crop_index
  output->crop_index = input->crop_index;
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
  // color_time_offset_sec
  output->color_time_offset_sec = input->color_time_offset_sec;
  // plane_found
  output->plane_found = input->plane_found;
  // foreground_mask_available
  output->foreground_mask_available = input->foreground_mask_available;
  // mask_fill_ratio
  output->mask_fill_ratio = input->mask_fill_ratio;
  // foreground_mask
  if (!sensor_msgs__msg__CompressedImage__copy(
      &(input->foreground_mask), &(output->foreground_mask)))
  {
    return false;
  }
  // encoded_width
  output->encoded_width = input->encoded_width;
  // encoded_height
  output->encoded_height = input->encoded_height;
  // jpeg_size_bytes
  output->jpeg_size_bytes = input->jpeg_size_bytes;
  // jpeg_quality
  output->jpeg_quality = input->jpeg_quality;
  // size_limit_met
  output->size_limit_met = input->size_limit_met;
  // image
  if (!sensor_msgs__msg__CompressedImage__copy(
      &(input->image), &(output->image)))
  {
    return false;
  }
  return true;
}

macrobot_interfaces__msg__RgbCandidateCrop *
macrobot_interfaces__msg__RgbCandidateCrop__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__RgbCandidateCrop * msg = (macrobot_interfaces__msg__RgbCandidateCrop *)allocator.allocate(sizeof(macrobot_interfaces__msg__RgbCandidateCrop), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(macrobot_interfaces__msg__RgbCandidateCrop));
  bool success = macrobot_interfaces__msg__RgbCandidateCrop__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
macrobot_interfaces__msg__RgbCandidateCrop__destroy(macrobot_interfaces__msg__RgbCandidateCrop * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    macrobot_interfaces__msg__RgbCandidateCrop__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
macrobot_interfaces__msg__RgbCandidateCrop__Sequence__init(macrobot_interfaces__msg__RgbCandidateCrop__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__RgbCandidateCrop * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(macrobot_interfaces__msg__RgbCandidateCrop)) {
      return false;
    }
    data = (macrobot_interfaces__msg__RgbCandidateCrop *)allocator.zero_allocate(size, sizeof(macrobot_interfaces__msg__RgbCandidateCrop), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = macrobot_interfaces__msg__RgbCandidateCrop__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        macrobot_interfaces__msg__RgbCandidateCrop__fini(&data[i - 1]);
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
macrobot_interfaces__msg__RgbCandidateCrop__Sequence__fini(macrobot_interfaces__msg__RgbCandidateCrop__Sequence * array)
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
      macrobot_interfaces__msg__RgbCandidateCrop__fini(&array->data[i]);
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

macrobot_interfaces__msg__RgbCandidateCrop__Sequence *
macrobot_interfaces__msg__RgbCandidateCrop__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__RgbCandidateCrop__Sequence * array = (macrobot_interfaces__msg__RgbCandidateCrop__Sequence *)allocator.allocate(sizeof(macrobot_interfaces__msg__RgbCandidateCrop__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = macrobot_interfaces__msg__RgbCandidateCrop__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
macrobot_interfaces__msg__RgbCandidateCrop__Sequence__destroy(macrobot_interfaces__msg__RgbCandidateCrop__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    macrobot_interfaces__msg__RgbCandidateCrop__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
macrobot_interfaces__msg__RgbCandidateCrop__Sequence__are_equal(const macrobot_interfaces__msg__RgbCandidateCrop__Sequence * lhs, const macrobot_interfaces__msg__RgbCandidateCrop__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!macrobot_interfaces__msg__RgbCandidateCrop__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
macrobot_interfaces__msg__RgbCandidateCrop__Sequence__copy(
  const macrobot_interfaces__msg__RgbCandidateCrop__Sequence * input,
  macrobot_interfaces__msg__RgbCandidateCrop__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(macrobot_interfaces__msg__RgbCandidateCrop)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(macrobot_interfaces__msg__RgbCandidateCrop);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    macrobot_interfaces__msg__RgbCandidateCrop * data =
      (macrobot_interfaces__msg__RgbCandidateCrop *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!macrobot_interfaces__msg__RgbCandidateCrop__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          macrobot_interfaces__msg__RgbCandidateCrop__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!macrobot_interfaces__msg__RgbCandidateCrop__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
