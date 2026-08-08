# Gripper constraints and direction convention

The physical gripper is a closed gear/four-bar mechanism. URDF remains a tree,
so the omitted closing joints are enforced by `linkage_state_node` and by the
full-model MoveIt state mapper.

Use only the logical command:

```text
gripper_joint = q3
```

Do not command the seven full visual gripper joints independently.

## Authoritative convention

The observation direction is from the protruding output-shaft side of the
MG90S.

```text
q3 = 0             : fully open reference pose
q3 > 0             : closes the gripper
q3 = pi/2          : 180 deg CCW at the MG90S, nominally fully closed
```

The servo gear radius is `r` and the directly driven gear radius is `2r`.
Therefore the driven gear turns in the opposite direction with half the servo
angle:

```text
servo shaft angle = +2*q3   (CCW positive)
driven gear angle = -q3
```

The full visual joint mapping is:

```text
gripper_servo_joint          = -2*q3  # its exported URDF axis is -Z
gripper_left_gear_joint      = -q3
gripper_right_gear_joint     = +q3
gripper_left_addition_joint  = -q3
gripper_right_addition_joint = +q3
clamp_left_addition_joint    = +q3
clamp_right_addition_joint   = -q3
```

The negative coordinate of `gripper_servo_joint` is not a reversal of the
physical command: the exported joint axis points opposite the protruding shaft,
so a physical CCW rotation is represented by a negative URDF coordinate.

## Approximate gap model

```text
gap(q3) = base_separation + 2*link_length*cos(q3)
```

With the current placeholders:

```text
gap(q3) = 0.010 + 2*0.030*cos(q3)  [m]
```

This is a frame-level estimate, not an exact contact-surface gap. Replace the
parameters with physical measurements during grasp-frame commissioning.
