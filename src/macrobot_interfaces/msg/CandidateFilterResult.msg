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

bool accepted
string reject_stage
string reject_reason

# Scores are in [0, 1]. A value of -1 means unavailable.
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
float32 color_similarity
float32 aspect_ratio
float32 estimated_width_m
float32 estimated_height_m
float32 sync_offset_abs_sec

DepthCandidate candidate
sensor_msgs/RegionOfInterest crop_roi
