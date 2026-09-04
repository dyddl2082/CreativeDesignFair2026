from __future__ import annotations

import math
from typing import Dict, Tuple

import rclpy
from geometry_msgs.msg import PoseStamped, TransformStamped
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64
from tf2_ros import TransformBroadcaster

from .model import ArmGeometry, JointLimits, MacRobotArmModel

MIMIC_MAP = {
    'clamp_left_addition_joint': ('gripper_joint', 1, 0),
    'clamp_right_addition_joint': ('gripper_joint', -1, 0),
    'gripper_left_addition_joint': ('gripper_joint', -1, 0),
    'gripper_left_gear_joint': ('gripper_joint', -1, 0),
    'gripper_right_addition_joint': ('gripper_joint', 1, 0),
    'gripper_right_gear_joint': ('gripper_joint', 1, 0),
    'gripper_servo_joint': ('gripper_joint', 2, 0),
}
WHEEL_JOINTS = ['front_left_wheel_joint', 'back_left_wheel_joint', 'front_right_wheel_joint', 'back_right_wheel_joint']


def _vector_parameter(node: Node, name: str) -> Tuple[float, float, float]:
    values = tuple(float(value) for value in node.get_parameter(name).value)
    if len(values) != 3:
        raise ValueError(f"{name} must contain three numbers")
    return values  # type: ignore[return-value]


class LinkageStateNode(Node):
    """Publish serial-2R logical state, exact tool pose, and gripper mimics."""

    def __init__(self) -> None:
        super().__init__("macrobot_linkage_state_node")
        self.declare_parameter("model_revision", 'macrobot-serial-2axis-2026-09-01-r3')
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("tool_frame", "grasp_frame")
        self.declare_parameter("logical_state_topic", "/macrobot/arm/logical_joint_states")
        self.declare_parameter("full_joint_state_topic", "/joint_states")
        self.declare_parameter("tool_pose_topic", "/macrobot/arm/tool_pose")
        self.declare_parameter("gripper_gap_topic", "/macrobot/gripper/gap")
        self.declare_parameter("publish_full_joint_states", True)
        self.declare_parameter("publish_mimic_joint_states", True)
        self.declare_parameter("publish_rate", 30.0)
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
        self.declare_parameter("gripper_open_gap_m", 0.070)
        self.declare_parameter("gripper_closed_gap_m", 0.010)
        self.declare_parameter("max_plane_error_m", 0.030)

        geometry = ArmGeometry(
            shoulder_origin_xyz=_vector_parameter(self, "shoulder_origin_xyz"),
            shoulder_origin_rpy=_vector_parameter(self, "shoulder_origin_rpy"),
            shoulder_axis=_vector_parameter(self, "shoulder_axis"),
            wrist_origin_xyz=_vector_parameter(self, "wrist_origin_xyz"),
            wrist_origin_rpy=_vector_parameter(self, "wrist_origin_rpy"),
            wrist_axis=_vector_parameter(self, "wrist_axis"),
            grasp_origin_xyz=_vector_parameter(self, "grasp_origin_xyz"),
            grasp_origin_rpy=_vector_parameter(self, "grasp_origin_rpy"),
            gripper_open_gap_m=float(self.get_parameter("gripper_open_gap_m").value),
            gripper_closed_gap_m=float(self.get_parameter("gripper_closed_gap_m").value),
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
        self.tool_frame = str(self.get_parameter("tool_frame").value)
        self.publish_full = bool(self.get_parameter("publish_full_joint_states").value)
        self.publish_mimics = bool(self.get_parameter("publish_mimic_joint_states").value)
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0

        logical_topic = str(self.get_parameter("logical_state_topic").value)
        full_topic = str(self.get_parameter("full_joint_state_topic").value)
        self.create_subscription(JointState, logical_topic, self.logical_callback, 10)
        self.joint_pub = self.create_publisher(JointState, full_topic, 10) if self.publish_full else None
        self.tool_pub = self.create_publisher(
            PoseStamped, str(self.get_parameter("tool_pose_topic").value), 10
        )
        self.gap_pub = self.create_publisher(
            Float64, str(self.get_parameter("gripper_gap_topic").value), 10
        )
        self.tf_broadcaster = TransformBroadcaster(self)
        rate = max(1.0, float(self.get_parameter("publish_rate").value))
        self.create_timer(1.0 / rate, self.publish_state)
        self.get_logger().info(
            f"Serial-2R state publisher ready; revision={self.get_parameter('model_revision').value}"
        )

    def logical_callback(self, msg: JointState) -> None:
        values: Dict[str, float] = dict(zip(msg.name, msg.position))
        candidate = (
            float(values.get("arm_lift_joint", self.q1)),
            float(values.get("wrist_pitch_joint", self.q2)),
            float(values.get("gripper_joint", self.q3)),
        )
        if not all(math.isfinite(value) for value in candidate):
            self.get_logger().warning("Rejected non-finite logical joint state")
            return
        if not self.model.limits.contains(*candidate):
            self.get_logger().warning(
                f"Rejected logical state outside limits: q={candidate}"
            )
            return
        self.q1, self.q2, self.q3 = candidate

    @staticmethod
    def _resolved_joint_positions(q1: float, q2: float, q3: float) -> Dict[str, float]:
        resolved: Dict[str, float] = {
            "arm_lift_joint": q1,
            "wrist_pitch_joint": q2,
            "gripper_joint": q3,
        }
        pending = dict(MIMIC_MAP)
        while pending:
            progressed = False
            for child, (master, multiplier, offset) in list(pending.items()):
                if master not in resolved:
                    continue
                resolved[child] = multiplier * resolved[master] + offset
                del pending[child]
                progressed = True
            if not progressed:
                break
        return resolved

    def publish_state(self) -> None:
        now = self.get_clock().now().to_msg()
        if self.joint_pub is not None:
            positions = self._resolved_joint_positions(self.q1, self.q2, self.q3)
            names = ["arm_lift_joint", "wrist_pitch_joint", "gripper_joint"]
            if self.publish_mimics:
                names.extend(name for name in sorted(MIMIC_MAP) if name not in names)
            names.extend(name for name in WHEEL_JOINTS if name not in names)
            msg = JointState()
            msg.header.stamp = now
            msg.name = names
            msg.position = [positions.get(name, 0.0) for name in names]
            self.joint_pub.publish(msg)

        pose = self.model.forward(self.q1, self.q2, self.q3)
        pmsg = PoseStamped()
        pmsg.header.stamp = now
        pmsg.header.frame_id = self.base_frame
        pmsg.pose.position.x = pose.x
        pmsg.pose.position.y = pose.y
        pmsg.pose.position.z = pose.z
        pmsg.pose.orientation.x = pose.qx
        pmsg.pose.orientation.y = pose.qy
        pmsg.pose.orientation.z = pose.qz
        pmsg.pose.orientation.w = pose.qw
        self.tool_pub.publish(pmsg)

        transform = TransformStamped()
        transform.header.stamp = now
        transform.header.frame_id = self.base_frame
        transform.child_frame_id = self.tool_frame
        transform.transform.translation.x = pose.x
        transform.transform.translation.y = pose.y
        transform.transform.translation.z = pose.z
        transform.transform.rotation = pmsg.pose.orientation
        self.tf_broadcaster.sendTransform(transform)

        gap = Float64()
        gap.data = self.model.gripper_gap(self.q3)
        self.gap_pub.publish(gap)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = LinkageStateNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
