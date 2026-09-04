# Transformation Matrices - macrobot

Homogeneous transformation matrices between consecutive frames.
Convention: URDF RPY (XYZ extrinsic / ZYX intrinsic).

## Notation

### Frames

| Index | Link |
|-------|------|
| $L_{0}$ | base_link |
| $L_{1}$ | camera_link |
| $L_{2}$ | front_left_wheel |
| $L_{3}$ | front_right_wheel |
| $L_{4}$ | back_left_wheel |
| $L_{5}$ | back_right_wheel |
| $L_{6}$ | robot_arm_link |
| $L_{7}$ | gripper_link |
| $L_{8}$ | gripper_servo_gear |
| $L_{9}$ | gripper_left_gear |
| $L_{10}$ | gripper_right_gear |
| $L_{11}$ | gripper_left_addition |
| $L_{12}$ | gripper_right_addition |
| $L_{13}$ | gripper_clamp_left |
| $L_{14}$ | gripper_clamp_right |

### Joint Variables

| Variable | Joint | Type | From | To |
|----------|-------|------|------|----|
| $q_{1}$ | front_left_wheel_joint | continuous (rad) | $L_{0}$ | $L_{2}$ |
| $q_{2}$ | front_right_wheel_joint | continuous (rad) | $L_{0}$ | $L_{3}$ |
| $q_{3}$ | back_left_wheel_joint | continuous (rad) | $L_{0}$ | $L_{4}$ |
| $q_{4}$ | back_right_wheel_joint | continuous (rad) | $L_{0}$ | $L_{5}$ |
| $q_{5}$ | robot_arm_joint | continuous (rad) | $L_{0}$ | $L_{6}$ |
| $q_{6}$ | gripper_joint | continuous (rad) | $L_{6}$ | $L_{7}$ |
| $q_{7}$ | gripper_servo_joint | continuous (rad) | $L_{7}$ | $L_{8}$ |
| $q_{8}$ | gripper_left_gear_joint | continuous (rad) | $L_{7}$ | $L_{9}$ |
| $q_{9}$ | gripper_right_gear_joint | continuous (rad) | $L_{7}$ | $L_{10}$ |
| $q_{10}$ | gripper_left_addition_joint | continuous (rad) | $L_{7}$ | $L_{11}$ |
| $q_{11}$ | gripper_right_addition_joint | continuous (rad) | $L_{7}$ | $L_{12}$ |
| $q_{12}$ | clamp_left_addition_joint | continuous (rad) | $L_{11}$ | $L_{13}$ |
| $q_{13}$ | clamp_right_addition_joint | continuous (rad) | $L_{12}$ | $L_{14}$ |

Shorthand: $c_i = \cos(q_i)$, $s_i = \sin(q_i)$

### Kinematic Tree

```
L0: base_link
  |-- [fixed] camera_fix_joint
  |   L1: camera_link
  |-- [continuous] front_left_wheel_joint (q1)
  |   L2: front_left_wheel
  |-- [continuous] front_right_wheel_joint (q2)
  |   L3: front_right_wheel
  |-- [continuous] back_left_wheel_joint (q3)
  |   L4: back_left_wheel
  |-- [continuous] back_right_wheel_joint (q4)
  |   L5: back_right_wheel
  +-- [continuous] robot_arm_joint (q5)
      L6: robot_arm_link
        +-- [continuous] gripper_joint (q6)
            L7: gripper_link
              |-- [continuous] gripper_servo_joint (q7)
              |   L8: gripper_servo_gear
              |-- [continuous] gripper_left_gear_joint (q8)
              |   L9: gripper_left_gear
              |-- [continuous] gripper_right_gear_joint (q9)
              |   L10: gripper_right_gear
              |-- [continuous] gripper_left_addition_joint (q10)
              |   L11: gripper_left_addition
              |     +-- [continuous] clamp_left_addition_joint (q12)
              |         L13: gripper_clamp_left
              +-- [continuous] gripper_right_addition_joint (q11)
                  L12: gripper_right_addition
                    +-- [continuous] clamp_right_addition_joint (q13)
                        L14: gripper_clamp_right
```

## Transforms

## camera_fix_joint

$L_{0}$ **base_link** -> $L_{1}$ **camera_link** (fixed)

- **origin xyz**: (0.397034, 0.038271, -0.117663) m
- **origin rpy**: (0, 0, 0) rad

### Local Transform

$$
T^{0}_{1} = \begin{bmatrix}
1 & 0 & 0 & 0.397034 \\
0 & 1 & 0 & 0.038271 \\
0 & 0 & 1 & -0.117663 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## front_left_wheel_joint

$L_{0}$ **base_link** -> $L_{2}$ **front_left_wheel** (continuous)
  Variable: $q_{1}$

- **origin xyz**: (0.397034, 0.038271, -0.098363) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, -1, 0)

### Local Transform

$$
T^{0}_{2}(q_{1}) = \begin{bmatrix}
c_{1} & 0 & -s_{1} & 0.397034 \\
0 & 1 & 0 & 0.038271 \\
s_{1} & 0 & c_{1} & -0.098363 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## front_right_wheel_joint

$L_{0}$ **base_link** -> $L_{3}$ **front_right_wheel** (continuous)
  Variable: $q_{2}$

- **origin xyz**: (0.397034, 0.205671, -0.098363) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, 1, 0)

### Local Transform

$$
T^{0}_{3}(q_{2}) = \begin{bmatrix}
c_{2} & 0 & s_{2} & 0.397034 \\
0 & 1 & 0 & 0.205671 \\
-s_{2} & 0 & c_{2} & -0.098363 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## back_left_wheel_joint

$L_{0}$ **base_link** -> $L_{4}$ **back_left_wheel** (continuous)
  Variable: $q_{3}$

- **origin xyz**: (0.483034, 0.038271, -0.098363) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, -1, 0)

### Local Transform

$$
T^{0}_{4}(q_{3}) = \begin{bmatrix}
c_{3} & 0 & -s_{3} & 0.483034 \\
0 & 1 & 0 & 0.038271 \\
s_{3} & 0 & c_{3} & -0.098363 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## back_right_wheel_joint

$L_{0}$ **base_link** -> $L_{5}$ **back_right_wheel** (continuous)
  Variable: $q_{4}$

- **origin xyz**: (0.483034, 0.205671, -0.098363) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, 1, 0)

### Local Transform

$$
T^{0}_{5}(q_{4}) = \begin{bmatrix}
c_{4} & 0 & s_{4} & 0.483034 \\
0 & 1 & 0 & 0.205671 \\
-s_{4} & 0 & c_{4} & -0.098363 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## robot_arm_joint

$L_{0}$ **base_link** -> $L_{6}$ **robot_arm_link** (continuous)
  Variable: $q_{5}$

- **origin xyz**: (0.390034, 0.150671, -0.059763) m
- **origin rpy**: (-1.637996, -1.570796, -2.865406) rad
- **axis**: (0, 0, -1)

### Local Transform

$T^{0}_{6}(q_{5}) = T_{fixed} \cdot R_{axis}(q_{5})$ where:

$$
T_{fixed} = \begin{bmatrix}
0 & -0.978242 & 0.207468 & 0.390034 \\
0 & -0.207468 & -0.978242 & 0.150671 \\
1 & 0 & 0 & -0.059763 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

$$
R_{axis}(q_{5}) = \begin{bmatrix}
c_{5} & s_{5} & 0 & 0 \\
-s_{5} & c_{5} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## gripper_joint

$L_{6}$ **robot_arm_link** -> $L_{7}$ **gripper_link** (continuous)
  Variable: $q_{6}$

- **origin xyz**: (0.161, 0.0004, 0.01) m
- **origin rpy**: (0, -1.570796, 0) rad
- **axis**: (-1, 0, 0)

### Local Transform

$T^{6}_{7}(q_{6}) = T_{fixed} \cdot R_{axis}(q_{6})$ where:

$$
T_{fixed} = \begin{bmatrix}
0 & 0 & -1 & 0.161 \\
0 & 1 & 0 & 0.0004 \\
1 & 0 & 0 & 0.01 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

$$
R_{axis}(q_{6}) = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & c_{6} & s_{6} & 0 \\
0 & -s_{6} & c_{6} & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## gripper_servo_joint

$L_{7}$ **gripper_link** -> $L_{8}$ **gripper_servo_gear** (continuous)
  Variable: $q_{7}$

- **origin xyz**: (0.026141, 0.176579, -0.00654) m
- **origin rpy**: (3.141593, 0, 3.141593) rad
- **axis**: (0, 0, -1)

### Local Transform

$T^{7}_{8}(q_{7}) = T_{fixed} \cdot R_{axis}(q_{7})$ where:

$$
T_{fixed} = \begin{bmatrix}
-1 & 0 & 0 & 0.026141 \\
0 & 1 & 0 & 0.176579 \\
0 & 0 & -1 & -0.00654 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

$$
R_{axis}(q_{7}) = \begin{bmatrix}
c_{7} & s_{7} & 0 & 0 \\
-s_{7} & c_{7} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## gripper_left_gear_joint

$L_{7}$ **gripper_link** -> $L_{9}$ **gripper_left_gear** (continuous)
  Variable: $q_{8}$

- **origin xyz**: (0.0327, 0.193349, -0.0125) m
- **origin rpy**: (3.141593, 0, -3.141593) rad
- **axis**: (0, 0, 1)

### Local Transform

$T^{7}_{9}(q_{8}) = T_{fixed} \cdot R_{axis}(q_{8})$ where:

$$
T_{fixed} = \begin{bmatrix}
-1 & 0 & 0 & 0.0327 \\
0 & 1 & 0 & 0.193349 \\
0 & 0 & -1 & -0.0125 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

$$
R_{axis}(q_{8}) = \begin{bmatrix}
c_{8} & -s_{8} & 0 & 0 \\
s_{8} & c_{8} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## gripper_right_gear_joint

$L_{7}$ **gripper_link** -> $L_{10}$ **gripper_right_gear** (continuous)
  Variable: $q_{9}$

- **origin xyz**: (0.0087, 0.193349, -0.0125) m
- **origin rpy**: (3.141593, 0, -3.141593) rad
- **axis**: (0, 0, 1)

### Local Transform

$T^{7}_{10}(q_{9}) = T_{fixed} \cdot R_{axis}(q_{9})$ where:

$$
T_{fixed} = \begin{bmatrix}
-1 & 0 & 0 & 0.0087 \\
0 & 1 & 0 & 0.193349 \\
0 & 0 & -1 & -0.0125 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

$$
R_{axis}(q_{9}) = \begin{bmatrix}
c_{9} & -s_{9} & 0 & 0 \\
s_{9} & c_{9} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## gripper_left_addition_joint

$L_{7}$ **gripper_link** -> $L_{11}$ **gripper_left_addition** (continuous)
  Variable: $q_{10}$

- **origin xyz**: (0.0257, 0.208349, -0.0125) m
- **origin rpy**: (3.141593, 0, -3.141593) rad
- **axis**: (0, 0, 1)

### Local Transform

$T^{7}_{11}(q_{10}) = T_{fixed} \cdot R_{axis}(q_{10})$ where:

$$
T_{fixed} = \begin{bmatrix}
-1 & 0 & 0 & 0.0257 \\
0 & 1 & 0 & 0.208349 \\
0 & 0 & -1 & -0.0125 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

$$
R_{axis}(q_{10}) = \begin{bmatrix}
c_{10} & -s_{10} & 0 & 0 \\
s_{10} & c_{10} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## gripper_right_addition_joint

$L_{7}$ **gripper_link** -> $L_{12}$ **gripper_right_addition** (continuous)
  Variable: $q_{11}$

- **origin xyz**: (0.0157, 0.208349, -0.0125) m
- **origin rpy**: (3.141593, 0, -3.141593) rad
- **axis**: (0, 0, 1)

### Local Transform

$T^{7}_{12}(q_{11}) = T_{fixed} \cdot R_{axis}(q_{11})$ where:

$$
T_{fixed} = \begin{bmatrix}
-1 & 0 & 0 & 0.0157 \\
0 & 1 & 0 & 0.208349 \\
0 & 0 & -1 & -0.0125 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

$$
R_{axis}(q_{11}) = \begin{bmatrix}
c_{11} & -s_{11} & 0 & 0 \\
s_{11} & c_{11} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## clamp_left_addition_joint

$L_{11}$ **gripper_left_addition** -> $L_{13}$ **gripper_clamp_left** (continuous)
  Variable: $q_{12}$

- **origin xyz**: (-0.03, 0, 0) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, 0, 1)

### Local Transform

$$
T^{11}_{13}(q_{12}) = \begin{bmatrix}
c_{12} & -s_{12} & 0 & -0.03 \\
s_{12} & c_{12} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## clamp_right_addition_joint

$L_{12}$ **gripper_right_addition** -> $L_{14}$ **gripper_clamp_right** (continuous)
  Variable: $q_{13}$

- **origin xyz**: (0.03, 0, 0) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, 0, 1)

### Local Transform

$$
T^{12}_{14}(q_{13}) = \begin{bmatrix}
c_{13} & -s_{13} & 0 & 0.03 \\
s_{13} & c_{13} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## Global Transform Chains

Transform from root $L_0$ to any link, as product of local transforms along the kinematic chain.

$$T^{0}_{7} = T^{0}_{6}(q_{5}) \cdot T^{6}_{7}(q_{6})\quad (L_0 \to L_{7}: \text{gripper_link})$$

$$T^{0}_{8} = T^{0}_{6}(q_{5}) \cdot T^{6}_{7}(q_{6}) \cdot T^{7}_{8}(q_{7})\quad (L_0 \to L_{8}: \text{gripper_servo_gear})$$

$$T^{0}_{9} = T^{0}_{6}(q_{5}) \cdot T^{6}_{7}(q_{6}) \cdot T^{7}_{9}(q_{8})\quad (L_0 \to L_{9}: \text{gripper_left_gear})$$

$$T^{0}_{10} = T^{0}_{6}(q_{5}) \cdot T^{6}_{7}(q_{6}) \cdot T^{7}_{10}(q_{9})\quad (L_0 \to L_{10}: \text{gripper_right_gear})$$

$$T^{0}_{11} = T^{0}_{6}(q_{5}) \cdot T^{6}_{7}(q_{6}) \cdot T^{7}_{11}(q_{10})\quad (L_0 \to L_{11}: \text{gripper_left_addition})$$

$$T^{0}_{12} = T^{0}_{6}(q_{5}) \cdot T^{6}_{7}(q_{6}) \cdot T^{7}_{12}(q_{11})\quad (L_0 \to L_{12}: \text{gripper_right_addition})$$

$$T^{0}_{13} = T^{0}_{6}(q_{5}) \cdot T^{6}_{7}(q_{6}) \cdot T^{7}_{11}(q_{10}) \cdot T^{11}_{13}(q_{12})\quad (L_0 \to L_{13}: \text{gripper_clamp_left})$$

$$T^{0}_{14} = T^{0}_{6}(q_{5}) \cdot T^{6}_{7}(q_{6}) \cdot T^{7}_{12}(q_{11}) \cdot T^{12}_{14}(q_{13})\quad (L_0 \to L_{14}: \text{gripper_clamp_right})$$

