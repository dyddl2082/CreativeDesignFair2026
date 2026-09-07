from __future__ import annotations

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    share = Path(get_package_share_directory("macrobot_ui"))
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_file",
                default_value=str(share / "config" / "ui.yaml"),
            ),
            Node(
                package="macrobot_ui",
                executable="macrobot_ui",
                name="macrobot_ui",
                output="screen",
                parameters=[LaunchConfiguration("config_file")],
            ),
        ]
    )
