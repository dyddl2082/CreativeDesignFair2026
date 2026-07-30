from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os


def generate_launch_description() -> LaunchDescription:
    package_share = get_package_share_directory("embedding_retrieval")
    default_params = os.path.join(
        package_share,
        "config",
        "embedding_retrieval.yaml",
    )
    params_file = LaunchConfiguration("params_file")
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value=default_params,
                description="DINOv2 embedding retrieval parameter file",
            ),
            Node(
                package="embedding_retrieval",
                executable="embedding_retrieval_node",
                name="embedding_retrieval",
                output="screen",
                parameters=[params_file],
            ),
        ]
    )
