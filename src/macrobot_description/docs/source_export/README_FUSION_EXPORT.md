# macrobot — Robot Description

![macrobot](images/robot.png)

## Overview

| Property | Value |
|----------|-------|
| Total mass | 5.867 kg |
| Links | 15 |
| Joints | 14 (13 movable) |
| Assemblies | 1 |
| Root link | `base_link` |

## Table of Contents

- [Kinematic Tree](#kinematic-tree)
- [Link Properties](#link-properties)
- [Joint Properties](#joint-properties)
- [Assembly Breakdown](#assembly-breakdown)
- [Quick Start (ROS 2)](#quick-start-ros-2)
- [Files](#files)

## Kinematic Tree

```
base_link
  └─ camera_fix_joint [fixed]
    camera_link
  └─ front_left_wheel_joint [continuous]
    front_left_wheel [BAKE]
  └─ front_right_wheel_joint [continuous]
    front_right_wheel [BAKE]
  └─ back_left_wheel_joint [continuous]
    back_left_wheel [BAKE]
  └─ back_right_wheel_joint [continuous]
    back_right_wheel [BAKE]
  └─ robot_arm_joint [continuous]
    robot_arm_link [BAKE]
      └─ gripper_joint [continuous]
        gripper_link [BAKE]
          └─ gripper_servo_joint [continuous]
            gripper_servo_gear [BAKE]
          └─ gripper_left_gear_joint [continuous]
            gripper_left_gear [BAKE]
          └─ gripper_right_gear_joint [continuous]
            gripper_right_gear [BAKE]
          └─ gripper_left_addition_joint [continuous]
            gripper_left_addition [BAKE]
              └─ clamp_left_addition_joint [continuous]
                gripper_clamp_left [BAKE]
          └─ gripper_right_addition_joint [continuous]
            gripper_right_addition [BAKE]
              └─ clamp_right_addition_joint [continuous]
                gripper_clamp_right [BAKE]
```

## Link Properties

| Link | Mass (kg) | Material | Collision | Bodies |
|------|-----------|----------|-----------|--------|
| `back_left_wheel` | 0.1096 | material | visual_reuse | 1 |
| `back_right_wheel` | 0.1096 | material | visual_reuse | 1 |
| `base_link` | 3.4968 | material | visual_reuse | 1 |
| `camera_link` | 0.0000 | material | visual_reuse | 1 |
| `front_left_wheel` | 0.1096 | material | visual_reuse | 1 |
| `front_right_wheel` | 0.1096 | material | visual_reuse | 1 |
| `gripper_clamp_left` | 0.0118 | material | visual_reuse | 1 |
| `gripper_clamp_right` | 0.0118 | material | visual_reuse | 1 |
| `gripper_left_addition` | 0.0058 | material | visual_reuse | 2 |
| `gripper_left_gear` | 0.0157 | material | visual_reuse | 2 |
| `gripper_link` | 0.7488 | material | visual_reuse | 2 |
| `gripper_right_addition` | 0.0058 | material | visual_reuse | 2 |
| `gripper_right_gear` | 0.0156 | material | visual_reuse | 2 |
| `gripper_servo_gear` | 0.0054 | material | visual_reuse | 1 |
| `robot_arm_link` | 1.1110 | material | visual_reuse | 1 |

## Joint Properties

| Joint | Type | Parent → Child | Axis | Limits |
|-------|------|---------------|------|--------|
| `back_left_wheel_joint` | continuous | `base_link` → `back_left_wheel` | (-0,-1,-0) | — |
| `back_right_wheel_joint` | continuous | `base_link` → `back_right_wheel` | (0,1,-0) | — |
| `camera_fix_joint` | fixed | `base_link` → `camera_link` | (0,0,1) | — |
| `clamp_left_addition_joint` | continuous | `gripper_left_addition` → `gripper_clamp_left` | (-0,-0,1) | — |
| `clamp_right_addition_joint` | continuous | `gripper_right_addition` → `gripper_clamp_right` | (-0,-0,1) | — |
| `front_left_wheel_joint` | continuous | `base_link` → `front_left_wheel` | (-0,-1,0) | — |
| `front_right_wheel_joint` | continuous | `base_link` → `front_right_wheel` | (-0,1,0) | — |
| `gripper_joint` | continuous | `robot_arm_link` → `gripper_link` | (-1,0,0) | — |
| `gripper_left_addition_joint` | continuous | `gripper_link` → `gripper_left_addition` | (0,-0,1) | — |
| `gripper_left_gear_joint` | continuous | `gripper_link` → `gripper_left_gear` | (0,-0,1) | — |
| `gripper_right_addition_joint` | continuous | `gripper_link` → `gripper_right_addition` | (0,-0,1) | — |
| `gripper_right_gear_joint` | continuous | `gripper_link` → `gripper_right_gear` | (0,-0,1) | — |
| `gripper_servo_joint` | continuous | `gripper_link` → `gripper_servo_gear` | (0,0,-1) | — |
| `robot_arm_joint` | continuous | `base_link` → `robot_arm_link` | (-0,0,-1) | — |

## Assembly Breakdown

### macrobot

- **Links**: base_link, camera_link, front_left_wheel, front_right_wheel, back_left_wheel, back_right_wheel, robot_arm_link, gripper_link, gripper_servo_gear, gripper_left_gear, gripper_right_gear, gripper_left_addition, gripper_right_addition, gripper_clamp_left, gripper_clamp_right
- **Total mass**: 5.867 kg

## Quick Start (ROS 2)

```bash
# 1. Copy package to your ROS 2 workspace
cp -r macrobot_description ~/ros2_ws/src/

# 2. Build
cd ~/ros2_ws
colcon build --packages-select macrobot_description
source install/setup.bash

# 3. Visualize in RViz2
ros2 launch macrobot_description display.launch.py

# 4. Validate URDF structure
check_urdf install/macrobot_description/share/macrobot_description/urdf/macrobot.urdf

# 5. Print kinematic tree
urdf_to_graphviz install/macrobot_description/share/macrobot_description/urdf/macrobot.urdf
```

**Joint control**: The launch file includes `joint_state_publisher_gui` —
use the sliders to move revolute/prismatic joints in RViz2.

**Topic inspection**:
```bash
# See published joint states
ros2 topic echo /joint_states

# See robot description parameter
ros2 param get /robot_state_publisher robot_description
```

## Files

| Path | Description |
|------|-------------|
| `urdf/macrobot.urdf.xacro` | Top-level xacro (entry point) |
| `urdf/macrobot.urdf` | Flat URDF (for validation) |
| `urdf/assemblies/` | Per-assembly xacro macros |
| `meshes/` | Visual (OBJ) and collision (STL) meshes |
| `launch/display.launch.py` | Launch robot_state_publisher, RViz, and generated controllers |
| `config/joint_state.yaml` | Joint state publisher config |
| `config/ros2_controllers.yaml` | Generated ros2_control controller manager config |
| `robot_data.yaml` | Supplementary data (beyond URDF) |
| `docs/transforms.md` | Transformation matrices (KaTeX) |

## Customizing

Assemblies tagged `!dummy_` are designed to be swapped out. To replace one:

1. Create your replacement as a xacro macro with the same interface
2. Place it in `urdf/assemblies/`
3. Update the `<xacro:include>` in `urdf/macrobot.urdf.xacro`
4. Update meshes in `meshes/<your_assembly>/`

The xacro prefix system (`${prefix}`) ensures link names stay unique
when multiple instances of the same assembly are used.

---
*Generated by Fusion URDF/XACRO Exporter v3.0.0*