# Validation Report: macrobot

## Status: PASS (with warnings)

## Summary

| Metric | Value |
|--------|-------|
| Links | 15 |
| Joints | 14 |
| Assemblies | 1 |
| Root | `base_link` |
| Errors | 0 |
| Warnings | 2 |

## Warnings

- Multi-parent link detected (child=gripper_clamp_left:1): keeping 'clamp_left_addition_joint' as the URDF tree parent; routing ['clamp_left_gear_joint'] to ``closing_joints`` (sidecar) — closed kinematic loop.  Tag the loop-closing joint(s) with prefix ``!closing_*`` in Fusion to make the choice explicit and avoid this warning.
- Multi-parent link detected (child=gripper_clamp_right:1): keeping 'clamp_right_addition_joint' as the URDF tree parent; routing ['clamp_right_gear_joint'] to ``closing_joints`` (sidecar) — closed kinematic loop.  Tag the loop-closing joint(s) with prefix ``!closing_*`` in Fusion to make the choice explicit and avoid this warning.

## Kinematic Tree

```
base_link [visual_reuse]
  └─ camera_fix_joint [fixed]
    camera_link [visual_reuse]
  └─ front_left_wheel_joint [continuous]
    front_left_wheel [BAKE] [visual_reuse]
  └─ front_right_wheel_joint [continuous]
    front_right_wheel [BAKE] [visual_reuse]
  └─ back_left_wheel_joint [continuous]
    back_left_wheel [BAKE] [visual_reuse]
  └─ back_right_wheel_joint [continuous]
    back_right_wheel [BAKE] [visual_reuse]
  └─ robot_arm_joint [continuous]
    robot_arm_link [BAKE] [visual_reuse]
      └─ gripper_joint [continuous]
        gripper_link [BAKE] [visual_reuse]
          └─ gripper_servo_joint [continuous]
            gripper_servo_gear [BAKE] [visual_reuse]
          └─ gripper_left_gear_joint [continuous]
            gripper_left_gear [BAKE] [visual_reuse]
          └─ gripper_right_gear_joint [continuous]
            gripper_right_gear [BAKE] [visual_reuse]
          └─ gripper_left_addition_joint [continuous]
            gripper_left_addition [BAKE] [visual_reuse]
              └─ clamp_left_addition_joint [continuous]
                gripper_clamp_left [BAKE] [visual_reuse]
          └─ gripper_right_addition_joint [continuous]
            gripper_right_addition [BAKE] [visual_reuse]
              └─ clamp_right_addition_joint [continuous]
                gripper_clamp_right [BAKE] [visual_reuse]
```

## Collision Geometry

| Link | Source | Shape/File |
|------|--------|------------|
| `back_left_wheel` | visual_reuse | — |
| `back_right_wheel` | visual_reuse | — |
| `base_link` | visual_reuse | — |
| `camera_link` | visual_reuse | — |
| `front_left_wheel` | visual_reuse | — |
| `front_right_wheel` | visual_reuse | — |
| `gripper_clamp_left` | visual_reuse | — |
| `gripper_clamp_right` | visual_reuse | — |
| `gripper_left_addition` | visual_reuse | — |
| `gripper_left_gear` | visual_reuse | — |
| `gripper_link` | visual_reuse | — |
| `gripper_right_addition` | visual_reuse | — |
| `gripper_right_gear` | visual_reuse | — |
| `gripper_servo_gear` | visual_reuse | — |
| `robot_arm_link` | visual_reuse | — |

## Mesh Bake Offsets

Links where joint frame ≠ component origin. Visual/inertial/collision origins shifted.

| Link | Offset (mm) |
|------|-------------|
| `front_left_wheel` | (-0.0, -0.0, -19.3) |
| `front_right_wheel` | (-0.0, -167.4, -19.3) |
| `back_left_wheel` | (-86.0, -0.0, -19.3) |
| `back_right_wheel` | (-86.0, -167.4, -19.3) |
| `robot_arm_link` | (-0.0, -0.0, -11.3) |
| `gripper_link` | (-4.5, 160.3, -4.5) |
| `gripper_servo_gear` | (30.6, -21.6, 2.5) |
| `gripper_left_gear` | (37.2, -38.3, -4.0) |
| `gripper_right_gear` | (13.2, -38.3, -4.0) |
| `gripper_left_addition` | (30.2, -53.3, -3.5) |
| `gripper_right_addition` | (20.2, -53.3, -3.5) |
| `gripper_clamp_left` | (60.2, -53.3, -3.5) |
| `gripper_clamp_right` | (-9.8, -53.3, -3.5) |
