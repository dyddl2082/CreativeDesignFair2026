// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from macrobot_interfaces:msg/DepthCandidateArray.idl
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
#include "macrobot_interfaces/msg/detail/depth_candidate_array__struct.h"
#include "macrobot_interfaces/msg/detail/depth_candidate_array__functions.h"

#include "rosidl_runtime_c/primitives_sequence.h"
#include "rosidl_runtime_c/primitives_sequence_functions.h"

// Nested array functions includes
#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"
// end nested array functions include
ROSIDL_GENERATOR_C_IMPORT
bool std_msgs__msg__header__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * std_msgs__msg__header__convert_to_py(void * raw_ros_message);
ROSIDL_GENERATOR_C_IMPORT
bool sensor_msgs__msg__compressed_image__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * sensor_msgs__msg__compressed_image__convert_to_py(void * raw_ros_message);
bool macrobot_interfaces__msg__depth_candidate__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * macrobot_interfaces__msg__depth_candidate__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool macrobot_interfaces__msg__depth_candidate_array__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[67];
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
    assert(strncmp("macrobot_interfaces.msg._depth_candidate_array.DepthCandidateArray", full_classname_dest, 66) == 0);
  }
  macrobot_interfaces__msg__DepthCandidateArray * ros_message = _ros_message;
  {  // header
    PyObject * field = PyObject_GetAttrString(_pymsg, "header");
    if (!field) {
      return false;
    }
    if (!std_msgs__msg__header__convert_from_py(field, &ros_message->header)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // image_width
    PyObject * field = PyObject_GetAttrString(_pymsg, "image_width");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->image_width = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // image_height
    PyObject * field = PyObject_GetAttrString(_pymsg, "image_height");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->image_height = PyLong_AsUnsignedLong(field);
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
  {  // plane_inlier_ratio
    PyObject * field = PyObject_GetAttrString(_pymsg, "plane_inlier_ratio");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->plane_inlier_ratio = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // plane_coefficients
    PyObject * field = PyObject_GetAttrString(_pymsg, "plane_coefficients");
    if (!field) {
      return false;
    }
    {
      // TODO(dirk-thomas) use a better way to check the type before casting
      assert(field->ob_type != NULL);
      assert(field->ob_type->tp_name != NULL);
      assert(strcmp(field->ob_type->tp_name, "numpy.ndarray") == 0);
      PyArrayObject * seq_field = (PyArrayObject *)field;
      Py_INCREF(seq_field);
      assert(PyArray_NDIM(seq_field) == 1);
      assert(PyArray_TYPE(seq_field) == NPY_FLOAT32);
      Py_ssize_t size = 4;
      float * dest = ros_message->plane_coefficients;
      for (Py_ssize_t i = 0; i < size; ++i) {
        float tmp = *(npy_float32 *)PyArray_GETPTR1(seq_field, i);
        memcpy(&dest[i], &tmp, sizeof(float));
      }
      Py_DECREF(seq_field);
    }
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
  {  // candidates
    PyObject * field = PyObject_GetAttrString(_pymsg, "candidates");
    if (!field) {
      return false;
    }
    PyObject * seq_field = PySequence_Fast(field, "expected a sequence in 'candidates'");
    if (!seq_field) {
      Py_DECREF(field);
      return false;
    }
    Py_ssize_t size = PySequence_Size(field);
    if (-1 == size) {
      Py_DECREF(seq_field);
      Py_DECREF(field);
      return false;
    }
    if (!macrobot_interfaces__msg__DepthCandidate__Sequence__init(&(ros_message->candidates), size)) {
      PyErr_SetString(PyExc_RuntimeError, "unable to create macrobot_interfaces__msg__DepthCandidate__Sequence ros_message");
      Py_DECREF(seq_field);
      Py_DECREF(field);
      return false;
    }
    macrobot_interfaces__msg__DepthCandidate * dest = ros_message->candidates.data;
    for (Py_ssize_t i = 0; i < size; ++i) {
      if (!macrobot_interfaces__msg__depth_candidate__convert_from_py(PySequence_Fast_GET_ITEM(seq_field, i), &dest[i])) {
        Py_DECREF(seq_field);
        Py_DECREF(field);
        return false;
      }
    }
    Py_DECREF(seq_field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * macrobot_interfaces__msg__depth_candidate_array__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of DepthCandidateArray */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("macrobot_interfaces.msg._depth_candidate_array");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "DepthCandidateArray");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  macrobot_interfaces__msg__DepthCandidateArray * ros_message = (macrobot_interfaces__msg__DepthCandidateArray *)raw_ros_message;
  {  // header
    PyObject * field = NULL;
    field = std_msgs__msg__header__convert_to_py(&ros_message->header);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "header", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // image_width
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->image_width);
    {
      int rc = PyObject_SetAttrString(_pymessage, "image_width", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // image_height
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->image_height);
    {
      int rc = PyObject_SetAttrString(_pymessage, "image_height", field);
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
  {  // plane_inlier_ratio
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->plane_inlier_ratio);
    {
      int rc = PyObject_SetAttrString(_pymessage, "plane_inlier_ratio", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // plane_coefficients
    PyObject * field = NULL;
    field = PyObject_GetAttrString(_pymessage, "plane_coefficients");
    if (!field) {
      return NULL;
    }
    assert(field->ob_type != NULL);
    assert(field->ob_type->tp_name != NULL);
    assert(strcmp(field->ob_type->tp_name, "numpy.ndarray") == 0);
    PyArrayObject * seq_field = (PyArrayObject *)field;
    assert(PyArray_NDIM(seq_field) == 1);
    assert(PyArray_TYPE(seq_field) == NPY_FLOAT32);
    assert(sizeof(npy_float32) == sizeof(float));
    npy_float32 * dst = (npy_float32 *)PyArray_GETPTR1(seq_field, 0);
    float * src = &(ros_message->plane_coefficients[0]);
    memcpy(dst, src, 4 * sizeof(float));
    Py_DECREF(field);
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
  {  // candidates
    PyObject * field = NULL;
    size_t size = ros_message->candidates.size;
    field = PyList_New(size);
    if (!field) {
      return NULL;
    }
    macrobot_interfaces__msg__DepthCandidate * item;
    for (size_t i = 0; i < size; ++i) {
      item = &(ros_message->candidates.data[i]);
      PyObject * pyitem = macrobot_interfaces__msg__depth_candidate__convert_to_py(item);
      if (!pyitem) {
        Py_DECREF(field);
        return NULL;
      }
      int rc = PyList_SetItem(field, i, pyitem);
      (void)rc;
      assert(rc == 0);
    }
    assert(PySequence_Check(field));
    {
      int rc = PyObject_SetAttrString(_pymessage, "candidates", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
