// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from macrobot_interfaces:msg/DepthCandidateArray.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/depth_candidate_array__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `foreground_mask`
#include "sensor_msgs/msg/detail/compressed_image__functions.h"
// Member `candidates`
#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"

bool
macrobot_interfaces__msg__DepthCandidateArray__init(macrobot_interfaces__msg__DepthCandidateArray * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    macrobot_interfaces__msg__DepthCandidateArray__fini(msg);
    return false;
  }
  // image_width
  // image_height
  // plane_found
  // plane_inlier_ratio
  // plane_coefficients
  // foreground_mask_available
  // foreground_mask
  if (!sensor_msgs__msg__CompressedImage__init(&msg->foreground_mask)) {
    macrobot_interfaces__msg__DepthCandidateArray__fini(msg);
    return false;
  }
  // candidates
  if (!macrobot_interfaces__msg__DepthCandidate__Sequence__init(&msg->candidates, 0)) {
    macrobot_interfaces__msg__DepthCandidateArray__fini(msg);
    return false;
  }
  return true;
}

void
macrobot_interfaces__msg__DepthCandidateArray__fini(macrobot_interfaces__msg__DepthCandidateArray * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // image_width
  // image_height
  // plane_found
  // plane_inlier_ratio
  // plane_coefficients
  // foreground_mask_available
  // foreground_mask
  sensor_msgs__msg__CompressedImage__fini(&msg->foreground_mask);
  // candidates
  macrobot_interfaces__msg__DepthCandidate__Sequence__fini(&msg->candidates);
}

bool
macrobot_interfaces__msg__DepthCandidateArray__are_equal(const macrobot_interfaces__msg__DepthCandidateArray * lhs, const macrobot_interfaces__msg__DepthCandidateArray * rhs)
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
  // image_width
  if (lhs->image_width != rhs->image_width) {
    return false;
  }
  // image_height
  if (lhs->image_height != rhs->image_height) {
    return false;
  }
  // plane_found
  if (lhs->plane_found != rhs->plane_found) {
    return false;
  }
  // plane_inlier_ratio
  if (lhs->plane_inlier_ratio != rhs->plane_inlier_ratio) {
    return false;
  }
  // plane_coefficients
  for (size_t i = 0; i < 4; ++i) {
    if (lhs->plane_coefficients[i] != rhs->plane_coefficients[i]) {
      return false;
    }
  }
  // foreground_mask_available
  if (lhs->foreground_mask_available != rhs->foreground_mask_available) {
    return false;
  }
  // foreground_mask
  if (!sensor_msgs__msg__CompressedImage__are_equal(
      &(lhs->foreground_mask), &(rhs->foreground_mask)))
  {
    return false;
  }
  // candidates
  if (!macrobot_interfaces__msg__DepthCandidate__Sequence__are_equal(
      &(lhs->candidates), &(rhs->candidates)))
  {
    return false;
  }
  return true;
}

bool
macrobot_interfaces__msg__DepthCandidateArray__copy(
  const macrobot_interfaces__msg__DepthCandidateArray * input,
  macrobot_interfaces__msg__DepthCandidateArray * output)
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
  // image_width
  output->image_width = input->image_width;
  // image_height
  output->image_height = input->image_height;
  // plane_found
  output->plane_found = input->plane_found;
  // plane_inlier_ratio
  output->plane_inlier_ratio = input->plane_inlier_ratio;
  // plane_coefficients
  for (size_t i = 0; i < 4; ++i) {
    output->plane_coefficients[i] = input->plane_coefficients[i];
  }
  // foreground_mask_available
  output->foreground_mask_available = input->foreground_mask_available;
  // foreground_mask
  if (!sensor_msgs__msg__CompressedImage__copy(
      &(input->foreground_mask), &(output->foreground_mask)))
  {
    return false;
  }
  // candidates
  if (!macrobot_interfaces__msg__DepthCandidate__Sequence__copy(
      &(input->candidates), &(output->candidates)))
  {
    return false;
  }
  return true;
}

macrobot_interfaces__msg__DepthCandidateArray *
macrobot_interfaces__msg__DepthCandidateArray__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__DepthCandidateArray * msg = (macrobot_interfaces__msg__DepthCandidateArray *)allocator.allocate(sizeof(macrobot_interfaces__msg__DepthCandidateArray), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(macrobot_interfaces__msg__DepthCandidateArray));
  bool success = macrobot_interfaces__msg__DepthCandidateArray__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
macrobot_interfaces__msg__DepthCandidateArray__destroy(macrobot_interfaces__msg__DepthCandidateArray * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    macrobot_interfaces__msg__DepthCandidateArray__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
macrobot_interfaces__msg__DepthCandidateArray__Sequence__init(macrobot_interfaces__msg__DepthCandidateArray__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__DepthCandidateArray * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(macrobot_interfaces__msg__DepthCandidateArray)) {
      return false;
    }
    data = (macrobot_interfaces__msg__DepthCandidateArray *)allocator.zero_allocate(size, sizeof(macrobot_interfaces__msg__DepthCandidateArray), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = macrobot_interfaces__msg__DepthCandidateArray__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        macrobot_interfaces__msg__DepthCandidateArray__fini(&data[i - 1]);
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
macrobot_interfaces__msg__DepthCandidateArray__Sequence__fini(macrobot_interfaces__msg__DepthCandidateArray__Sequence * array)
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
      macrobot_interfaces__msg__DepthCandidateArray__fini(&array->data[i]);
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

macrobot_interfaces__msg__DepthCandidateArray__Sequence *
macrobot_interfaces__msg__DepthCandidateArray__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__DepthCandidateArray__Sequence * array = (macrobot_interfaces__msg__DepthCandidateArray__Sequence *)allocator.allocate(sizeof(macrobot_interfaces__msg__DepthCandidateArray__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = macrobot_interfaces__msg__DepthCandidateArray__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
macrobot_interfaces__msg__DepthCandidateArray__Sequence__destroy(macrobot_interfaces__msg__DepthCandidateArray__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    macrobot_interfaces__msg__DepthCandidateArray__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
macrobot_interfaces__msg__DepthCandidateArray__Sequence__are_equal(const macrobot_interfaces__msg__DepthCandidateArray__Sequence * lhs, const macrobot_interfaces__msg__DepthCandidateArray__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!macrobot_interfaces__msg__DepthCandidateArray__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
macrobot_interfaces__msg__DepthCandidateArray__Sequence__copy(
  const macrobot_interfaces__msg__DepthCandidateArray__Sequence * input,
  macrobot_interfaces__msg__DepthCandidateArray__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(macrobot_interfaces__msg__DepthCandidateArray)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(macrobot_interfaces__msg__DepthCandidateArray);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    macrobot_interfaces__msg__DepthCandidateArray * data =
      (macrobot_interfaces__msg__DepthCandidateArray *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!macrobot_interfaces__msg__DepthCandidateArray__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          macrobot_interfaces__msg__DepthCandidateArray__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!macrobot_interfaces__msg__DepthCandidateArray__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
