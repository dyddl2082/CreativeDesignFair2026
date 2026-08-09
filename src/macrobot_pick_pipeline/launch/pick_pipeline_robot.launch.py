from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    package = Path(get_package_share_directory("macrobot_pick_pipeline"))
    arm_control = Path(get_package_share_directory("macrobot_arm_control"))

    safe_region_csv = LaunchConfiguration("safe_region_csv")
    serial_port = LaunchConfiguration("serial_port")
    start_pico_debug = LaunchConfiguration("start_pico_debug")
    profile_file = LaunchConfiguration("profile_file")
    commissioning_report = LaunchConfiguration("commissioning_report")

    return LaunchDescription([
        DeclareLaunchArgument("safe_region_csv"),
        DeclareLaunchArgument("serial_port", default_value="/dev/ttyACM0"),
        DeclareLaunchArgument("start_pico_debug", default_value="true"),
        DeclareLaunchArgument(
            "profile_file",
            default_value=str(package / "config" / "pick_profiles.yaml"),
        ),
        DeclareLaunchArgument(
            "commissioning_report",
            default_value=str(
                Path.home()
                / "MacRobot"
                / "data"
                / "commissioning"
                / "arm_commissioning_report.yaml"
            ),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(arm_control / "launch" / "arm_pipeline.launch.py")
            ),
            launch_arguments={
                "dry_run": "false",
                "require_safe_region": "true",
                "safe_region_csv": safe_region_csv,
                "command_home_on_start": "false",
                "start_rviz": "false",
            }.items(),
        ),
        Node(
            package="pico_debug",
            executable="pico_debug_node",
            name="pico_debug_node",
            output="screen",
            condition=IfCondition(start_pico_debug),
            parameters=[{
                "serial_port": serial_port,
                "interactive": False,
                "auto_reconnect": True,
            }],
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="detection_localizer_node",
            name="macrobot_detection_localizer",
            output="screen",
            parameters=[str(package / "config" / "perception.yaml")],
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="pick_coordinator_node",
            name="macrobot_pick_coordinator",
            output="screen",
            parameters=[
                str(package / "config" / "coordinator.yaml"),
                {
                    "use_finder": True,
                    "profile_file": profile_file,
                    "commissioning_report": commissioning_report,
                },
            ],
        ),
    ])
