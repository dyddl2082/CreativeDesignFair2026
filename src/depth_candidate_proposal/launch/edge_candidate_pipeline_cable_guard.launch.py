"""D435 depth candidate pipeline with cable-clutter refinement.

This launch intentionally changes the candidate topic flow:

aligned_depth_candidate_node -> /depth_candidates/raw_candidates
candidate_refiner_node       -> /depth_candidates/candidates
rgb_candidate_crop_node      -> /depth_candidates/rgb_crops
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from pathlib import Path


def generate_launch_description():
    package_share = Path(get_package_share_directory("depth_candidate_proposal"))
    default_config = str(package_share / "config" / "depth_candidate.yaml")
    default_refiner_config = str(package_share / "config" / "candidate_refiner.yaml")

    config_file = LaunchConfiguration("config_file")
    refiner_config_file = LaunchConfiguration("refiner_config_file")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_file",
                default_value=default_config,
                description="Depth candidate and RGB crop parameter YAML",
            ),
            DeclareLaunchArgument(
                "refiner_config_file",
                default_value=default_refiner_config,
                description="Cable-aware candidate refiner parameter YAML",
            ),
            Node(
                package="depth_candidate_proposal",
                executable="aligned_depth_candidate_node",
                name="aligned_depth_candidate",
                output="screen",
                parameters=[
                    config_file,
                    {"candidate_topic": "/depth_candidates/raw_candidates"},
                ],
            ),
            Node(
                package="depth_candidate_proposal",
                executable="candidate_refiner_node",
                name="candidate_refiner",
                output="screen",
                parameters=[refiner_config_file],
            ),
            Node(
                package="depth_candidate_proposal",
                executable="rgb_candidate_crop_node",
                name="rgb_candidate_crop",
                output="screen",
                parameters=[
                    config_file,
                    {"candidate_topic": "/depth_candidates/candidates"},
                ],
            ),
        ]
    )
