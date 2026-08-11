// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from macrobot_interfaces:msg/RgbCandidateCrop.idl
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
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__struct.h"
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__functions.h"

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
ROSIDL_GENERATOR_C_IMPORT
bool sensor_msgs__msg__compressed_image__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * sensor_msgs__msg__compressed_image__convert_to_py(void * raw_ros_message);
ROSIDL_GENERATOR_C_IMPORT
bool sensor_msgs__msg__compressed_image__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * sensor_msgs__msg__compressed_image__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool macrobot_interfaces__msg__rgb_candidate_crop__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[61];
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
    assert(strncmp("macrobot_interfaces.msg._rgb_candidate_crop.RgbCandidateCrop", full_classname_dest, 60) == 0);
  }
  macrobot_interfaces__msg__RgbCandidateCrop * ros_message = _ros_message;
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
  {  // proposal_image_width
    PyObject * field = PyObject_GetAttrString(_pymsg, "proposal_image_width");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->proposal_image_width = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // proposal_image_height
    PyObject * field = PyObject_GetAttrString(_pymsg, "proposal_image_height");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->proposal_image_height = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // color_image_width
    PyObject * field = PyObject_GetAttrString(_pymsg, "color_image_width");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->color_image_width = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // color_image_height
    PyObject * field = PyObject_GetAttrString(_pymsg, "color_image_height");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->color_image_height = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // source_candidate_count
    PyObject * field = PyObject_GetAttrString(_pymsg, "source_candidate_count");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->source_candidate_count = PyLong_AsUnsignedLong(field);
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
  {  // crop_index
    PyObject * field = PyObject_GetAttrString(_pymsg, "crop_index");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->crop_index = PyLong_AsUnsignedLong(field);
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
  {  // color_time_offset_sec
    PyObject * field = PyObject_GetAttrString(_pymsg, "color_time_offset_sec");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->color_time_offset_sec = (float)PyFloat_AS_DOUBLE(field);
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
  {  // foreground_mask_available
    PyObject * field = PyObject_GetAttrString(_pymsg, "foreground_mask_available");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->foreground_mask_available = (Py_True == field);
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
  {  // foreground_mask
    PyObject * field = PyObject_GetAttrString(_pymsg, "foreground_mask");
    if (!field) {
      return false;
    }
    if (!sensor_msgs__msg__compressed_image__convert_from_py(field, &ros_message->foreground_mask)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // encoded_width
    PyObject * field = PyObject_GetAttrString(_pymsg, "encoded_width");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->encoded_width = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // encoded_height
    PyObject * field = PyObject_GetAttrString(_pymsg, "encoded_height");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->encoded_height = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // jpeg_size_bytes
    PyObject * field = PyObject_GetAttrString(_pymsg, "jpeg_size_bytes");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->jpeg_size_bytes = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // jpeg_quality
    PyObject * field = PyObject_GetAttrString(_pymsg, "jpeg_quality");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->jpeg_quality = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // size_limit_met
    PyObject * field = PyObject_GetAttrString(_pymsg, "size_limit_met");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->size_limit_met = (Py_True == field);
    Py_DECREF(field);
  }
  {  // image
    PyObject * field = PyObject_GetAttrString(_pymsg, "image");
    if (!field) {
      return false;
    }
    if (!sensor_msgs__msg__compressed_image__convert_from_py(field, &ros_message->image)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * macrobot_interfaces__msg__rgb_candidate_crop__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of RgbCandidateCrop */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("macrobot_interfaces.msg._rgb_candidate_crop");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "RgbCandidateCrop");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  macrobot_interfaces__msg__RgbCandidateCrop * ros_message = (macrobot_interfaces__msg__RgbCandidateCrop *)raw_ros_message;
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
  {  // proposal_image_width
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->proposal_image_width);
    {
      int rc = PyObject_SetAttrString(_pymessage, "proposal_image_width", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // proposal_image_height
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->proposal_image_height);
    {
      int rc = PyObject_SetAttrString(_pymessage, "proposal_image_height", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // color_image_width
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->color_image_width);
    {
      int rc = PyObject_SetAttrString(_pymessage, "color_image_width", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // color_image_height
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->color_image_height);
    {
      int rc = PyObject_SetAttrString(_pymessage, "color_image_height", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // source_candidate_count
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->source_candidate_count);
    {
      int rc = PyObject_SetAttrString(_pymessage, "source_candidate_count", field);
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
  {  // color_time_offset_sec
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->color_time_offset_sec);
    {
      int rc = PyObject_SetAttrString(_pymessage, "color_time_offset_sec", field);
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
  {  // foreground_mask
    PyObject * field = NULL;
    field = sensor_msgs__msg__compressed_image__convert_to_py(&ros_message->foreground_mask);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "foreground_mask", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // encoded_width
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->encoded_width);
    {
      int rc = PyObject_SetAttrString(_pymessage, "encoded_width", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // encoded_height
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->encoded_height);
    {
      int rc = PyObject_SetAttrString(_pymessage, "encoded_height", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // jpeg_size_bytes
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->jpeg_size_bytes);
    {
      int rc = PyObject_SetAttrString(_pymessage, "jpeg_size_bytes", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // jpeg_quality
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->jpeg_quality);
    {
      int rc = PyObject_SetAttrString(_pymessage, "jpeg_quality", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // size_limit_met
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->size_limit_met ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "size_limit_met", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // image
    PyObject * field = NULL;
    field = sensor_msgs__msg__compressed_image__convert_to_py(&ros_message->image);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "image", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
