# MacRobot D435 Capture & Crop v1

A ROS 2 Jazzy Python package for Raspberry Pi that subscribes to Intel RealSense D435/D435f color, aligned-depth, and camera-info topics. It provides an offline browser UI for the workflow:

```text
live preview -> freeze capture -> drag crop -> inspect depth -> save or discard
```

The detailed Korean installation and operation guide is in [`README_KO.md`](README_KO.md).

## Package

```text
d435_capture_crop
```

Executable:

```text
d435_capture_crop_node
```

Default UI:

```text
http://<RASPBERRY_PI_IP>:8090
```

Default ROS inputs:

```text
/camera/camera/color/image_raw
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/color/camera_info
```

Default output layout:

```text
~/MacRobot/data/objects/<object>/*_original.jpg
~/MacRobot/data/curated/objects/<object>/*.jpg
~/MacRobot/data/curated/depth/<object>/*_depth.png
~/MacRobot/data/curated/metadata/<object>/*.json
```
