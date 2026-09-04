# Export Log: macrobot

**Generated:** 2026-09-04T14:56:37.215903

```
[14:55:53] fusion2URDF v3.0.0
[14:55:53] Time: 2026-09-04T14:55:53.680098
[14:55:53] Design: macrobot
[14:55:53] Components: 16
[14:55:53] 
=== PHASE 1: EXTRACTION ===
[14:55:53]   Document unit: mm
[14:55:53] 
=== EXTRACTION: OCCURRENCES ===
[14:55:53]   [LEAF] d=0 base_link
[14:55:53]     path: base_link:1
[14:55:53]     global_pos: (-0.397601, -0.038138, 0.117663) m
[14:55:53]     mass: 3.496760 kg, bodies: 1
[14:55:53]     com_global: (0.037046, 0.086980, 0.064318) m
[14:55:53]     com_component_local: (0.434647, 0.125119, -0.053344) m
[14:55:53]     inertia@origin: ixx=7.897516e-02 iyy=6.899068e-01 izz=7.296661e-01 kg·m²
[14:55:53]     inertia@com:    ixx=1.428406e-02 iyy=1.935554e-02 izz=1.432474e-02 kg·m²
[14:55:53]     material: material
[14:55:53]     color: RGB(0.63, 0.63, 0.63) [appearance]
[14:55:53]     bbox: (0.1850 x 0.1674 x 0.1499) m
[14:55:53]   [LEAF] d=0 camera_link
[14:55:53]     path: camera_link:1
[14:55:53]     global_pos: (-0.000567, 0.000133, -0.000000) m
[14:55:53]     mass: 0.000034 kg, bodies: 1
[14:55:53]     com_global: (-0.068217, 0.079456, 0.025820) m
[14:55:53]     com_component_local: (-0.067650, 0.079323, 0.025820) m
[14:55:53]     inertia@origin: ixx=2.370859e-07 iyy=1.785739e-07 izz=3.700441e-07 kg·m²
[14:55:53]     inertia@com:    ixx=2.348685e-10 iyy=1.174626e-10 izz=1.174626e-10 kg·m²
[14:55:53]     material: material
[14:55:53]     color: RGB(0.63, 0.63, 0.63) [appearance]
[14:55:53]     bbox: (0.0001 x 0.0074 x 0.0074) m
[14:55:53]   [LEAF] d=0 front_left_wheel
[14:55:53]     path: front_left_wheel:1
[14:55:53]     global_pos: (-0.000567, 0.000133, -0.000000) m
[14:55:53]     mass: 0.109612 kg, bodies: 1
[14:55:53]     com_global: (-0.000567, 0.006133, 0.019300) m
[14:55:53]     com_component_local: (0.000000, 0.006000, 0.019300) m
[14:55:53]     inertia@origin: ixx=5.635558e-05 iyy=6.135915e-05 izz=1.552630e-05 kg·m²
[14:55:53]     inertia@com:    ixx=1.158027e-05 iyy=2.052987e-05 izz=1.158028e-05 kg·m²
[14:55:53]     material: material
[14:55:53]     color: RGB(0.63, 0.63, 0.63) [appearance]
[14:55:53]     bbox: (0.0386 x 0.0120 x 0.0386) m
[14:55:53]   [LEAF] d=0 front_right_wheel
[14:55:53]     path: front_right_wheel:1
[14:55:53]     global_pos: (-0.000567, 0.000133, -0.000000) m
[14:55:53]     mass: 0.109612 kg, bodies: 1
[14:55:53]     com_global: (-0.000567, 0.161533, 0.019300) m
[14:55:53]     com_component_local: (0.000000, 0.161400, 0.019300) m
[14:55:53]     inertia@origin: ixx=2.907791e-03 iyy=6.135915e-05 izz=2.866962e-03 kg·m²
[14:55:53]     inertia@com:    ixx=1.158027e-05 iyy=2.052987e-05 izz=1.158028e-05 kg·m²
[14:55:53]     material: material
[14:55:53]     color: RGB(0.63, 0.63, 0.63) [appearance]
[14:55:53]     bbox: (0.0386 x 0.0120 x 0.0386) m
[14:55:53]   [LEAF] d=0 back_left_wheel
[14:55:53]     path: back_left_wheel:1
[14:55:53]     global_pos: (-0.000567, 0.000133, -0.000000) m
[14:55:53]     mass: 0.109612 kg, bodies: 1
[14:55:53]     com_global: (0.085433, 0.006133, 0.019300) m
[14:55:53]     com_component_local: (0.086000, 0.006000, 0.019300) m
[14:55:53]     inertia@origin: ixx=5.635558e-05 iyy=8.720476e-04 izz=8.262148e-04 kg·m²
[14:55:53]     inertia@com:    ixx=1.158027e-05 iyy=2.052987e-05 izz=1.158028e-05 kg·m²
[14:55:53]     material: material
[14:55:53]     color: RGB(0.63, 0.63, 0.63) [appearance]
[14:55:53]     bbox: (0.0386 x 0.0120 x 0.0386) m
[14:55:53]   [LEAF] d=0 back_right_wheel
[14:55:53]     path: back_right_wheel:1
[14:55:53]     global_pos: (-0.000567, 0.000133, -0.000000) m
[14:55:53]     mass: 0.109612 kg, bodies: 1
[14:55:53]     com_global: (0.085433, 0.161533, 0.019300) m
[14:55:53]     com_component_local: (0.086000, 0.161400, 0.019300) m
[14:55:53]     inertia@origin: ixx=2.907791e-03 iyy=8.720476e-04 izz=3.677650e-03 kg·m²
[14:55:53]     inertia@com:    ixx=1.158027e-05 iyy=2.052987e-05 izz=1.158028e-05 kg·m²
[14:55:53]     material: material
[14:55:53]     color: RGB(0.63, 0.63, 0.63) [appearance]
[14:55:53]     bbox: (0.0386 x 0.0120 x 0.0386) m
[14:55:54]   [LEAF] d=0 robot_arm_link
[14:55:54]     path: robot_arm_link:1
[14:55:54]     global_pos: (-0.007567, 0.123833, 0.057900) m
[14:55:54]     mass: 1.110983 kg, bodies: 1
[14:55:54]     com_global: (0.095103, 0.122976, 0.094091) m
[14:55:54]     com_component_local: (0.102670, -0.000857, 0.036191) m
[14:55:54]     inertia@origin: ixx=1.930724e-03 iyy=1.719667e-02 izz=1.555498e-02 kg·m²
[14:55:54]     inertia@com:    ixx=4.747553e-04 iyy=4.030443e-03 izz=3.843086e-03 kg·m²
[14:55:54]     material: material
[14:55:54]     color: RGB(0.79, 0.82, 0.93) [Opaque_202_209_238]
[14:55:54]     bbox: (0.1920 x 0.0548 x 0.0762) m
[14:55:54]   [LEAF] d=0 gripper_link
[14:55:54]     path: gripper_link:1
[14:55:54]     global_pos: (-0.168267, 0.107033, 0.223400) m
[14:55:54]     mass: 0.748771 kg, bodies: 2
[14:55:54]     com_global: (-0.144330, 0.027883, 0.228014) m
[14:55:54]     com_component_local: (0.023937, -0.079150, 0.004614) m
[14:55:54]     inertia@origin: ixx=7.697600e-03 iyy=7.677140e-04 izz=8.331620e-03 kg·m²
[14:55:54]     inertia@com:    ixx=2.990810e-03 iyy=3.227377e-04 izz=3.211737e-03 kg·m²
[14:55:54]     material: material
[14:55:54]     color: RGB(0.63, 0.63, 0.63) [appearance]
[14:55:54]     bbox: (0.0762 x 0.2254 x 0.0360) m
[14:55:54]   [LEAF] d=0 gripper_servo_gear
[14:55:54]     path: gripper_servo_gear:1
[14:55:54]     global_pos: (-0.162967, 0.107033, 0.227900) m
[14:55:54]     mass: 0.005385 kg, bodies: 1
[14:55:54]     com_global: (-0.193625, 0.128611, 0.231040) m
[14:55:54]     com_component_local: (-0.030658, 0.021578, 0.003140) m
[14:55:54]     inertia@origin: ixx=2.645635e-06 iyy=5.199567e-06 izz=7.657248e-06 kg·m²
[14:55:54]     inertia@com:    ixx=8.506852e-08 iyy=8.501934e-08 izz=8.829207e-08 kg·m²
[14:55:54]     material: material
[14:55:54]     color: RGB(0.96, 0.96, 0.95) [Opaque_246_246_243]
[14:55:54]     bbox: (0.0138 x 0.0138 x 0.0095) m
[14:55:54]   [LEAF] d=0 gripper_left_gear
[14:55:54]     path: gripper_left_gear:1
[14:55:54]     global_pos: (-0.162967, 0.107033, 0.227400) m
[14:55:54]     mass: 0.015694 kg, bodies: 2
[14:55:54]     com_global: (-0.206109, 0.145382, 0.231605) m
[14:55:54]     com_component_local: (-0.043142, 0.038349, 0.004205) m
[14:55:54]     inertia@origin: ixx=2.387930e-05 iyy=3.155323e-05 izz=5.462202e-05 kg·m²
[14:55:54]     inertia@com:    ixx=5.207374e-07 iyy=2.064126e-06 izz=2.329471e-06 kg·m²
[14:55:54]     material: material
[14:55:54]     color: RGB(0.96, 0.96, 0.95) [Opaque_246_246_243]
[14:55:54]     bbox: (0.0455 x 0.0260 x 0.0100) m
[14:55:54]   [LEAF] d=0 gripper_right_gear
[14:55:54]     path: gripper_right_gear:1
[14:55:54]     global_pos: (-0.162967, 0.107033, 0.227400) m
[14:55:54]     mass: 0.015645 kg, bodies: 2
[14:55:54]     com_global: (-0.170243, 0.145382, 0.231601) m
[14:55:54]     com_component_local: (-0.007276, 0.038349, 0.004201) m
[14:55:54]     inertia@origin: ixx=2.380460e-05 iyy=3.166699e-06 izz=2.616387e-05 kg·m²
[14:55:54]     inertia@com:    ixx=5.203763e-07 iyy=2.062285e-06 izz=2.327511e-06 kg·m²
[14:55:54]     material: material
[14:55:54]     color: RGB(0.96, 0.96, 0.95) [Opaque_246_246_243]
[14:55:54]     bbox: (0.0454 x 0.0258 x 0.0100) m
[14:55:54]   [LEAF] d=0 gripper_left_addition
[14:55:54]     path: gripper_left_addition:1
[14:55:54]     global_pos: (-0.162967, 0.107033, 0.227900) m
[14:55:54]     mass: 0.005805 kg, bodies: 2
[14:55:54]     com_global: (-0.208167, 0.160382, 0.229400) m
[14:55:54]     com_component_local: (-0.045200, 0.053349, 0.001500) m
[14:55:54]     inertia@origin: ixx=1.661891e-05 iyy=1.256191e-05 izz=2.900376e-05 kg·m²
[14:55:54]     inertia@com:    ixx=8.320049e-08 iyy=6.883510e-07 izz=6.206132e-07 kg·m²
[14:55:54]     material: material
[14:55:54]     color: RGB(0.96, 0.96, 0.95) [Opaque_246_246_243]
[14:55:54]     bbox: (0.0350 x 0.0050 x 0.0100) m
[14:55:54]   [LEAF] d=0 gripper_right_addition
[14:55:54]     path: gripper_right_addition:1
[14:55:54]     global_pos: (-0.162967, 0.107033, 0.227900) m
[14:55:54]     mass: 0.005805 kg, bodies: 2
[14:55:54]     com_global: (-0.168167, 0.160382, 0.229400) m
[14:55:54]     com_component_local: (-0.005200, 0.053349, 0.001500) m
[14:55:54]     inertia@origin: ixx=1.661891e-05 iyy=8.583888e-07 izz=1.730023e-05 kg·m²
[14:55:54]     inertia@com:    ixx=8.320049e-08 iyy=6.883510e-07 izz=6.206132e-07 kg·m²
[14:55:54]     material: material
[14:55:54]     color: RGB(0.96, 0.96, 0.95) [Opaque_246_246_243]
[14:55:54]     bbox: (0.0350 x 0.0050 x 0.0100) m
[14:55:54]   [LEAF] d=0 gripper_clamp_left
[14:55:54]     path: gripper_clamp_left:1
[14:55:54]     global_pos: (-0.162967, 0.107033, 0.227900) m
[14:55:54]     mass: 0.011841 kg, bodies: 1
[14:55:54]     com_global: (-0.222555, 0.184250, 0.222503) m
[14:55:54]     com_component_local: (-0.059588, 0.077217, -0.005397) m
[14:55:54]     inertia@origin: ixx=7.366143e-05 iyy=4.291668e-05 izz=1.150233e-04 kg·m²
[14:55:54]     inertia@com:    ixx=2.717208e-06 iyy=5.283410e-07 izz=2.380502e-06 kg·m²
[14:55:54]     material: material
[14:55:54]     color: RGB(0.96, 0.96, 0.95) [Opaque_246_246_243]
[14:55:54]     bbox: (0.0160 x 0.0622 x 0.0200) m
[14:55:54]   [LEAF] d=0 gripper_clamp_right
[14:55:54]     path: gripper_clamp_right:1
[14:55:54]     global_pos: (-0.162967, 0.107033, 0.227900) m
[14:55:54]     mass: 0.011841 kg, bodies: 1
[14:55:54]     com_global: (-0.153779, 0.184250, 0.222503) m
[14:55:54]     com_component_local: (0.009188, 0.077217, -0.005397) m
[14:55:54]     inertia@origin: ixx=7.366143e-05 iyy=1.872894e-06 izz=7.397950e-05 kg·m²
[14:55:54]     inertia@com:    ixx=2.717208e-06 iyy=5.283410e-07 izz=2.380502e-06 kg·m²
[14:55:54]     material: material
[14:55:54]     color: RGB(0.96, 0.96, 0.95) [Opaque_246_246_243]
[14:55:54]     bbox: (0.0160 x 0.0622 x 0.0200) m
[14:55:54]   Extracted 15 occurrences
[14:55:54] 
=== EXTRACTION: JOINTS ===
[14:55:54]   [REGULAR in macrobot] camera_fix_joint
[14:55:54]     parent(occ2): base_link path=base_link:1
[14:55:54]     child(occ1):  camera_link path=camera_link:1
[14:55:54]     geometryOrOriginOne: (-6.8167, 7.9456, 2.5820) cm
[14:55:54]     geometryOrOriginTwo: (-6.8167, 7.9456, 2.5820) cm
[14:55:54]     occ1.transform: (-0.0567, 0.0133, -0.0000) cm (ctx_depth=0)
[14:55:54]     occ1.global:    (-0.0567, 0.0133, -0.0000) cm
[14:55:54]     occ2.transform: (-39.7601, -3.8138, 11.7663) cm (ctx_depth=0)
[14:55:54]     occ2.global:    (-39.7601, -3.8138, 11.7663) cm
[14:55:54]     → origin_global: (-0.068167, 0.079456, 0.025820) m [via geometryOrOriginOne]
[14:55:54]     motion: rigid, axis: (0.000, 0.000, 1.000)
[14:55:54]   [REGULAR in macrobot] front_left_wheel_joint
[14:55:54]     parent(occ2): base_link path=base_link:1
[14:55:54]     child(occ1):  front_left_wheel path=front_left_wheel:1
[14:55:54]     geometryOrOriginOne: (-0.0567, 0.0133, 1.9300) cm
[14:55:54]     geometryOrOriginTwo: (-0.0567, 0.0133, 1.9300) cm
[14:55:54]     occ1.transform: (-0.0567, 0.0133, -0.0000) cm (ctx_depth=0)
[14:55:54]     occ1.global:    (-0.0567, 0.0133, -0.0000) cm
[14:55:54]     occ2.transform: (-39.7601, -3.8138, 11.7663) cm (ctx_depth=0)
[14:55:54]     occ2.global:    (-39.7601, -3.8138, 11.7663) cm
[14:55:54]     → origin_global: (-0.000567, 0.000133, 0.019300) m [via geometryOrOriginOne]
[14:55:54]     motion: revolute, axis: (-0.000, -1.000, 0.000)
[14:55:54]   [REGULAR in macrobot] front_right_wheel_joint
[14:55:54]     parent(occ2): base_link path=base_link:1
[14:55:54]     child(occ1):  front_right_wheel path=front_right_wheel:1
[14:55:54]     geometryOrOriginOne: (-0.0567, 16.7533, 1.9300) cm
[14:55:54]     geometryOrOriginTwo: (-0.0567, 16.7533, 1.9300) cm
[14:55:54]     occ1.transform: (-0.0567, 0.0133, -0.0000) cm (ctx_depth=0)
[14:55:54]     occ1.global:    (-0.0567, 0.0133, -0.0000) cm
[14:55:54]     occ2.transform: (-39.7601, -3.8138, 11.7663) cm (ctx_depth=0)
[14:55:54]     occ2.global:    (-39.7601, -3.8138, 11.7663) cm
[14:55:54]     → origin_global: (-0.000567, 0.167533, 0.019300) m [via geometryOrOriginOne]
[14:55:54]     motion: revolute, axis: (-0.000, 1.000, 0.000)
[14:55:54]   [REGULAR in macrobot] back_left_wheel_joint
[14:55:54]     parent(occ2): base_link path=base_link:1
[14:55:54]     child(occ1):  back_left_wheel path=back_left_wheel:1
[14:55:54]     geometryOrOriginOne: (8.5433, 0.0133, 1.9300) cm
[14:55:54]     geometryOrOriginTwo: (8.5433, 0.0133, 1.9300) cm
[14:55:54]     occ1.transform: (-0.0567, 0.0133, -0.0000) cm (ctx_depth=0)
[14:55:54]     occ1.global:    (-0.0567, 0.0133, -0.0000) cm
[14:55:54]     occ2.transform: (-39.7601, -3.8138, 11.7663) cm (ctx_depth=0)
[14:55:54]     occ2.global:    (-39.7601, -3.8138, 11.7663) cm
[14:55:54]     → origin_global: (0.085433, 0.000133, 0.019300) m [via geometryOrOriginOne]
[14:55:54]     motion: revolute, axis: (-0.000, -1.000, -0.000)
[14:55:54]   [REGULAR in macrobot] back_right_wheel_joint
[14:55:54]     parent(occ2): base_link path=base_link:1
[14:55:54]     child(occ1):  back_right_wheel path=back_right_wheel:1
[14:55:54]     geometryOrOriginOne: (8.5433, 16.7533, 1.9300) cm
[14:55:54]     geometryOrOriginTwo: (8.5433, 16.7533, 1.9300) cm
[14:55:54]     occ1.transform: (-0.0567, 0.0133, -0.0000) cm (ctx_depth=0)
[14:55:54]     occ1.global:    (-0.0567, 0.0133, -0.0000) cm
[14:55:54]     occ2.transform: (-39.7601, -3.8138, 11.7663) cm (ctx_depth=0)
[14:55:54]     occ2.global:    (-39.7601, -3.8138, 11.7663) cm
[14:55:54]     → origin_global: (0.085433, 0.167533, 0.019300) m [via geometryOrOriginOne]
[14:55:54]     motion: revolute, axis: (0.000, 1.000, -0.000)
[14:55:54]   [REGULAR in macrobot] robot_arm_joint
[14:55:54]     parent(occ2): base_link path=base_link:1
[14:55:54]     child(occ1):  robot_arm_link path=robot_arm_link:1
[14:55:54]     geometryOrOriginOne: (-0.7567, 11.2533, 5.7900) cm
[14:55:54]     geometryOrOriginTwo: (-0.7567, 11.2533, 5.7900) cm
[14:55:54]     occ1.transform: (-0.7567, 12.3833, 5.7900) cm (ctx_depth=0)
[14:55:54]     occ1.global:    (-0.7567, 12.3833, 5.7900) cm
[14:55:54]     occ2.transform: (-39.7601, -3.8138, 11.7663) cm (ctx_depth=0)
[14:55:54]     occ2.global:    (-39.7601, -3.8138, 11.7663) cm
[14:55:54]     → origin_global: (-0.007567, 0.112533, 0.057900) m [via geometryOrOriginOne]
[14:55:54]     motion: revolute, axis: (-0.000, 1.000, -0.000)
[14:55:54]   [REGULAR in macrobot] gripper_joint
[14:55:54]     parent(occ2): robot_arm_link path=robot_arm_link:1
[14:55:54]     child(occ1):  gripper_link path=gripper_link:1
[14:55:54]     geometryOrOriginOne: (-0.7967, 10.2533, 21.8900) cm
[14:55:54]     geometryOrOriginTwo: (-0.7967, 10.2533, 21.8900) cm
[14:55:54]     occ1.transform: (-16.8267, 10.7033, 22.3400) cm (ctx_depth=0)
[14:55:54]     occ1.global:    (-16.8267, 10.7033, 22.3400) cm
[14:55:54]     occ2.transform: (-0.7567, 12.3833, 5.7900) cm (ctx_depth=0)
[14:55:54]     occ2.global:    (-0.7567, 12.3833, 5.7900) cm
[14:55:54]     → origin_global: (-0.007967, 0.102533, 0.218900) m [via geometryOrOriginOne]
[14:55:54]     motion: revolute, axis: (0.000, 1.000, -0.000)
[14:55:54]   [REGULAR in macrobot] clamp_left_gear_joint
[14:55:54]     parent(occ2): gripper_left_gear path=gripper_left_gear:1
[14:55:54]     child(occ1):  gripper_clamp_left path=gripper_clamp_left:1
[14:55:54]     geometryOrOriginOne: (-20.1316, 3.9833, 23.1400) cm
[14:55:54]     geometryOrOriginTwo: (-20.1316, 3.9833, 23.1400) cm
[14:55:54]     occ1.transform: (-16.2967, 10.7033, 22.7900) cm (ctx_depth=0)
[14:55:54]     occ1.global:    (-16.2967, 10.7033, 22.7900) cm
[14:55:54]     occ2.transform: (-16.2967, 10.7033, 22.7400) cm (ctx_depth=0)
[14:55:54]     occ2.global:    (-16.2967, 10.7033, 22.7400) cm
[14:55:54]     → origin_global: (-0.201316, 0.039833, 0.231400) m [via geometryOrOriginOne]
[14:55:54]     motion: revolute, axis: (-0.000, -0.000, 1.000)
[14:55:54]   [REGULAR in macrobot] clamp_left_addition_joint
[14:55:54]     parent(occ2): gripper_left_addition path=gripper_left_addition:1
[14:55:54]     child(occ1):  gripper_clamp_left path=gripper_clamp_left:1
[14:55:54]     geometryOrOriginOne: (-21.6316, 4.6833, 23.1400) cm
[14:55:54]     geometryOrOriginTwo: (-21.6316, 4.6833, 23.1400) cm
[14:55:54]     occ1.transform: (-16.2967, 10.7033, 22.7900) cm (ctx_depth=0)
[14:55:54]     occ1.global:    (-16.2967, 10.7033, 22.7900) cm
[14:55:54]     occ2.transform: (-16.2967, 10.7033, 22.7900) cm (ctx_depth=0)
[14:55:54]     occ2.global:    (-16.2967, 10.7033, 22.7900) cm
[14:55:54]     → origin_global: (-0.216316, 0.046833, 0.231400) m [via geometryOrOriginOne]
[14:55:54]     motion: revolute, axis: (-0.000, -0.000, 1.000)
[14:55:54]   [REGULAR in macrobot] clamp_right_gear_joint
[14:55:54]     parent(occ2): gripper_right_gear path=gripper_right_gear:1
[14:55:54]     child(occ1):  gripper_clamp_right path=gripper_clamp_right:1
[14:55:54]     geometryOrOriginOne: (-20.1316, 12.3833, 23.1400) cm
[14:55:54]     geometryOrOriginTwo: (-20.1316, 12.3833, 23.1400) cm
[14:55:54]     occ1.transform: (-16.2967, 10.7033, 22.7900) cm (ctx_depth=0)
[14:55:54]     occ1.global:    (-16.2967, 10.7033, 22.7900) cm
[14:55:54]     occ2.transform: (-16.2967, 10.7033, 22.7400) cm (ctx_depth=0)
[14:55:54]     occ2.global:    (-16.2967, 10.7033, 22.7400) cm
[14:55:54]     → origin_global: (-0.201316, 0.123833, 0.231400) m [via geometryOrOriginOne]
[14:55:54]     motion: revolute, axis: (-0.000, -0.000, 1.000)
[14:55:54]   [REGULAR in macrobot] clamp_right_addition_joint
[14:55:54]     parent(occ2): gripper_right_addition path=gripper_right_addition:1
[14:55:54]     child(occ1):  gripper_clamp_right path=gripper_clamp_right:1
[14:55:54]     geometryOrOriginOne: (-21.6316, 11.6833, 23.1400) cm
[14:55:54]     geometryOrOriginTwo: (-21.6316, 11.6833, 23.1400) cm
[14:55:54]     occ1.transform: (-16.2967, 10.7033, 22.7900) cm (ctx_depth=0)
[14:55:54]     occ1.global:    (-16.2967, 10.7033, 22.7900) cm
[14:55:54]     occ2.transform: (-16.2967, 10.7033, 22.7900) cm (ctx_depth=0)
[14:55:54]     occ2.global:    (-16.2967, 10.7033, 22.7900) cm
[14:55:54]     → origin_global: (-0.216316, 0.116833, 0.231400) m [via geometryOrOriginOne]
[14:55:54]     motion: revolute, axis: (-0.000, -0.000, 1.000)
[14:55:55]   [REGULAR in macrobot] gripper_servo_joint
[14:55:55]     parent(occ2): gripper_link path=gripper_link:1
[14:55:55]     child(occ1):  gripper_servo_gear path=gripper_servo_gear:1
[14:55:55]     geometryOrOriginOne: (-18.4546, 7.6392, 22.5440) cm
[14:55:55]     geometryOrOriginTwo: (-18.4546, 7.6392, 22.5440) cm
[14:55:55]     occ1.transform: (-16.2967, 10.7033, 22.7900) cm (ctx_depth=0)
[14:55:55]     occ1.global:    (-16.2967, 10.7033, 22.7900) cm
[14:55:55]     occ2.transform: (-16.8267, 10.7033, 22.3400) cm (ctx_depth=0)
[14:55:55]     occ2.global:    (-16.8267, 10.7033, 22.3400) cm
[14:55:55]     → origin_global: (-0.184546, 0.076392, 0.225440) m [via geometryOrOriginOne]
[14:55:55]     motion: revolute, axis: (-0.000, -0.000, -1.000)
[14:55:55]   [REGULAR in macrobot] gripper_left_gear_joint
[14:55:55]     parent(occ2): gripper_link path=gripper_link:1
[14:55:55]     child(occ1):  gripper_left_gear path=gripper_left_gear:1
[14:55:55]     geometryOrOriginOne: (-20.1316, 6.9833, 23.1400) cm
[14:55:55]     geometryOrOriginTwo: (-20.1316, 6.9833, 23.1400) cm
[14:55:55]     occ1.transform: (-16.2967, 10.7033, 22.7400) cm (ctx_depth=0)
[14:55:55]     occ1.global:    (-16.2967, 10.7033, 22.7400) cm
[14:55:55]     occ2.transform: (-16.8267, 10.7033, 22.3400) cm (ctx_depth=0)
[14:55:55]     occ2.global:    (-16.8267, 10.7033, 22.3400) cm
[14:55:55]     → origin_global: (-0.201316, 0.069833, 0.231400) m [via geometryOrOriginOne]
[14:55:55]     motion: revolute, axis: (0.000, -0.000, 1.000)
[14:55:55]   [REGULAR in macrobot] gripper_right_gear_joint
[14:55:55]     parent(occ2): gripper_link path=gripper_link:1
[14:55:55]     child(occ1):  gripper_right_gear path=gripper_right_gear:1
[14:55:55]     geometryOrOriginOne: (-20.1316, 9.3833, 23.1400) cm
[14:55:55]     geometryOrOriginTwo: (-20.1316, 9.3833, 23.1400) cm
[14:55:55]     occ1.transform: (-16.2967, 10.7033, 22.7400) cm (ctx_depth=0)
[14:55:55]     occ1.global:    (-16.2967, 10.7033, 22.7400) cm
[14:55:55]     occ2.transform: (-16.8267, 10.7033, 22.3400) cm (ctx_depth=0)
[14:55:55]     occ2.global:    (-16.8267, 10.7033, 22.3400) cm
[14:55:55]     → origin_global: (-0.201316, 0.093833, 0.231400) m [via geometryOrOriginOne]
[14:55:55]     motion: revolute, axis: (0.000, -0.000, 1.000)
[14:55:55]   [REGULAR in macrobot] gripper_left_addition_joint
[14:55:55]     parent(occ2): gripper_link path=gripper_link:1
[14:55:55]     child(occ1):  gripper_left_addition path=gripper_left_addition:1
[14:55:55]     geometryOrOriginOne: (-21.6316, 7.6833, 23.1400) cm
[14:55:55]     geometryOrOriginTwo: (-21.6316, 7.6833, 23.1400) cm
[14:55:55]     occ1.transform: (-16.2967, 10.7033, 22.7900) cm (ctx_depth=0)
[14:55:55]     occ1.global:    (-16.2967, 10.7033, 22.7900) cm
[14:55:55]     occ2.transform: (-16.8267, 10.7033, 22.3400) cm (ctx_depth=0)
[14:55:55]     occ2.global:    (-16.8267, 10.7033, 22.3400) cm
[14:55:55]     → origin_global: (-0.216316, 0.076833, 0.231400) m [via geometryOrOriginOne]
[14:55:55]     motion: revolute, axis: (0.000, -0.000, 1.000)
[14:55:55]   [REGULAR in macrobot] gripper_right_addition_joint
[14:55:55]     parent(occ2): gripper_link path=gripper_link:1
[14:55:55]     child(occ1):  gripper_right_addition path=gripper_right_addition:1
[14:55:55]     geometryOrOriginOne: (-21.6316, 8.6833, 23.1400) cm
[14:55:55]     geometryOrOriginTwo: (-21.6316, 8.6833, 23.1400) cm
[14:55:55]     occ1.transform: (-16.2967, 10.7033, 22.7900) cm (ctx_depth=0)
[14:55:55]     occ1.global:    (-16.2967, 10.7033, 22.7900) cm
[14:55:55]     occ2.transform: (-16.8267, 10.7033, 22.3400) cm (ctx_depth=0)
[14:55:55]     occ2.global:    (-16.8267, 10.7033, 22.3400) cm
[14:55:55]     → origin_global: (-0.216316, 0.086833, 0.231400) m [via geometryOrOriginOne]
[14:55:55]     motion: revolute, axis: (0.000, -0.000, 1.000)
[14:55:55]   Extracted 16 unique joints
[14:55:55] 
=== EXTRACTION: RIGID GROUPS ===
[14:55:55]   No rigid groups found
[14:55:55] 
=== EXTRACTION SUMMARY ===
[14:55:55]   Occurrences: 15 (0 subassemblies, 15 leaf components)
[14:55:55]   Joints: 16 (0 as-built, 16 regular)
[14:55:55]   Max nesting depth: 0
[14:56:14] 
=== PHASE 1: DEBUG DATA ===
[14:56:14]   extraction_report.md
[14:56:14]   snapshot.json
[14:56:14]   fusion_transforms.json
[14:56:14] 
=== PHASE 2: BUILD ROBOT MODEL ===
[14:56:14] 
=== MODEL: ASSEMBLY HIERARCHY ===
[14:56:14]   Assembly: macrobot (synthetic root, wraps design-root leaves so phase 2 has a macro to xacro:include)
[14:56:14]   base_link → macrobot
[14:56:14]   camera_link → macrobot
[14:56:14]   front_left_wheel → macrobot
[14:56:14]   front_right_wheel → macrobot
[14:56:14]   back_left_wheel → macrobot
[14:56:14]   back_right_wheel → macrobot
[14:56:14]   robot_arm_link → macrobot
[14:56:14]   gripper_link → macrobot
[14:56:14]   gripper_servo_gear → macrobot
[14:56:14]   gripper_left_gear → macrobot
[14:56:14]   gripper_right_gear → macrobot
[14:56:14]   gripper_left_addition → macrobot
[14:56:14]   gripper_right_addition → macrobot
[14:56:14]   gripper_clamp_left → macrobot
[14:56:14]   gripper_clamp_right → macrobot
[14:56:14] 
=== MODEL: RIGID GROUP MERGE ===
[14:56:14]   No explicit rigid groups to merge
[14:56:14]   No auto rigid islands found
[14:56:14]   No rigid groups or auto rigid islands produced merged links
[14:56:14] 
=== MODEL: RESOLVE JOINT PATHS ===
[14:56:14]   camera_fix_joint     macrobot/base_link → macrobot/camera_link  [rigid] internal
[14:56:14]   front_left_wheel_joint macrobot/base_link → macrobot/front_left_wheel  [revolute] internal
[14:56:14]   front_right_wheel_joint macrobot/base_link → macrobot/front_right_wheel  [revolute] internal
[14:56:14]   back_left_wheel_joint macrobot/base_link → macrobot/back_left_wheel  [revolute] internal
[14:56:14]   back_right_wheel_joint macrobot/base_link → macrobot/back_right_wheel  [revolute] internal
[14:56:14]   robot_arm_joint      macrobot/base_link → macrobot/robot_arm_link  [revolute] internal
[14:56:14]   gripper_joint        macrobot/robot_arm_link → macrobot/gripper_link  [revolute] internal
[14:56:14]   clamp_left_gear_joint macrobot/gripper_left_gear → macrobot/gripper_clamp_left  [revolute] internal
[14:56:14]   clamp_left_addition_joint macrobot/gripper_left_addition → macrobot/gripper_clamp_left  [revolute] internal
[14:56:14]   clamp_right_gear_joint macrobot/gripper_right_gear → macrobot/gripper_clamp_right  [revolute] internal
[14:56:14]   clamp_right_addition_joint macrobot/gripper_right_addition → macrobot/gripper_clamp_right  [revolute] internal
[14:56:14]   gripper_servo_joint  macrobot/gripper_link → macrobot/gripper_servo_gear  [revolute] internal
[14:56:14]   gripper_left_gear_joint macrobot/gripper_link → macrobot/gripper_left_gear  [revolute] internal
[14:56:14]   gripper_right_gear_joint macrobot/gripper_link → macrobot/gripper_right_gear  [revolute] internal
[14:56:14]   gripper_left_addition_joint macrobot/gripper_link → macrobot/gripper_left_addition  [revolute] internal
[14:56:14]   gripper_right_addition_joint macrobot/gripper_link → macrobot/gripper_right_addition  [revolute] internal
[14:56:14]   WARNING:   CLOSING(auto): Multi-parent link detected (child=gripper_clamp_left:1): keeping 'clamp_left_addition_joint' as the URDF tree parent; routing ['clamp_left_gear_joint'] to ``closing_joints`` (sidecar) — closed kinematic loop.  Tag the loop-closing joint(s) with prefix ``!closing_*`` in Fusion to make the choice explicit and avoid this warning.
[14:56:14]   WARNING:   CLOSING(auto): Multi-parent link detected (child=gripper_clamp_right:1): keeping 'clamp_right_addition_joint' as the URDF tree parent; routing ['clamp_right_gear_joint'] to ``closing_joints`` (sidecar) — closed kinematic loop.  Tag the loop-closing joint(s) with prefix ``!closing_*`` in Fusion to make the choice explicit and avoid this warning.
[14:56:14] 
=== MODEL: DETECT ROOT ===
[14:56:14]   Parent-only nodes: 1
[14:56:14]     macrobot/base_link
[14:56:14]   → Root: macrobot/base_link
[14:56:14] 
=== MODEL: RESOLVE NAMES ===
[14:56:14]   back_left_wheel (macrobot) → back_left_wheel
[14:56:14]   back_right_wheel (macrobot) → back_right_wheel
[14:56:14]   base_link (macrobot) → base_link
[14:56:14]   camera_link (macrobot) → camera_link
[14:56:14]   front_left_wheel (macrobot) → front_left_wheel
[14:56:14]   front_right_wheel (macrobot) → front_right_wheel
[14:56:14]   gripper_clamp_left (macrobot) → gripper_clamp_left
[14:56:14]   gripper_clamp_right (macrobot) → gripper_clamp_right
[14:56:14]   gripper_left_addition (macrobot) → gripper_left_addition
[14:56:14]   gripper_left_gear (macrobot) → gripper_left_gear
[14:56:14]   gripper_link (macrobot) → gripper_link
[14:56:14]   gripper_right_addition (macrobot) → gripper_right_addition
[14:56:14]   gripper_right_gear (macrobot) → gripper_right_gear
[14:56:14]   gripper_servo_gear (macrobot) → gripper_servo_gear
[14:56:14]   robot_arm_link (macrobot) → robot_arm_link
[14:56:14]   Root link URDF name: base_link
[14:56:14] 
=== MODEL: BUILD LINKS ===
[14:56:14]   Built 15 links
[14:56:14] 
=== MODEL: BUILD JOINTS ===
[14:56:14]   NOTE: joint origin rpy derived from child occurrence's transform2 rotation (was hardcoded 0,0,0 pre-2026-04-13)
[14:56:14]   camera_fix_joint: base_link → camera_link [fixed]
[14:56:14]     origin_xyz: (0.397034, 0.038271, -0.117663) m [child_minus_parent]
[14:56:14]     origin_global: (-0.068167, 0.079456, 0.025820) m
[14:56:14]   front_left_wheel_joint: mesh bake offset = (-0.00, -0.00, -19.30) mm [child-local frame]
[14:56:14]   front_left_wheel_joint: base_link → front_left_wheel [continuous]
[14:56:14]     origin_xyz: (0.397034, 0.038271, -0.098363) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.000567, 0.000133, 0.019300) m
[14:56:14]   front_right_wheel_joint: mesh bake offset = (-0.00, -167.40, -19.30) mm [child-local frame]
[14:56:14]   front_right_wheel_joint: base_link → front_right_wheel [continuous]
[14:56:14]     origin_xyz: (0.397034, 0.205671, -0.098363) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.000567, 0.167533, 0.019300) m
[14:56:14]   back_left_wheel_joint: mesh bake offset = (-86.00, -0.00, -19.30) mm [child-local frame]
[14:56:14]   back_left_wheel_joint: base_link → back_left_wheel [continuous]
[14:56:14]     origin_xyz: (0.483034, 0.038271, -0.098363) m [joint_minus_parent]
[14:56:14]     origin_global: (0.085433, 0.000133, 0.019300) m
[14:56:14]   back_right_wheel_joint: mesh bake offset = (-86.00, -167.40, -19.30) mm [child-local frame]
[14:56:14]   back_right_wheel_joint: base_link → back_right_wheel [continuous]
[14:56:14]     origin_xyz: (0.483034, 0.205671, -0.098363) m [joint_minus_parent]
[14:56:14]     origin_global: (0.085433, 0.167533, 0.019300) m
[14:56:14]   robot_arm_joint: mesh bake offset = (-0.00, -0.00, -11.30) mm [child-local frame]
[14:56:14]   robot_arm_joint: joint origin rpy = (-1.637996, -1.570796, -2.865406) rad (-93.85°, -90.00°, -164.18°) [from child transform2 rotation]
[14:56:14]   robot_arm_joint: base_link → robot_arm_link [continuous]
[14:56:14]     origin_xyz: (0.390034, 0.150671, -0.059763) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.007567, 0.112533, 0.057900) m
[14:56:14]   gripper_joint: mesh bake offset = (-4.50, 160.30, -4.50) mm [child-local frame]
[14:56:14]   gripper_joint: parent bake correction += (0.00, 11.30, -0.00) mm [world frame]
[14:56:14]   gripper_joint: joint origin rpy = (-0.000000, -1.570796, 0.000000) rad (-0.00°, -90.00°, +0.00°) [from child transform2 rotation]
[14:56:14]   gripper_joint: origin_xyz rotated into parent-local frame: (-0.000400, -0.010000, 0.161000) → (0.161000, 0.000400, 0.010000) m
[14:56:14]   gripper_joint: robot_arm_link → gripper_link [continuous]
[14:56:14]     origin_xyz: (0.161000, 0.000400, 0.010000) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.007967, 0.102533, 0.218900) m
[14:56:14]   gripper_servo_joint: mesh bake offset = (30.64, -21.58, 2.46) mm [child-local frame]
[14:56:14]   gripper_servo_joint: parent bake correction += (-160.30, 4.50, 4.50) mm [world frame]
[14:56:14]   gripper_servo_joint: joint origin rpy = (3.141593, -0.000000, 3.141593) rad (+180.00°, -0.00°, +180.00°) [from child transform2 rotation]
[14:56:14]   gripper_servo_joint: origin_xyz rotated into parent-local frame: (-0.176579, -0.026141, 0.006540) → (0.026141, 0.176579, -0.006540) m
[14:56:14]   gripper_servo_joint: gripper_link → gripper_servo_gear [continuous]
[14:56:14]     origin_xyz: (0.026141, 0.176579, -0.006540) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.184546, 0.076392, 0.225440) m
[14:56:14]   gripper_left_gear_joint: mesh bake offset = (37.20, -38.35, -4.00) mm [child-local frame]
[14:56:14]   gripper_left_gear_joint: parent bake correction += (-160.30, 4.50, 4.50) mm [world frame]
[14:56:14]   gripper_left_gear_joint: joint origin rpy = (3.141593, 0.000000, -3.141593) rad (+180.00°, +0.00°, -180.00°) [from child transform2 rotation]
[14:56:14]   gripper_left_gear_joint: origin_xyz rotated into parent-local frame: (-0.193349, -0.032700, 0.012500) → (0.032700, 0.193349, -0.012500) m
[14:56:14]   gripper_left_gear_joint: gripper_link → gripper_left_gear [continuous]
[14:56:14]     origin_xyz: (0.032700, 0.193349, -0.012500) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.201316, 0.069833, 0.231400) m
[14:56:14]   gripper_right_gear_joint: mesh bake offset = (13.20, -38.35, -4.00) mm [child-local frame]
[14:56:14]   gripper_right_gear_joint: parent bake correction += (-160.30, 4.50, 4.50) mm [world frame]
[14:56:14]   gripper_right_gear_joint: joint origin rpy = (3.141593, 0.000000, -3.141593) rad (+180.00°, +0.00°, -180.00°) [from child transform2 rotation]
[14:56:14]   gripper_right_gear_joint: origin_xyz rotated into parent-local frame: (-0.193349, -0.008700, 0.012500) → (0.008700, 0.193349, -0.012500) m
[14:56:14]   gripper_right_gear_joint: gripper_link → gripper_right_gear [continuous]
[14:56:14]     origin_xyz: (0.008700, 0.193349, -0.012500) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.201316, 0.093833, 0.231400) m
[14:56:14]   gripper_left_addition_joint: mesh bake offset = (30.20, -53.35, -3.50) mm [child-local frame]
[14:56:14]   gripper_left_addition_joint: parent bake correction += (-160.30, 4.50, 4.50) mm [world frame]
[14:56:14]   gripper_left_addition_joint: joint origin rpy = (3.141593, 0.000000, -3.141593) rad (+180.00°, +0.00°, -180.00°) [from child transform2 rotation]
[14:56:14]   gripper_left_addition_joint: origin_xyz rotated into parent-local frame: (-0.208349, -0.025700, 0.012500) → (0.025700, 0.208349, -0.012500) m
[14:56:14]   gripper_left_addition_joint: gripper_link → gripper_left_addition [continuous]
[14:56:14]     origin_xyz: (0.025700, 0.208349, -0.012500) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.216316, 0.076833, 0.231400) m
[14:56:14]   gripper_right_addition_joint: mesh bake offset = (20.20, -53.35, -3.50) mm [child-local frame]
[14:56:14]   gripper_right_addition_joint: parent bake correction += (-160.30, 4.50, 4.50) mm [world frame]
[14:56:14]   gripper_right_addition_joint: joint origin rpy = (3.141593, 0.000000, -3.141593) rad (+180.00°, +0.00°, -180.00°) [from child transform2 rotation]
[14:56:14]   gripper_right_addition_joint: origin_xyz rotated into parent-local frame: (-0.208349, -0.015700, 0.012500) → (0.015700, 0.208349, -0.012500) m
[14:56:14]   gripper_right_addition_joint: gripper_link → gripper_right_addition [continuous]
[14:56:14]     origin_xyz: (0.015700, 0.208349, -0.012500) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.216316, 0.086833, 0.231400) m
[14:56:14]   clamp_left_gear_joint: parent bake correction += (38.35, 37.20, -4.00) mm [world frame]
[14:56:14]   clamp_left_gear_joint: origin_xyz rotated into parent-local frame: (-0.000000, -0.030000, -0.000000) → (-0.030000, -0.000000, -0.000000) m
[14:56:14]   clamp_left_gear_joint: gripper_left_gear → gripper_clamp_left [continuous] [closing/auto_detected]
[14:56:14]     origin_xyz: (-0.030000, -0.000000, -0.000000) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.201316, 0.039833, 0.231400) m
[14:56:14]   clamp_right_gear_joint: parent bake correction += (38.35, 13.20, -4.00) mm [world frame]
[14:56:14]   clamp_right_gear_joint: origin_xyz rotated into parent-local frame: (0.000000, 0.030000, -0.000000) → (0.030000, 0.000000, -0.000000) m
[14:56:14]   clamp_right_gear_joint: gripper_right_gear → gripper_clamp_right [continuous] [closing/auto_detected]
[14:56:14]     origin_xyz: (0.030000, 0.000000, -0.000000) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.201316, 0.123833, 0.231400) m
[14:56:14]   clamp_left_addition_joint: mesh bake offset = (60.20, -53.35, -3.50) mm [child-local frame]
[14:56:14]   clamp_left_addition_joint: parent bake correction += (53.35, 30.20, -3.50) mm [world frame]
[14:56:14]   clamp_left_addition_joint: origin_xyz rotated into parent-local frame: (-0.000000, -0.030000, 0.000000) → (-0.030000, -0.000000, 0.000000) m
[14:56:14]   clamp_left_addition_joint: gripper_left_addition → gripper_clamp_left [continuous]
[14:56:14]     origin_xyz: (-0.030000, -0.000000, 0.000000) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.216316, 0.046833, 0.231400) m
[14:56:14]   clamp_right_addition_joint: mesh bake offset = (-9.80, -53.35, -3.50) mm [child-local frame]
[14:56:14]   clamp_right_addition_joint: parent bake correction += (53.35, 20.20, -3.50) mm [world frame]
[14:56:14]   clamp_right_addition_joint: origin_xyz rotated into parent-local frame: (0.000000, 0.030000, 0.000000) → (0.030000, 0.000000, 0.000000) m
[14:56:14]   clamp_right_addition_joint: gripper_right_addition → gripper_clamp_right [continuous]
[14:56:14]     origin_xyz: (0.030000, 0.000000, 0.000000) m [joint_minus_parent]
[14:56:14]     origin_global: (-0.216316, 0.116833, 0.231400) m
[14:56:14]   Built 14 joints
[14:56:14] 
=== MODEL: VALIDATE ===
[14:56:14]   Validation passed (2 warnings)
[14:56:14] 
[14:56:14] Kinematic tree:
[14:56:14]   base_link (3497g)
[14:56:14]     ─── camera_fix_joint [fixed]
[14:56:14]       camera_link (0g)
[14:56:14]     ─⟳─ front_left_wheel_joint [continuous]
[14:56:14]       front_left_wheel (110g)
[14:56:14]     ─⟳─ front_right_wheel_joint [continuous]
[14:56:14]       front_right_wheel (110g)
[14:56:14]     ─⟳─ back_left_wheel_joint [continuous]
[14:56:14]       back_left_wheel (110g)
[14:56:14]     ─⟳─ back_right_wheel_joint [continuous]
[14:56:14]       back_right_wheel (110g)
[14:56:14]     ─⟳─ robot_arm_joint [continuous]
[14:56:14]       robot_arm_link (1111g)
[14:56:14]         ─⟳─ gripper_joint [continuous]
[14:56:14]           gripper_link (749g)
[14:56:14]             ─⟳─ gripper_servo_joint [continuous]
[14:56:14]               gripper_servo_gear (5g)
[14:56:14]             ─⟳─ gripper_left_gear_joint [continuous]
[14:56:14]               gripper_left_gear (16g)
[14:56:14]             ─⟳─ gripper_right_gear_joint [continuous]
[14:56:14]               gripper_right_gear (16g)
[14:56:14]             ─⟳─ gripper_left_addition_joint [continuous]
[14:56:14]               gripper_left_addition (6g)
[14:56:14]                 ─⟳─ clamp_left_addition_joint [continuous]
[14:56:14]                   gripper_clamp_left (12g)
[14:56:14]             ─⟳─ gripper_right_addition_joint [continuous]
[14:56:14]               gripper_right_addition (6g)
[14:56:14]                 ─⟳─ clamp_right_addition_joint [continuous]
[14:56:14]                   gripper_clamp_right (12g)
[14:56:14]   
[14:56:14]   Closed-loop joints (sidecar) — emitted to robot_data.yaml,
[14:56:14]   re-applied by downstream URDF→USD pipelines as USD physics joints:
[14:56:14]       ─⟳─ clamp_left_gear_joint [continuous] [auto_detected]: gripper_left_gear → gripper_clamp_left
[14:56:14]       ─⟳─ clamp_right_gear_joint [continuous] [auto_detected]: gripper_right_gear → gripper_clamp_right
[14:56:14] 
=== MODEL SUMMARY ===
[14:56:14]   Robot: macrobot
[14:56:14]   Root link: base_link
[14:56:14]   Links: 15
[14:56:14]   Joints: 14
[14:56:14]   Assemblies: 1
[14:56:14]   Warnings: 2
[14:56:14]   Errors: 0
[14:56:25] 
=== MESH EXPORT ===
[14:56:25]   base_link:
[14:56:26]     OBJ exported (5828622 bytes)
[14:56:26]     MTL preserved from Fusion (multi-material)
[14:56:27]     DAE written → meshes/macrobot/base_link.dae (OBJ retained for collision fit)
[14:56:27]   camera_link:
[14:56:27]     OBJ exported (48870 bytes)
[14:56:27]     MTL preserved from Fusion (multi-material)
[14:56:27]     DAE written → meshes/macrobot/camera_link.dae (OBJ retained for collision fit)
[14:56:27]   front_left_wheel:
[14:56:28]     OBJ exported (67043 bytes)
[14:56:28]     MTL preserved from Fusion (multi-material)
[14:56:28]     DAE written → meshes/macrobot/front_left_wheel.dae (OBJ retained for collision fit)
[14:56:28]   front_right_wheel:
[14:56:28]     OBJ exported (67249 bytes)
[14:56:28]     MTL preserved from Fusion (multi-material)
[14:56:28]     DAE written → meshes/macrobot/front_right_wheel.dae (OBJ retained for collision fit)
[14:56:28]   back_left_wheel:
[14:56:28]     OBJ exported (66853 bytes)
[14:56:28]     MTL preserved from Fusion (multi-material)
[14:56:28]     DAE written → meshes/macrobot/back_left_wheel.dae (OBJ retained for collision fit)
[14:56:28]   back_right_wheel:
[14:56:28]     OBJ exported (67150 bytes)
[14:56:28]     MTL preserved from Fusion (multi-material)
[14:56:28]     DAE written → meshes/macrobot/back_right_wheel.dae (OBJ retained for collision fit)
[14:56:28]   robot_arm_link:
[14:56:29]     OBJ exported (983026 bytes)
[14:56:29]     MTL preserved from Fusion (multi-material)
[14:56:29]     DAE written → meshes/macrobot/robot_arm_link.dae (OBJ retained for collision fit)
[14:56:29]   gripper_link:
[14:56:30]     OBJ exported (3003640 bytes)
[14:56:30]     MTL preserved from Fusion (multi-material)
[14:56:30]     DAE written → meshes/macrobot/gripper_link.dae (OBJ retained for collision fit)
[14:56:30]   gripper_servo_gear:
[14:56:31]     OBJ exported (2492316 bytes)
[14:56:32]     MTL preserved from Fusion (multi-material)
[14:56:32]     DAE written → meshes/macrobot/gripper_servo_gear.dae (OBJ retained for collision fit)
[14:56:32]   gripper_left_gear:
[14:56:33]     OBJ exported (791220 bytes)
[14:56:33]     MTL preserved from Fusion (multi-material)
[14:56:33]     DAE written → meshes/macrobot/gripper_left_gear.dae (OBJ retained for collision fit)
[14:56:33]   gripper_right_gear:
[14:56:33]     OBJ exported (784897 bytes)
[14:56:34]     MTL preserved from Fusion (multi-material)
[14:56:34]     DAE written → meshes/macrobot/gripper_right_gear.dae (OBJ retained for collision fit)
[14:56:34]   gripper_left_addition:
[14:56:34]     OBJ exported (149877 bytes)
[14:56:34]     MTL preserved from Fusion (multi-material)
[14:56:34]     DAE written → meshes/macrobot/gripper_left_addition.dae (OBJ retained for collision fit)
[14:56:34]   gripper_right_addition:
[14:56:34]     OBJ exported (149590 bytes)
[14:56:34]     MTL preserved from Fusion (multi-material)
[14:56:34]     DAE written → meshes/macrobot/gripper_right_addition.dae (OBJ retained for collision fit)
[14:56:34]   gripper_clamp_left:
[14:56:34]     OBJ exported (63799 bytes)
[14:56:34]     MTL preserved from Fusion (multi-material)
[14:56:34]     DAE written → meshes/macrobot/gripper_clamp_left.dae (OBJ retained for collision fit)
[14:56:34]   gripper_clamp_right:
[14:56:35]     OBJ exported (63614 bytes)
[14:56:35]     MTL preserved from Fusion (multi-material)
[14:56:35]     DAE written → meshes/macrobot/gripper_clamp_right.dae (OBJ retained for collision fit)
[14:56:35] 
  Mesh export summary:
[14:56:35]     Visual (OBJ+MTL):              15
[14:56:35]     Collision sub-component (STL):  0
[14:56:35]     Collision body + warning (STL): 0
[14:56:35]     Skipped (no Fusion ref):        0
[14:56:35] 
=== PHASE 3: SCREENSHOT ===
[14:56:37]   → images/robot.png
[14:56:37] 
=== PACKAGE: GENERATE ===
[14:56:37]   Package: macrobot_description
[14:56:37]   Output:  D:/서울대/제15회 창의설계축전/CAD files/urdf/macrobot_description\macrobot_description
[14:56:37] 
=== COLLISION: RESOLVE ===
[14:56:37]   base_link: visual reuse (collision = visual mesh)
[14:56:37]   camera_link: visual reuse (collision = visual mesh)
[14:56:37]   front_left_wheel: visual reuse (collision = visual mesh)
[14:56:37]   front_right_wheel: visual reuse (collision = visual mesh)
[14:56:37]   back_left_wheel: visual reuse (collision = visual mesh)
[14:56:37]   back_right_wheel: visual reuse (collision = visual mesh)
[14:56:37]   robot_arm_link: visual reuse (collision = visual mesh)
[14:56:37]   gripper_link: visual reuse (collision = visual mesh)
[14:56:37]   gripper_servo_gear: visual reuse (collision = visual mesh)
[14:56:37]   gripper_left_gear: visual reuse (collision = visual mesh)
[14:56:37]   gripper_right_gear: visual reuse (collision = visual mesh)
[14:56:37]   gripper_left_addition: visual reuse (collision = visual mesh)
[14:56:37]   gripper_right_addition: visual reuse (collision = visual mesh)
[14:56:37]   gripper_clamp_left: visual reuse (collision = visual mesh)
[14:56:37]   gripper_clamp_right: visual reuse (collision = visual mesh)
[14:56:37] 
  Collision summary:
[14:56:37]     Explicit:        0
[14:56:37]     Primitive (STL): 0
[14:56:37]     Convex hull STL: 0
[14:56:37]     Visual reuse:    15
[14:56:37]     Visual fallback: 0
[14:56:37] 
=== COLLISION: GENERATE STL ===
[14:56:37] 
  Generated 0 collision STL files
[14:56:37] 
=== PACKAGE: XACRO ===
[14:56:37]   → urdf/assemblies/macrobot.urdf.xacro
[14:56:37]   → urdf/macrobot.urdf.xacro
[14:56:37] 
=== PACKAGE: URDF (flat, for validation) ===
[14:56:37]   → urdf/macrobot.urdf
[14:56:37] 
=== PACKAGE: ROS2 FILES ===
[14:56:37]   → package.xml
[14:56:37]   → CMakeLists.txt
[14:56:37]   → launch/display.launch.py
[14:56:37]   → rviz/display.rviz
[14:56:37]   → config/joint_state.yaml
[14:56:37]   → config/ros2_controllers.yaml
[14:56:37] 
=== PACKAGE: SUPPLEMENTARY DATA ===
[14:56:37]   → robot_data.yaml
[14:56:37]   -> docs/transforms.md
[14:56:37] 
=== PACKAGE: README ===
[14:56:37]   → README.md
[14:56:37]   Cleaned up 30 retained OBJ/MTL files
[14:56:37] 
=== PACKAGE: COMPLETE ===
[14:56:37]   Package generated: D:/서울대/제15회 창의설계축전/CAD files/urdf/macrobot_description\macrobot_description
[14:56:37]   Xacro: urdf/macrobot.urdf.xacro (+ 1 assembly macros)
[14:56:37]   URDF:  urdf/macrobot.urdf (flat, for validation)
[14:56:37]   Launch: ros2 launch macrobot_description display.launch.py
[14:56:37] 
=== EXPORT COMPLETE ===
```
