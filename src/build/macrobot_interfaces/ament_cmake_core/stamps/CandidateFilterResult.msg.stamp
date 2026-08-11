# Per-candidate filtering decision produced by the PC-side candidate filter.

std_msgs/Header proposal_header
std_msgs/Header image_header
uint32 candidate_id
uint32 crop_index
uint32 frame_crop_count

string target_object
bool reference_profile_available
uint32 reference_image_count
bool camera_info_available
bool plane_found
bool foreground_height_valid
bool foreground_mask_available

bool accepted
string reject_stage
string reject_reason

# Generic score: is this a valid, stable physical-object candidate?
float32 objectness_score

# Weak target-specific hint from color and optional physical size.
# This is not the final Buds3 confidence.
float32 target_hint_score

# Temporary compatibility alias. Set equal to objectness_score.
# Remove after old log-analysis tools have been migrated.
float32 filter_score

float32 depth_score
float32 quality_score
float32 color_score
float32 shape_score
float32 physical_size_score

float32 sharpness
float32 mean_brightness
float32 dark_ratio
float32 bright_clip_ratio
float32 edge_density
float32 mask_fill_ratio
float32 mask_solidity
float32 color_similarity
float32 aspect_ratio
float32 estimated_width_m
float32 estimated_height_m
float32 sync_offset_abs_sec

DepthCandidate candidate
sensor_msgs/RegionOfInterest crop_roi
