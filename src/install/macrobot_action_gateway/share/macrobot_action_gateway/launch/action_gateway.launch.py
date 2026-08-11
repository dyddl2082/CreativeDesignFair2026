from __future__ import annotations

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    share = Path(get_package_share_directory("macrobot_action_gateway"))
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "real_motion_enabled",
                default_value="false",
                description="Allow actual ROS/Pico motion. Default false for safety.",
            ),
            DeclareLaunchArgument(
                "socket_path",
                default_value="/tmp/macrobot_action_gateway.sock",
            ),
            DeclareLaunchArgument(
                "settings_file",
                default_value=str(share / "config" / "gateway.yaml"),
            ),
            DeclareLaunchArgument(
                "object_catalog_file",
                default_value=str(share / "config" / "object_catalog.yaml"),
            ),
            Node(
                package="macrobot_action_gateway",
                executable="action_gateway_node",
                name="macrobot_action_gateway",
                output="screen",
                parameters=[
                    {
                        "real_motion_enabled": ParameterValue(
                            LaunchConfiguration("real_motion_enabled"), value_type=bool
                        ),
                        "socket_path": LaunchConfiguration("socket_path"),
                        "settings_file": LaunchConfiguration("settings_file"),
                        "object_catalog_file": LaunchConfiguration("object_catalog_file"),
                    }
                ],
            ),
        ]
    )
