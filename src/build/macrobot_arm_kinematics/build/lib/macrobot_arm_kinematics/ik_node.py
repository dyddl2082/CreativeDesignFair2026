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


class IKNode(Node):
    def __init__(self) -> None:
        super().__init__('macrobot_arm_ik_node')

        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('logical_state_topic', '/macrobot/arm/logical_joint_states')
        self.declare_parameter('target_topic', '/macrobot/arm/target_point')
        self.declare_parameter('solution_topic', '/macrobot/arm/ik_solution')
        self.declare_parameter('status_topic', '/macrobot/arm/ik_status')
        self.declare_parameter('auto_apply_ik', False)
        self.declare_parameter('seed_weight', 0.001)

        self.declare_parameter('pivot_x', 0.02095)
        self.declare_parameter('pivot_y', 0.06340)
        self.declare_parameter('pivot_z', 0.064595)
        self.declare_parameter('main_link_length', 0.10000)
        self.declare_parameter('tool_offset_x', -0.184756)
        self.declare_parameter('tool_offset_z', -0.006000)
        self.declare_parameter('tool_y', 0.064500)
        self.declare_parameter('gripper_link_length', 0.03000)
        self.declare_parameter('gripper_base_separation', 0.01000)

        self.declare_parameter('arm_lift_min', -1.0)
        self.declare_parameter('arm_lift_max', 1.0)
        self.declare_parameter('wrist_pitch_min', -1.30)
        self.declare_parameter('wrist_pitch_max', 1.30)
        self.declare_parameter('tool_pitch_min', -2.0)
        self.declare_parameter('tool_pitch_max', 2.0)
        self.declare_parameter('four_bar_margin', math.radians(10.0))
        self.declare_parameter('gripper_min', 0.0)
        self.declare_parameter('gripper_max', math.pi / 2.0)

        geometry = ArmGeometry(
            pivot_x=float(self.get_parameter('pivot_x').value),
            pivot_y=float(self.get_parameter('pivot_y').value),
            pivot_z=float(self.get_parameter('pivot_z').value),
            main_link_length=float(self.get_parameter('main_link_length').value),
            tool_offset_x=float(self.get_parameter('tool_offset_x').value),
            tool_offset_z=float(self.get_parameter('tool_offset_z').value),
            tool_y=float(self.get_parameter('tool_y').value),
            gripper_link_length=float(self.get_parameter('gripper_link_length').value),
            gripper_base_separation=float(self.get_parameter('gripper_base_separation').value),
        )
        limits = JointLimits(
            arm_lift_min=float(self.get_parameter('arm_lift_min').value),
            arm_lift_max=float(self.get_parameter('arm_lift_max').value),
            wrist_pitch_min=float(self.get_parameter('wrist_pitch_min').value),
            wrist_pitch_max=float(self.get_parameter('wrist_pitch_max').value),
            tool_pitch_min=float(self.get_parameter('tool_pitch_min').value),
            tool_pitch_max=float(self.get_parameter('tool_pitch_max').value),
            four_bar_margin=float(self.get_parameter('four_bar_margin').value),
            gripper_min=float(self.get_parameter('gripper_min').value),
            gripper_max=float(self.get_parameter('gripper_max').value),
        )
        self.model = MacRobotArmModel(geometry, limits)
        self.base_frame = str(self.get_parameter('base_frame').value)
        self.auto_apply = bool(self.get_parameter('auto_apply_ik').value)
        self.seed_weight = float(self.get_parameter('seed_weight').value)
        self.seed: Optional[Tuple[float, float]] = (0.0, 0.0)
        self.gripper_q = 0.0

        logical_topic = str(self.get_parameter('logical_state_topic').value)
        target_topic = str(self.get_parameter('target_topic').value)
        solution_topic = str(self.get_parameter('solution_topic').value)
        status_topic = str(self.get_parameter('status_topic').value)

        self.create_subscription(JointState, logical_topic, self.state_callback, 10)
        self.create_subscription(PointStamped, target_topic, self.target_callback, 10)
        self.solution_pub = self.create_publisher(JointState, solution_topic, 10)
        self.apply_pub = self.create_publisher(JointState, logical_topic, 10)
        self.status_pub = self.create_publisher(String, status_topic, 10)
        self.get_logger().info(
            f'IK target topic: {target_topic}; auto_apply={self.auto_apply}'
        )

    def state_callback(self, msg: JointState) -> None:
        values = dict(zip(msg.name, msg.position))
        if 'arm_lift_joint' in values and 'wrist_pitch_joint' in values:
            self.seed = (values['arm_lift_joint'], values['wrist_pitch_joint'])
        if 'gripper_joint' in values:
            self.gripper_q = values['gripper_joint']

    def target_callback(self, msg: PointStamped) -> None:
        if msg.header.frame_id and msg.header.frame_id != self.base_frame:
            self.publish_status(
                False,
                'frame_mismatch',
                {
                    'expected_frame': self.base_frame,
                    'received_frame': msg.header.frame_id,
                },
            )
            return

        solutions = self.model.inverse(
            msg.point.x,
            msg.point.z,
            seed=self.seed,
            seed_weight=self.seed_weight,
            gripper_q=self.gripper_q,
        )
        if not solutions:
            self.publish_status(
                False,
                'unreachable',
                {
                    'target_x': msg.point.x,
                    'target_y': msg.point.y,
                    'target_z': msg.point.z,
                    'gripper_joint': self.gripper_q,
                },
            )
            return

        best = solutions[0]
        result = JointState()
        result.header.stamp = self.get_clock().now().to_msg()
        result.name = ['arm_lift_joint', 'wrist_pitch_joint', 'gripper_joint']
        result.position = [best.q1, best.q2, self.gripper_q]
        self.solution_pub.publish(result)
        if self.auto_apply:
            self.apply_pub.publish(result)
        self.seed = (best.q1, best.q2)

        pose = self.model.forward(best.q1, best.q2, self.gripper_q)
        self.publish_status(
            True,
            'solution',
            {
                'q1': best.q1,
                'q2': best.q2,
                'gripper_joint': self.gripper_q,
                'gripper_gap_m': self.model.gripper_gap(self.gripper_q),
                'rear_lift_angle': best.q1 + best.q2,
                'urdf_pitch_about_positive_y': pose.pitch,
                'position_error_m': best.position_error,
                'seed_distance': best.seed_distance,
                'target_x': msg.point.x,
                'target_z': msg.point.z,
                'solution_x': pose.x,
                'solution_y': pose.y,
                'solution_z': pose.z,
            },
        )

    def publish_status(self, ok: bool, event: str, details: dict) -> None:
        msg = String()
        msg.data = json.dumps({'ok': ok, 'event': event, **details}, ensure_ascii=False)
        self.status_pub.publish(msg)
        if ok:
            self.get_logger().info(msg.data)
        else:
            self.get_logger().warning(msg.data)


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
