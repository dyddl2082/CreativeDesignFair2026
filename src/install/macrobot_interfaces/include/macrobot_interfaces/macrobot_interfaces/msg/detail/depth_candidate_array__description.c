// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from macrobot_interfaces:msg/DepthCandidateArray.idl
// generated code does not contain a copyright notice

#include "macrobot_interfaces/msg/detail/depth_candidate_array__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
const rosidl_type_hash_t *
macrobot_interfaces__msg__DepthCandidateArray__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x37, 0x60, 0x4f, 0xed, 0x04, 0x5c, 0xfd, 0x12,
      0xc0, 0xe5, 0x37, 0xc9, 0x01, 0xfd, 0xee, 0x54,
      0xad, 0x75, 0x7e, 0x87, 0xfa, 0xa1, 0x4e, 0x8e,
      0xbd, 0x62, 0x51, 0xc1, 0x4b, 0xe0, 0xc2, 0xe5,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "builtin_interfaces/msg/detail/time__functions.h"
#include "std_msgs/msg/detail/header__functions.h"
#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"
#include "sensor_msgs/msg/detail/compressed_image__functions.h"
#include "sensor_msgs/msg/detail/region_of_interest__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t builtin_interfaces__msg__Time__EXPECTED_HASH = {1, {
    0xb1, 0x06, 0x23, 0x5e, 0x25, 0xa4, 0xc5, 0xed,
    0x35, 0x09, 0x8a, 0xa0, 0xa6, 0x1a, 0x3e, 0xe9,
    0xc9, 0xb1, 0x8d, 0x19, 0x7f, 0x39, 0x8b, 0x0e,
    0x42, 0x06, 0xce, 0xa9, 0xac, 0xf9, 0xc1, 0x97,
  }};
static const rosidl_type_hash_t macrobot_interfaces__msg__DepthCandidate__EXPECTED_HASH = {1, {
    0xcd, 0xeb, 0x51, 0xb8, 0xe3, 0x2f, 0x64, 0x0a,
    0x5f, 0x3b, 0x1d, 0xf1, 0x76, 0x6d, 0x49, 0x72,
    0x2e, 0x46, 0x92, 0xf7, 0x8e, 0x27, 0x5d, 0xe7,
    0x2d, 0x4f, 0xac, 0xec, 0x63, 0x64, 0x59, 0x34,
  }};
static const rosidl_type_hash_t sensor_msgs__msg__CompressedImage__EXPECTED_HASH = {1, {
    0x15, 0x64, 0x07, 0x71, 0x53, 0x15, 0x71, 0x18,
    0x5e, 0x2e, 0xfc, 0x8a, 0x10, 0x0b, 0xaf, 0x92,
    0x39, 0x61, 0xa4, 0xd1, 0x5d, 0x55, 0x69, 0x65,
    0x2e, 0x6c, 0xb6, 0x69, 0x1e, 0x8e, 0x37, 0x1a,
  }};
static const rosidl_type_hash_t sensor_msgs__msg__RegionOfInterest__EXPECTED_HASH = {1, {
    0xad, 0x16, 0xbc, 0xba, 0x5f, 0x91, 0x31, 0xdc,
    0xdb, 0xa6, 0xfb, 0xde, 0xd1, 0x9f, 0x72, 0x6f,
    0x54, 0x40, 0xe3, 0xc5, 0x13, 0xb4, 0xfb, 0x58,
    0x6d, 0xd3, 0x02, 0x7e, 0xee, 0xd8, 0xab, 0xb1,
  }};
static const rosidl_type_hash_t std_msgs__msg__Header__EXPECTED_HASH = {1, {
    0xf4, 0x9f, 0xb3, 0xae, 0x2c, 0xf0, 0x70, 0xf7,
    0x93, 0x64, 0x5f, 0xf7, 0x49, 0x68, 0x3a, 0xc6,
    0xb0, 0x62, 0x03, 0xe4, 0x1c, 0x89, 0x1e, 0x17,
    0x70, 0x1b, 0x1c, 0xb5, 0x97, 0xce, 0x6a, 0x01,
  }};
#endif

static char macrobot_interfaces__msg__DepthCandidateArray__TYPE_NAME[] = "macrobot_interfaces/msg/DepthCandidateArray";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char macrobot_interfaces__msg__DepthCandidate__TYPE_NAME[] = "macrobot_interfaces/msg/DepthCandidate";
static char sensor_msgs__msg__CompressedImage__TYPE_NAME[] = "sensor_msgs/msg/CompressedImage";
static char sensor_msgs__msg__RegionOfInterest__TYPE_NAME[] = "sensor_msgs/msg/RegionOfInterest";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";

// Define type names, field names, and default values
static char macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__header[] = "header";
static char macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__image_width[] = "image_width";
static char macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__image_height[] = "image_height";
static char macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__plane_found[] = "plane_found";
static char macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__plane_inlier_ratio[] = "plane_inlier_ratio";
static char macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__plane_coefficients[] = "plane_coefficients";
static char macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__foreground_mask_available[] = "foreground_mask_available";
static char macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__foreground_mask[] = "foreground_mask";
static char macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__candidates[] = "candidates";

static rosidl_runtime_c__type_description__Field macrobot_interfaces__msg__DepthCandidateArray__FIELDS[] = {
  {
    {macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__header, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__image_width, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__image_height, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__plane_found, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__plane_inlier_ratio, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__plane_coefficients, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      4,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__foreground_mask_available, 25, 25},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__foreground_mask, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {sensor_msgs__msg__CompressedImage__TYPE_NAME, 31, 31},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidateArray__FIELD_NAME__candidates, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {macrobot_interfaces__msg__DepthCandidate__TYPE_NAME, 38, 38},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription macrobot_interfaces__msg__DepthCandidateArray__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__TYPE_NAME, 38, 38},
    {NULL, 0, 0},
  },
  {
    {sensor_msgs__msg__CompressedImage__TYPE_NAME, 31, 31},
    {NULL, 0, 0},
  },
  {
    {sensor_msgs__msg__RegionOfInterest__TYPE_NAME, 32, 32},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
macrobot_interfaces__msg__DepthCandidateArray__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {macrobot_interfaces__msg__DepthCandidateArray__TYPE_NAME, 43, 43},
      {macrobot_interfaces__msg__DepthCandidateArray__FIELDS, 9, 9},
    },
    {macrobot_interfaces__msg__DepthCandidateArray__REFERENCED_TYPE_DESCRIPTIONS, 5, 5},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&macrobot_interfaces__msg__DepthCandidate__EXPECTED_HASH, macrobot_interfaces__msg__DepthCandidate__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = macrobot_interfaces__msg__DepthCandidate__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__CompressedImage__EXPECTED_HASH, sensor_msgs__msg__CompressedImage__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = sensor_msgs__msg__CompressedImage__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__RegionOfInterest__EXPECTED_HASH, sensor_msgs__msg__RegionOfInterest__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = sensor_msgs__msg__RegionOfInterest__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Header copied from the source aligned-depth image.\n"
  "std_msgs/Header header\n"
  "\n"
  "uint32 image_width\n"
  "uint32 image_height\n"
  "\n"
  "# Background-plane diagnostics for this frame.\n"
  "bool plane_found\n"
  "float32 plane_inlier_ratio\n"
  "float32[4] plane_coefficients\n"
  "\n"
  "# Full-frame binary foreground mask in proposal/depth coordinates.\n"
  "# Pixel values are 0 for background and 255 for foreground.\n"
  "bool foreground_mask_available\n"
  "sensor_msgs/CompressedImage foreground_mask\n"
  "\n"
  "DepthCandidate[] candidates";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
macrobot_interfaces__msg__DepthCandidateArray__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {macrobot_interfaces__msg__DepthCandidateArray__TYPE_NAME, 43, 43},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 470, 470},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
macrobot_interfaces__msg__DepthCandidateArray__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[6];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 6, 6};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *macrobot_interfaces__msg__DepthCandidateArray__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *macrobot_interfaces__msg__DepthCandidate__get_individual_type_description_source(NULL);
    sources[3] = *sensor_msgs__msg__CompressedImage__get_individual_type_description_source(NULL);
    sources[4] = *sensor_msgs__msg__RegionOfInterest__get_individual_type_description_source(NULL);
    sources[5] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
