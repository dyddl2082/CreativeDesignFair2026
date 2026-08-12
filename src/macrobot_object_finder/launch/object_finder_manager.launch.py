from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    share = Path(get_package_share_directory("macrobot_object_finder"))
    params = LaunchConfiguration("params_file")
    return LaunchDescription([
        DeclareLaunchArgument(
            "params_file",
            default_value=str(share / "config" / "object_finder.yaml"),
        ),
        Node(
            package="macrobot_object_finder",
            executable="object_finder_node",
            name="macrobot_object_finder",
            output="screen",
            parameters=[params],
        ),
    ])
