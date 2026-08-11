#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to macrobot_interfaces__msg__DepthCandidate
/// Frame-local identifier. It is not a persistent tracking ID.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DepthCandidate {

    // This member is not documented.
    #[allow(missing_docs)]
    pub id: u32,

    /// Padded region that can be applied directly to the aligned RGB image.
    pub roi: sensor_msgs::msg::RegionOfInterest,

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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::DepthCandidate::default())
  }
}

impl rosidl_runtime_rs::Message for DepthCandidate {
  type RmwMsg = super::msg::rmw::DepthCandidate;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        id: msg.id,
        roi: sensor_msgs::msg::RegionOfInterest::into_rmw_message(std::borrow::Cow::Owned(msg.roi)).into_owned(),
        center_x: msg.center_x,
        center_y: msg.center_y,
        median_depth_m: msg.median_depth_m,
        near_depth_m: msg.near_depth_m,
        far_depth_m: msg.far_depth_m,
        depth_std_m: msg.depth_std_m,
        valid_depth_ratio: msg.valid_depth_ratio,
        fill_ratio: msg.fill_ratio,
        area_ratio: msg.area_ratio,
        foreground_height_m: msg.foreground_height_m,
        foreground_height_valid: msg.foreground_height_valid,
        proposal_score: msg.proposal_score,
        touches_border: msg.touches_border,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      id: msg.id,
        roi: sensor_msgs::msg::RegionOfInterest::into_rmw_message(std::borrow::Cow::Borrowed(&msg.roi)).into_owned(),
      center_x: msg.center_x,
      center_y: msg.center_y,
      median_depth_m: msg.median_depth_m,
      near_depth_m: msg.near_depth_m,
      far_depth_m: msg.far_depth_m,
      depth_std_m: msg.depth_std_m,
      valid_depth_ratio: msg.valid_depth_ratio,
      fill_ratio: msg.fill_ratio,
      area_ratio: msg.area_ratio,
      foreground_height_m: msg.foreground_height_m,
      foreground_height_valid: msg.foreground_height_valid,
      proposal_score: msg.proposal_score,
      touches_border: msg.touches_border,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      id: msg.id,
      roi: sensor_msgs::msg::RegionOfInterest::from_rmw_message(msg.roi),
      center_x: msg.center_x,
      center_y: msg.center_y,
      median_depth_m: msg.median_depth_m,
      near_depth_m: msg.near_depth_m,
      far_depth_m: msg.far_depth_m,
      depth_std_m: msg.depth_std_m,
      valid_depth_ratio: msg.valid_depth_ratio,
      fill_ratio: msg.fill_ratio,
      area_ratio: msg.area_ratio,
      foreground_height_m: msg.foreground_height_m,
      foreground_height_valid: msg.foreground_height_valid,
      proposal_score: msg.proposal_score,
      touches_border: msg.touches_border,
    }
  }
}


// Corresponds to macrobot_interfaces__msg__DepthCandidateArray
/// Header copied from the source aligned-depth image.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DepthCandidateArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


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
    pub foreground_mask: sensor_msgs::msg::CompressedImage,


    // This member is not documented.
    #[allow(missing_docs)]
    pub candidates: Vec<super::msg::DepthCandidate>,

}



impl Default for DepthCandidateArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::DepthCandidateArray::default())
  }
}

impl rosidl_runtime_rs::Message for DepthCandidateArray {
  type RmwMsg = super::msg::rmw::DepthCandidateArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        image_width: msg.image_width,
        image_height: msg.image_height,
        plane_found: msg.plane_found,
        plane_inlier_ratio: msg.plane_inlier_ratio,
        plane_coefficients: msg.plane_coefficients,
        foreground_mask_available: msg.foreground_mask_available,
        foreground_mask: sensor_msgs::msg::CompressedImage::into_rmw_message(std::borrow::Cow::Owned(msg.foreground_mask)).into_owned(),
        candidates: msg.candidates
          .into_iter()
          .map(|elem| super::msg::DepthCandidate::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
      image_width: msg.image_width,
      image_height: msg.image_height,
      plane_found: msg.plane_found,
      plane_inlier_ratio: msg.plane_inlier_ratio,
        plane_coefficients: msg.plane_coefficients,
      foreground_mask_available: msg.foreground_mask_available,
        foreground_mask: sensor_msgs::msg::CompressedImage::into_rmw_message(std::borrow::Cow::Borrowed(&msg.foreground_mask)).into_owned(),
        candidates: msg.candidates
          .iter()
          .map(|elem| super::msg::DepthCandidate::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      image_width: msg.image_width,
      image_height: msg.image_height,
      plane_found: msg.plane_found,
      plane_inlier_ratio: msg.plane_inlier_ratio,
      plane_coefficients: msg.plane_coefficients,
      foreground_mask_available: msg.foreground_mask_available,
      foreground_mask: sensor_msgs::msg::CompressedImage::from_rmw_message(msg.foreground_mask),
      candidates: msg.candidates
          .into_iter()
          .map(super::msg::DepthCandidate::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to macrobot_interfaces__msg__RgbCandidateCrop
/// One JPEG-compressed RGB crop associated with a depth proposal.
/// A frame can produce zero or more messages on the crop topic.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RgbCandidateCrop {
    /// Header copied from the source aligned-depth proposal frame.
    pub proposal_header: std_msgs::msg::Header,

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
    pub candidate: super::msg::DepthCandidate,

    /// Actual RGB region used after coordinate scaling and optional extra padding.
    pub crop_roi: sensor_msgs::msg::RegionOfInterest,

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
    pub foreground_mask: sensor_msgs::msg::CompressedImage,

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
    pub image: sensor_msgs::msg::CompressedImage,

}



impl Default for RgbCandidateCrop {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::RgbCandidateCrop::default())
  }
}

impl rosidl_runtime_rs::Message for RgbCandidateCrop {
  type RmwMsg = super::msg::rmw::RgbCandidateCrop;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        proposal_header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.proposal_header)).into_owned(),
        proposal_image_width: msg.proposal_image_width,
        proposal_image_height: msg.proposal_image_height,
        color_image_width: msg.color_image_width,
        color_image_height: msg.color_image_height,
        source_candidate_count: msg.source_candidate_count,
        frame_crop_count: msg.frame_crop_count,
        crop_index: msg.crop_index,
        candidate: super::msg::DepthCandidate::into_rmw_message(std::borrow::Cow::Owned(msg.candidate)).into_owned(),
        crop_roi: sensor_msgs::msg::RegionOfInterest::into_rmw_message(std::borrow::Cow::Owned(msg.crop_roi)).into_owned(),
        color_time_offset_sec: msg.color_time_offset_sec,
        plane_found: msg.plane_found,
        foreground_mask_available: msg.foreground_mask_available,
        mask_fill_ratio: msg.mask_fill_ratio,
        foreground_mask: sensor_msgs::msg::CompressedImage::into_rmw_message(std::borrow::Cow::Owned(msg.foreground_mask)).into_owned(),
        encoded_width: msg.encoded_width,
        encoded_height: msg.encoded_height,
        jpeg_size_bytes: msg.jpeg_size_bytes,
        jpeg_quality: msg.jpeg_quality,
        size_limit_met: msg.size_limit_met,
        image: sensor_msgs::msg::CompressedImage::into_rmw_message(std::borrow::Cow::Owned(msg.image)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        proposal_header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.proposal_header)).into_owned(),
      proposal_image_width: msg.proposal_image_width,
      proposal_image_height: msg.proposal_image_height,
      color_image_width: msg.color_image_width,
      color_image_height: msg.color_image_height,
      source_candidate_count: msg.source_candidate_count,
      frame_crop_count: msg.frame_crop_count,
      crop_index: msg.crop_index,
        candidate: super::msg::DepthCandidate::into_rmw_message(std::borrow::Cow::Borrowed(&msg.candidate)).into_owned(),
        crop_roi: sensor_msgs::msg::RegionOfInterest::into_rmw_message(std::borrow::Cow::Borrowed(&msg.crop_roi)).into_owned(),
      color_time_offset_sec: msg.color_time_offset_sec,
      plane_found: msg.plane_found,
      foreground_mask_available: msg.foreground_mask_available,
      mask_fill_ratio: msg.mask_fill_ratio,
        foreground_mask: sensor_msgs::msg::CompressedImage::into_rmw_message(std::borrow::Cow::Borrowed(&msg.foreground_mask)).into_owned(),
      encoded_width: msg.encoded_width,
      encoded_height: msg.encoded_height,
      jpeg_size_bytes: msg.jpeg_size_bytes,
      jpeg_quality: msg.jpeg_quality,
      size_limit_met: msg.size_limit_met,
        image: sensor_msgs::msg::CompressedImage::into_rmw_message(std::borrow::Cow::Borrowed(&msg.image)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      proposal_header: std_msgs::msg::Header::from_rmw_message(msg.proposal_header),
      proposal_image_width: msg.proposal_image_width,
      proposal_image_height: msg.proposal_image_height,
      color_image_width: msg.color_image_width,
      color_image_height: msg.color_image_height,
      source_candidate_count: msg.source_candidate_count,
      frame_crop_count: msg.frame_crop_count,
      crop_index: msg.crop_index,
      candidate: super::msg::DepthCandidate::from_rmw_message(msg.candidate),
      crop_roi: sensor_msgs::msg::RegionOfInterest::from_rmw_message(msg.crop_roi),
      color_time_offset_sec: msg.color_time_offset_sec,
      plane_found: msg.plane_found,
      foreground_mask_available: msg.foreground_mask_available,
      mask_fill_ratio: msg.mask_fill_ratio,
      foreground_mask: sensor_msgs::msg::CompressedImage::from_rmw_message(msg.foreground_mask),
      encoded_width: msg.encoded_width,
      encoded_height: msg.encoded_height,
      jpeg_size_bytes: msg.jpeg_size_bytes,
      jpeg_quality: msg.jpeg_quality,
      size_limit_met: msg.size_limit_met,
      image: sensor_msgs::msg::CompressedImage::from_rmw_message(msg.image),
    }
  }
}


// Corresponds to macrobot_interfaces__msg__CandidateFilterResult
/// Per-candidate filtering decision produced by the PC-side candidate filter.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CandidateFilterResult {

    // This member is not documented.
    #[allow(missing_docs)]
    pub proposal_header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub image_header: std_msgs::msg::Header,


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
    pub target_object: std::string::String,


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
    pub reject_stage: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub reject_reason: std::string::String,

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
    pub candidate: super::msg::DepthCandidate,


    // This member is not documented.
    #[allow(missing_docs)]
    pub crop_roi: sensor_msgs::msg::RegionOfInterest,

}



impl Default for CandidateFilterResult {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::CandidateFilterResult::default())
  }
}

impl rosidl_runtime_rs::Message for CandidateFilterResult {
  type RmwMsg = super::msg::rmw::CandidateFilterResult;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        proposal_header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.proposal_header)).into_owned(),
        image_header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.image_header)).into_owned(),
        candidate_id: msg.candidate_id,
        crop_index: msg.crop_index,
        frame_crop_count: msg.frame_crop_count,
        target_object: msg.target_object.as_str().into(),
        reference_profile_available: msg.reference_profile_available,
        reference_image_count: msg.reference_image_count,
        camera_info_available: msg.camera_info_available,
        plane_found: msg.plane_found,
        foreground_height_valid: msg.foreground_height_valid,
        foreground_mask_available: msg.foreground_mask_available,
        accepted: msg.accepted,
        reject_stage: msg.reject_stage.as_str().into(),
        reject_reason: msg.reject_reason.as_str().into(),
        objectness_score: msg.objectness_score,
        target_hint_score: msg.target_hint_score,
        filter_score: msg.filter_score,
        depth_score: msg.depth_score,
        quality_score: msg.quality_score,
        color_score: msg.color_score,
        shape_score: msg.shape_score,
        physical_size_score: msg.physical_size_score,
        sharpness: msg.sharpness,
        mean_brightness: msg.mean_brightness,
        dark_ratio: msg.dark_ratio,
        bright_clip_ratio: msg.bright_clip_ratio,
        edge_density: msg.edge_density,
        mask_fill_ratio: msg.mask_fill_ratio,
        mask_solidity: msg.mask_solidity,
        color_similarity: msg.color_similarity,
        aspect_ratio: msg.aspect_ratio,
        estimated_width_m: msg.estimated_width_m,
        estimated_height_m: msg.estimated_height_m,
        sync_offset_abs_sec: msg.sync_offset_abs_sec,
        candidate: super::msg::DepthCandidate::into_rmw_message(std::borrow::Cow::Owned(msg.candidate)).into_owned(),
        crop_roi: sensor_msgs::msg::RegionOfInterest::into_rmw_message(std::borrow::Cow::Owned(msg.crop_roi)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        proposal_header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.proposal_header)).into_owned(),
        image_header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.image_header)).into_owned(),
      candidate_id: msg.candidate_id,
      crop_index: msg.crop_index,
      frame_crop_count: msg.frame_crop_count,
        target_object: msg.target_object.as_str().into(),
      reference_profile_available: msg.reference_profile_available,
      reference_image_count: msg.reference_image_count,
      camera_info_available: msg.camera_info_available,
      plane_found: msg.plane_found,
      foreground_height_valid: msg.foreground_height_valid,
      foreground_mask_available: msg.foreground_mask_available,
      accepted: msg.accepted,
        reject_stage: msg.reject_stage.as_str().into(),
        reject_reason: msg.reject_reason.as_str().into(),
      objectness_score: msg.objectness_score,
      target_hint_score: msg.target_hint_score,
      filter_score: msg.filter_score,
      depth_score: msg.depth_score,
      quality_score: msg.quality_score,
      color_score: msg.color_score,
      shape_score: msg.shape_score,
      physical_size_score: msg.physical_size_score,
      sharpness: msg.sharpness,
      mean_brightness: msg.mean_brightness,
      dark_ratio: msg.dark_ratio,
      bright_clip_ratio: msg.bright_clip_ratio,
      edge_density: msg.edge_density,
      mask_fill_ratio: msg.mask_fill_ratio,
      mask_solidity: msg.mask_solidity,
      color_similarity: msg.color_similarity,
      aspect_ratio: msg.aspect_ratio,
      estimated_width_m: msg.estimated_width_m,
      estimated_height_m: msg.estimated_height_m,
      sync_offset_abs_sec: msg.sync_offset_abs_sec,
        candidate: super::msg::DepthCandidate::into_rmw_message(std::borrow::Cow::Borrowed(&msg.candidate)).into_owned(),
        crop_roi: sensor_msgs::msg::RegionOfInterest::into_rmw_message(std::borrow::Cow::Borrowed(&msg.crop_roi)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      proposal_header: std_msgs::msg::Header::from_rmw_message(msg.proposal_header),
      image_header: std_msgs::msg::Header::from_rmw_message(msg.image_header),
      candidate_id: msg.candidate_id,
      crop_index: msg.crop_index,
      frame_crop_count: msg.frame_crop_count,
      target_object: msg.target_object.to_string(),
      reference_profile_available: msg.reference_profile_available,
      reference_image_count: msg.reference_image_count,
      camera_info_available: msg.camera_info_available,
      plane_found: msg.plane_found,
      foreground_height_valid: msg.foreground_height_valid,
      foreground_mask_available: msg.foreground_mask_available,
      accepted: msg.accepted,
      reject_stage: msg.reject_stage.to_string(),
      reject_reason: msg.reject_reason.to_string(),
      objectness_score: msg.objectness_score,
      target_hint_score: msg.target_hint_score,
      filter_score: msg.filter_score,
      depth_score: msg.depth_score,
      quality_score: msg.quality_score,
      color_score: msg.color_score,
      shape_score: msg.shape_score,
      physical_size_score: msg.physical_size_score,
      sharpness: msg.sharpness,
      mean_brightness: msg.mean_brightness,
      dark_ratio: msg.dark_ratio,
      bright_clip_ratio: msg.bright_clip_ratio,
      edge_density: msg.edge_density,
      mask_fill_ratio: msg.mask_fill_ratio,
      mask_solidity: msg.mask_solidity,
      color_similarity: msg.color_similarity,
      aspect_ratio: msg.aspect_ratio,
      estimated_width_m: msg.estimated_width_m,
      estimated_height_m: msg.estimated_height_m,
      sync_offset_abs_sec: msg.sync_offset_abs_sec,
      candidate: super::msg::DepthCandidate::from_rmw_message(msg.candidate),
      crop_roi: sensor_msgs::msg::RegionOfInterest::from_rmw_message(msg.crop_roi),
    }
  }
}


// Corresponds to macrobot_interfaces__msg__FilteredCandidateCrop
/// Accepted candidate passed to embedding retrieval or another downstream stage.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct FilteredCandidateCrop {

    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::msg::CandidateFilterResult,


    // This member is not documented.
    #[allow(missing_docs)]
    pub crop: super::msg::RgbCandidateCrop,

}



impl Default for FilteredCandidateCrop {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::FilteredCandidateCrop::default())
  }
}

impl rosidl_runtime_rs::Message for FilteredCandidateCrop {
  type RmwMsg = super::msg::rmw::FilteredCandidateCrop;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        result: super::msg::CandidateFilterResult::into_rmw_message(std::borrow::Cow::Owned(msg.result)).into_owned(),
        crop: super::msg::RgbCandidateCrop::into_rmw_message(std::borrow::Cow::Owned(msg.crop)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        result: super::msg::CandidateFilterResult::into_rmw_message(std::borrow::Cow::Borrowed(&msg.result)).into_owned(),
        crop: super::msg::RgbCandidateCrop::into_rmw_message(std::borrow::Cow::Borrowed(&msg.crop)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      result: super::msg::CandidateFilterResult::from_rmw_message(msg.result),
      crop: super::msg::RgbCandidateCrop::from_rmw_message(msg.crop),
    }
  }
}


// Corresponds to macrobot_interfaces__msg__EmbeddingRetrievalResult
/// Per-candidate DINOv2 retrieval and negative-margin result.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct EmbeddingRetrievalResult {

    // This member is not documented.
    #[allow(missing_docs)]
    pub proposal_header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub image_header: std_msgs::msg::Header,


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
    pub target_object: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub model_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pooling: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub device: std::string::String,


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
    pub best_positive_path: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub best_negative_path: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub top_positive_paths: Vec<std::string::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub top_positive_scores: Vec<f32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub top_negative_paths: Vec<std::string::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub top_negative_scores: Vec<f32>,

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
    pub reject_reason: std::string::String,


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
    pub candidate: super::msg::DepthCandidate,


    // This member is not documented.
    #[allow(missing_docs)]
    pub crop_roi: sensor_msgs::msg::RegionOfInterest,

}



impl Default for EmbeddingRetrievalResult {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::EmbeddingRetrievalResult::default())
  }
}

impl rosidl_runtime_rs::Message for EmbeddingRetrievalResult {
  type RmwMsg = super::msg::rmw::EmbeddingRetrievalResult;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        proposal_header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.proposal_header)).into_owned(),
        image_header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.image_header)).into_owned(),
        candidate_id: msg.candidate_id,
        crop_index: msg.crop_index,
        frame_crop_count: msg.frame_crop_count,
        target_object: msg.target_object.as_str().into(),
        model_id: msg.model_id.as_str().into(),
        pooling: msg.pooling.as_str().into(),
        device: msg.device.as_str().into(),
        embedding_dim: msg.embedding_dim,
        positive_bank_available: msg.positive_bank_available,
        positive_reference_count: msg.positive_reference_count,
        negative_bank_available: msg.negative_bank_available,
        negative_reference_count: msg.negative_reference_count,
        foreground_mask_used: msg.foreground_mask_used,
        objectness_score: msg.objectness_score,
        target_hint_score: msg.target_hint_score,
        positive_similarity: msg.positive_similarity,
        best_positive_similarity: msg.best_positive_similarity,
        negative_similarity: msg.negative_similarity,
        best_negative_similarity: msg.best_negative_similarity,
        margin: msg.margin,
        best_positive_path: msg.best_positive_path.as_str().into(),
        best_negative_path: msg.best_negative_path.as_str().into(),
        top_positive_paths: msg.top_positive_paths
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        top_positive_scores: msg.top_positive_scores.into(),
        top_negative_paths: msg.top_negative_paths
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        top_negative_scores: msg.top_negative_scores.into(),
        thresholds_enforced: msg.thresholds_enforced,
        passed_positive_threshold: msg.passed_positive_threshold,
        passed_margin_threshold: msg.passed_margin_threshold,
        accepted: msg.accepted,
        reject_reason: msg.reject_reason.as_str().into(),
        preprocessing_ms: msg.preprocessing_ms,
        inference_ms: msg.inference_ms,
        matching_ms: msg.matching_ms,
        candidate: super::msg::DepthCandidate::into_rmw_message(std::borrow::Cow::Owned(msg.candidate)).into_owned(),
        crop_roi: sensor_msgs::msg::RegionOfInterest::into_rmw_message(std::borrow::Cow::Owned(msg.crop_roi)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        proposal_header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.proposal_header)).into_owned(),
        image_header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.image_header)).into_owned(),
      candidate_id: msg.candidate_id,
      crop_index: msg.crop_index,
      frame_crop_count: msg.frame_crop_count,
        target_object: msg.target_object.as_str().into(),
        model_id: msg.model_id.as_str().into(),
        pooling: msg.pooling.as_str().into(),
        device: msg.device.as_str().into(),
      embedding_dim: msg.embedding_dim,
      positive_bank_available: msg.positive_bank_available,
      positive_reference_count: msg.positive_reference_count,
      negative_bank_available: msg.negative_bank_available,
      negative_reference_count: msg.negative_reference_count,
      foreground_mask_used: msg.foreground_mask_used,
      objectness_score: msg.objectness_score,
      target_hint_score: msg.target_hint_score,
      positive_similarity: msg.positive_similarity,
      best_positive_similarity: msg.best_positive_similarity,
      negative_similarity: msg.negative_similarity,
      best_negative_similarity: msg.best_negative_similarity,
      margin: msg.margin,
        best_positive_path: msg.best_positive_path.as_str().into(),
        best_negative_path: msg.best_negative_path.as_str().into(),
        top_positive_paths: msg.top_positive_paths
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        top_positive_scores: msg.top_positive_scores.as_slice().into(),
        top_negative_paths: msg.top_negative_paths
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        top_negative_scores: msg.top_negative_scores.as_slice().into(),
      thresholds_enforced: msg.thresholds_enforced,
      passed_positive_threshold: msg.passed_positive_threshold,
      passed_margin_threshold: msg.passed_margin_threshold,
      accepted: msg.accepted,
        reject_reason: msg.reject_reason.as_str().into(),
      preprocessing_ms: msg.preprocessing_ms,
      inference_ms: msg.inference_ms,
      matching_ms: msg.matching_ms,
        candidate: super::msg::DepthCandidate::into_rmw_message(std::borrow::Cow::Borrowed(&msg.candidate)).into_owned(),
        crop_roi: sensor_msgs::msg::RegionOfInterest::into_rmw_message(std::borrow::Cow::Borrowed(&msg.crop_roi)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      proposal_header: std_msgs::msg::Header::from_rmw_message(msg.proposal_header),
      image_header: std_msgs::msg::Header::from_rmw_message(msg.image_header),
      candidate_id: msg.candidate_id,
      crop_index: msg.crop_index,
      frame_crop_count: msg.frame_crop_count,
      target_object: msg.target_object.to_string(),
      model_id: msg.model_id.to_string(),
      pooling: msg.pooling.to_string(),
      device: msg.device.to_string(),
      embedding_dim: msg.embedding_dim,
      positive_bank_available: msg.positive_bank_available,
      positive_reference_count: msg.positive_reference_count,
      negative_bank_available: msg.negative_bank_available,
      negative_reference_count: msg.negative_reference_count,
      foreground_mask_used: msg.foreground_mask_used,
      objectness_score: msg.objectness_score,
      target_hint_score: msg.target_hint_score,
      positive_similarity: msg.positive_similarity,
      best_positive_similarity: msg.best_positive_similarity,
      negative_similarity: msg.negative_similarity,
      best_negative_similarity: msg.best_negative_similarity,
      margin: msg.margin,
      best_positive_path: msg.best_positive_path.to_string(),
      best_negative_path: msg.best_negative_path.to_string(),
      top_positive_paths: msg.top_positive_paths
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
      top_positive_scores: msg.top_positive_scores
          .into_iter()
          .collect(),
      top_negative_paths: msg.top_negative_paths
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
      top_negative_scores: msg.top_negative_scores
          .into_iter()
          .collect(),
      thresholds_enforced: msg.thresholds_enforced,
      passed_positive_threshold: msg.passed_positive_threshold,
      passed_margin_threshold: msg.passed_margin_threshold,
      accepted: msg.accepted,
      reject_reason: msg.reject_reason.to_string(),
      preprocessing_ms: msg.preprocessing_ms,
      inference_ms: msg.inference_ms,
      matching_ms: msg.matching_ms,
      candidate: super::msg::DepthCandidate::from_rmw_message(msg.candidate),
      crop_roi: sensor_msgs::msg::RegionOfInterest::from_rmw_message(msg.crop_roi),
    }
  }
}


// Corresponds to macrobot_interfaces__msg__EmbeddingMatchedCandidate
/// Candidate forwarded to temporal confirmation after embedding retrieval.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct EmbeddingMatchedCandidate {

    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::msg::EmbeddingRetrievalResult,


    // This member is not documented.
    #[allow(missing_docs)]
    pub filtered_crop: super::msg::FilteredCandidateCrop,

}



impl Default for EmbeddingMatchedCandidate {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::EmbeddingMatchedCandidate::default())
  }
}

impl rosidl_runtime_rs::Message for EmbeddingMatchedCandidate {
  type RmwMsg = super::msg::rmw::EmbeddingMatchedCandidate;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        result: super::msg::EmbeddingRetrievalResult::into_rmw_message(std::borrow::Cow::Owned(msg.result)).into_owned(),
        filtered_crop: super::msg::FilteredCandidateCrop::into_rmw_message(std::borrow::Cow::Owned(msg.filtered_crop)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        result: super::msg::EmbeddingRetrievalResult::into_rmw_message(std::borrow::Cow::Borrowed(&msg.result)).into_owned(),
        filtered_crop: super::msg::FilteredCandidateCrop::into_rmw_message(std::borrow::Cow::Borrowed(&msg.filtered_crop)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      result: super::msg::EmbeddingRetrievalResult::from_rmw_message(msg.result),
      filtered_crop: super::msg::FilteredCandidateCrop::from_rmw_message(msg.filtered_crop),
    }
  }
}


// Corresponds to macrobot_interfaces__msg__TemporalConfirmationResult
/// Multi-frame state for one spatially consistent object-candidate track.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TemporalConfirmationResult {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub target_object: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub track_id: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub frame_index: u64,

    /// state: tentative, confirmed, lost
    /// event: update, confirmed, deconfirmed, expired
    pub state: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub event: std::string::String,


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
    pub roi: sensor_msgs::msg::RegionOfInterest,


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
    pub suggested_turn: std::string::String,

    /// Most recent per-candidate retrieval result associated with this track.
    pub latest_result: super::msg::EmbeddingRetrievalResult,

}



impl Default for TemporalConfirmationResult {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::TemporalConfirmationResult::default())
  }
}

impl rosidl_runtime_rs::Message for TemporalConfirmationResult {
  type RmwMsg = super::msg::rmw::TemporalConfirmationResult;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        target_object: msg.target_object.as_str().into(),
        track_id: msg.track_id,
        frame_index: msg.frame_index,
        state: msg.state.as_str().into(),
        event: msg.event.as_str().into(),
        confirmed: msg.confirmed,
        track_age_frames: msg.track_age_frames,
        window_size: msg.window_size,
        required_hits: msg.required_hits,
        samples_in_window: msg.samples_in_window,
        matched_frames_in_window: msg.matched_frames_in_window,
        hits_in_window: msg.hits_in_window,
        misses_in_window: msg.misses_in_window,
        consecutive_hits: msg.consecutive_hits,
        consecutive_misses: msg.consecutive_misses,
        hit_ratio: msg.hit_ratio,
        temporal_score: msg.temporal_score,
        stability_score: msg.stability_score,
        mean_positive_similarity: msg.mean_positive_similarity,
        mean_negative_similarity: msg.mean_negative_similarity,
        mean_margin: msg.mean_margin,
        min_margin_in_window: msg.min_margin_in_window,
        mean_objectness_score: msg.mean_objectness_score,
        roi: sensor_msgs::msg::RegionOfInterest::into_rmw_message(std::borrow::Cow::Owned(msg.roi)).into_owned(),
        center_x: msg.center_x,
        center_y: msg.center_y,
        depth_m: msg.depth_m,
        center_std_px: msg.center_std_px,
        depth_std_m: msg.depth_std_m,
        horizontal_error_norm: msg.horizontal_error_norm,
        suggested_turn: msg.suggested_turn.as_str().into(),
        latest_result: super::msg::EmbeddingRetrievalResult::into_rmw_message(std::borrow::Cow::Owned(msg.latest_result)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        target_object: msg.target_object.as_str().into(),
      track_id: msg.track_id,
      frame_index: msg.frame_index,
        state: msg.state.as_str().into(),
        event: msg.event.as_str().into(),
      confirmed: msg.confirmed,
      track_age_frames: msg.track_age_frames,
      window_size: msg.window_size,
      required_hits: msg.required_hits,
      samples_in_window: msg.samples_in_window,
      matched_frames_in_window: msg.matched_frames_in_window,
      hits_in_window: msg.hits_in_window,
      misses_in_window: msg.misses_in_window,
      consecutive_hits: msg.consecutive_hits,
      consecutive_misses: msg.consecutive_misses,
      hit_ratio: msg.hit_ratio,
      temporal_score: msg.temporal_score,
      stability_score: msg.stability_score,
      mean_positive_similarity: msg.mean_positive_similarity,
      mean_negative_similarity: msg.mean_negative_similarity,
      mean_margin: msg.mean_margin,
      min_margin_in_window: msg.min_margin_in_window,
      mean_objectness_score: msg.mean_objectness_score,
        roi: sensor_msgs::msg::RegionOfInterest::into_rmw_message(std::borrow::Cow::Borrowed(&msg.roi)).into_owned(),
      center_x: msg.center_x,
      center_y: msg.center_y,
      depth_m: msg.depth_m,
      center_std_px: msg.center_std_px,
      depth_std_m: msg.depth_std_m,
      horizontal_error_norm: msg.horizontal_error_norm,
        suggested_turn: msg.suggested_turn.as_str().into(),
        latest_result: super::msg::EmbeddingRetrievalResult::into_rmw_message(std::borrow::Cow::Borrowed(&msg.latest_result)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      target_object: msg.target_object.to_string(),
      track_id: msg.track_id,
      frame_index: msg.frame_index,
      state: msg.state.to_string(),
      event: msg.event.to_string(),
      confirmed: msg.confirmed,
      track_age_frames: msg.track_age_frames,
      window_size: msg.window_size,
      required_hits: msg.required_hits,
      samples_in_window: msg.samples_in_window,
      matched_frames_in_window: msg.matched_frames_in_window,
      hits_in_window: msg.hits_in_window,
      misses_in_window: msg.misses_in_window,
      consecutive_hits: msg.consecutive_hits,
      consecutive_misses: msg.consecutive_misses,
      hit_ratio: msg.hit_ratio,
      temporal_score: msg.temporal_score,
      stability_score: msg.stability_score,
      mean_positive_similarity: msg.mean_positive_similarity,
      mean_negative_similarity: msg.mean_negative_similarity,
      mean_margin: msg.mean_margin,
      min_margin_in_window: msg.min_margin_in_window,
      mean_objectness_score: msg.mean_objectness_score,
      roi: sensor_msgs::msg::RegionOfInterest::from_rmw_message(msg.roi),
      center_x: msg.center_x,
      center_y: msg.center_y,
      depth_m: msg.depth_m,
      center_std_px: msg.center_std_px,
      depth_std_m: msg.depth_std_m,
      horizontal_error_norm: msg.horizontal_error_norm,
      suggested_turn: msg.suggested_turn.to_string(),
      latest_result: super::msg::EmbeddingRetrievalResult::from_rmw_message(msg.latest_result),
    }
  }
}


