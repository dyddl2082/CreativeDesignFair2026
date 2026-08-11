from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = Path(get_package_share_directory("macrobot_description"))
    rviz_file = LaunchConfiguration("rviz_file")

    return LaunchDescription([
        DeclareLaunchArgument(
            "rviz_file",
            default_value=str(pkg / "rviz" / "display.rviz"),
            description="RViz config file to open",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2_macrobot",
            output="screen",
            arguments=["-d", rviz_file],
        ),
    ])
