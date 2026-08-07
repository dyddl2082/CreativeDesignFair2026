# Gripper constraint notes

The gripper contains two small four-bar jaw mechanisms and a gear train. URDF stores only a tree, so the omitted closing joints are enforced by `linkage_state_node` rather than inserted into the file.

Use only the logical input:

```text
gripper_joint
```

Do not publish independent commands to the seven full visual gripper joints.

The current branch is:

```text
q3 = 0     : Fusion open pose
q3 < 0     : jaws close
q3 <= 1.25 : conservative placeholder upper limit
```

Approximate jaw-frame gap:

```text
gap(q3) = 0.010 + 2 * 0.030 * cos(q3)  [m]
```

This is a geometric estimate between linkage frames, not the exact contact-surface gap. Replace it with measured values when the physical gripper is calibrated.
