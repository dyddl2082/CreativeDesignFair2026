// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from macrobot_interfaces:msg/DepthCandidate.idl
// generated code does not contain a copyright notice

#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
const rosidl_type_hash_t *
macrobot_interfaces__msg__DepthCandidate__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xcd, 0xeb, 0x51, 0xb8, 0xe3, 0x2f, 0x64, 0x0a,
      0x5f, 0x3b, 0x1d, 0xf1, 0x76, 0x6d, 0x49, 0x72,
      0x2e, 0x46, 0x92, 0xf7, 0x8e, 0x27, 0x5d, 0xe7,
      0x2d, 0x4f, 0xac, 0xec, 0x63, 0x64, 0x59, 0x34,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "sensor_msgs/msg/detail/region_of_interest__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t sensor_msgs__msg__RegionOfInterest__EXPECTED_HASH = {1, {
    0xad, 0x16, 0xbc, 0xba, 0x5f, 0x91, 0x31, 0xdc,
    0xdb, 0xa6, 0xfb, 0xde, 0xd1, 0x9f, 0x72, 0x6f,
    0x54, 0x40, 0xe3, 0xc5, 0x13, 0xb4, 0xfb, 0x58,
    0x6d, 0xd3, 0x02, 0x7e, 0xee, 0xd8, 0xab, 0xb1,
  }};
#endif

static char macrobot_interfaces__msg__DepthCandidate__TYPE_NAME[] = "macrobot_interfaces/msg/DepthCandidate";
static char sensor_msgs__msg__RegionOfInterest__TYPE_NAME[] = "sensor_msgs/msg/RegionOfInterest";

// Define type names, field names, and default values
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__id[] = "id";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__roi[] = "roi";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__center_x[] = "center_x";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__center_y[] = "center_y";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__median_depth_m[] = "median_depth_m";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__near_depth_m[] = "near_depth_m";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__far_depth_m[] = "far_depth_m";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__depth_std_m[] = "depth_std_m";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__valid_depth_ratio[] = "valid_depth_ratio";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__fill_ratio[] = "fill_ratio";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__area_ratio[] = "area_ratio";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__foreground_height_m[] = "foreground_height_m";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__foreground_height_valid[] = "foreground_height_valid";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__proposal_score[] = "proposal_score";
static char macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__touches_border[] = "touches_border";

static rosidl_runtime_c__type_description__Field macrobot_interfaces__msg__DepthCandidate__FIELDS[] = {
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__id, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__roi, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {sensor_msgs__msg__RegionOfInterest__TYPE_NAME, 32, 32},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__center_x, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__center_y, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__median_depth_m, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__near_depth_m, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__far_depth_m, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__depth_std_m, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__valid_depth_ratio, 17, 17},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__fill_ratio, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__area_ratio, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__foreground_height_m, 19, 19},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__foreground_height_valid, 23, 23},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__proposal_score, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__FIELD_NAME__touches_border, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription macrobot_interfaces__msg__DepthCandidate__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {sensor_msgs__msg__RegionOfInterest__TYPE_NAME, 32, 32},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
macrobot_interfaces__msg__DepthCandidate__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {macrobot_interfaces__msg__DepthCandidate__TYPE_NAME, 38, 38},
      {macrobot_interfaces__msg__DepthCandidate__FIELDS, 15, 15},
    },
    {macrobot_interfaces__msg__DepthCandidate__REFERENCED_TYPE_DESCRIPTIONS, 1, 1},
  };
  if (!constructed) {
    assert(0 == memcmp(&sensor_msgs__msg__RegionOfInterest__EXPECTED_HASH, sensor_msgs__msg__RegionOfInterest__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = sensor_msgs__msg__RegionOfInterest__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Frame-local identifier. It is not a persistent tracking ID.\n"
  "uint32 id\n"
  "\n"
  "# Padded region that can be applied directly to the aligned RGB image.\n"
  "sensor_msgs/RegionOfInterest roi\n"
  "\n"
  "# Connected-component centroid in image pixels.\n"
  "float32 center_x\n"
  "float32 center_y\n"
  "\n"
  "# Robust depth statistics computed from the component pixels.\n"
  "float32 median_depth_m\n"
  "float32 near_depth_m\n"
  "float32 far_depth_m\n"
  "float32 depth_std_m\n"
  "\n"
  "# Component-quality descriptors.\n"
  "float32 valid_depth_ratio\n"
  "float32 fill_ratio\n"
  "float32 area_ratio\n"
  "\n"
  "# Median optical-axis separation from the fitted background plane.\n"
  "# Zero when plane removal was unavailable and fallback mode was used.\n"
  "float32 foreground_height_m\n"
  "\n"
  "# True only when foreground_height_m was measured from a valid fitted plane.\n"
  "# False means the height is unavailable, not that the measured height is zero.\n"
  "bool foreground_height_valid\n"
  "\n"
  "# Heuristic proposal score in the range [0, 1].\n"
  "float32 proposal_score\n"
  "\n"
  "# True when the unpadded component touches the configured image border.\n"
  "bool touches_border";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
macrobot_interfaces__msg__DepthCandidate__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {macrobot_interfaces__msg__DepthCandidate__TYPE_NAME, 38, 38},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 1022, 1022},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
macrobot_interfaces__msg__DepthCandidate__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[2];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 2, 2};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *macrobot_interfaces__msg__DepthCandidate__get_individual_type_description_source(NULL),
    sources[1] = *sensor_msgs__msg__RegionOfInterest__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
