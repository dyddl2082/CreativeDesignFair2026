# One JPEG-compressed RGB crop associated with a depth proposal.
# A frame can produce zero or more messages on the crop topic.

# Header copied from the source aligned-depth proposal frame.
std_msgs/Header proposal_header

# Dimensions of the proposal frame and matched RGB frame before cropping.
uint32 proposal_image_width
uint32 proposal_image_height
uint32 color_image_width
uint32 color_image_height

# Frame grouping metadata for per-candidate messages.
uint32 source_candidate_count
uint32 frame_crop_count
uint32 crop_index

# Original depth candidate metadata. candidate.roi remains in proposal coordinates.
DepthCandidate candidate

# Actual RGB region used after coordinate scaling and optional extra padding.
sensor_msgs/RegionOfInterest crop_roi

# Matched RGB timestamp minus proposal timestamp. Near zero is ideal.
float32 color_time_offset_sec

# Whether the source proposal frame had a valid fitted background plane.
bool plane_found

# Candidate-local mask transformed to the encoded RGB crop dimensions.
bool foreground_mask_available
float32 mask_fill_ratio
sensor_msgs/CompressedImage foreground_mask

# Encoded crop diagnostics.
uint32 encoded_width
uint32 encoded_height
uint32 jpeg_size_bytes
uint8 jpeg_quality
bool size_limit_met

# Header is copied from the matched RGB frame.
sensor_msgs/CompressedImage image
