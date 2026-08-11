from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = Path(get_package_share_directory("d435_capture_crop"))
    default_config = str(package_share / "config" / "d435_capture_crop.yaml")

    config_argument = DeclareLaunchArgument(
        "config_file",
        default_value=default_config,
        description="YAML parameter file for the D435 capture/crop node",
    )

    node = Node(
        package="d435_capture_crop",
        executable="d435_capture_crop_node",
        name="d435_capture_crop",
        output="screen",
        parameters=[LaunchConfiguration("config_file")],
    )

    return LaunchDescription([config_argument, node])
