# d435_capture_crop v2

ROS 2 Jazzy node for Intel RealSense D435/D435f capture, pre-save browser cropping, and reusable negative dataset management.

Canonical distractors are saved once in `negative/library`. The node generates relative links under `negative/confusers/<target>/_auto`, combining shared distractors with positive views of every other registered object. Existing embedding-retrieval negative paths therefore remain compatible.

See `README_KO.md` for installation and operation details.
