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
    description = Path(get_package_share_directory("macrobot_description"))

    start_rviz = LaunchConfiguration("start_rviz")
    start_arm_demo = LaunchConfiguration("start_arm_demo")
    start_camera_teach = LaunchConfiguration("start_camera_teach")
    allow_motion = LaunchConfiguration("allow_motion_commands")
    use_finder = LaunchConfiguration("use_finder")
    report_path = LaunchConfiguration("report_path")
    recordings_dir = LaunchConfiguration("recordings_dir")
    generated_profile_file = LaunchConfiguration("generated_profile_file")

    return LaunchDescription([
        DeclareLaunchArgument("start_rviz", default_value="true"),
        DeclareLaunchArgument("start_arm_demo", default_value="true"),
        DeclareLaunchArgument("start_camera_teach", default_value="false"),
        DeclareLaunchArgument("allow_motion_commands", default_value="true"),
        DeclareLaunchArgument("use_finder", default_value="true"),
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
        DeclareLaunchArgument(
            "generated_profile_file",
            default_value=str(
                Path.home()
                / "MacRobot"
                / "data"
                / "commissioning"
                / "pick_profiles_recorded.yaml"
            ),
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="arm_demo_recorder_node",
            name="macrobot_arm_demo_recorder",
            output="screen",
            condition=IfCondition(start_arm_demo),
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
            package="macrobot_pick_pipeline",
            executable="camera_teach_node",
            name="macrobot_camera_teach",
            output="screen",
            condition=IfCondition(start_camera_teach),
            parameters=[
                str(package / "config" / "camera_teach.yaml"),
                {
                    "use_finder": ParameterValue(use_finder, value_type=bool),
                    "allow_motion_commands": ParameterValue(
                        allow_motion, value_type=bool
                    ),
                    "report_path": report_path,
                    "generated_profile_file": generated_profile_file,
                    "kinematics_file": str(
                        description / "config" / "kinematics.yaml"
                    ),
                },
            ],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2_pick_teach",
            output="screen",
            arguments=["-d", str(package / "rviz" / "pick_pipeline.rviz")],
            condition=IfCondition(start_rviz),
        ),
    ])
