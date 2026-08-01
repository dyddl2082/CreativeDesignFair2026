from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os


def generate_launch_description() -> LaunchDescription:
    package_share = get_package_share_directory("temporal_confirmation")
    default_params = os.path.join(
        package_share,
        "config",
        "temporal_confirmation.yaml",
    )
    params_file = LaunchConfiguration("params_file")
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value=default_params,
                description="Temporal confirmation parameter file",
            ),
            Node(
                package="temporal_confirmation",
                executable="temporal_confirmation_node",
                name="temporal_confirmation",
                output="screen",
                parameters=[params_file],
            ),
        ]
    )
