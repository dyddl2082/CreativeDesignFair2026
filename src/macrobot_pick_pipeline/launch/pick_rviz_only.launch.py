from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg = Path(get_package_share_directory("macrobot_pick_pipeline"))
    rviz_file = pkg / "rviz" / "pick_pipeline.rviz"

    return LaunchDescription([
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2_pick_pipeline",
            output="screen",
            arguments=["-d", str(rviz_file)],
        ),
    ])
