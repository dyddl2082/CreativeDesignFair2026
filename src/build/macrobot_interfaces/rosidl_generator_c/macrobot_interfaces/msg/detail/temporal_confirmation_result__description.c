// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from macrobot_interfaces:msg/TemporalConfirmationResult.idl
// generated code does not contain a copyright notice

#include "macrobot_interfaces/msg/detail/temporal_confirmation_result__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_macrobot_interfaces
const rosidl_type_hash_t *
macrobot_interfaces__msg__TemporalConfirmationResult__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x92, 0x9b, 0x80, 0x0a, 0xd2, 0xa7, 0x2c, 0xbf,
      0xd8, 0xcb, 0x4b, 0x5d, 0xd8, 0xb9, 0x2e, 0xac,
      0xf9, 0xdd, 0xeb, 0xf9, 0x93, 0xec, 0xd4, 0x7d,
      0x85, 0xdd, 0x13, 0x39, 0x75, 0xd1, 0x3c, 0xce,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "builtin_interfaces/msg/detail/time__functions.h"
#include "macrobot_interfaces/msg/detail/embedding_retrieval_result__functions.h"
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
static const rosidl_type_hash_t macrobot_interfaces__msg__EmbeddingRetrievalResult__EXPECTED_HASH = {1, {
    0xdb, 0x59, 0x19, 0xcb, 0x0a, 0xc2, 0x5e, 0x05,
    0x9a, 0xcd, 0x9c, 0x13, 0x4f, 0x57, 0x36, 0x62,
    0x67, 0x5b, 0x32, 0xe3, 0xc5, 0x70, 0x75, 0x1d,
    0x87, 0x70, 0x5f, 0x25, 0xc7, 0x74, 0xc5, 0x01,
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

static char macrobot_interfaces__msg__TemporalConfirmationResult__TYPE_NAME[] = "macrobot_interfaces/msg/TemporalConfirmationResult";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char macrobot_interfaces__msg__DepthCandidate__TYPE_NAME[] = "macrobot_interfaces/msg/DepthCandidate";
static char macrobot_interfaces__msg__EmbeddingRetrievalResult__TYPE_NAME[] = "macrobot_interfaces/msg/EmbeddingRetrievalResult";
static char sensor_msgs__msg__RegionOfInterest__TYPE_NAME[] = "sensor_msgs/msg/RegionOfInterest";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";

// Define type names, field names, and default values
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__header[] = "header";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__target_object[] = "target_object";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__track_id[] = "track_id";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__frame_index[] = "frame_index";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__state[] = "state";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__event[] = "event";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__confirmed[] = "confirmed";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__track_age_frames[] = "track_age_frames";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__window_size[] = "window_size";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__required_hits[] = "required_hits";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__samples_in_window[] = "samples_in_window";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__matched_frames_in_window[] = "matched_frames_in_window";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__hits_in_window[] = "hits_in_window";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__misses_in_window[] = "misses_in_window";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__consecutive_hits[] = "consecutive_hits";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__consecutive_misses[] = "consecutive_misses";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__hit_ratio[] = "hit_ratio";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__temporal_score[] = "temporal_score";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__stability_score[] = "stability_score";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__mean_positive_similarity[] = "mean_positive_similarity";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__mean_negative_similarity[] = "mean_negative_similarity";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__mean_margin[] = "mean_margin";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__min_margin_in_window[] = "min_margin_in_window";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__mean_objectness_score[] = "mean_objectness_score";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__roi[] = "roi";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__center_x[] = "center_x";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__center_y[] = "center_y";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__depth_m[] = "depth_m";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__center_std_px[] = "center_std_px";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__depth_std_m[] = "depth_std_m";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__horizontal_error_norm[] = "horizontal_error_norm";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__suggested_turn[] = "suggested_turn";
static char macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__latest_result[] = "latest_result";

static rosidl_runtime_c__type_description__Field macrobot_interfaces__msg__TemporalConfirmationResult__FIELDS[] = {
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__header, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__target_object, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__track_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__frame_index, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT64,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__state, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__event, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__confirmed, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__track_age_frames, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__window_size, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__required_hits, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__samples_in_window, 17, 17},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__matched_frames_in_window, 24, 24},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__hits_in_window, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__misses_in_window, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__consecutive_hits, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__consecutive_misses, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__hit_ratio, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__temporal_score, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__stability_score, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__mean_positive_similarity, 24, 24},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__mean_negative_similarity, 24, 24},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__mean_margin, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__min_margin_in_window, 20, 20},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__mean_objectness_score, 21, 21},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__roi, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {sensor_msgs__msg__RegionOfInterest__TYPE_NAME, 32, 32},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__center_x, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__center_y, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__depth_m, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__center_std_px, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__depth_std_m, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__horizontal_error_norm, 21, 21},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__suggested_turn, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {macrobot_interfaces__msg__TemporalConfirmationResult__FIELD_NAME__latest_result, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {macrobot_interfaces__msg__EmbeddingRetrievalResult__TYPE_NAME, 48, 48},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription macrobot_interfaces__msg__TemporalConfirmationResult__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
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
    {sensor_msgs__msg__RegionOfInterest__TYPE_NAME, 32, 32},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
macrobot_interfaces__msg__TemporalConfirmationResult__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {macrobot_interfaces__msg__TemporalConfirmationResult__TYPE_NAME, 50, 50},
      {macrobot_interfaces__msg__TemporalConfirmationResult__FIELDS, 33, 33},
    },
    {macrobot_interfaces__msg__TemporalConfirmationResult__REFERENCED_TYPE_DESCRIPTIONS, 5, 5},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&macrobot_interfaces__msg__DepthCandidate__EXPECTED_HASH, macrobot_interfaces__msg__DepthCandidate__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = macrobot_interfaces__msg__DepthCandidate__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&macrobot_interfaces__msg__EmbeddingRetrievalResult__EXPECTED_HASH, macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = macrobot_interfaces__msg__EmbeddingRetrievalResult__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__RegionOfInterest__EXPECTED_HASH, sensor_msgs__msg__RegionOfInterest__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = sensor_msgs__msg__RegionOfInterest__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Multi-frame state for one spatially consistent object-candidate track.\n"
  "\n"
  "std_msgs/Header header\n"
  "string target_object\n"
  "uint32 track_id\n"
  "uint64 frame_index\n"
  "\n"
  "# state: tentative, confirmed, lost\n"
  "# event: update, confirmed, deconfirmed, expired\n"
  "string state\n"
  "string event\n"
  "bool confirmed\n"
  "\n"
  "uint32 track_age_frames\n"
  "uint32 window_size\n"
  "uint32 required_hits\n"
  "uint32 samples_in_window\n"
  "uint32 matched_frames_in_window\n"
  "uint32 hits_in_window\n"
  "uint32 misses_in_window\n"
  "uint32 consecutive_hits\n"
  "uint32 consecutive_misses\n"
  "float32 hit_ratio\n"
  "\n"
  "# Temporal confidence is not a calibrated probability.\n"
  "float32 temporal_score\n"
  "float32 stability_score\n"
  "float32 mean_positive_similarity\n"
  "float32 mean_negative_similarity\n"
  "float32 mean_margin\n"
  "float32 min_margin_in_window\n"
  "float32 mean_objectness_score\n"
  "\n"
  "sensor_msgs/RegionOfInterest roi\n"
  "float32 center_x\n"
  "float32 center_y\n"
  "float32 depth_m\n"
  "float32 center_std_px\n"
  "float32 depth_std_m\n"
  "\n"
  "# Normalized horizontal displacement from the image center, approximately [-1, 1].\n"
  "float32 horizontal_error_norm\n"
  "string suggested_turn\n"
  "\n"
  "# Most recent per-candidate retrieval result associated with this track.\n"
  "EmbeddingRetrievalResult latest_result";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
macrobot_interfaces__msg__TemporalConfirmationResult__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {macrobot_interfaces__msg__TemporalConfirmationResult__TYPE_NAME, 50, 50},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 1139, 1139},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
macrobot_interfaces__msg__TemporalConfirmationResult__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[6];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 6, 6};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *macrobot_interfaces__msg__TemporalConfirmationResult__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *macrobot_interfaces__msg__DepthCandidate__get_individual_type_description_source(NULL);
    sources[3] = *macrobot_interfaces__msg__EmbeddingRetrievalResult__get_individual_type_description_source(NULL);
    sources[4] = *sensor_msgs__msg__RegionOfInterest__get_individual_type_description_source(NULL);
    sources[5] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
