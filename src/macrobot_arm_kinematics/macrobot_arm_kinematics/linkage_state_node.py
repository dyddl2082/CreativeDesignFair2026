from __future__ import annotations

import math
from typing import Dict

import rclpy
from geometry_msgs.msg import PoseStamped, Quaternion, TransformStamped
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64
from tf2_ros import TransformBroadcaster

from .model import ArmGeometry, JointLimits, MacRobotArmModel


def quaternion_from_pitch(pitch: float) -> Quaternion:
    q = Quaternion()
    q.x = 0.0
    q.y = math.sin(pitch / 2.0)
    q.z = 0.0
    q.w = math.cos(pitch / 2.0)
    return q


class LinkageStateNode(Node):
    """Map three logical actuator coordinates to the full Fusion visual joints.

    The node can also run in a pose-only mode for the reduced kinematic model:
    set ``publish_full_joint_states:=false`` and subscribe its logical input to
    ``/joint_states`` from joint_state_publisher_gui.
    """

    def __init__(self) -> None:
        super().__init__('macrobot_linkage_state_node')

        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('tool_frame', 'grasp_frame')
        self.declare_parameter('logical_state_topic', '/macrobot/arm/logical_joint_states')
        self.declare_parameter('full_joint_state_topic', '/joint_states')
        self.declare_parameter('tool_pose_topic', '/macrobot/arm/tool_pose')
        self.declare_parameter('gripper_gap_topic', '/macrobot/gripper/gap')
        self.declare_parameter('publish_full_joint_states', True)
        self.declare_parameter('publish_rate', 30.0)

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
        self.declare_parameter('gripper_min', -1.25)
        self.declare_parameter('gripper_max', 0.0)

        self.declare_parameter('lift_servo_joint', 'servo_left_gear_joint')
        self.declare_parameter('tilt_servo_joint', 'servo_right_gear_joint')
        self.declare_parameter('lift_ratio_joint', 'ratio_left_gear_joint')
        self.declare_parameter('tilt_ratio_joint', 'ratio_right_gear_joint')
        self.declare_parameter('rear_passive_joint', 'ratio_left_gear_back_link_joint')
        self.declare_parameter('top_passive_joint', 'back_link_top_link_joint')
        self.declare_parameter('lift_servo_multiplier', -2.0)
        self.declare_parameter('tilt_servo_multiplier', 2.0)

        self.declare_parameter('gripper_servo_joint', 'gripper_servo_joint')
        self.declare_parameter('gripper_left_gear_joint', 'gripper_left_gear_joint')
        self.declare_parameter('gripper_right_gear_joint', 'gripper_right_gear_joint')
        self.declare_parameter('gripper_left_addition_joint', 'gripper_left_addition_joint')
        self.declare_parameter('gripper_right_addition_joint', 'gripper_right_addition_joint')
        self.declare_parameter('gripper_left_clamp_joint', 'clamp_left_addition_joint')
        self.declare_parameter('gripper_right_clamp_joint', 'clamp_right_addition_joint')
        self.declare_parameter('gripper_servo_multiplier', 2.0)

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
        self.tool_frame = str(self.get_parameter('tool_frame').value)
        self.publish_full = bool(self.get_parameter('publish_full_joint_states').value)
        self.lift_servo_multiplier = float(self.get_parameter('lift_servo_multiplier').value)
        self.tilt_servo_multiplier = float(self.get_parameter('tilt_servo_multiplier').value)
        self.gripper_servo_multiplier = float(
            self.get_parameter('gripper_servo_multiplier').value
        )

        self.full_names = {
            'lift_servo': str(self.get_parameter('lift_servo_joint').value),
            'tilt_servo': str(self.get_parameter('tilt_servo_joint').value),
            'lift_ratio': str(self.get_parameter('lift_ratio_joint').value),
            'tilt_ratio': str(self.get_parameter('tilt_ratio_joint').value),
            'rear_passive': str(self.get_parameter('rear_passive_joint').value),
            'top_passive': str(self.get_parameter('top_passive_joint').value),
            'gripper_servo': str(self.get_parameter('gripper_servo_joint').value),
            'gripper_left_gear': str(self.get_parameter('gripper_left_gear_joint').value),
            'gripper_right_gear': str(self.get_parameter('gripper_right_gear_joint').value),
            'gripper_left_addition': str(
                self.get_parameter('gripper_left_addition_joint').value
            ),
            'gripper_right_addition': str(
                self.get_parameter('gripper_right_addition_joint').value
            ),
            'gripper_left_clamp': str(self.get_parameter('gripper_left_clamp_joint').value),
            'gripper_right_clamp': str(
                self.get_parameter('gripper_right_clamp_joint').value
            ),
        }
        self.wheel_names = [
            'front_left_wheel_joint',
            'back_left_wheel_joint',
            'front_right_wheel_joint',
            'back_right_wheel_joint',
        ]

        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0

        logical_topic = str(self.get_parameter('logical_state_topic').value)
        full_topic = str(self.get_parameter('full_joint_state_topic').value)
        tool_topic = str(self.get_parameter('tool_pose_topic').value)
        gap_topic = str(self.get_parameter('gripper_gap_topic').value)

        self.create_subscription(JointState, logical_topic, self.logical_callback, 10)
        self.joint_pub = (
            self.create_publisher(JointState, full_topic, 10) if self.publish_full else None
        )
        self.tool_pub = self.create_publisher(PoseStamped, tool_topic, 10)
        self.gap_pub = self.create_publisher(Float64, gap_topic, 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        rate = max(1.0, float(self.get_parameter('publish_rate').value))
        self.create_timer(1.0 / rate, self.publish_state)

        self.get_logger().info(
            'Linkage mapper ready: logical=%s, full_joint_states=%s, grasp_frame=%s'
            % (logical_topic, self.publish_full, self.tool_frame)
        )

    def logical_callback(self, msg: JointState) -> None:
        values: Dict[str, float] = dict(zip(msg.name, msg.position))
        q1 = values.get('arm_lift_joint', self.q1)
        q2 = values.get('wrist_pitch_joint', self.q2)
        q3 = values.get('gripper_joint', self.q3)
        if not self.model.limits.contains(q1, q2, q3):
            self.get_logger().warning(
                f'Rejected logical state outside constraints: '
                f'q1={q1:.3f}, q2={q2:.3f}, q3={q3:.3f}'
            )
            return
        self.q1 = q1
        self.q2 = q2
        self.q3 = q3

    def publish_state(self) -> None:
        now = self.get_clock().now().to_msg()

        if self.joint_pub is not None:
            mapped = self.model.full_visual_joint_positions(
                self.q1,
                self.q2,
                self.q3,
                self.lift_servo_multiplier,
                self.tilt_servo_multiplier,
                self.gripper_servo_multiplier,
            )
            order = (
                'lift_servo',
                'tilt_servo',
                'lift_ratio',
                'tilt_ratio',
                'rear_passive',
                'top_passive',
                'gripper_servo',
                'gripper_left_gear',
                'gripper_right_gear',
                'gripper_left_addition',
                'gripper_right_addition',
                'gripper_left_clamp',
                'gripper_right_clamp',
            )
            msg = JointState()
            msg.header.stamp = now
            msg.name = [self.full_names[key] for key in order] + self.wheel_names
            msg.position = [mapped[key] for key in order] + [0.0] * len(self.wheel_names)
            self.joint_pub.publish(msg)

        pose = self.model.forward(self.q1, self.q2, self.q3)
        orientation = quaternion_from_pitch(pose.pitch)

        pmsg = PoseStamped()
        pmsg.header.stamp = now
        pmsg.header.frame_id = self.base_frame
        pmsg.pose.position.x = pose.x
        pmsg.pose.position.y = pose.y
        pmsg.pose.position.z = pose.z
        pmsg.pose.orientation = orientation
        self.tool_pub.publish(pmsg)

        transform = TransformStamped()
        transform.header.stamp = now
        transform.header.frame_id = self.base_frame
        transform.child_frame_id = self.tool_frame
        transform.transform.translation.x = pose.x
        transform.transform.translation.y = pose.y
        transform.transform.translation.z = pose.z
        transform.transform.rotation = orientation
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
