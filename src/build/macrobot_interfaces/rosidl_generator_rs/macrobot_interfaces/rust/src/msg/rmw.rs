#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "macrobot_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__DepthCandidate() -> *const std::ffi::c_void;
}

#[link(name = "macrobot_interfaces__rosidl_generator_c")]
extern "C" {
    fn macrobot_interfaces__msg__DepthCandidate__init(msg: *mut DepthCandidate) -> bool;
    fn macrobot_interfaces__msg__DepthCandidate__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<DepthCandidate>, size: usize) -> bool;
    fn macrobot_interfaces__msg__DepthCandidate__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<DepthCandidate>);
    fn macrobot_interfaces__msg__DepthCandidate__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<DepthCandidate>, out_seq: *mut rosidl_runtime_rs::Sequence<DepthCandidate>) -> bool;
}

// Corresponds to macrobot_interfaces__msg__DepthCandidate
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Frame-local identifier. It is not a persistent tracking ID.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DepthCandidate {

    // This member is not documented.
    #[allow(missing_docs)]
    pub id: u32,

    /// Padded region that can be applied directly to the aligned RGB image.
    pub roi: sensor_msgs::msg::rmw::RegionOfInterest,

    /// Connected-component centroid in image pixels.
    pub center_x: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub center_y: f32,

    /// Robust depth statistics computed from the component pixels.
    pub median_depth_m: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub near_depth_m: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub far_depth_m: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub depth_std_m: f32,

    /// Component-quality descriptors.
    pub valid_depth_ratio: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fill_ratio: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub area_ratio: f32,

    /// Median optical-axis separation from the fitted background plane.
    /// Zero when plane removal was unavailable and fallback mode was used.
    pub foreground_height_m: f32,

    /// True only when foreground_height_m was measured from a valid fitted plane.
    /// False means the height is unavailable, not that the measured height is zero.
    pub foreground_height_valid: bool,

    /// Heuristic proposal score in the range [0, 1].
    pub proposal_score: f32,

    /// True when the unpadded component touches the configured image border.
    pub touches_border: bool,

}



impl Default for DepthCandidate {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !macrobot_interfaces__msg__DepthCandidate__init(&mut msg as *mut _) {
        panic!("Call to macrobot_interfaces__msg__DepthCandidate__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for DepthCandidate {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__DepthCandidate__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__DepthCandidate__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__DepthCandidate__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for DepthCandidate {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for DepthCandidate where Self: Sized {
  const TYPE_NAME: &'static str = "macrobot_interfaces/msg/DepthCandidate";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__DepthCandidate() }
  }
}


#[link(name = "macrobot_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__DepthCandidateArray() -> *const std::ffi::c_void;
}

#[link(name = "macrobot_interfaces__rosidl_generator_c")]
extern "C" {
    fn macrobot_interfaces__msg__DepthCandidateArray__init(msg: *mut DepthCandidateArray) -> bool;
    fn macrobot_interfaces__msg__DepthCandidateArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<DepthCandidateArray>, size: usize) -> bool;
    fn macrobot_interfaces__msg__DepthCandidateArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<DepthCandidateArray>);
    fn macrobot_interfaces__msg__DepthCandidateArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<DepthCandidateArray>, out_seq: *mut rosidl_runtime_rs::Sequence<DepthCandidateArray>) -> bool;
}

// Corresponds to macrobot_interfaces__msg__DepthCandidateArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Header copied from the source aligned-depth image.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DepthCandidateArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub image_width: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub image_height: u32,

    /// Background-plane diagnostics for this frame.
    pub plane_found: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub plane_inlier_ratio: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub plane_coefficients: [f32; 4],

    /// Full-frame binary foreground mask in proposal/depth coordinates.
    /// Pixel values are 0 for background and 255 for foreground.
    pub foreground_mask_available: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub foreground_mask: sensor_msgs::msg::rmw::CompressedImage,


    // This member is not documented.
    #[allow(missing_docs)]
    pub candidates: rosidl_runtime_rs::Sequence<super::super::msg::rmw::DepthCandidate>,

}



impl Default for DepthCandidateArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !macrobot_interfaces__msg__DepthCandidateArray__init(&mut msg as *mut _) {
        panic!("Call to macrobot_interfaces__msg__DepthCandidateArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for DepthCandidateArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__DepthCandidateArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__DepthCandidateArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__DepthCandidateArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for DepthCandidateArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for DepthCandidateArray where Self: Sized {
  const TYPE_NAME: &'static str = "macrobot_interfaces/msg/DepthCandidateArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__DepthCandidateArray() }
  }
}


#[link(name = "macrobot_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__RgbCandidateCrop() -> *const std::ffi::c_void;
}

#[link(name = "macrobot_interfaces__rosidl_generator_c")]
extern "C" {
    fn macrobot_interfaces__msg__RgbCandidateCrop__init(msg: *mut RgbCandidateCrop) -> bool;
    fn macrobot_interfaces__msg__RgbCandidateCrop__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RgbCandidateCrop>, size: usize) -> bool;
    fn macrobot_interfaces__msg__RgbCandidateCrop__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RgbCandidateCrop>);
    fn macrobot_interfaces__msg__RgbCandidateCrop__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RgbCandidateCrop>, out_seq: *mut rosidl_runtime_rs::Sequence<RgbCandidateCrop>) -> bool;
}

// Corresponds to macrobot_interfaces__msg__RgbCandidateCrop
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// One JPEG-compressed RGB crop associated with a depth proposal.
/// A frame can produce zero or more messages on the crop topic.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RgbCandidateCrop {
    /// Header copied from the source aligned-depth proposal frame.
    pub proposal_header: std_msgs::msg::rmw::Header,

    /// Dimensions of the proposal frame and matched RGB frame before cropping.
    pub proposal_image_width: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub proposal_image_height: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub color_image_width: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub color_image_height: u32,

    /// Frame grouping metadata for per-candidate messages.
    pub source_candidate_count: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub frame_crop_count: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub crop_index: u32,

    /// Original depth candidate metadata. candidate.roi remains in proposal coordinates.
    pub candidate: super::super::msg::rmw::DepthCandidate,

    /// Actual RGB region used after coordinate scaling and optional extra padding.
    pub crop_roi: sensor_msgs::msg::rmw::RegionOfInterest,

    /// Matched RGB timestamp minus proposal timestamp. Near zero is ideal.
    pub color_time_offset_sec: f32,

    /// Whether the source proposal frame had a valid fitted background plane.
    pub plane_found: bool,

    /// Candidate-local mask transformed to the encoded RGB crop dimensions.
    pub foreground_mask_available: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mask_fill_ratio: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub foreground_mask: sensor_msgs::msg::rmw::CompressedImage,

    /// Encoded crop diagnostics.
    pub encoded_width: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub encoded_height: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub jpeg_size_bytes: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub jpeg_quality: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub size_limit_met: bool,

    /// Header is copied from the matched RGB frame.
    pub image: sensor_msgs::msg::rmw::CompressedImage,

}



impl Default for RgbCandidateCrop {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !macrobot_interfaces__msg__RgbCandidateCrop__init(&mut msg as *mut _) {
        panic!("Call to macrobot_interfaces__msg__RgbCandidateCrop__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RgbCandidateCrop {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__RgbCandidateCrop__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__RgbCandidateCrop__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__RgbCandidateCrop__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RgbCandidateCrop {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RgbCandidateCrop where Self: Sized {
  const TYPE_NAME: &'static str = "macrobot_interfaces/msg/RgbCandidateCrop";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__RgbCandidateCrop() }
  }
}


#[link(name = "macrobot_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__CandidateFilterResult() -> *const std::ffi::c_void;
}

#[link(name = "macrobot_interfaces__rosidl_generator_c")]
extern "C" {
    fn macrobot_interfaces__msg__CandidateFilterResult__init(msg: *mut CandidateFilterResult) -> bool;
    fn macrobot_interfaces__msg__CandidateFilterResult__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CandidateFilterResult>, size: usize) -> bool;
    fn macrobot_interfaces__msg__CandidateFilterResult__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CandidateFilterResult>);
    fn macrobot_interfaces__msg__CandidateFilterResult__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CandidateFilterResult>, out_seq: *mut rosidl_runtime_rs::Sequence<CandidateFilterResult>) -> bool;
}

// Corresponds to macrobot_interfaces__msg__CandidateFilterResult
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Per-candidate filtering decision produced by the PC-side candidate filter.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CandidateFilterResult {

    // This member is not documented.
    #[allow(missing_docs)]
    pub proposal_header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub image_header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub candidate_id: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub crop_index: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub frame_crop_count: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub target_object: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub reference_profile_available: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub reference_image_count: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub camera_info_available: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub plane_found: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub foreground_height_valid: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub foreground_mask_available: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub reject_stage: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub reject_reason: rosidl_runtime_rs::String,

    /// Generic score: is this a valid, stable physical-object candidate?
    pub objectness_score: f32,

    /// Weak target-specific hint from color and optional physical size.
    /// This is not the final Buds3 confidence.
    pub target_hint_score: f32,

    /// Temporary compatibility alias. Set equal to objectness_score.
    /// Remove after old log-analysis tools have been migrated.
    pub filter_score: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub depth_score: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub quality_score: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub color_score: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub shape_score: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub physical_size_score: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub sharpness: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mean_brightness: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub dark_ratio: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub bright_clip_ratio: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub edge_density: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mask_fill_ratio: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mask_solidity: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub color_similarity: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub aspect_ratio: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub estimated_width_m: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub estimated_height_m: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub sync_offset_abs_sec: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub candidate: super::super::msg::rmw::DepthCandidate,


    // This member is not documented.
    #[allow(missing_docs)]
    pub crop_roi: sensor_msgs::msg::rmw::RegionOfInterest,

}



impl Default for CandidateFilterResult {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !macrobot_interfaces__msg__CandidateFilterResult__init(&mut msg as *mut _) {
        panic!("Call to macrobot_interfaces__msg__CandidateFilterResult__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CandidateFilterResult {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__CandidateFilterResult__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__CandidateFilterResult__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__CandidateFilterResult__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CandidateFilterResult {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CandidateFilterResult where Self: Sized {
  const TYPE_NAME: &'static str = "macrobot_interfaces/msg/CandidateFilterResult";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__CandidateFilterResult() }
  }
}


#[link(name = "macrobot_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__FilteredCandidateCrop() -> *const std::ffi::c_void;
}

#[link(name = "macrobot_interfaces__rosidl_generator_c")]
extern "C" {
    fn macrobot_interfaces__msg__FilteredCandidateCrop__init(msg: *mut FilteredCandidateCrop) -> bool;
    fn macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<FilteredCandidateCrop>, size: usize) -> bool;
    fn macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<FilteredCandidateCrop>);
    fn macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<FilteredCandidateCrop>, out_seq: *mut rosidl_runtime_rs::Sequence<FilteredCandidateCrop>) -> bool;
}

// Corresponds to macrobot_interfaces__msg__FilteredCandidateCrop
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Accepted candidate passed to embedding retrieval or another downstream stage.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct FilteredCandidateCrop {

    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::super::msg::rmw::CandidateFilterResult,


    // This member is not documented.
    #[allow(missing_docs)]
    pub crop: super::super::msg::rmw::RgbCandidateCrop,

}



impl Default for FilteredCandidateCrop {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !macrobot_interfaces__msg__FilteredCandidateCrop__init(&mut msg as *mut _) {
        panic!("Call to macrobot_interfaces__msg__FilteredCandidateCrop__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for FilteredCandidateCrop {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__FilteredCandidateCrop__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for FilteredCandidateCrop {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for FilteredCandidateCrop where Self: Sized {
  const TYPE_NAME: &'static str = "macrobot_interfaces/msg/FilteredCandidateCrop";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__FilteredCandidateCrop() }
  }
}


#[link(name = "macrobot_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__EmbeddingRetrievalResult() -> *const std::ffi::c_void;
}

#[link(name = "macrobot_interfaces__rosidl_generator_c")]
extern "C" {
    fn macrobot_interfaces__msg__EmbeddingRetrievalResult__init(msg: *mut EmbeddingRetrievalResult) -> bool;
    fn macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<EmbeddingRetrievalResult>, size: usize) -> bool;
    fn macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<EmbeddingRetrievalResult>);
    fn macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<EmbeddingRetrievalResult>, out_seq: *mut rosidl_runtime_rs::Sequence<EmbeddingRetrievalResult>) -> bool;
}

// Corresponds to macrobot_interfaces__msg__EmbeddingRetrievalResult
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Per-candidate DINOv2 retrieval and negative-margin result.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct EmbeddingRetrievalResult {

    // This member is not documented.
    #[allow(missing_docs)]
    pub proposal_header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub image_header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub candidate_id: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub crop_index: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub frame_crop_count: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub target_object: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub model_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pooling: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub device: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub embedding_dim: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub positive_bank_available: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub positive_reference_count: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub negative_bank_available: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub negative_reference_count: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub foreground_mask_used: bool,

    /// Copied from CandidateFilterResult when available. -1 means unavailable.
    pub objectness_score: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub target_hint_score: f32,

    /// positive_similarity and negative_similarity are top-k means.
    /// best_* fields are the single highest cosine similarities.
    pub positive_similarity: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub best_positive_similarity: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub negative_similarity: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub best_negative_similarity: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub margin: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub best_positive_path: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub best_negative_path: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub top_positive_paths: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub top_positive_scores: rosidl_runtime_rs::Sequence<f32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub top_negative_paths: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub top_negative_scores: rosidl_runtime_rs::Sequence<f32>,

    /// Observation mode forwards evaluated candidates even when these thresholds fail.
    pub thresholds_enforced: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub passed_positive_threshold: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub passed_margin_threshold: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub reject_reason: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub preprocessing_ms: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub inference_ms: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub matching_ms: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub candidate: super::super::msg::rmw::DepthCandidate,


    // This member is not documented.
    #[allow(missing_docs)]
    pub crop_roi: sensor_msgs::msg::rmw::RegionOfInterest,

}



impl Default for EmbeddingRetrievalResult {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !macrobot_interfaces__msg__EmbeddingRetrievalResult__init(&mut msg as *mut _) {
        panic!("Call to macrobot_interfaces__msg__EmbeddingRetrievalResult__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for EmbeddingRetrievalResult {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__EmbeddingRetrievalResult__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for EmbeddingRetrievalResult {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for EmbeddingRetrievalResult where Self: Sized {
  const TYPE_NAME: &'static str = "macrobot_interfaces/msg/EmbeddingRetrievalResult";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__EmbeddingRetrievalResult() }
  }
}


#[link(name = "macrobot_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__EmbeddingMatchedCandidate() -> *const std::ffi::c_void;
}

#[link(name = "macrobot_interfaces__rosidl_generator_c")]
extern "C" {
    fn macrobot_interfaces__msg__EmbeddingMatchedCandidate__init(msg: *mut EmbeddingMatchedCandidate) -> bool;
    fn macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<EmbeddingMatchedCandidate>, size: usize) -> bool;
    fn macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<EmbeddingMatchedCandidate>);
    fn macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<EmbeddingMatchedCandidate>, out_seq: *mut rosidl_runtime_rs::Sequence<EmbeddingMatchedCandidate>) -> bool;
}

// Corresponds to macrobot_interfaces__msg__EmbeddingMatchedCandidate
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Candidate forwarded to temporal confirmation after embedding retrieval.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct EmbeddingMatchedCandidate {

    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::super::msg::rmw::EmbeddingRetrievalResult,


    // This member is not documented.
    #[allow(missing_docs)]
    pub filtered_crop: super::super::msg::rmw::FilteredCandidateCrop,

}



impl Default for EmbeddingMatchedCandidate {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !macrobot_interfaces__msg__EmbeddingMatchedCandidate__init(&mut msg as *mut _) {
        panic!("Call to macrobot_interfaces__msg__EmbeddingMatchedCandidate__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for EmbeddingMatchedCandidate {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__EmbeddingMatchedCandidate__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for EmbeddingMatchedCandidate {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for EmbeddingMatchedCandidate where Self: Sized {
  const TYPE_NAME: &'static str = "macrobot_interfaces/msg/EmbeddingMatchedCandidate";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__EmbeddingMatchedCandidate() }
  }
}


#[link(name = "macrobot_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__TemporalConfirmationResult() -> *const std::ffi::c_void;
}

#[link(name = "macrobot_interfaces__rosidl_generator_c")]
extern "C" {
    fn macrobot_interfaces__msg__TemporalConfirmationResult__init(msg: *mut TemporalConfirmationResult) -> bool;
    fn macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TemporalConfirmationResult>, size: usize) -> bool;
    fn macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TemporalConfirmationResult>);
    fn macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TemporalConfirmationResult>, out_seq: *mut rosidl_runtime_rs::Sequence<TemporalConfirmationResult>) -> bool;
}

// Corresponds to macrobot_interfaces__msg__TemporalConfirmationResult
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Multi-frame state for one spatially consistent object-candidate track.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TemporalConfirmationResult {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub target_object: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub track_id: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub frame_index: u64,

    /// state: tentative, confirmed, lost
    /// event: update, confirmed, deconfirmed, expired
    pub state: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub event: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confirmed: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub track_age_frames: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub window_size: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub required_hits: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub samples_in_window: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub matched_frames_in_window: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub hits_in_window: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub misses_in_window: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub consecutive_hits: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub consecutive_misses: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub hit_ratio: f32,

    /// Temporal confidence is not a calibrated probability.
    pub temporal_score: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub stability_score: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mean_positive_similarity: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mean_negative_similarity: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mean_margin: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub min_margin_in_window: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mean_objectness_score: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub roi: sensor_msgs::msg::rmw::RegionOfInterest,


    // This member is not documented.
    #[allow(missing_docs)]
    pub center_x: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub center_y: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub depth_m: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub center_std_px: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub depth_std_m: f32,

    /// Normalized horizontal displacement from the image center, approximately [-1, 1].
    pub horizontal_error_norm: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub suggested_turn: rosidl_runtime_rs::String,

    /// Most recent per-candidate retrieval result associated with this track.
    pub latest_result: super::super::msg::rmw::EmbeddingRetrievalResult,

}



impl Default for TemporalConfirmationResult {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !macrobot_interfaces__msg__TemporalConfirmationResult__init(&mut msg as *mut _) {
        panic!("Call to macrobot_interfaces__msg__TemporalConfirmationResult__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TemporalConfirmationResult {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { macrobot_interfaces__msg__TemporalConfirmationResult__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TemporalConfirmationResult {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TemporalConfirmationResult where Self: Sized {
  const TYPE_NAME: &'static str = "macrobot_interfaces/msg/TemporalConfirmationResult";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__macrobot_interfaces__msg__TemporalConfirmationResult() }
  }
}


