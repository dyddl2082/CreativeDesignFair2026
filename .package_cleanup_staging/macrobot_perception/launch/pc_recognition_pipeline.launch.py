from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    share = Path(get_package_share_directory("macrobot_perception"))
    filter_params = LaunchConfiguration("filter_params")
    embedding_params = LaunchConfiguration("embedding_params")
    temporal_params = LaunchConfiguration("temporal_params")
    return LaunchDescription([
        DeclareLaunchArgument(
            "filter_params",
            default_value=str(share / "config" / "candidate_filter.yaml"),
        ),
        DeclareLaunchArgument(
            "embedding_params",
            default_value=str(share / "config" / "embedding_retrieval.yaml"),
        ),
        DeclareLaunchArgument(
            "temporal_params",
            default_value=str(share / "config" / "temporal_confirmation.yaml"),
        ),
        Node(
            package="macrobot_perception",
            executable="candidate_filter_node",
            name="candidate_filter",
            output="screen",
            parameters=[filter_params],
        ),
        Node(
            package="macrobot_perception",
            executable="embedding_retrieval_node",
            name="embedding_retrieval",
            output="screen",
            parameters=[embedding_params],
        ),
        Node(
            package="macrobot_perception",
            executable="temporal_confirmation_node",
            name="temporal_confirmation",
            output="screen",
            parameters=[temporal_params],
        ),
    ])
