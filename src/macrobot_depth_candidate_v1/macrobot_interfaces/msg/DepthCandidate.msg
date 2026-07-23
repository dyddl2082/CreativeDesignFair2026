# Frame-local identifier. It is not a persistent tracking ID.
uint32 id

# Padded region that can be applied directly to the aligned RGB image.
sensor_msgs/RegionOfInterest roi

# Connected-component centroid in image pixels.
float32 center_x
float32 center_y

# Robust depth statistics computed from the component pixels.
float32 median_depth_m
float32 near_depth_m
float32 far_depth_m
float32 depth_std_m

# Component-quality descriptors.
float32 valid_depth_ratio
float32 fill_ratio
float32 area_ratio

# Median optical-axis separation from the fitted background plane.
# Zero when plane removal was unavailable and fallback mode was used.
float32 foreground_height_m

# Heuristic proposal score in the range [0, 1].
float32 proposal_score

# True when the unpadded component touches the configured image border.
bool touches_border
