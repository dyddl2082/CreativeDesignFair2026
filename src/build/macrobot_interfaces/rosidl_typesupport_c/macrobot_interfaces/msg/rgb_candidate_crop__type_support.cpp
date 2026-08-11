// generated from rosidl_typesupport_c/resource/idl__type_support.cpp.em
// with input from macrobot_interfaces:msg/RgbCandidateCrop.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__struct.h"
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__type_support.h"
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__functions.h"
#include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/message_type_support_dispatch.h"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_c/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace macrobot_interfaces
{

namespace msg
{

namespace rosidl_typesupport_c
{

typedef struct _RgbCandidateCrop_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _RgbCandidateCrop_type_support_ids_t;

static const _RgbCandidateCrop_type_support_ids_t _RgbCandidateCrop_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _RgbCandidateCrop_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _RgbCandidateCrop_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _RgbCandidateCrop_type_support_symbol_names_t _RgbCandidateCrop_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, macrobot_interfaces, msg, RgbCandidateCrop)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, macrobot_interfaces, msg, RgbCandidateCrop)),
  }
};

typedef struct _RgbCandidateCrop_type_support_data_t
{
  void * data[2];
} _RgbCandidateCrop_type_support_data_t;

static _RgbCandidateCrop_type_support_data_t _RgbCandidateCrop_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _RgbCandidateCrop_message_typesupport_map = {
  2,
  "macrobot_interfaces",
  &_RgbCandidateCrop_message_typesupport_ids.typesupport_identifier[0],
  &_RgbCandidateCrop_message_typesupport_symbol_names.symbol_name[0],
  &_RgbCandidateCrop_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t RgbCandidateCrop_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_RgbCandidateCrop_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
  &macrobot_interfaces__msg__RgbCandidateCrop__get_type_hash,
  &macrobot_interfaces__msg__RgbCandidateCrop__get_type_description,
  &macrobot_interfaces__msg__RgbCandidateCrop__get_type_description_sources,
};

}  // namespace rosidl_typesupport_c

}  // namespace msg

}  // namespace macrobot_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, macrobot_interfaces, msg, RgbCandidateCrop)() {
  return &::macrobot_interfaces::msg::rosidl_typesupport_c::RgbCandidateCrop_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
