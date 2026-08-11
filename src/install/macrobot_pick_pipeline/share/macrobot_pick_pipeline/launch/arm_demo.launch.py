from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    package = Path(get_package_share_directory("macrobot_pick_pipeline"))

    start_rviz = LaunchConfiguration("start_rviz")
    allow_motion = LaunchConfiguration("allow_motion_commands")
    report_path = LaunchConfiguration("report_path")
    recordings_dir = LaunchConfiguration("recordings_dir")

    return LaunchDescription([
        DeclareLaunchArgument("start_rviz", default_value="false"),
        DeclareLaunchArgument("allow_motion_commands", default_value="true"),
        DeclareLaunchArgument(
            "report_path",
            default_value=str(
                Path.home()
                / "MacRobot"
                / "data"
                / "commissioning"
                / "arm_commissioning_report.yaml"
            ),
        ),
        DeclareLaunchArgument(
            "recordings_dir",
            default_value=str(Path.home() / "MacRobot" / "data" / "arm_primitives"),
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="arm_demo_recorder_node",
            name="macrobot_arm_demo_recorder",
            output="screen",
            parameters=[
                str(package / "config" / "arm_demo.yaml"),
                {
                    "allow_motion_commands": ParameterValue(
                        allow_motion, value_type=bool
                    ),
                    "report_path": report_path,
                    "recordings_dir": recordings_dir,
                },
            ],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2_arm_demo",
            output="screen",
            arguments=["-d", str(package / "rviz" / "pick_pipeline.rviz")],
            condition=IfCondition(start_rviz),
        ),
    ])
