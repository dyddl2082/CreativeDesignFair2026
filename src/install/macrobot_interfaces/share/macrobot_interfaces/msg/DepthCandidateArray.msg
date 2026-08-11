# Header copied from the source aligned-depth image.
std_msgs/Header header

uint32 image_width
uint32 image_height

# Background-plane diagnostics for this frame.
bool plane_found
float32 plane_inlier_ratio
float32[4] plane_coefficients

# Full-frame binary foreground mask in proposal/depth coordinates.
# Pixel values are 0 for background and 255 for foreground.
bool foreground_mask_available
sensor_msgs/CompressedImage foreground_mask

DepthCandidate[] candidates
