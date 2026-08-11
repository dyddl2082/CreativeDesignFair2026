// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from macrobot_interfaces:msg/EmbeddingRetrievalResult.idl
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
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__struct.h"
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__functions.h"

#include "rosidl_runtime_c/string.h"
#include "rosidl_runtime_c/string_functions.h"

#include "rosidl_runtime_c/primitives_sequence.h"
#include "rosidl_runtime_c/primitives_sequence_functions.h"

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
bool macrobot_interfaces__msg__embedding_retrieval_result__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[77];
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
    assert(strncmp("macrobot_interfaces.msg._embedding_retrieval_result.EmbeddingRetrievalResult", full_classname_dest, 76) == 0);
  }
  macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message = _ros_message;
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
  {  // model_id
    PyObject * field = PyObject_GetAttrString(_pymsg, "model_id");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->model_id, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // pooling
    PyObject * field = PyObject_GetAttrString(_pymsg, "pooling");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->pooling, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // device
    PyObject * field = PyObject_GetAttrString(_pymsg, "device");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->device, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // embedding_dim
    PyObject * field = PyObject_GetAttrString(_pymsg, "embedding_dim");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->embedding_dim = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // positive_bank_available
    PyObject * field = PyObject_GetAttrString(_pymsg, "positive_bank_available");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->positive_bank_available = (Py_True == field);
    Py_DECREF(field);
  }
  {  // positive_reference_count
    PyObject * field = PyObject_GetAttrString(_pymsg, "positive_reference_count");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->positive_reference_count = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // negative_bank_available
    PyObject * field = PyObject_GetAttrString(_pymsg, "negative_bank_available");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->negative_bank_available = (Py_True == field);
    Py_DECREF(field);
  }
  {  // negative_reference_count
    PyObject * field = PyObject_GetAttrString(_pymsg, "negative_reference_count");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->negative_reference_count = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // foreground_mask_used
    PyObject * field = PyObject_GetAttrString(_pymsg, "foreground_mask_used");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->foreground_mask_used = (Py_True == field);
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
  {  // positive_similarity
    PyObject * field = PyObject_GetAttrString(_pymsg, "positive_similarity");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->positive_similarity = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // best_positive_similarity
    PyObject * field = PyObject_GetAttrString(_pymsg, "best_positive_similarity");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->best_positive_similarity = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // negative_similarity
    PyObject * field = PyObject_GetAttrString(_pymsg, "negative_similarity");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->negative_similarity = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // best_negative_similarity
    PyObject * field = PyObject_GetAttrString(_pymsg, "best_negative_similarity");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->best_negative_similarity = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // margin
    PyObject * field = PyObject_GetAttrString(_pymsg, "margin");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->margin = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // best_positive_path
    PyObject * field = PyObject_GetAttrString(_pymsg, "best_positive_path");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->best_positive_path, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // best_negative_path
    PyObject * field = PyObject_GetAttrString(_pymsg, "best_negative_path");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->best_negative_path, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // top_positive_paths
    PyObject * field = PyObject_GetAttrString(_pymsg, "top_positive_paths");
    if (!field) {
      return false;
    }
    {
      PyObject * seq_field = PySequence_Fast(field, "expected a sequence in 'top_positive_paths'");
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
      if (!rosidl_runtime_c__String__Sequence__init(&(ros_message->top_positive_paths), size)) {
        PyErr_SetString(PyExc_RuntimeError, "unable to create String__Sequence ros_message");
        Py_DECREF(seq_field);
        Py_DECREF(field);
        return false;
      }
      rosidl_runtime_c__String * dest = ros_message->top_positive_paths.data;
      for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject * item = PySequence_Fast_GET_ITEM(seq_field, i);
        if (!item) {
          Py_DECREF(seq_field);
          Py_DECREF(field);
          return false;
        }
        assert(PyUnicode_Check(item));
        PyObject * encoded_item = PyUnicode_AsUTF8String(item);
        if (!encoded_item) {
          Py_DECREF(seq_field);
          Py_DECREF(field);
          return false;
        }
        rosidl_runtime_c__String__assign(&dest[i], PyBytes_AS_STRING(encoded_item));
        Py_DECREF(encoded_item);
      }
      Py_DECREF(seq_field);
    }
    Py_DECREF(field);
  }
  {  // top_positive_scores
    PyObject * field = PyObject_GetAttrString(_pymsg, "top_positive_scores");
    if (!field) {
      return false;
    }
    if (PyObject_CheckBuffer(field)) {
      // Optimization for converting arrays of primitives
      Py_buffer view;
      int rc = PyObject_GetBuffer(field, &view, PyBUF_SIMPLE);
      if (rc < 0) {
        Py_DECREF(field);
        return false;
      }
      Py_ssize_t size = view.len / sizeof(float);
      if (!rosidl_runtime_c__float__Sequence__init(&(ros_message->top_positive_scores), size)) {
        PyErr_SetString(PyExc_RuntimeError, "unable to create float__Sequence ros_message");
        PyBuffer_Release(&view);
        Py_DECREF(field);
        return false;
      }
      float * dest = ros_message->top_positive_scores.data;
      rc = PyBuffer_ToContiguous(dest, &view, view.len, 'C');
      if (rc < 0) {
        PyBuffer_Release(&view);
        Py_DECREF(field);
        return false;
      }
      PyBuffer_Release(&view);
    } else {
      PyObject * seq_field = PySequence_Fast(field, "expected a sequence in 'top_positive_scores'");
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
      if (!rosidl_runtime_c__float__Sequence__init(&(ros_message->top_positive_scores), size)) {
        PyErr_SetString(PyExc_RuntimeError, "unable to create float__Sequence ros_message");
        Py_DECREF(seq_field);
        Py_DECREF(field);
        return false;
      }
      float * dest = ros_message->top_positive_scores.data;
      for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject * item = PySequence_Fast_GET_ITEM(seq_field, i);
        if (!item) {
          Py_DECREF(seq_field);
          Py_DECREF(field);
          return false;
        }
        assert(PyFloat_Check(item));
        float tmp = (float)PyFloat_AS_DOUBLE(item);
        memcpy(&dest[i], &tmp, sizeof(float));
      }
      Py_DECREF(seq_field);
    }
    Py_DECREF(field);
  }
  {  // top_negative_paths
    PyObject * field = PyObject_GetAttrString(_pymsg, "top_negative_paths");
    if (!field) {
      return false;
    }
    {
      PyObject * seq_field = PySequence_Fast(field, "expected a sequence in 'top_negative_paths'");
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
      if (!rosidl_runtime_c__String__Sequence__init(&(ros_message->top_negative_paths), size)) {
        PyErr_SetString(PyExc_RuntimeError, "unable to create String__Sequence ros_message");
        Py_DECREF(seq_field);
        Py_DECREF(field);
        return false;
      }
      rosidl_runtime_c__String * dest = ros_message->top_negative_paths.data;
      for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject * item = PySequence_Fast_GET_ITEM(seq_field, i);
        if (!item) {
          Py_DECREF(seq_field);
          Py_DECREF(field);
          return false;
        }
        assert(PyUnicode_Check(item));
        PyObject * encoded_item = PyUnicode_AsUTF8String(item);
        if (!encoded_item) {
          Py_DECREF(seq_field);
          Py_DECREF(field);
          return false;
        }
        rosidl_runtime_c__String__assign(&dest[i], PyBytes_AS_STRING(encoded_item));
        Py_DECREF(encoded_item);
      }
      Py_DECREF(seq_field);
    }
    Py_DECREF(field);
  }
  {  // top_negative_scores
    PyObject * field = PyObject_GetAttrString(_pymsg, "top_negative_scores");
    if (!field) {
      return false;
    }
    if (PyObject_CheckBuffer(field)) {
      // Optimization for converting arrays of primitives
      Py_buffer view;
      int rc = PyObject_GetBuffer(field, &view, PyBUF_SIMPLE);
      if (rc < 0) {
        Py_DECREF(field);
        return false;
      }
      Py_ssize_t size = view.len / sizeof(float);
      if (!rosidl_runtime_c__float__Sequence__init(&(ros_message->top_negative_scores), size)) {
        PyErr_SetString(PyExc_RuntimeError, "unable to create float__Sequence ros_message");
        PyBuffer_Release(&view);
        Py_DECREF(field);
        return false;
      }
      float * dest = ros_message->top_negative_scores.data;
      rc = PyBuffer_ToContiguous(dest, &view, view.len, 'C');
      if (rc < 0) {
        PyBuffer_Release(&view);
        Py_DECREF(field);
        return false;
      }
      PyBuffer_Release(&view);
    } else {
      PyObject * seq_field = PySequence_Fast(field, "expected a sequence in 'top_negative_scores'");
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
      if (!rosidl_runtime_c__float__Sequence__init(&(ros_message->top_negative_scores), size)) {
        PyErr_SetString(PyExc_RuntimeError, "unable to create float__Sequence ros_message");
        Py_DECREF(seq_field);
        Py_DECREF(field);
        return false;
      }
      float * dest = ros_message->top_negative_scores.data;
      for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject * item = PySequence_Fast_GET_ITEM(seq_field, i);
        if (!item) {
          Py_DECREF(seq_field);
          Py_DECREF(field);
          return false;
        }
        assert(PyFloat_Check(item));
        float tmp = (float)PyFloat_AS_DOUBLE(item);
        memcpy(&dest[i], &tmp, sizeof(float));
      }
      Py_DECREF(seq_field);
    }
    Py_DECREF(field);
  }
  {  // thresholds_enforced
    PyObject * field = PyObject_GetAttrString(_pymsg, "thresholds_enforced");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->thresholds_enforced = (Py_True == field);
    Py_DECREF(field);
  }
  {  // passed_positive_threshold
    PyObject * field = PyObject_GetAttrString(_pymsg, "passed_positive_threshold");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->passed_positive_threshold = (Py_True == field);
    Py_DECREF(field);
  }
  {  // passed_margin_threshold
    PyObject * field = PyObject_GetAttrString(_pymsg, "passed_margin_threshold");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->passed_margin_threshold = (Py_True == field);
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
  {  // preprocessing_ms
    PyObject * field = PyObject_GetAttrString(_pymsg, "preprocessing_ms");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->preprocessing_ms = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // inference_ms
    PyObject * field = PyObject_GetAttrString(_pymsg, "inference_ms");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->inference_ms = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // matching_ms
    PyObject * field = PyObject_GetAttrString(_pymsg, "matching_ms");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->matching_ms = (float)PyFloat_AS_DOUBLE(field);
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
PyObject * macrobot_interfaces__msg__embedding_retrieval_result__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of EmbeddingRetrievalResult */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("macrobot_interfaces.msg._embedding_retrieval_result");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "EmbeddingRetrievalResult");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  macrobot_interfaces__msg__EmbeddingRetrievalResult * ros_message = (macrobot_interfaces__msg__EmbeddingRetrievalResult *)raw_ros_message;
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
  {  // model_id
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->model_id.data,
      strlen(ros_message->model_id.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "model_id", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // pooling
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->pooling.data,
      strlen(ros_message->pooling.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "pooling", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // device
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->device.data,
      strlen(ros_message->device.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "device", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // embedding_dim
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->embedding_dim);
    {
      int rc = PyObject_SetAttrString(_pymessage, "embedding_dim", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // positive_bank_available
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->positive_bank_available ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "positive_bank_available", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // positive_reference_count
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->positive_reference_count);
    {
      int rc = PyObject_SetAttrString(_pymessage, "positive_reference_count", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // negative_bank_available
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->negative_bank_available ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "negative_bank_available", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // negative_reference_count
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->negative_reference_count);
    {
      int rc = PyObject_SetAttrString(_pymessage, "negative_reference_count", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // foreground_mask_used
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->foreground_mask_used ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "foreground_mask_used", field);
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
  {  // positive_similarity
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->positive_similarity);
    {
      int rc = PyObject_SetAttrString(_pymessage, "positive_similarity", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // best_positive_similarity
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->best_positive_similarity);
    {
      int rc = PyObject_SetAttrString(_pymessage, "best_positive_similarity", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // negative_similarity
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->negative_similarity);
    {
      int rc = PyObject_SetAttrString(_pymessage, "negative_similarity", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // best_negative_similarity
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->best_negative_similarity);
    {
      int rc = PyObject_SetAttrString(_pymessage, "best_negative_similarity", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // margin
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->margin);
    {
      int rc = PyObject_SetAttrString(_pymessage, "margin", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // best_positive_path
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->best_positive_path.data,
      strlen(ros_message->best_positive_path.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "best_positive_path", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // best_negative_path
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->best_negative_path.data,
      strlen(ros_message->best_negative_path.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "best_negative_path", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // top_positive_paths
    PyObject * field = NULL;
    size_t size = ros_message->top_positive_paths.size;
    rosidl_runtime_c__String * src = ros_message->top_positive_paths.data;
    field = PyList_New(size);
    if (!field) {
      return NULL;
    }
    for (size_t i = 0; i < size; ++i) {
      PyObject * decoded_item = PyUnicode_DecodeUTF8(src[i].data, strlen(src[i].data), "replace");
      if (!decoded_item) {
        return NULL;
      }
      int rc = PyList_SetItem(field, i, decoded_item);
      (void)rc;
      assert(rc == 0);
    }
    assert(PySequence_Check(field));
    {
      int rc = PyObject_SetAttrString(_pymessage, "top_positive_paths", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // top_positive_scores
    PyObject * field = NULL;
    field = PyObject_GetAttrString(_pymessage, "top_positive_scores");
    if (!field) {
      return NULL;
    }
    assert(field->ob_type != NULL);
    assert(field->ob_type->tp_name != NULL);
    assert(strcmp(field->ob_type->tp_name, "array.array") == 0);
    // ensure that itemsize matches the sizeof of the ROS message field
    PyObject * itemsize_attr = PyObject_GetAttrString(field, "itemsize");
    assert(itemsize_attr != NULL);
    size_t itemsize = PyLong_AsSize_t(itemsize_attr);
    Py_DECREF(itemsize_attr);
    if (itemsize != sizeof(float)) {
      PyErr_SetString(PyExc_RuntimeError, "itemsize doesn't match expectation");
      Py_DECREF(field);
      return NULL;
    }
    // clear the array, poor approach to remove potential default values
    Py_ssize_t length = PyObject_Length(field);
    if (-1 == length) {
      Py_DECREF(field);
      return NULL;
    }
    if (length > 0) {
      PyObject * pop = PyObject_GetAttrString(field, "pop");
      assert(pop != NULL);
      for (Py_ssize_t i = 0; i < length; ++i) {
        PyObject * ret = PyObject_CallFunctionObjArgs(pop, NULL);
        if (!ret) {
          Py_DECREF(pop);
          Py_DECREF(field);
          return NULL;
        }
        Py_DECREF(ret);
      }
      Py_DECREF(pop);
    }
    if (ros_message->top_positive_scores.size > 0) {
      // populating the array.array using the frombytes method
      PyObject * frombytes = PyObject_GetAttrString(field, "frombytes");
      assert(frombytes != NULL);
      float * src = &(ros_message->top_positive_scores.data[0]);
      PyObject * data = PyBytes_FromStringAndSize((const char *)src, ros_message->top_positive_scores.size * sizeof(float));
      assert(data != NULL);
      PyObject * ret = PyObject_CallFunctionObjArgs(frombytes, data, NULL);
      Py_DECREF(data);
      Py_DECREF(frombytes);
      if (!ret) {
        Py_DECREF(field);
        return NULL;
      }
      Py_DECREF(ret);
    }
    Py_DECREF(field);
  }
  {  // top_negative_paths
    PyObject * field = NULL;
    size_t size = ros_message->top_negative_paths.size;
    rosidl_runtime_c__String * src = ros_message->top_negative_paths.data;
    field = PyList_New(size);
    if (!field) {
      return NULL;
    }
    for (size_t i = 0; i < size; ++i) {
      PyObject * decoded_item = PyUnicode_DecodeUTF8(src[i].data, strlen(src[i].data), "replace");
      if (!decoded_item) {
        return NULL;
      }
      int rc = PyList_SetItem(field, i, decoded_item);
      (void)rc;
      assert(rc == 0);
    }
    assert(PySequence_Check(field));
    {
      int rc = PyObject_SetAttrString(_pymessage, "top_negative_paths", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // top_negative_scores
    PyObject * field = NULL;
    field = PyObject_GetAttrString(_pymessage, "top_negative_scores");
    if (!field) {
      return NULL;
    }
    assert(field->ob_type != NULL);
    assert(field->ob_type->tp_name != NULL);
    assert(strcmp(field->ob_type->tp_name, "array.array") == 0);
    // ensure that itemsize matches the sizeof of the ROS message field
    PyObject * itemsize_attr = PyObject_GetAttrString(field, "itemsize");
    assert(itemsize_attr != NULL);
    size_t itemsize = PyLong_AsSize_t(itemsize_attr);
    Py_DECREF(itemsize_attr);
    if (itemsize != sizeof(float)) {
      PyErr_SetString(PyExc_RuntimeError, "itemsize doesn't match expectation");
      Py_DECREF(field);
      return NULL;
    }
    // clear the array, poor approach to remove potential default values
    Py_ssize_t length = PyObject_Length(field);
    if (-1 == length) {
      Py_DECREF(field);
      return NULL;
    }
    if (length > 0) {
      PyObject * pop = PyObject_GetAttrString(field, "pop");
      assert(pop != NULL);
      for (Py_ssize_t i = 0; i < length; ++i) {
        PyObject * ret = PyObject_CallFunctionObjArgs(pop, NULL);
        if (!ret) {
          Py_DECREF(pop);
          Py_DECREF(field);
          return NULL;
        }
        Py_DECREF(ret);
      }
      Py_DECREF(pop);
    }
    if (ros_message->top_negative_scores.size > 0) {
      // populating the array.array using the frombytes method
      PyObject * frombytes = PyObject_GetAttrString(field, "frombytes");
      assert(frombytes != NULL);
      float * src = &(ros_message->top_negative_scores.data[0]);
      PyObject * data = PyBytes_FromStringAndSize((const char *)src, ros_message->top_negative_scores.size * sizeof(float));
      assert(data != NULL);
      PyObject * ret = PyObject_CallFunctionObjArgs(frombytes, data, NULL);
      Py_DECREF(data);
      Py_DECREF(frombytes);
      if (!ret) {
        Py_DECREF(field);
        return NULL;
      }
      Py_DECREF(ret);
    }
    Py_DECREF(field);
  }
  {  // thresholds_enforced
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->thresholds_enforced ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "thresholds_enforced", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // passed_positive_threshold
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->passed_positive_threshold ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "passed_positive_threshold", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // passed_margin_threshold
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->passed_margin_threshold ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "passed_margin_threshold", field);
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
  {  // preprocessing_ms
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->preprocessing_ms);
    {
      int rc = PyObject_SetAttrString(_pymessage, "preprocessing_ms", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // inference_ms
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->inference_ms);
    {
      int rc = PyObject_SetAttrString(_pymessage, "inference_ms", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // matching_ms
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->matching_ms);
    {
      int rc = PyObject_SetAttrString(_pymessage, "matching_ms", field);
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
