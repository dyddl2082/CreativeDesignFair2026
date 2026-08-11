// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from macrobot_interfaces:msg/FilteredCandidateCrop.idl
// generated code does not contain a copyright notice
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `result`
#include "macrobot_interfaces/msg/detail/candidate_filter_result__functions.h"
// Member `crop`
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__functions.h"

bool
macrobot_interfaces__msg__FilteredCandidateCrop__init(macrobot_interfaces__msg__FilteredCandidateCrop * msg)
{
  if (!msg) {
    return false;
  }
  // result
  if (!macrobot_interfaces__msg__CandidateFilterResult__init(&msg->result)) {
    macrobot_interfaces__msg__FilteredCandidateCrop__fini(msg);
    return false;
  }
  // crop
  if (!macrobot_interfaces__msg__RgbCandidateCrop__init(&msg->crop)) {
    macrobot_interfaces__msg__FilteredCandidateCrop__fini(msg);
    return false;
  }
  return true;
}

void
macrobot_interfaces__msg__FilteredCandidateCrop__fini(macrobot_interfaces__msg__FilteredCandidateCrop * msg)
{
  if (!msg) {
    return;
  }
  // result
  macrobot_interfaces__msg__CandidateFilterResult__fini(&msg->result);
  // crop
  macrobot_interfaces__msg__RgbCandidateCrop__fini(&msg->crop);
}

bool
macrobot_interfaces__msg__FilteredCandidateCrop__are_equal(const macrobot_interfaces__msg__FilteredCandidateCrop * lhs, const macrobot_interfaces__msg__FilteredCandidateCrop * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // result
  if (!macrobot_interfaces__msg__CandidateFilterResult__are_equal(
      &(lhs->result), &(rhs->result)))
  {
    return false;
  }
  // crop
  if (!macrobot_interfaces__msg__RgbCandidateCrop__are_equal(
      &(lhs->crop), &(rhs->crop)))
  {
    return false;
  }
  return true;
}

bool
macrobot_interfaces__msg__FilteredCandidateCrop__copy(
  const macrobot_interfaces__msg__FilteredCandidateCrop * input,
  macrobot_interfaces__msg__FilteredCandidateCrop * output)
{
  if (!input || !output) {
    return false;
  }
  // result
  if (!macrobot_interfaces__msg__CandidateFilterResult__copy(
      &(input->result), &(output->result)))
  {
    return false;
  }
  // crop
  if (!macrobot_interfaces__msg__RgbCandidateCrop__copy(
      &(input->crop), &(output->crop)))
  {
    return false;
  }
  return true;
}

macrobot_interfaces__msg__FilteredCandidateCrop *
macrobot_interfaces__msg__FilteredCandidateCrop__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__FilteredCandidateCrop * msg = (macrobot_interfaces__msg__FilteredCandidateCrop *)allocator.allocate(sizeof(macrobot_interfaces__msg__FilteredCandidateCrop), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(macrobot_interfaces__msg__FilteredCandidateCrop));
  bool success = macrobot_interfaces__msg__FilteredCandidateCrop__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
macrobot_interfaces__msg__FilteredCandidateCrop__destroy(macrobot_interfaces__msg__FilteredCandidateCrop * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    macrobot_interfaces__msg__FilteredCandidateCrop__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__init(macrobot_interfaces__msg__FilteredCandidateCrop__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__FilteredCandidateCrop * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(macrobot_interfaces__msg__FilteredCandidateCrop)) {
      return false;
    }
    data = (macrobot_interfaces__msg__FilteredCandidateCrop *)allocator.zero_allocate(size, sizeof(macrobot_interfaces__msg__FilteredCandidateCrop), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = macrobot_interfaces__msg__FilteredCandidateCrop__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        macrobot_interfaces__msg__FilteredCandidateCrop__fini(&data[i - 1]);
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
macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__fini(macrobot_interfaces__msg__FilteredCandidateCrop__Sequence * array)
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
      macrobot_interfaces__msg__FilteredCandidateCrop__fini(&array->data[i]);
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

macrobot_interfaces__msg__FilteredCandidateCrop__Sequence *
macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  macrobot_interfaces__msg__FilteredCandidateCrop__Sequence * array = (macrobot_interfaces__msg__FilteredCandidateCrop__Sequence *)allocator.allocate(sizeof(macrobot_interfaces__msg__FilteredCandidateCrop__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__destroy(macrobot_interfaces__msg__FilteredCandidateCrop__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__are_equal(const macrobot_interfaces__msg__FilteredCandidateCrop__Sequence * lhs, const macrobot_interfaces__msg__FilteredCandidateCrop__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!macrobot_interfaces__msg__FilteredCandidateCrop__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__copy(
  const macrobot_interfaces__msg__FilteredCandidateCrop__Sequence * input,
  macrobot_interfaces__msg__FilteredCandidateCrop__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(macrobot_interfaces__msg__FilteredCandidateCrop)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(macrobot_interfaces__msg__FilteredCandidateCrop);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    macrobot_interfaces__msg__FilteredCandidateCrop * data =
      (macrobot_interfaces__msg__FilteredCandidateCrop *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!macrobot_interfaces__msg__FilteredCandidateCrop__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          macrobot_interfaces__msg__FilteredCandidateCrop__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!macrobot_interfaces__msg__FilteredCandidateCrop__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
