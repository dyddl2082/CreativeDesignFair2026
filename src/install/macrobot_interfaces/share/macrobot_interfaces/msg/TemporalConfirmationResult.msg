# Multi-frame state for one spatially consistent object-candidate track.

std_msgs/Header header
string target_object
uint32 track_id
uint64 frame_index

# state: tentative, confirmed, lost
# event: update, confirmed, deconfirmed, expired
string state
string event
bool confirmed

uint32 track_age_frames
uint32 window_size
uint32 required_hits
uint32 samples_in_window
uint32 matched_frames_in_window
uint32 hits_in_window
uint32 misses_in_window
uint32 consecutive_hits
uint32 consecutive_misses
float32 hit_ratio

# Temporal confidence is not a calibrated probability.
float32 temporal_score
float32 stability_score
float32 mean_positive_similarity
float32 mean_negative_similarity
float32 mean_margin
float32 min_margin_in_window
float32 mean_objectness_score

sensor_msgs/RegionOfInterest roi
float32 center_x
float32 center_y
float32 depth_m
float32 center_std_px
float32 depth_std_m

# Normalized horizontal displacement from the image center, approximately [-1, 1].
float32 horizontal_error_norm
string suggested_turn

# Most recent per-candidate retrieval result associated with this track.
EmbeddingRetrievalResult latest_result
