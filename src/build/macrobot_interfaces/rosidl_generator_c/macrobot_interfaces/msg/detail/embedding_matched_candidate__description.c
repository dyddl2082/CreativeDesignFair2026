// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from macrobot_interfaces:msg/EmbeddingMatchedCandidate.idl
// generated code does not contain a copyright notice

#include "macrobot_interfaces/msg/detail/embedding_matched_candidate__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
const rosidl_type_hash_t *
macrobot_interfaces__msg__EmbeddingMatchedCandidate__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xed, 0xc8, 0x60, 0x3b, 0xe6, 0x38, 0x2e, 0x24,
      0xb2, 0x69, 0x0f, 0xed, 0x0e, 0x87, 0x74, 0x76,
      0x7b, 0x88, 0xfb, 0x97, 0x3b, 0x5d, 0x91, 0x42,
      0x0b, 0x5e, 0x18, 0x03, 0x66, 0x5e, 0x47, 0x61,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "builtin_interfaces/msg/detail/time__functions.h"
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__functions.h"
#include "std_msgs/msg/detail/header__functions.h"
#include "macrobot_interfaces/msg/detail/filtered_candidate_crop__functions.h"
#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"
#include "macrobot_interfaces/msg/detail/candidate_filter_result__functions.h"
#include "macrobot_interfaces/msg/detail/rgb_candidate_crop__functions.h"
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
static const rosidl_type_hash_t macrobot_interfaces__msg__CandidateFilterResult__EXPECTED_HASH = {1, {
    0xab, 0xbc, 0x99, 0x8e, 0x6f, 0x1f, 0xd5, 0x98,
    0x16, 0x0b, 0x9d, 0x75, 0x52, 0x59, 0x79, 0xa6,
    0x48, 0x6d, 0x14, 0x1d, 0xc3, 0xd6, 0xac, 0x8c,
    0x21, 0xc0, 0x38, 0xaf, 0x4a, 0x90, 0x7b, 0xd1,
  }};
static const rosidl_type_hash_t macrobot_interfaces__msg__DepthCandidate__EXPECTED_HASH = {1, {
    0xcd, 0xeb, 0x51, 0xb8, 0xe3, 0x2f, 0x64, 0x0a,
    0x5f, 0x3b, 0x1d, 0xf1, 0x76, 0x6d, 0x49, 0x72,
    0x2e, 0x46, 0x92, 0xf7, 0x8e, 0x27, 0x5d, 0xe7,
    0x2d, 0x4f, 0xac, 0xec, 0x63, 0x64, 0x59, 0x34,
  }};
static const rosidl_type_hash_t macrobot_interfaces__msg__EmbeddingRetrievalResult__EXPECTED_HASH = {1, {
    0xdb, 0x59, 0x19, 0xcb, 0x0a, 0xc2, 0x5e, 0x05,
    0x9a, 0xcd, 0x9c, 0x13, 0x4f, 0x57, 0x36, 0x62,
    0x67, 0x5b, 0x32, 0xe3, 0xc5, 0x70, 0x75, 0x1d,
    0x87, 0x70, 0x5f, 0x25, 0xc7, 0x74, 0xc5, 0x01,
  }};
static const rosidl_type_hash_t macrobot_interfaces__msg__FilteredCandidateCrop__EXPECTED_HASH = {1, {
    0x11, 0xa1, 0x50, 0x57, 0xf9, 0x2c, 0xcc, 0x84,
    0x9a, 0x75, 0xf4, 0xd9, 0x20, 0x96, 0xe1, 0xc2,
    0x08, 0xf0, 0x83, 0xb1, 0x69, 0xbe, 0x0a, 0xe0,
    0x57, 0x80, 0x52, 0xb4, 0x6f, 0x98, 0xbb, 0x55,
  }};
static const rosidl_type_hash_t macrobot_interfaces__msg__RgbCandidateCrop__EXPECTED_HASH = {1, {
    0x92, 0xb9, 0xa1, 0xcf, 0xfc, 0xfa, 0xa1, 0x52,
    0xd9, 0xdd, 0xb8, 0xf3, 0x5f, 0x41, 0xba, 0x6b,
    0xd2, 0xd5, 0x8b, 0x19, 0x19, 0x8d, 0x16, 0xef,
    0x74, 0xf2, 0xe3, 0xb6, 0x31, 0x7e, 0x40, 0x2c,
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

static char macrobot_interfaces__msg__EmbeddingMatchedCandidate__TYPE_NAME[] = "macrobot_interfaces/msg/EmbeddingMatchedCandidate";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char macrobot_interfaces__msg__CandidateFilterResult__TYPE_NAME[] = "macrobot_interfaces/msg/CandidateFilterResult";
static char macrobot_interfaces__msg__DepthCandidate__TYPE_NAME[] = "macrobot_interfaces/msg/DepthCandidate";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__TYPE_NAME[] = "macrobot_interfaces/msg/EmbeddingRetrievalResult";
static char macrobot_interfaces__msg__FilteredCandidateCrop__TYPE_NAME[] = "macrobot_interfaces/msg/FilteredCandidateCrop";
static char macrobot_interfaces__msg__RgbCandidateCrop__TYPE_NAME[] = "macrobot_interfaces/msg/RgbCandidateCrop";
static char sensor_msgs__msg__CompressedImage__TYPE_NAME[] = "sensor_msgs/msg/CompressedImage";
static char sensor_msgs__msg__RegionOfInterest__TYPE_NAME[] = "sensor_msgs/msg/RegionOfInterest";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";

// Define type names, field names, and default values
static char macrobot_interfaces__msg__EmbeddingMatchedCandidate__FIELD_NAME__result[] = "result";
static char macrobot_interfaces__msg__EmbeddingMatchedCandidate__FIELD_NAME__filtered_crop[] = "filtered_crop";

static rosidl_runtime_c__type_description__Field macrobot_interfaces__msg__EmbeddingMatchedCandidate__FIELDS[] = {
  {
    {macrobot_interfaces__msg__EmbeddingMatchedCandidate__FIELD_NAME__result, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {macrobot_interfaces__msg__EmbeddingRetrievalResult__TYPE_NAME, 48, 48},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingMatchedCandidate__FIELD_NAME__filtered_crop, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {macrobot_interfaces__msg__FilteredCandidateCrop__TYPE_NAME, 45, 45},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription macrobot_interfaces__msg__EmbeddingMatchedCandidate__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__CandidateFilterResult__TYPE_NAME, 45, 45},
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__TYPE_NAME, 38, 38},
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__TYPE_NAME, 48, 48},
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__FilteredCandidateCrop__TYPE_NAME, 45, 45},
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__RgbCandidateCrop__TYPE_NAME, 40, 40},
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
macrobot_interfaces__msg__EmbeddingMatchedCandidate__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {macrobot_interfaces__msg__EmbeddingMatchedCandidate__TYPE_NAME, 49, 49},
      {macrobot_interfaces__msg__EmbeddingMatchedCandidate__FIELDS, 2, 2},
    },
    {macrobot_interfaces__msg__EmbeddingMatchedCandidate__REFERENCED_TYPE_DESCRIPTIONS, 9, 9},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&macrobot_interfaces__msg__CandidateFilterResult__EXPECTED_HASH, macrobot_interfaces__msg__CandidateFilterResult__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = macrobot_interfaces__msg__CandidateFilterResult__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&macrobot_interfaces__msg__DepthCandidate__EXPECTED_HASH, macrobot_interfaces__msg__DepthCandidate__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = macrobot_interfaces__msg__DepthCandidate__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&macrobot_interfaces__msg__EmbeddingRetrievalResult__EXPECTED_HASH, macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&macrobot_interfaces__msg__FilteredCandidateCrop__EXPECTED_HASH, macrobot_interfaces__msg__FilteredCandidateCrop__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = macrobot_interfaces__msg__FilteredCandidateCrop__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&macrobot_interfaces__msg__RgbCandidateCrop__EXPECTED_HASH, macrobot_interfaces__msg__RgbCandidateCrop__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[5].fields = macrobot_interfaces__msg__RgbCandidateCrop__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__CompressedImage__EXPECTED_HASH, sensor_msgs__msg__CompressedImage__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[6].fields = sensor_msgs__msg__CompressedImage__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__RegionOfInterest__EXPECTED_HASH, sensor_msgs__msg__RegionOfInterest__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[7].fields = sensor_msgs__msg__RegionOfInterest__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[8].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Candidate forwarded to temporal confirmation after embedding retrieval.\n"
  "EmbeddingRetrievalResult result\n"
  "FilteredCandidateCrop filtered_crop";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
macrobot_interfaces__msg__EmbeddingMatchedCandidate__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {macrobot_interfaces__msg__EmbeddingMatchedCandidate__TYPE_NAME, 49, 49},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 142, 142},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
macrobot_interfaces__msg__EmbeddingMatchedCandidate__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[10];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 10, 10};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *macrobot_interfaces__msg__EmbeddingMatchedCandidate__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *macrobot_interfaces__msg__CandidateFilterResult__get_individual_type_description_source(NULL);
    sources[3] = *macrobot_interfaces__msg__DepthCandidate__get_individual_type_description_source(NULL);
    sources[4] = *macrobot_interfaces__msg__EmbeddingRetrievalResult__get_individual_type_description_source(NULL);
    sources[5] = *macrobot_interfaces__msg__FilteredCandidateCrop__get_individual_type_description_source(NULL);
    sources[6] = *macrobot_interfaces__msg__RgbCandidateCrop__get_individual_type_description_source(NULL);
    sources[7] = *sensor_msgs__msg__CompressedImage__get_individual_type_description_source(NULL);
    sources[8] = *sensor_msgs__msg__RegionOfInterest__get_individual_type_description_source(NULL);
    sources[9] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
