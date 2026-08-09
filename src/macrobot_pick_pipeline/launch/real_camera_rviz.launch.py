from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package = Path(get_package_share_directory("macrobot_pick_pipeline"))
    start_rviz = LaunchConfiguration("start_rviz")
    return LaunchDescription([
        DeclareLaunchArgument("start_rviz", default_value="true"),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2_macrobot_real_camera",
            output="screen",
            arguments=["-d", str(package / "rviz" / "real_camera.rviz")],
            condition=IfCondition(start_rviz),
        ),
    ])
