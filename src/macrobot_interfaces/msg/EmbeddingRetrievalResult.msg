# Per-candidate DINOv2 retrieval, negative-margin scoring, and patch localization.

std_msgs/Header proposal_header
std_msgs/Header image_header
uint32 candidate_id
uint32 crop_index
uint32 frame_crop_count

string target_object
string model_id
string pooling
string device
uint32 embedding_dim

bool positive_bank_available
uint32 positive_reference_count
bool negative_bank_available
uint32 negative_reference_count
bool foreground_mask_used

# Copied from CandidateFilterResult when available. -1 means unavailable.
float32 objectness_score
float32 target_hint_score

# positive_similarity and negative_similarity are top-k means.
# best_* fields are the single highest cosine similarities.
float32 positive_similarity
float32 best_positive_similarity
float32 negative_similarity
float32 best_negative_similarity
float32 margin

string best_positive_path
string best_negative_path
string[] top_positive_paths
float32[] top_positive_scores
string[] top_negative_paths
float32[] top_negative_scores

# Observation mode forwards evaluated candidates even when these thresholds fail.
bool thresholds_enforced
bool passed_positive_threshold
bool passed_margin_threshold
bool accepted
string reject_reason

# DINOv2 patch-token localization inside the candidate crop.
# localized_center_* are in the original color-image pixel coordinate system.
bool localization_available
string localization_method
float32 localization_quality
float32 localization_peak_positive
float32 localization_peak_margin
float32 localized_center_x
float32 localized_center_y
float32 localized_center_x_crop
float32 localized_center_y_crop
sensor_msgs/RegionOfInterest localized_roi
uint32 localization_mask_area_px

# Principal-axis orientation in the image plane, [0, 180) degrees.
# 0 is horizontal image direction and 90 is vertical image direction.
float32 orientation_deg
string orientation_class
float32 orientation_quality

float32 preprocessing_ms
float32 inference_ms
float32 matching_ms
float32 localization_ms

DepthCandidate candidate
sensor_msgs/RegionOfInterest crop_roi
