from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os


def _default_config(package_name: str, filename: str) -> str:
    return os.path.join(
        get_package_share_directory(package_name),
        "config",
        filename,
    )


def generate_launch_description() -> LaunchDescription:
    filter_params = LaunchConfiguration("filter_params")
    embedding_params = LaunchConfiguration("embedding_params")
    temporal_params = LaunchConfiguration("temporal_params")
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "filter_params",
                default_value=_default_config(
                    "candidate_filter",
                    "candidate_filter.yaml",
                ),
            ),
            DeclareLaunchArgument(
                "embedding_params",
                default_value=_default_config(
                    "embedding_retrieval",
                    "embedding_retrieval.yaml",
                ),
            ),
            DeclareLaunchArgument(
                "temporal_params",
                default_value=_default_config(
                    "temporal_confirmation",
                    "temporal_confirmation.yaml",
                ),
            ),
            Node(
                package="candidate_filter",
                executable="candidate_filter_node",
                name="candidate_filter",
                output="screen",
                parameters=[filter_params],
            ),
            Node(
                package="embedding_retrieval",
                executable="embedding_retrieval_node",
                name="embedding_retrieval",
                output="screen",
                parameters=[embedding_params],
            ),
            Node(
                package="temporal_confirmation",
                executable="temporal_confirmation_node",
                name="temporal_confirmation",
                output="screen",
                parameters=[temporal_params],
            ),
        ]
    )
