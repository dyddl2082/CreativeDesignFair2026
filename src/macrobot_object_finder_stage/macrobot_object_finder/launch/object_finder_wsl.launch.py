from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    finder_share = Path(get_package_share_directory("macrobot_object_finder"))
    perception_share = Path(get_package_share_directory("macrobot_perception"))

    start_perception = LaunchConfiguration("start_perception")
    filter_params = LaunchConfiguration("filter_params")
    embedding_params = LaunchConfiguration("embedding_params")
    temporal_params = LaunchConfiguration("temporal_params")
    finder_params = LaunchConfiguration("finder_params")

    return LaunchDescription([
        DeclareLaunchArgument("start_perception", default_value="true"),
        DeclareLaunchArgument(
            "filter_params",
            default_value=str(perception_share / "config" / "candidate_filter.yaml"),
        ),
        DeclareLaunchArgument(
            "embedding_params",
            default_value=str(perception_share / "config" / "embedding_retrieval.yaml"),
        ),
        DeclareLaunchArgument(
            "temporal_params",
            default_value=str(perception_share / "config" / "temporal_confirmation.yaml"),
        ),
        DeclareLaunchArgument(
            "finder_params",
            default_value=str(finder_share / "config" / "object_finder.yaml"),
        ),
        Node(
            package="macrobot_perception",
            executable="candidate_filter_node",
            name="candidate_filter",
            output="screen",
            parameters=[filter_params, {"publish_debug": False}],
            condition=IfCondition(start_perception),
        ),
        Node(
            package="macrobot_perception",
            executable="embedding_retrieval_node",
            name="embedding_retrieval",
            output="screen",
            parameters=[
                embedding_params,
                {"publish_debug": False, "publish_matched_crops": False},
            ],
            condition=IfCondition(start_perception),
        ),
        Node(
            package="macrobot_perception",
            executable="temporal_confirmation_node",
            name="temporal_confirmation",
            output="screen",
            parameters=[
                temporal_params,
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
