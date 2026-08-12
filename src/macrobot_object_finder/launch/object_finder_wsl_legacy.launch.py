from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    finder_share = Path(get_package_share_directory("macrobot_object_finder"))
    filter_share = Path(get_package_share_directory("candidate_filter"))
    embedding_share = Path(get_package_share_directory("embedding_retrieval"))
    temporal_share = Path(get_package_share_directory("temporal_confirmation"))

    start_perception = LaunchConfiguration("start_perception")
    finder_params = LaunchConfiguration("finder_params")

    return LaunchDescription([
        DeclareLaunchArgument("start_perception", default_value="true"),
        DeclareLaunchArgument(
            "finder_params",
            default_value=str(finder_share / "config" / "object_finder.yaml"),
        ),
        Node(
            package="candidate_filter",
            executable="candidate_filter_node",
            name="candidate_filter",
            output="screen",
            parameters=[
                str(filter_share / "config" / "candidate_filter.yaml"),
                {"publish_debug": False},
            ],
            condition=IfCondition(start_perception),
        ),
        Node(
            package="embedding_retrieval",
            executable="embedding_retrieval_node",
            name="embedding_retrieval",
            output="screen",
            parameters=[
                str(embedding_share / "config" / "embedding_retrieval.yaml"),
                {"publish_debug": False, "publish_matched_crops": False},
            ],
            condition=IfCondition(start_perception),
        ),
        Node(
            package="temporal_confirmation",
            executable="temporal_confirmation_node",
            name="temporal_confirmation",
            output="screen",
            parameters=[
                str(temporal_share / "config" / "temporal_confirmation.yaml"),
                {
                    "publish_legacy_json": False,
                    "publish_lost_legacy_event": False,
                },
            ],
            condition=IfCondition(start_perception),
        ),
        Node(
            package="macrobot_object_finder",
            executable="object_finder_node",
            name="macrobot_object_finder",
            output="screen",
            parameters=[finder_params],
        ),
    ])
