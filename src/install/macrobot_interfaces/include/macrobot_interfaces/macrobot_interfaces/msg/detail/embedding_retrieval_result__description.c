// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from macrobot_interfaces:msg/EmbeddingRetrievalResult.idl
// generated code does not contain a copyright notice

#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
const rosidl_type_hash_t *
macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xdb, 0x59, 0x19, 0xcb, 0x0a, 0xc2, 0x5e, 0x05,
      0x9a, 0xcd, 0x9c, 0x13, 0x4f, 0x57, 0x36, 0x62,
      0x67, 0x5b, 0x32, 0xe3, 0xc5, 0x70, 0x75, 0x1d,
      0x87, 0x70, 0x5f, 0x25, 0xc7, 0x74, 0xc5, 0x01,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "builtin_interfaces/msg/detail/time__functions.h"
#include "std_msgs/msg/detail/header__functions.h"
#include "macrobot_interfaces/msg/detail/depth_candidate__functions.h"
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

static char macrobot_interfaces__msg__EmbeddingRetrievalResult__TYPE_NAME[] = "macrobot_interfaces/msg/EmbeddingRetrievalResult";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char macrobot_interfaces__msg__DepthCandidate__TYPE_NAME[] = "macrobot_interfaces/msg/DepthCandidate";
static char sensor_msgs__msg__RegionOfInterest__TYPE_NAME[] = "sensor_msgs/msg/RegionOfInterest";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";

// Define type names, field names, and default values
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__proposal_header[] = "proposal_header";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__image_header[] = "image_header";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__candidate_id[] = "candidate_id";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__crop_index[] = "crop_index";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__frame_crop_count[] = "frame_crop_count";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__target_object[] = "target_object";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__model_id[] = "model_id";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__pooling[] = "pooling";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__device[] = "device";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__embedding_dim[] = "embedding_dim";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__positive_bank_available[] = "positive_bank_available";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__positive_reference_count[] = "positive_reference_count";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__negative_bank_available[] = "negative_bank_available";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__negative_reference_count[] = "negative_reference_count";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__foreground_mask_used[] = "foreground_mask_used";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__objectness_score[] = "objectness_score";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__target_hint_score[] = "target_hint_score";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__positive_similarity[] = "positive_similarity";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__best_positive_similarity[] = "best_positive_similarity";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__negative_similarity[] = "negative_similarity";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__best_negative_similarity[] = "best_negative_similarity";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__margin[] = "margin";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__best_positive_path[] = "best_positive_path";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__best_negative_path[] = "best_negative_path";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__top_positive_paths[] = "top_positive_paths";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__top_positive_scores[] = "top_positive_scores";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__top_negative_paths[] = "top_negative_paths";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__top_negative_scores[] = "top_negative_scores";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__thresholds_enforced[] = "thresholds_enforced";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__passed_positive_threshold[] = "passed_positive_threshold";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__passed_margin_threshold[] = "passed_margin_threshold";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__accepted[] = "accepted";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__reject_reason[] = "reject_reason";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__preprocessing_ms[] = "preprocessing_ms";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__inference_ms[] = "inference_ms";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__matching_ms[] = "matching_ms";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__candidate[] = "candidate";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__crop_roi[] = "crop_roi";

static rosidl_runtime_c__type_description__Field macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELDS[] = {
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__proposal_header, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__image_header, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__candidate_id, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__crop_index, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__frame_crop_count, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__target_object, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__model_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__pooling, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__device, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__embedding_dim, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__positive_bank_available, 23, 23},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__positive_reference_count, 24, 24},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__negative_bank_available, 23, 23},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__negative_reference_count, 24, 24},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__foreground_mask_used, 20, 20},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__objectness_score, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__target_hint_score, 17, 17},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__positive_similarity, 19, 19},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__best_positive_similarity, 24, 24},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__negative_similarity, 19, 19},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__best_negative_similarity, 24, 24},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__margin, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__best_positive_path, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__best_negative_path, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__top_positive_paths, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__top_positive_scores, 19, 19},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__top_negative_paths, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__top_negative_scores, 19, 19},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__thresholds_enforced, 19, 19},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__passed_positive_threshold, 25, 25},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__passed_margin_threshold, 23, 23},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__accepted, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__reject_reason, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__preprocessing_ms, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__inference_ms, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__matching_ms, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__candidate, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {macrobot_interfaces__msg__DepthCandidate__TYPE_NAME, 38, 38},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELD_NAME__crop_roi, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {sensor_msgs__msg__RegionOfInterest__TYPE_NAME, 32, 32},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription macrobot_interfaces__msg__EmbeddingRetrievalResult__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__DepthCandidate__TYPE_NAME, 38, 38},
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
macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {macrobot_interfaces__msg__EmbeddingRetrievalResult__TYPE_NAME, 48, 48},
      {macrobot_interfaces__msg__EmbeddingRetrievalResult__FIELDS, 38, 38},
    },
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__REFERENCED_TYPE_DESCRIPTIONS, 4, 4},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&macrobot_interfaces__msg__DepthCandidate__EXPECTED_HASH, macrobot_interfaces__msg__DepthCandidate__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = macrobot_interfaces__msg__DepthCandidate__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__RegionOfInterest__EXPECTED_HASH, sensor_msgs__msg__RegionOfInterest__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = sensor_msgs__msg__RegionOfInterest__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Per-candidate DINOv2 retrieval and negative-margin result.\n"
  "\n"
  "std_msgs/Header proposal_header\n"
  "std_msgs/Header image_header\n"
  "uint32 candidate_id\n"
  "uint32 crop_index\n"
  "uint32 frame_crop_count\n"
  "\n"
  "string target_object\n"
  "string model_id\n"
  "string pooling\n"
  "string device\n"
  "uint32 embedding_dim\n"
  "\n"
  "bool positive_bank_available\n"
  "uint32 positive_reference_count\n"
  "bool negative_bank_available\n"
  "uint32 negative_reference_count\n"
  "bool foreground_mask_used\n"
  "\n"
  "# Copied from CandidateFilterResult when available. -1 means unavailable.\n"
  "float32 objectness_score\n"
  "float32 target_hint_score\n"
  "\n"
  "# positive_similarity and negative_similarity are top-k means.\n"
  "# best_* fields are the single highest cosine similarities.\n"
  "float32 positive_similarity\n"
  "float32 best_positive_similarity\n"
  "float32 negative_similarity\n"
  "float32 best_negative_similarity\n"
  "float32 margin\n"
  "\n"
  "string best_positive_path\n"
  "string best_negative_path\n"
  "string[] top_positive_paths\n"
  "float32[] top_positive_scores\n"
  "string[] top_negative_paths\n"
  "float32[] top_negative_scores\n"
  "\n"
  "# Observation mode forwards evaluated candidates even when these thresholds fail.\n"
  "bool thresholds_enforced\n"
  "bool passed_positive_threshold\n"
  "bool passed_margin_threshold\n"
  "bool accepted\n"
  "string reject_reason\n"
  "\n"
  "float32 preprocessing_ms\n"
  "float32 inference_ms\n"
  "float32 matching_ms\n"
  "\n"
  "DepthCandidate candidate\n"
  "sensor_msgs/RegionOfInterest crop_roi";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
macrobot_interfaces__msg__EmbeddingRetrievalResult__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {macrobot_interfaces__msg__EmbeddingRetrievalResult__TYPE_NAME, 48, 48},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 1312, 1312},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[5];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 5, 5};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *macrobot_interfaces__msg__EmbeddingRetrievalResult__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *macrobot_interfaces__msg__DepthCandidate__get_individual_type_description_source(NULL);
    sources[3] = *sensor_msgs__msg__RegionOfInterest__get_individual_type_description_source(NULL);
    sources[4] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
