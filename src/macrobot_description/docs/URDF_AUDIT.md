# New Fusion URDF audit and applied corrections

## Source model

The new Fusion export contains:

- 19 exported links
- 18 tree joints
- 3 sidecar closing joints
- D435F depth-origin marker link
- complete geared gripper geometry

The sidecar closing joints are:

```text
ratio_left_gear_top_link_joint
clamp_left_gear_joint
clamp_right_gear_joint
```

They are intentionally not inserted into URDF because doing so would create closed loops and violate the URDF tree requirement.

## Applied changes from the preceding reviewed package

- removed the generated mock `ros2_control` system
- retained only logical-actuator control through the linkage mapper
- restored robust Xacro launch handling
- restored static `world -> base_link` for RViz
- restored full and reduced descriptions
- restored analytical planar FK/IK
- restored arm four-bar and 2:1 gear constraints
- restored explicit joint, wrist-pitch, and toggle-position limits
- restored working RViz configuration

## New gripper export correction

Five joints directly under `gripper_link` were emitted with XYZ values that describe their assembly/base-frame locations rather than URDF parent-relative locations. Left unmodified, their child meshes appear roughly twice the expected height and disconnected from the gripper platform.

The package converts those positions to `gripper_link`-relative values while preserving the exported 90-degree joint-frame rotation and joint axes.

Corrected parent-relative origins:

```text
gripper_servo_joint:
  (-0.168380, -0.014141, -0.005960)

gripper_left_gear_joint:
  (-0.185150, -0.020700,  0.004000)

gripper_right_gear_joint:
  (-0.185150,  0.003300,  0.004000)

gripper_left_addition_joint:
  (-0.200150, -0.013700,  0.004000)

gripper_right_addition_joint:
  (-0.200150, -0.003700,  0.004000)
```

At q=0, the corrected collision geometry forms one connected gripper around x approximately `-0.195 .. -0.112 m` and z approximately `0.148 .. 0.173 m`.

## Gripper logical constraint

The physical build confirms a 1:2 external gear ratio. `q3=0` is open and
positive `q3` closes the jaws. At `q3=pi/2`, the MG90S has turned 180 degrees
CCW when viewed from its protruding shaft. The full visual tree uses:

```text
gripper_servo_joint          = -2*q3  # exported axis is -Z
gripper_left_gear_joint      = -q3
gripper_right_gear_joint     = +q3
gripper_left_addition_joint  = -q3
gripper_right_addition_joint = +q3
clamp_left_addition_joint    = +q3
clamp_right_addition_joint   = -q3
```

The negative servo-joint coordinate is caused by the exported -Z axis pointing
opposite the physical protruding-shaft viewing direction. The actual MG90S
command angle still increases CCW from 0 to 180 degrees.

## Arm four-bar constraint

The physically confirmed mapping is:

```text
h = q1 + q2
servo_left_gear_joint              = +2*q1
servo_right_gear_joint             = -2*h
ratio_left_gear_joint              = q1
ratio_right_gear_joint             = h
ratio_left_gear_back_link_joint    = q2
back_link_top_link_joint           = q2
```

Positive q1 makes the left MG996R rotate CCW and tilts the arm forward.
Positive h makes the right MG996R rotate CW and lifts the rear linkage. The
passive-joint mapping keeps both pairs of opposite four-bar links parallel.
`q2` remains separated from the +/-90-degree toggle configuration by
`four_bar_margin`.

## Camera frame correction

The exported `camera_link` mesh marker was located at the D435F depth origin, but `camera_fix_joint` was zero, which would place the TF frame at `base_link` rather than at the sensor.

The package uses:

```text
base_link -> camera_link
xyz = -0.030850 -0.000413 0.017858
rpy = 0 0 0
```

The camera marker is represented as a small sphere at the link origin. RealSense internal optical frames remain the driver's responsibility.

## Grasp-frame geometry

The nominal open-jaw grasp center is the midpoint of the transformed clamp collision centroids:

```text
base_link zero pose:
  x = -0.163806 m
  y =  0.064500 m
  z =  0.158595 m
```

Relative to the main arm endpoint, the nominal offset is:

```text
x = -0.184756 m
z = -0.006000 m
```

As q3 closes, the symmetric four-bar shifts the jaw center by approximately `0.03*sin(q3)` in local tool X. `linkage_state_node` includes that shift in the published pose and the dynamic `grasp_frame` TF.

## Robot height

No base-height or `base_footprint` correction is applied. The user stated that the new Fusion model already has the intended robot height.
