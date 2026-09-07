from __future__ import annotations

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    share = Path(get_package_share_directory("macrobot_ui"))
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_file",
                default_value=str(share / "config" / "backend.yaml"),
            ),
            DeclareLaunchArgument(
                "allow_execution",
                default_value="false",
                description=(
                    "Allow approved programs to invoke robot_code_runner. "
                    "Action Gateway real_motion_enabled remains a separate gate."
                ),
            ),
            DeclareLaunchArgument(
                "gateway_socket",
                default_value="/tmp/macrobot_action_gateway.sock",
            ),
            Node(
                package="macrobot_ui",
                executable="macrobot_ui_backend",
                name="macrobot_ui_backend",
                output="screen",
                parameters=[
                    LaunchConfiguration("config_file"),
                    {
                        "allow_execution": ParameterValue(
                            LaunchConfiguration("allow_execution"),
                            value_type=bool,
                        ),
                        "gateway_socket": LaunchConfiguration("gateway_socket"),
                    },
                ],
            ),
        ]
    )
