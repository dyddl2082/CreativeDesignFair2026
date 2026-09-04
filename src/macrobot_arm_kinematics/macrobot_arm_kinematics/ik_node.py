from __future__ import annotations

import json
import math
from typing import Optional, Tuple

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String

from .model import ArmGeometry, JointLimits, MacRobotArmModel


def _vector_parameter(node: Node, name: str) -> Tuple[float, float, float]:
    values = tuple(float(value) for value in node.get_parameter(name).value)
    if len(values) != 3:
        raise ValueError(f"{name} must contain three numbers")
    return values  # type: ignore[return-value]


class IKNode(Node):
    def __init__(self) -> None:
        super().__init__("macrobot_arm_ik_node")
        self.declare_parameter("model_revision", 'macrobot-serial-2axis-2026-09-01-r3')
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("logical_state_topic", "/macrobot/arm/logical_joint_states")
        self.declare_parameter("target_topic", "/macrobot/arm/target_point")
        self.declare_parameter("solution_topic", "/macrobot/arm/ik_solution")
        self.declare_parameter("status_topic", "/macrobot/arm/ik_status")
        self.declare_parameter("auto_apply_ik", False)
        self.declare_parameter("seed_weight", 0.001)
        self.declare_parameter("max_plane_error_m", 0.030)
        self.declare_parameter('shoulder_origin_xyz', [0.03, 0.0937, 0.0579])
        self.declare_parameter('shoulder_origin_rpy', [-1.662703, -1.570796, -3.049686])
        self.declare_parameter('shoulder_axis', [-0.0, 0.0, -1.0])
        self.declare_parameter('wrist_origin_xyz', [0.161, 0.0004, 0.0])
        self.declare_parameter('wrist_origin_rpy', [-0.0, -1.570796, 0.0])
        self.declare_parameter('wrist_axis', [-1.0, 0.0, 0.0])
        self.declare_parameter('grasp_origin_xyz', [0.013, 0.218151, -0.008098])
        self.declare_parameter('grasp_origin_rpy', [0.0, 0.0, 0.0])
        self.declare_parameter("arm_lift_min", -1)
        self.declare_parameter("arm_lift_max", 1)
        self.declare_parameter("wrist_pitch_min", -1.3)
        self.declare_parameter("wrist_pitch_max", 1.3)
        self.declare_parameter("gripper_min", 0)
        self.declare_parameter("gripper_max", 1.5707963268)

        geometry = ArmGeometry(
            shoulder_origin_xyz=_vector_parameter(self, "shoulder_origin_xyz"),
            shoulder_origin_rpy=_vector_parameter(self, "shoulder_origin_rpy"),
            shoulder_axis=_vector_parameter(self, "shoulder_axis"),
            wrist_origin_xyz=_vector_parameter(self, "wrist_origin_xyz"),
            wrist_origin_rpy=_vector_parameter(self, "wrist_origin_rpy"),
            wrist_axis=_vector_parameter(self, "wrist_axis"),
            grasp_origin_xyz=_vector_parameter(self, "grasp_origin_xyz"),
            grasp_origin_rpy=_vector_parameter(self, "grasp_origin_rpy"),
        )
        limits = JointLimits(
            arm_lift_min=float(self.get_parameter("arm_lift_min").value),
            arm_lift_max=float(self.get_parameter("arm_lift_max").value),
            wrist_pitch_min=float(self.get_parameter("wrist_pitch_min").value),
            wrist_pitch_max=float(self.get_parameter("wrist_pitch_max").value),
            gripper_min=float(self.get_parameter("gripper_min").value),
            gripper_max=float(self.get_parameter("gripper_max").value),
        )
        self.model = MacRobotArmModel(
            geometry,
            limits,
            max_plane_error_m=float(self.get_parameter("max_plane_error_m").value),
        )
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.auto_apply = bool(self.get_parameter("auto_apply_ik").value)
        self.seed_weight = float(self.get_parameter("seed_weight").value)
        self.seed: Optional[Tuple[float, float]] = (0.0, 0.0)
        self.gripper_q = 0.0

        logical_topic = str(self.get_parameter("logical_state_topic").value)
        self.create_subscription(JointState, logical_topic, self.state_callback, 10)
        self.create_subscription(
            PointStamped,
            str(self.get_parameter("target_topic").value),
            self.target_callback,
            10,
        )
        self.solution_pub = self.create_publisher(
            JointState, str(self.get_parameter("solution_topic").value), 10
        )
        self.apply_pub = self.create_publisher(JointState, logical_topic, 10)
        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), 10
        )

    def state_callback(self, msg: JointState) -> None:
        values = dict(zip(msg.name, msg.position))
        if "arm_lift_joint" in values and "wrist_pitch_joint" in values:
            self.seed = (float(values["arm_lift_joint"]), float(values["wrist_pitch_joint"]))
        if "gripper_joint" in values:
            self.gripper_q = float(values["gripper_joint"])

    def target_callback(self, msg: PointStamped) -> None:
        if msg.header.frame_id and msg.header.frame_id != self.base_frame:
            self.publish_status(False, "frame_mismatch", {
                "expected_frame": self.base_frame,
                "received_frame": msg.header.frame_id,
            })
            return
        target = (float(msg.point.x), float(msg.point.y), float(msg.point.z))
        if not all(math.isfinite(value) for value in target):
            self.publish_status(False, "non_finite_target", {"target": list(target)})
            return
        solutions = self.model.inverse_xyz(
            *target,
            seed=self.seed,
            seed_weight=self.seed_weight,
            gripper_q=self.gripper_q,
        )
        if not solutions:
            self.publish_status(False, "unreachable_or_out_of_plane", {
                "target_x": target[0],
                "target_y": target[1],
                "target_z": target[2],
                "gripper_joint": self.gripper_q,
            })
            return

        best = solutions[0]
        result = JointState()
        result.header.stamp = self.get_clock().now().to_msg()
        result.name = ["arm_lift_joint", "wrist_pitch_joint", "gripper_joint"]
        result.position = [best.q1, best.q2, self.gripper_q]
        self.solution_pub.publish(result)
        if self.auto_apply:
            self.apply_pub.publish(result)
        self.seed = (best.q1, best.q2)

        pose = self.model.forward(best.q1, best.q2, self.gripper_q)
        self.publish_status(True, "solution", {
            "model_type": "serial_2r",
            "model_revision": self.get_parameter("model_revision").value,
            "q1": best.q1,
            "q2": best.q2,
            "gripper_joint": self.gripper_q,
            "gripper_gap_m": self.model.gripper_gap(self.gripper_q),
            "plane_error_m": best.plane_error_m,
            "in_plane_error_m": best.in_plane_error_m,
            "position_error_m": best.position_error,
            "seed_distance": best.seed_distance,
            "target_x": target[0],
            "target_y": target[1],
            "target_z": target[2],
            "solution_x": pose.x,
            "solution_y": pose.y,
            "solution_z": pose.z,
            "solution_rpy": [pose.roll, pose.pitch, pose.yaw],
        })

    def publish_status(self, ok: bool, event: str, details: dict) -> None:
        message = String()
        message.data = json.dumps({"ok": ok, "event": event, **details}, ensure_ascii=False)
        self.status_pub.publish(message)
        logger = self.get_logger()
        if ok:
            logger.info(message.data)
        else:
            logger.warning(message.data)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = IKNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
