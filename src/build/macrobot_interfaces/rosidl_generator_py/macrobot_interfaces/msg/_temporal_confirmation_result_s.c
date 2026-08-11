// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from macrobot_interfaces:msg/TemporalConfirmationResult.idl
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
#include "macrobot_interfaces/msg/detail/temporal_confirmation_result__struct.h"
#include "macrobot_interfaces/msg/detail/temporal_confirmation_result__functions.h"

#include "rosidl_runtime_c/string.h"
#include "rosidl_runtime_c/string_functions.h"

ROSIDL_GENERATOR_C_IMPORT
bool std_msgs__msg__header__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * std_msgs__msg__header__convert_to_py(void * raw_ros_message);
ROSIDL_GENERATOR_C_IMPORT
bool sensor_msgs__msg__region_of_interest__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * sensor_msgs__msg__region_of_interest__convert_to_py(void * raw_ros_message);
bool macrobot_interfaces__msg__embedding_retrieval_result__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * macrobot_interfaces__msg__embedding_retrieval_result__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool macrobot_interfaces__msg__temporal_confirmation_result__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[81];
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
    assert(strncmp("macrobot_interfaces.msg._temporal_confirmation_result.TemporalConfirmationResult", full_classname_dest, 80) == 0);
  }
  macrobot_interfaces__msg__TemporalConfirmationResult * ros_message = _ros_message;
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
  {  // track_id
    PyObject * field = PyObject_GetAttrString(_pymsg, "track_id");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->track_id = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // frame_index
    PyObject * field = PyObject_GetAttrString(_pymsg, "frame_index");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->frame_index = PyLong_AsUnsignedLongLong(field);
    Py_DECREF(field);
  }
  {  // state
    PyObject * field = PyObject_GetAttrString(_pymsg, "state");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->state, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // event
    PyObject * field = PyObject_GetAttrString(_pymsg, "event");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->event, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // confirmed
    PyObject * field = PyObject_GetAttrString(_pymsg, "confirmed");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->confirmed = (Py_True == field);
    Py_DECREF(field);
  }
  {  // track_age_frames
    PyObject * field = PyObject_GetAttrString(_pymsg, "track_age_frames");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->track_age_frames = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // window_size
    PyObject * field = PyObject_GetAttrString(_pymsg, "window_size");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->window_size = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // required_hits
    PyObject * field = PyObject_GetAttrString(_pymsg, "required_hits");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->required_hits = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // samples_in_window
    PyObject * field = PyObject_GetAttrString(_pymsg, "samples_in_window");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->samples_in_window = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // matched_frames_in_window
    PyObject * field = PyObject_GetAttrString(_pymsg, "matched_frames_in_window");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->matched_frames_in_window = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // hits_in_window
    PyObject * field = PyObject_GetAttrString(_pymsg, "hits_in_window");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->hits_in_window = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // misses_in_window
    PyObject * field = PyObject_GetAttrString(_pymsg, "misses_in_window");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->misses_in_window = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // consecutive_hits
    PyObject * field = PyObject_GetAttrString(_pymsg, "consecutive_hits");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->consecutive_hits = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // consecutive_misses
    PyObject * field = PyObject_GetAttrString(_pymsg, "consecutive_misses");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->consecutive_misses = PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // hit_ratio
    PyObject * field = PyObject_GetAttrString(_pymsg, "hit_ratio");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->hit_ratio = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // temporal_score
    PyObject * field = PyObject_GetAttrString(_pymsg, "temporal_score");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->temporal_score = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // stability_score
    PyObject * field = PyObject_GetAttrString(_pymsg, "stability_score");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->stability_score = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // mean_positive_similarity
    PyObject * field = PyObject_GetAttrString(_pymsg, "mean_positive_similarity");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->mean_positive_similarity = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // mean_negative_similarity
    PyObject * field = PyObject_GetAttrString(_pymsg, "mean_negative_similarity");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->mean_negative_similarity = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // mean_margin
    PyObject * field = PyObject_GetAttrString(_pymsg, "mean_margin");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->mean_margin = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // min_margin_in_window
    PyObject * field = PyObject_GetAttrString(_pymsg, "min_margin_in_window");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->min_margin_in_window = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // mean_objectness_score
    PyObject * field = PyObject_GetAttrString(_pymsg, "mean_objectness_score");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->mean_objectness_score = (float)PyFloat_AS_DOUBLE(field);
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
  {  // depth_m
    PyObject * field = PyObject_GetAttrString(_pymsg, "depth_m");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->depth_m = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // center_std_px
    PyObject * field = PyObject_GetAttrString(_pymsg, "center_std_px");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->center_std_px = (float)PyFloat_AS_DOUBLE(field);
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
  {  // horizontal_error_norm
    PyObject * field = PyObject_GetAttrString(_pymsg, "horizontal_error_norm");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->horizontal_error_norm = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // suggested_turn
    PyObject * field = PyObject_GetAttrString(_pymsg, "suggested_turn");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->suggested_turn, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // latest_result
    PyObject * field = PyObject_GetAttrString(_pymsg, "latest_result");
    if (!field) {
      return false;
    }
    if (!macrobot_interfaces__msg__embedding_retrieval_result__convert_from_py(field, &ros_message->latest_result)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * macrobot_interfaces__msg__temporal_confirmation_result__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of TemporalConfirmationResult */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("macrobot_interfaces.msg._temporal_confirmation_result");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "TemporalConfirmationResult");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  macrobot_interfaces__msg__TemporalConfirmationResult * ros_message = (macrobot_interfaces__msg__TemporalConfirmationResult *)raw_ros_message;
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
  {  // track_id
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->track_id);
    {
      int rc = PyObject_SetAttrString(_pymessage, "track_id", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // frame_index
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLongLong(ros_message->frame_index);
    {
      int rc = PyObject_SetAttrString(_pymessage, "frame_index", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // state
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->state.data,
      strlen(ros_message->state.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "state", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // event
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->event.data,
      strlen(ros_message->event.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "event", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // confirmed
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->confirmed ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "confirmed", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // track_age_frames
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->track_age_frames);
    {
      int rc = PyObject_SetAttrString(_pymessage, "track_age_frames", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // window_size
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->window_size);
    {
      int rc = PyObject_SetAttrString(_pymessage, "window_size", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // required_hits
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->required_hits);
    {
      int rc = PyObject_SetAttrString(_pymessage, "required_hits", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // samples_in_window
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->samples_in_window);
    {
      int rc = PyObject_SetAttrString(_pymessage, "samples_in_window", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // matched_frames_in_window
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->matched_frames_in_window);
    {
      int rc = PyObject_SetAttrString(_pymessage, "matched_frames_in_window", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // hits_in_window
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->hits_in_window);
    {
      int rc = PyObject_SetAttrString(_pymessage, "hits_in_window", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // misses_in_window
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->misses_in_window);
    {
      int rc = PyObject_SetAttrString(_pymessage, "misses_in_window", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // consecutive_hits
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->consecutive_hits);
    {
      int rc = PyObject_SetAttrString(_pymessage, "consecutive_hits", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // consecutive_misses
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->consecutive_misses);
    {
      int rc = PyObject_SetAttrString(_pymessage, "consecutive_misses", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // hit_ratio
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->hit_ratio);
    {
      int rc = PyObject_SetAttrString(_pymessage, "hit_ratio", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // temporal_score
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->temporal_score);
    {
      int rc = PyObject_SetAttrString(_pymessage, "temporal_score", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // stability_score
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->stability_score);
    {
      int rc = PyObject_SetAttrString(_pymessage, "stability_score", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // mean_positive_similarity
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->mean_positive_similarity);
    {
      int rc = PyObject_SetAttrString(_pymessage, "mean_positive_similarity", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // mean_negative_similarity
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->mean_negative_similarity);
    {
      int rc = PyObject_SetAttrString(_pymessage, "mean_negative_similarity", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // mean_margin
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->mean_margin);
    {
      int rc = PyObject_SetAttrString(_pymessage, "mean_margin", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // min_margin_in_window
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->min_margin_in_window);
    {
      int rc = PyObject_SetAttrString(_pymessage, "min_margin_in_window", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // mean_objectness_score
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->mean_objectness_score);
    {
      int rc = PyObject_SetAttrString(_pymessage, "mean_objectness_score", field);
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
  {  // depth_m
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->depth_m);
    {
      int rc = PyObject_SetAttrString(_pymessage, "depth_m", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // center_std_px
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->center_std_px);
    {
      int rc = PyObject_SetAttrString(_pymessage, "center_std_px", field);
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
  {  // horizontal_error_norm
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->horizontal_error_norm);
    {
      int rc = PyObject_SetAttrString(_pymessage, "horizontal_error_norm", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // suggested_turn
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->suggested_turn.data,
      strlen(ros_message->suggested_turn.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "suggested_turn", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // latest_result
    PyObject * field = NULL;
    field = macrobot_interfaces__msg__embedding_retrieval_result__convert_to_py(&ros_message->latest_result);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "latest_result", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
