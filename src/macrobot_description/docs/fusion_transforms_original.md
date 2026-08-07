# Transformation Matrices - macrobot

Homogeneous transformation matrices between consecutive frames.
Convention: URDF RPY (XYZ extrinsic / ZYX intrinsic).

## Notation

### Frames

| Index | Link |
|-------|------|
| $L_{0}$ | base_link |
| $L_{1}$ | servo_left_gear |
| $L_{2}$ | servo_right_gear |
| $L_{3}$ | ratio_left_gear |
| $L_{4}$ | ratio_right_gear |
| $L_{5}$ | front_right_wheel |
| $L_{6}$ | back_right_wheel |
| $L_{7}$ | front_left_wheel |
| $L_{8}$ | back_left_wheel |
| $L_{9}$ | camera_link |
| $L_{10}$ | back_link |
| $L_{11}$ | gripper_link |
| $L_{12}$ | gripper_servo_gear |
| $L_{13}$ | gripper_left_gear |
| $L_{14}$ | gripper_right_gear |
| $L_{15}$ | gripper_left_addition |
| $L_{16}$ | gripper_right_addition |
| $L_{17}$ | gripper_clamp_left |
| $L_{18}$ | gripper_clamp_right |

### Joint Variables

| Variable | Joint | Type | From | To |
|----------|-------|------|------|----|
| $q_{1}$ | servo_left_gear_joint | continuous (rad) | $L_{0}$ | $L_{1}$ |
| $q_{2}$ | servo_right_gear_joint | continuous (rad) | $L_{0}$ | $L_{2}$ |
| $q_{3}$ | ratio_left_gear_joint | continuous (rad) | $L_{0}$ | $L_{3}$ |
| $q_{4}$ | ratio_right_gear_joint | continuous (rad) | $L_{0}$ | $L_{4}$ |
| $q_{5}$ | front_right_wheel_joint | continuous (rad) | $L_{0}$ | $L_{5}$ |
| $q_{6}$ | back_right_wheel_joint | continuous (rad) | $L_{0}$ | $L_{6}$ |
| $q_{7}$ | front_left_wheel_joint | continuous (rad) | $L_{0}$ | $L_{7}$ |
| $q_{8}$ | back_left_wheel_joint | continuous (rad) | $L_{0}$ | $L_{8}$ |
| $q_{9}$ | ratio_left_gear_back_link_joint | continuous (rad) | $L_{4}$ | $L_{10}$ |
| $q_{10}$ | back_link_top_link_joint | continuous (rad) | $L_{10}$ | $L_{11}$ |
| $q_{11}$ | gripper_servo_joint | continuous (rad) | $L_{11}$ | $L_{12}$ |
| $q_{12}$ | gripper_left_gear_joint | continuous (rad) | $L_{11}$ | $L_{13}$ |
| $q_{13}$ | gripper_right_gear_joint | continuous (rad) | $L_{11}$ | $L_{14}$ |
| $q_{14}$ | gripper_left_addition_joint | continuous (rad) | $L_{11}$ | $L_{15}$ |
| $q_{15}$ | gripper_right_addition_joint | continuous (rad) | $L_{11}$ | $L_{16}$ |
| $q_{16}$ | clamp_left_addition_joint | continuous (rad) | $L_{15}$ | $L_{17}$ |
| $q_{17}$ | clamp_right_addition_joint | continuous (rad) | $L_{16}$ | $L_{18}$ |

Shorthand: $c_i = \cos(q_i)$, $s_i = \sin(q_i)$

### Kinematic Tree

```
L0: base_link
  |-- [continuous] servo_left_gear_joint (q1)
  |   L1: servo_left_gear
  |-- [continuous] servo_right_gear_joint (q2)
  |   L2: servo_right_gear
  |-- [continuous] ratio_left_gear_joint (q3)
  |   L3: ratio_left_gear
  |-- [continuous] ratio_right_gear_joint (q4)
  |   L4: ratio_right_gear
  |     +-- [continuous] ratio_left_gear_back_link_joint (q9)
  |         L10: back_link
  |           +-- [continuous] back_link_top_link_joint (q10)
  |               L11: gripper_link
  |                 |-- [continuous] gripper_servo_joint (q11)
  |                 |   L12: gripper_servo_gear
  |                 |-- [continuous] gripper_left_gear_joint (q12)
  |                 |   L13: gripper_left_gear
  |                 |-- [continuous] gripper_right_gear_joint (q13)
  |                 |   L14: gripper_right_gear
  |                 |-- [continuous] gripper_left_addition_joint (q14)
  |                 |   L15: gripper_left_addition
  |                 |     +-- [continuous] clamp_left_addition_joint (q16)
  |                 |         L17: gripper_clamp_left
  |                 +-- [continuous] gripper_right_addition_joint (q15)
  |                     L16: gripper_right_addition
  |                       +-- [continuous] clamp_right_addition_joint (q17)
  |                           L18: gripper_clamp_right
  |-- [continuous] front_right_wheel_joint (q5)
  |   L5: front_right_wheel
  |-- [continuous] back_right_wheel_joint (q6)
  |   L6: back_right_wheel
  |-- [continuous] front_left_wheel_joint (q7)
  |   L7: front_left_wheel
  |-- [continuous] back_left_wheel_joint (q8)
  |   L8: back_left_wheel
  +-- [fixed] camera_fix_joint
      L9: camera_link
```

## Transforms

## servo_left_gear_joint

$L_{0}$ **base_link** -> $L_{1}$ **servo_left_gear** (continuous)
  Variable: $q_{1}$

- **origin xyz**: (0.02095, 0.0411, 0.039) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, 1, 0)

### Local Transform

$$
T^{0}_{1}(q_{1}) = \begin{bmatrix}
c_{1} & 0 & s_{1} & 0.02095 \\
0 & 1 & 0 & 0.0411 \\
-s_{1} & 0 & c_{1} & 0.039 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## servo_right_gear_joint

$L_{0}$ **base_link** -> $L_{2}$ **servo_right_gear** (continuous)
  Variable: $q_{2}$

- **origin xyz**: (0.02095, 0.0889, 0.039) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, -1, 0)

### Local Transform

$$
T^{0}_{2}(q_{2}) = \begin{bmatrix}
c_{2} & 0 & -s_{2} & 0.02095 \\
0 & 1 & 0 & 0.0889 \\
s_{2} & 0 & c_{2} & 0.039 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## ratio_left_gear_joint

$L_{0}$ **base_link** -> $L_{3}$ **ratio_left_gear** (continuous)
  Variable: $q_{3}$

- **origin xyz**: (0.02095, 0.0579, 0.064595) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, 1, 0)

### Local Transform

$$
T^{0}_{3}(q_{3}) = \begin{bmatrix}
c_{3} & 0 & s_{3} & 0.02095 \\
0 & 1 & 0 & 0.0579 \\
-s_{3} & 0 & c_{3} & 0.064595 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## ratio_right_gear_joint

$L_{0}$ **base_link** -> $L_{4}$ **ratio_right_gear** (continuous)
  Variable: $q_{4}$

- **origin xyz**: (0.02095, 0.0723, 0.064595) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, -1, 0)

### Local Transform

$$
T^{0}_{4}(q_{4}) = \begin{bmatrix}
c_{4} & 0 & -s_{4} & 0.02095 \\
0 & 1 & 0 & 0.0723 \\
s_{4} & 0 & c_{4} & 0.064595 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## front_right_wheel_joint

$L_{0}$ **base_link** -> $L_{5}$ **front_right_wheel** (continuous)
  Variable: $q_{5}$

- **origin xyz**: (0.037, 0.1487, 0.0193) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, 1, 0)

### Local Transform

$$
T^{0}_{5}(q_{5}) = \begin{bmatrix}
c_{5} & 0 & s_{5} & 0.037 \\
0 & 1 & 0 & 0.1487 \\
-s_{5} & 0 & c_{5} & 0.0193 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## back_right_wheel_joint

$L_{0}$ **base_link** -> $L_{6}$ **back_right_wheel** (continuous)
  Variable: $q_{6}$

- **origin xyz**: (0.1235, 0.1487, 0.0193) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, 1, 0)

### Local Transform

$$
T^{0}_{6}(q_{6}) = \begin{bmatrix}
c_{6} & 0 & s_{6} & 0.1235 \\
0 & 1 & 0 & 0.1487 \\
-s_{6} & 0 & c_{6} & 0.0193 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## front_left_wheel_joint

$L_{0}$ **base_link** -> $L_{7}$ **front_left_wheel** (continuous)
  Variable: $q_{7}$

- **origin xyz**: (0.037, -0.0187, 0.0193) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, -1, 0)

### Local Transform

$$
T^{0}_{7}(q_{7}) = \begin{bmatrix}
c_{7} & 0 & -s_{7} & 0.037 \\
0 & 1 & 0 & -0.0187 \\
s_{7} & 0 & c_{7} & 0.0193 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## back_left_wheel_joint

$L_{0}$ **base_link** -> $L_{8}$ **back_left_wheel** (continuous)
  Variable: $q_{8}$

- **origin xyz**: (0.1235, -0.0187, 0.01905) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, -1, 0)

### Local Transform

$$
T^{0}_{8}(q_{8}) = \begin{bmatrix}
c_{8} & 0 & -s_{8} & 0.1235 \\
0 & 1 & 0 & -0.0187 \\
s_{8} & 0 & c_{8} & 0.01905 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## camera_fix_joint

$L_{0}$ **base_link** -> $L_{9}$ **camera_link** (fixed)

- **origin xyz**: (0, 0, 0) m
- **origin rpy**: (0, 0, 0) rad

### Local Transform

$$
T^{0}_{9} = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## ratio_left_gear_back_link_joint

$L_{4}$ **ratio_right_gear** -> $L_{10}$ **back_link** (continuous)
  Variable: $q_{9}$

- **origin xyz**: (0.028, 0.0043, 0) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, 1, 0)

### Local Transform

$$
T^{4}_{10}(q_{9}) = \begin{bmatrix}
c_{9} & 0 & s_{9} & 0.028 \\
0 & 1 & 0 & 0.0043 \\
-s_{9} & 0 & c_{9} & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## back_link_top_link_joint

$L_{10}$ **back_link** -> $L_{11}$ **gripper_link** (continuous)
  Variable: $q_{10}$

- **origin xyz**: (0, -0.0034, 0.1) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, -1, 0)

### Local Transform

$$
T^{10}_{11}(q_{10}) = \begin{bmatrix}
c_{10} & 0 & -s_{10} & 0 \\
0 & 1 & 0 & -0.0034 \\
s_{10} & 0 & c_{10} & 0.1 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## gripper_servo_joint

$L_{11}$ **gripper_link** -> $L_{12}$ **gripper_servo_gear** (continuous)
  Variable: $q_{11}$

- **origin xyz**: (-0.11943, 0.059059, 0.158635) m
- **origin rpy**: (0, 0, 1.570796) rad
- **axis**: (0, 0, -1)

### Local Transform

$T^{11}_{12}(q_{11}) = T_{fixed} \cdot R_{axis}(q_{11})$ where:

$$
T_{fixed} = \begin{bmatrix}
0 & -1 & 0 & -0.11943 \\
1 & 0 & 0 & 0.059059 \\
0 & 0 & 1 & 0.158635 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

$$
R_{axis}(q_{11}) = \begin{bmatrix}
c_{11} & s_{11} & 0 & 0 \\
-s_{11} & c_{11} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## gripper_left_gear_joint

$L_{11}$ **gripper_link** -> $L_{13}$ **gripper_left_gear** (continuous)
  Variable: $q_{12}$

- **origin xyz**: (-0.1362, 0.0525, 0.168595) m
- **origin rpy**: (0, 0, 1.570796) rad
- **axis**: (0, 0, 1)

### Local Transform

$T^{11}_{13}(q_{12}) = T_{fixed} \cdot R_{axis}(q_{12})$ where:

$$
T_{fixed} = \begin{bmatrix}
0 & -1 & 0 & -0.1362 \\
1 & 0 & 0 & 0.0525 \\
0 & 0 & 1 & 0.168595 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

$$
R_{axis}(q_{12}) = \begin{bmatrix}
c_{12} & -s_{12} & 0 & 0 \\
s_{12} & c_{12} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## gripper_right_gear_joint

$L_{11}$ **gripper_link** -> $L_{14}$ **gripper_right_gear** (continuous)
  Variable: $q_{13}$

- **origin xyz**: (-0.1362, 0.0765, 0.168595) m
- **origin rpy**: (0, 0, 1.570796) rad
- **axis**: (0, 0, 1)

### Local Transform

$T^{11}_{14}(q_{13}) = T_{fixed} \cdot R_{axis}(q_{13})$ where:

$$
T_{fixed} = \begin{bmatrix}
0 & -1 & 0 & -0.1362 \\
1 & 0 & 0 & 0.0765 \\
0 & 0 & 1 & 0.168595 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

$$
R_{axis}(q_{13}) = \begin{bmatrix}
c_{13} & -s_{13} & 0 & 0 \\
s_{13} & c_{13} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## gripper_left_addition_joint

$L_{11}$ **gripper_link** -> $L_{15}$ **gripper_left_addition** (continuous)
  Variable: $q_{14}$

- **origin xyz**: (-0.1512, 0.0595, 0.168595) m
- **origin rpy**: (0, 0, 1.570796) rad
- **axis**: (0, 0, 1)

### Local Transform

$T^{11}_{15}(q_{14}) = T_{fixed} \cdot R_{axis}(q_{14})$ where:

$$
T_{fixed} = \begin{bmatrix}
0 & -1 & 0 & -0.1512 \\
1 & 0 & 0 & 0.0595 \\
0 & 0 & 1 & 0.168595 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

$$
R_{axis}(q_{14}) = \begin{bmatrix}
c_{14} & -s_{14} & 0 & 0 \\
s_{14} & c_{14} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## gripper_right_addition_joint

$L_{11}$ **gripper_link** -> $L_{16}$ **gripper_right_addition** (continuous)
  Variable: $q_{15}$

- **origin xyz**: (-0.1512, 0.0695, 0.168595) m
- **origin rpy**: (0, 0, 1.570796) rad
- **axis**: (0, 0, 1)

### Local Transform

$T^{11}_{16}(q_{15}) = T_{fixed} \cdot R_{axis}(q_{15})$ where:

$$
T_{fixed} = \begin{bmatrix}
0 & -1 & 0 & -0.1512 \\
1 & 0 & 0 & 0.0695 \\
0 & 0 & 1 & 0.168595 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

$$
R_{axis}(q_{15}) = \begin{bmatrix}
c_{15} & -s_{15} & 0 & 0 \\
s_{15} & c_{15} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## clamp_left_addition_joint

$L_{15}$ **gripper_left_addition** -> $L_{17}$ **gripper_clamp_left** (continuous)
  Variable: $q_{16}$

- **origin xyz**: (-0.03, 0, 0) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, 0, 1)

### Local Transform

$$
T^{15}_{17}(q_{16}) = \begin{bmatrix}
c_{16} & -s_{16} & 0 & -0.03 \\
s_{16} & c_{16} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## clamp_right_addition_joint

$L_{16}$ **gripper_right_addition** -> $L_{18}$ **gripper_clamp_right** (continuous)
  Variable: $q_{17}$

- **origin xyz**: (0.03, 0, 0) m
- **origin rpy**: (0, 0, 0) rad
- **axis**: (0, 0, 1)

### Local Transform

$$
T^{16}_{18}(q_{17}) = \begin{bmatrix}
c_{17} & -s_{17} & 0 & 0.03 \\
s_{17} & c_{17} & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

---

## Global Transform Chains

Transform from root $L_0$ to any link, as product of local transforms along the kinematic chain.

$$T^{0}_{10} = T^{0}_{4}(q_{4}) \cdot T^{4}_{10}(q_{9})\quad (L_0 \to L_{10}: \text{back_link})$$

$$T^{0}_{11} = T^{0}_{4}(q_{4}) \cdot T^{4}_{10}(q_{9}) \cdot T^{10}_{11}(q_{10})\quad (L_0 \to L_{11}: \text{gripper_link})$$

$$T^{0}_{12} = T^{0}_{4}(q_{4}) \cdot T^{4}_{10}(q_{9}) \cdot T^{10}_{11}(q_{10}) \cdot T^{11}_{12}(q_{11})\quad (L_0 \to L_{12}: \text{gripper_servo_gear})$$

$$T^{0}_{13} = T^{0}_{4}(q_{4}) \cdot T^{4}_{10}(q_{9}) \cdot T^{10}_{11}(q_{10}) \cdot T^{11}_{13}(q_{12})\quad (L_0 \to L_{13}: \text{gripper_left_gear})$$

$$T^{0}_{14} = T^{0}_{4}(q_{4}) \cdot T^{4}_{10}(q_{9}) \cdot T^{10}_{11}(q_{10}) \cdot T^{11}_{14}(q_{13})\quad (L_0 \to L_{14}: \text{gripper_right_gear})$$

$$T^{0}_{15} = T^{0}_{4}(q_{4}) \cdot T^{4}_{10}(q_{9}) \cdot T^{10}_{11}(q_{10}) \cdot T^{11}_{15}(q_{14})\quad (L_0 \to L_{15}: \text{gripper_left_addition})$$

$$T^{0}_{16} = T^{0}_{4}(q_{4}) \cdot T^{4}_{10}(q_{9}) \cdot T^{10}_{11}(q_{10}) \cdot T^{11}_{16}(q_{15})\quad (L_0 \to L_{16}: \text{gripper_right_addition})$$

$$T^{0}_{17} = T^{0}_{4}(q_{4}) \cdot T^{4}_{10}(q_{9}) \cdot T^{10}_{11}(q_{10}) \cdot T^{11}_{15}(q_{14}) \cdot T^{15}_{17}(q_{16})\quad (L_0 \to L_{17}: \text{gripper_clamp_left})$$

$$T^{0}_{18} = T^{0}_{4}(q_{4}) \cdot T^{4}_{10}(q_{9}) \cdot T^{10}_{11}(q_{10}) \cdot T^{11}_{16}(q_{15}) \cdot T^{16}_{18}(q_{17})\quad (L_0 \to L_{18}: \text{gripper_clamp_right})$$

