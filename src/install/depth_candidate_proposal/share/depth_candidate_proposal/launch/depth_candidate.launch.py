from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = Path(get_package_share_directory("depth_candidate_proposal"))
    default_config = str(package_share / "config" / "depth_candidate.yaml")

    config_argument = DeclareLaunchArgument(
        "config_file",
        default_value=default_config,
        description="YAML parameter file for the aligned-depth proposal node",
    )

    node = Node(
        package="depth_candidate_proposal",
        executable="aligned_depth_candidate_node",
        name="aligned_depth_candidate",
        output="screen",
        parameters=[LaunchConfiguration("config_file")],
    )

    return LaunchDescription([config_argument, node])
