// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from macrobot_interfaces:msg/DepthCandidate.idl
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
#include "macrobot_interfaces/msg/detail/depth_candidate__struct.h"
#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"

ROSIDL_GENERATOR_C_IMPORT
bool sensor_msgs__msg__region_of_interest__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * sensor_msgs__msg__region_of_interest__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool macrobot_interfaces__msg__depth_candidate__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[56];
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
    assert(strncmp("macrobot_interfaces.msg._depth_candidate.DepthCandidate", full_classname_dest, 55) == 0);
  }
  macrobot_interfaces__msg__DepthCandidate * ros_message = _ros_message;
  {  // id
    PyObject * field = PyObject_GetAttrString(_pymsg, "id");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->id = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // roi
    PyObject * field = PyObject_GetAttrString(_pymsg, "roi");
    if (!field) {
      return false;
    }
    if (!sensor_msgs__msg__region_of_interest__convert_from_py(field, &ros_message->roi)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // center_x
    PyObject * field = PyObject_GetAttrString(_pymsg, "center_x");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->center_x = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // center_y
    PyObject * field = PyObject_GetAttrString(_pymsg, "center_y");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->center_y = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // median_depth_m
    PyObject * field = PyObject_GetAttrString(_pymsg, "median_depth_m");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->median_depth_m = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // near_depth_m
    PyObject * field = PyObject_GetAttrString(_pymsg, "near_depth_m");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->near_depth_m = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // far_depth_m
    PyObject * field = PyObject_GetAttrString(_pymsg, "far_depth_m");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->far_depth_m = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // depth_std_m
    PyObject * field = PyObject_GetAttrString(_pymsg, "depth_std_m");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->depth_std_m = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // valid_depth_ratio
    PyObject * field = PyObject_GetAttrString(_pymsg, "valid_depth_ratio");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->valid_depth_ratio = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // fill_ratio
    PyObject * field = PyObject_GetAttrString(_pymsg, "fill_ratio");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->fill_ratio = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // area_ratio
    PyObject * field = PyObject_GetAttrString(_pymsg, "area_ratio");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->area_ratio = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // foreground_height_m
    PyObject * field = PyObject_GetAttrString(_pymsg, "foreground_height_m");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->foreground_height_m = (float)PyFloat_AS_DOUBLE(field);
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
  {  // proposal_score
    PyObject * field = PyObject_GetAttrString(_pymsg, "proposal_score");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->proposal_score = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // touches_border
    PyObject * field = PyObject_GetAttrString(_pymsg, "touches_border");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->touches_border = (Py_True == field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * macrobot_interfaces__msg__depth_candidate__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of DepthCandidate */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("macrobot_interfaces.msg._depth_candidate");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "DepthCandidate");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  macrobot_interfaces__msg__DepthCandidate * ros_message = (macrobot_interfaces__msg__DepthCandidate *)raw_ros_message;
  {  // id
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->id);
    {
      int rc = PyObject_SetAttrString(_pymessage, "id", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // roi
    PyObject * field = NULL;
    field = sensor_msgs__msg__region_of_interest__convert_to_py(&ros_message->roi);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "roi", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // center_x
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->center_x);
    {
      int rc = PyObject_SetAttrString(_pymessage, "center_x", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // center_y
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->center_y);
    {
      int rc = PyObject_SetAttrString(_pymessage, "center_y", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // median_depth_m
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->median_depth_m);
    {
      int rc = PyObject_SetAttrString(_pymessage, "median_depth_m", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // near_depth_m
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->near_depth_m);
    {
      int rc = PyObject_SetAttrString(_pymessage, "near_depth_m", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // far_depth_m
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->far_depth_m);
    {
      int rc = PyObject_SetAttrString(_pymessage, "far_depth_m", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // depth_std_m
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->depth_std_m);
    {
      int rc = PyObject_SetAttrString(_pymessage, "depth_std_m", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // valid_depth_ratio
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->valid_depth_ratio);
    {
      int rc = PyObject_SetAttrString(_pymessage, "valid_depth_ratio", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fill_ratio
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->fill_ratio);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fill_ratio", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // area_ratio
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->area_ratio);
    {
      int rc = PyObject_SetAttrString(_pymessage, "area_ratio", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // foreground_height_m
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->foreground_height_m);
    {
      int rc = PyObject_SetAttrString(_pymessage, "foreground_height_m", field);
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
  {  // proposal_score
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->proposal_score);
    {
      int rc = PyObject_SetAttrString(_pymessage, "proposal_score", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // touches_border
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->touches_border ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "touches_border", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
