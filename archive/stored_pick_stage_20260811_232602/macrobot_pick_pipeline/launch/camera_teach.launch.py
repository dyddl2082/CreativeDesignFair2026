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
    start_localizer = LaunchConfiguration("start_localizer")
    start_coordinator = LaunchConfiguration("start_coordinator")
    use_finder = LaunchConfiguration("use_finder")
    allow_motion = LaunchConfiguration("allow_motion_commands")
    report_path = LaunchConfiguration("report_path")
    generated_profile_file = LaunchConfiguration("generated_profile_file")
    profile_file = LaunchConfiguration("profile_file")
    require_camera_health = LaunchConfiguration("require_camera_health")

    return LaunchDescription([
        DeclareLaunchArgument("start_rviz", default_value="true"),
        DeclareLaunchArgument("start_localizer", default_value="false"),
        DeclareLaunchArgument("start_coordinator", default_value="false"),
        DeclareLaunchArgument("use_finder", default_value="true"),
        DeclareLaunchArgument("allow_motion_commands", default_value="true"),
        DeclareLaunchArgument("require_camera_health", default_value="true"),
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
            "generated_profile_file",
            default_value=str(
                Path.home()
                / "MacRobot"
                / "data"
                / "commissioning"
                / "pick_profiles_recorded.yaml"
            ),
        ),
        DeclareLaunchArgument(
            "profile_file",
            default_value=str(package / "config" / "pick_profiles.yaml"),
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="detection_localizer_node",
            name="macrobot_detection_localizer",
            output="screen",
            condition=IfCondition(start_localizer),
            parameters=[str(package / "config" / "perception.yaml")],
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="pick_coordinator_node",
            name="macrobot_pick_coordinator",
            output="screen",
            condition=IfCondition(start_coordinator),
            parameters=[
                str(package / "config" / "coordinator.yaml"),
                {
                    "use_finder": ParameterValue(use_finder, value_type=bool),
                    "profile_file": profile_file,
                    "commissioning_report": report_path,
                },
            ],
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="camera_teach_node",
            name="macrobot_camera_teach",
            output="screen",
            parameters=[
                str(package / "config" / "camera_teach.yaml"),
                {
                    "use_finder": ParameterValue(use_finder, value_type=bool),
                    "allow_motion_commands": ParameterValue(
                        allow_motion, value_type=bool
                    ),
                    "require_camera_health": ParameterValue(
                        require_camera_health, value_type=bool
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
            name="rviz2_camera_teach",
            output="screen",
            arguments=["-d", str(package / "rviz" / "pick_pipeline.rviz")],
            condition=IfCondition(start_rviz),
        ),
    ])
