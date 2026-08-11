// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from macrobot_interfaces:msg/CandidateFilterResult.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "macrobot_interfaces/msg/detail/candidate_filter_result__struct.h"
#include "macrobot_interfaces/msg/detail/candidate_filter_result__functions.h"

#include "rosidl_runtime_c/string.h"
#include "rosidl_runtime_c/string_functions.h"

ROSIDL_GENERATOR_C_IMPORT
bool std_msgs__msg__header__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * std_msgs__msg__header__convert_to_py(void * raw_ros_message);
ROSIDL_GENERATOR_C_IMPORT
bool std_msgs__msg__header__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * std_msgs__msg__header__convert_to_py(void * raw_ros_message);
bool macrobot_interfaces__msg__depth_candidate__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * macrobot_interfaces__msg__depth_candidate__convert_to_py(void * raw_ros_message);
ROSIDL_GENERATOR_C_IMPORT
bool sensor_msgs__msg__region_of_interest__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * sensor_msgs__msg__region_of_interest__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool macrobot_interfaces__msg__candidate_filter_result__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[71];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("macrobot_interfaces.msg._candidate_filter_result.CandidateFilterResult", full_classname_dest, 70) == 0);
  }
  macrobot_interfaces__msg__CandidateFilterResult * ros_message = _ros_message;
  {  // proposal_header
    PyObject * field = PyObject_GetAttrString(_pymsg, "proposal_header");
    if (!field) {
      return false;
    }
    if (!std_msgs__msg__header__convert_from_py(field, &ros_message->proposal_header)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // image_header
    PyObject * field = PyObject_GetAttrString(_pymsg, "image_header");
    if (!field) {
      return false;
    }
    if (!std_msgs__msg__header__convert_from_py(field, &ros_message->image_header)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // candidate_id
    PyObject * field = PyObject_GetAttrString(_pymsg, "candidate_id");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->candidate_id = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // crop_index
    PyObject * field = PyObject_GetAttrString(_pymsg, "crop_index");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->crop_index = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // frame_crop_count
    PyObject * field = PyObject_GetAttrString(_pymsg, "frame_crop_count");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->frame_crop_count = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // target_object
    PyObject * field = PyObject_GetAttrString(_pymsg, "target_object");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->target_object, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // reference_profile_available
    PyObject * field = PyObject_GetAttrString(_pymsg, "reference_profile_available");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->reference_profile_available = (Py_True == field);
    Py_DECREF(field);
  }
  {  // reference_image_count
    PyObject * field = PyObject_GetAttrString(_pymsg, "reference_image_count");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->reference_image_count = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // camera_info_available
    PyObject * field = PyObject_GetAttrString(_pymsg, "camera_info_available");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->camera_info_available = (Py_True == field);
    Py_DECREF(field);
  }
  {  // plane_found
    PyObject * field = PyObject_GetAttrString(_pymsg, "plane_found");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->plane_found = (Py_True == field);
    Py_DECREF(field);
  }
  {  // foreground_height_valid
    PyObject * field = PyObject_GetAttrString(_pymsg, "foreground_height_valid");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->foreground_height_valid = (Py_True == field);
    Py_DECREF(field);
  }
  {  // foreground_mask_available
    PyObject * field = PyObject_GetAttrString(_pymsg, "foreground_mask_available");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->foreground_mask_available = (Py_True == field);
    Py_DECREF(field);
  }
  {  // accepted
    PyObject * field = PyObject_GetAttrString(_pymsg, "accepted");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->accepted = (Py_True == field);
    Py_DECREF(field);
  }
  {  // reject_stage
    PyObject * field = PyObject_GetAttrString(_pymsg, "reject_stage");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->reject_stage, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // reject_reason
    PyObject * field = PyObject_GetAttrString(_pymsg, "reject_reason");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->reject_reason, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // objectness_score
    PyObject * field = PyObject_GetAttrString(_pymsg, "objectness_score");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->objectness_score = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // target_hint_score
    PyObject * field = PyObject_GetAttrString(_pymsg, "target_hint_score");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->target_hint_score = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // filter_score
    PyObject * field = PyObject_GetAttrString(_pymsg, "filter_score");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->filter_score = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // depth_score
    PyObject * field = PyObject_GetAttrString(_pymsg, "depth_score");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->depth_score = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // quality_score
    PyObject * field = PyObject_GetAttrString(_pymsg, "quality_score");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->quality_score = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // color_score
    PyObject * field = PyObject_GetAttrString(_pymsg, "color_score");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->color_score = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // shape_score
    PyObject * field = PyObject_GetAttrString(_pymsg, "shape_score");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->shape_score = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // physical_size_score
    PyObject * field = PyObject_GetAttrString(_pymsg, "physical_size_score");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->physical_size_score = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // sharpness
    PyObject * field = PyObject_GetAttrString(_pymsg, "sharpness");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->sharpness = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // mean_brightness
    PyObject * field = PyObject_GetAttrString(_pymsg, "mean_brightness");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->mean_brightness = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // dark_ratio
    PyObject * field = PyObject_GetAttrString(_pymsg, "dark_ratio");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->dark_ratio = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // bright_clip_ratio
    PyObject * field = PyObject_GetAttrString(_pymsg, "bright_clip_ratio");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->bright_clip_ratio = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // edge_density
    PyObject * field = PyObject_GetAttrString(_pymsg, "edge_density");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->edge_density = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // mask_fill_ratio
    PyObject * field = PyObject_GetAttrString(_pymsg, "mask_fill_ratio");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->mask_fill_ratio = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // mask_solidity
    PyObject * field = PyObject_GetAttrString(_pymsg, "mask_solidity");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->mask_solidity = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // color_similarity
    PyObject * field = PyObject_GetAttrString(_pymsg, "color_similarity");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->color_similarity = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // aspect_ratio
    PyObject * field = PyObject_GetAttrString(_pymsg, "aspect_ratio");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->aspect_ratio = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // estimated_width_m
    PyObject * field = PyObject_GetAttrString(_pymsg, "estimated_width_m");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->estimated_width_m = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // estimated_height_m
    PyObject * field = PyObject_GetAttrString(_pymsg, "estimated_height_m");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->estimated_height_m = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // sync_offset_abs_sec
    PyObject * field = PyObject_GetAttrString(_pymsg, "sync_offset_abs_sec");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->sync_offset_abs_sec = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // candidate
    PyObject * field = PyObject_GetAttrString(_pymsg, "candidate");
    if (!field) {
      return false;
    }
    if (!macrobot_interfaces__msg__depth_candidate__convert_from_py(field, &ros_message->candidate)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // crop_roi
    PyObject * field = PyObject_GetAttrString(_pymsg, "crop_roi");
    if (!field) {
      return false;
    }
    if (!sensor_msgs__msg__region_of_interest__convert_from_py(field, &ros_message->crop_roi)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * macrobot_interfaces__msg__candidate_filter_result__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of CandidateFilterResult */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("macrobot_interfaces.msg._candidate_filter_result");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "CandidateFilterResult");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  macrobot_interfaces__msg__CandidateFilterResult * ros_message = (macrobot_interfaces__msg__CandidateFilterResult *)raw_ros_message;
  {  // proposal_header
    PyObject * field = NULL;
    field = std_msgs__msg__header__convert_to_py(&ros_message->proposal_header);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "proposal_header", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // image_header
    PyObject * field = NULL;
    field = std_msgs__msg__header__convert_to_py(&ros_message->image_header);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "image_header", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // candidate_id
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->candidate_id);
    {
      int rc = PyObject_SetAttrString(_pymessage, "candidate_id", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // crop_index
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->crop_index);
    {
      int rc = PyObject_SetAttrString(_pymessage, "crop_index", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // frame_crop_count
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->frame_crop_count);
    {
      int rc = PyObject_SetAttrString(_pymessage, "frame_crop_count", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // target_object
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->target_object.data,
      strlen(ros_message->target_object.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "target_object", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // reference_profile_available
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->reference_profile_available ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "reference_profile_available", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // reference_image_count
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->reference_image_count);
    {
      int rc = PyObject_SetAttrString(_pymessage, "reference_image_count", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // camera_info_available
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->camera_info_available ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "camera_info_available", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // plane_found
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->plane_found ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "plane_found", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // foreground_height_valid
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->foreground_height_valid ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "foreground_height_valid", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // foreground_mask_available
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->foreground_mask_available ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "foreground_mask_available", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // accepted
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->accepted ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "accepted", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // reject_stage
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->reject_stage.data,
      strlen(ros_message->reject_stage.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "reject_stage", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // reject_reason
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->reject_reason.data,
      strlen(ros_message->reject_reason.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "reject_reason", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // objectness_score
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->objectness_score);
    {
      int rc = PyObject_SetAttrString(_pymessage, "objectness_score", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // target_hint_score
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->target_hint_score);
    {
      int rc = PyObject_SetAttrString(_pymessage, "target_hint_score", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // filter_score
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->filter_score);
    {
      int rc = PyObject_SetAttrString(_pymessage, "filter_score", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // depth_score
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->depth_score);
    {
      int rc = PyObject_SetAttrString(_pymessage, "depth_score", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // quality_score
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->quality_score);
    {
      int rc = PyObject_SetAttrString(_pymessage, "quality_score", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // color_score
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->color_score);
    {
      int rc = PyObject_SetAttrString(_pymessage, "color_score", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // shape_score
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->shape_score);
    {
      int rc = PyObject_SetAttrString(_pymessage, "shape_score", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // physical_size_score
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->physical_size_score);
    {
      int rc = PyObject_SetAttrString(_pymessage, "physical_size_score", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // sharpness
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->sharpness);
    {
      int rc = PyObject_SetAttrString(_pymessage, "sharpness", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // mean_brightness
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->mean_brightness);
    {
      int rc = PyObject_SetAttrString(_pymessage, "mean_brightness", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // dark_ratio
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->dark_ratio);
    {
      int rc = PyObject_SetAttrString(_pymessage, "dark_ratio", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // bright_clip_ratio
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->bright_clip_ratio);
    {
      int rc = PyObject_SetAttrString(_pymessage, "bright_clip_ratio", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // edge_density
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->edge_density);
    {
      int rc = PyObject_SetAttrString(_pymessage, "edge_density", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // mask_fill_ratio
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->mask_fill_ratio);
    {
      int rc = PyObject_SetAttrString(_pymessage, "mask_fill_ratio", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // mask_solidity
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->mask_solidity);
    {
      int rc = PyObject_SetAttrString(_pymessage, "mask_solidity", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // color_similarity
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->color_similarity);
    {
      int rc = PyObject_SetAttrString(_pymessage, "color_similarity", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // aspect_ratio
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->aspect_ratio);
    {
      int rc = PyObject_SetAttrString(_pymessage, "aspect_ratio", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // estimated_width_m
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->estimated_width_m);
    {
      int rc = PyObject_SetAttrString(_pymessage, "estimated_width_m", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // estimated_height_m
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->estimated_height_m);
    {
      int rc = PyObject_SetAttrString(_pymessage, "estimated_height_m", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // sync_offset_abs_sec
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->sync_offset_abs_sec);
    {
      int rc = PyObject_SetAttrString(_pymessage, "sync_offset_abs_sec", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // candidate
    PyObject * field = NULL;
    field = macrobot_interfaces__msg__depth_candidate__convert_to_py(&ros_message->candidate);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "candidate", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // crop_roi
    PyObject * field = NULL;
    field = sensor_msgs__msg__region_of_interest__convert_to_py(&ros_message->crop_roi);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "crop_roi", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
