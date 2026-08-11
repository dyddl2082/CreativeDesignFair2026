// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from macrobot_interfaces:msg/DepthCandidate.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `roi`
#include "sensor_msgs/msg/detail/region_of_interest__functions.h"

bool
macrobot_interfaces__msg__DepthCandidate__init(macrobot_interfaces__msg__DepthCandidate * msg)
{
  if (!msg) {
    return false;
  }
  // id
  // roi
  if (!sensor_msgs__msg__RegionOfInterest__init(&msg->roi)) {
    macrobot_interfaces__msg__DepthCandidate__fini(msg);
    return false;
  }
  // center_x
  // center_y
  // median_depth_m
  // near_depth_m
  // far_depth_m
  // depth_std_m
  // valid_depth_ratio
  // fill_ratio
  // area_ratio
  // foreground_height_m
  // foreground_height_valid
  // proposal_score
  // touches_border
  return true;
}

void
macrobot_interfaces__msg__DepthCandidate__fini(macrobot_interfaces__msg__DepthCandidate * msg)
{
  if (!msg) {
    return;
  }
  // id
  // roi
  sensor_msgs__msg__RegionOfInterest__fini(&msg->roi);
  // center_x
  // center_y
  // median_depth_m
  // near_depth_m
  // far_depth_m
  // depth_std_m
  // valid_depth_ratio
  // fill_ratio
  // area_ratio
  // foreground_height_m
  // foreground_height_valid
  // proposal_score
  // touches_border
}

bool
macrobot_interfaces__msg__DepthCandidate__are_equal(const macrobot_interfaces__msg__DepthCandidate * lhs, const macrobot_interfaces__msg__DepthCandidate * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // id
  if (lhs->id != rhs->id) {
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
  // median_depth_m
  if (lhs->median_depth_m != rhs->median_depth_m) {
    return false;
  }
  // near_depth_m
  if (lhs->near_depth_m != rhs->near_depth_m) {
    return false;
  }
  // far_depth_m
  if (lhs->far_depth_m != rhs->far_depth_m) {
    return false;
  }
  // depth_std_m
  if (lhs->depth_std_m != rhs->depth_std_m) {
    return false;
  }
  // valid_depth_ratio
  if (lhs->valid_depth_ratio != rhs->valid_depth_ratio) {
    return false;
  }
  // fill_ratio
  if (lhs->fill_ratio != rhs->fill_ratio) {
    return false;
  }
  // area_ratio
  if (lhs->area_ratio != rhs->area_ratio) {
    return false;
  }
  // foreground_height_m
  if (lhs->foreground_height_m != rhs->foreground_height_m) {
    return false;
  }
  // foreground_height_valid
  if (lhs->foreground_height_valid != rhs->foreground_height_valid) {
    return false;
  }
  // proposal_score
  if (lhs->proposal_score != rhs->proposal_score) {
    return false;
  }
  // touches_border
  if (lhs->touches_border != rhs->touches_border) {
    return false;
  }
  return true;
}

bool
macrobot_interfaces__msg__DepthCandidate__copy(
  const macrobot_interfaces__msg__DepthCandidate * input,
  macrobot_interfaces__msg__DepthCandidate * output)
{
  if (!input || !output) {
    return false;
  }
  // id
  output->id = input->id;
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
  // median_depth_m
  output->median_depth_m = input->median_depth_m;
  // near_depth_m
  output->near_depth_m = input->near_depth_m;
  // far_depth_m
  output->far_depth_m = input->far_depth_m;
  // depth_std_m
  output->depth_std_m = input->depth_std_m;
  // valid_depth_ratio
  output->valid_depth_ratio = input->valid_depth_ratio;
  // fill_ratio
  output->fill_ratio = input->fill_ratio;
  // area_ratio
  output->area_ratio = input->area_ratio;
  // foreground_height_m
  output->foreground_height_m = input->foreground_height_m;
  // foreground_height_valid
  output->foreground_height_valid = input->foreground_height_valid;
  // proposal_score
  output->proposal_score = input->proposal_score;
  // touches_border
  output->touches_border = input->touches_border;
  return true;
}

macrobot_interfaces__msg__DepthCandidate *
macrobot_interfaces__msg__DepthCandidate__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__DepthCandidate * msg = (macrobot_interfaces__msg__DepthCandidate *)allocator.allocate(sizeof(macrobot_interfaces__msg__DepthCandidate), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(macrobot_interfaces__msg__DepthCandidate));
  bool success = macrobot_interfaces__msg__DepthCandidate__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
macrobot_interfaces__msg__DepthCandidate__destroy(macrobot_interfaces__msg__DepthCandidate * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    macrobot_interfaces__msg__DepthCandidate__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
macrobot_interfaces__msg__DepthCandidate__Sequence__init(macrobot_interfaces__msg__DepthCandidate__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__DepthCandidate * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(macrobot_interfaces__msg__DepthCandidate)) {
      return false;
    }
    data = (macrobot_interfaces__msg__DepthCandidate *)allocator.zero_allocate(size, sizeof(macrobot_interfaces__msg__DepthCandidate), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = macrobot_interfaces__msg__DepthCandidate__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        macrobot_interfaces__msg__DepthCandidate__fini(&data[i - 1]);
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
macrobot_interfaces__msg__DepthCandidate__Sequence__fini(macrobot_interfaces__msg__DepthCandidate__Sequence * array)
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
      macrobot_interfaces__msg__DepthCandidate__fini(&array->data[i]);
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

macrobot_interfaces__msg__DepthCandidate__Sequence *
macrobot_interfaces__msg__DepthCandidate__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__DepthCandidate__Sequence * array = (macrobot_interfaces__msg__DepthCandidate__Sequence *)allocator.allocate(sizeof(macrobot_interfaces__msg__DepthCandidate__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = macrobot_interfaces__msg__DepthCandidate__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
macrobot_interfaces__msg__DepthCandidate__Sequence__destroy(macrobot_interfaces__msg__DepthCandidate__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    macrobot_interfaces__msg__DepthCandidate__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
macrobot_interfaces__msg__DepthCandidate__Sequence__are_equal(const macrobot_interfaces__msg__DepthCandidate__Sequence * lhs, const macrobot_interfaces__msg__DepthCandidate__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!macrobot_interfaces__msg__DepthCandidate__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
macrobot_interfaces__msg__DepthCandidate__Sequence__copy(
  const macrobot_interfaces__msg__DepthCandidate__Sequence * input,
  macrobot_interfaces__msg__DepthCandidate__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(macrobot_interfaces__msg__DepthCandidate)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(macrobot_interfaces__msg__DepthCandidate);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    macrobot_interfaces__msg__DepthCandidate * data =
      (macrobot_interfaces__msg__DepthCandidate *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!macrobot_interfaces__msg__DepthCandidate__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          macrobot_interfaces__msg__DepthCandidate__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!macrobot_interfaces__msg__DepthCandidate__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
