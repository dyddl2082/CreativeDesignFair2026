from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    share = Path(get_package_share_directory("macrobot_perception"))
    params_file = LaunchConfiguration("params_file")
    return LaunchDescription([
        DeclareLaunchArgument(
            "params_file",
            default_value=str(share / "config" / "candidate_filter.yaml"),
        ),
        Node(
            package="macrobot_perception",
            executable="candidate_filter_node",
            name="candidate_filter",
            output="screen",
            parameters=[params_file],
        ),
    ])
