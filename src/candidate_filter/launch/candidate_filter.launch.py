from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os


def generate_launch_description() -> LaunchDescription:
    package_share = get_package_share_directory("candidate_filter")
    default_params = os.path.join(package_share, "config", "candidate_filter.yaml")
    params_file = LaunchConfiguration("params_file")
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value=default_params,
                description="Candidate filter parameter file",
            ),
            Node(
                package="candidate_filter",
                executable="candidate_filter_node",
                name="candidate_filter",
                output="screen",
                parameters=[params_file],
            ),
        ]
    )
