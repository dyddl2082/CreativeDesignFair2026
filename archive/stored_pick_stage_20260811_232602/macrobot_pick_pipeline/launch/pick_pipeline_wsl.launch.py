from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    package = Path(get_package_share_directory("macrobot_pick_pipeline"))
    arm_control = Path(get_package_share_directory("macrobot_arm_control"))

    use_mock = LaunchConfiguration("use_mock_perception")
    use_finder = LaunchConfiguration("use_finder")
    start_rviz = LaunchConfiguration("start_rviz")
    start_arm_pipeline = LaunchConfiguration("start_arm_pipeline")
    require_safe_region = LaunchConfiguration("require_safe_region")
    safe_region_csv = LaunchConfiguration("safe_region_csv")
    profile_file = LaunchConfiguration("profile_file")
    commissioning_report = LaunchConfiguration("commissioning_report")

    return LaunchDescription([
        DeclareLaunchArgument("use_mock_perception", default_value="true"),
        DeclareLaunchArgument("use_finder", default_value="false"),
        DeclareLaunchArgument("start_rviz", default_value="true"),
        DeclareLaunchArgument("start_arm_pipeline", default_value="true"),
        DeclareLaunchArgument("require_safe_region", default_value="false"),
        DeclareLaunchArgument("safe_region_csv", default_value=""),
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
            condition=IfCondition(start_arm_pipeline),
            launch_arguments={
                "dry_run": "true",
                "require_safe_region": require_safe_region,
                "safe_region_csv": safe_region_csv,
                "command_home_on_start": "false",
                "start_rviz": "false",
            }.items(),
        ),

        Node(
            package="macrobot_pick_pipeline",
            executable="mock_perception_node",
            name="macrobot_mock_perception",
            output="screen",
            condition=IfCondition(use_mock),
            parameters=[str(package / "config" / "mock_perception.yaml")],
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="detection_localizer_node",
            name="macrobot_detection_localizer",
            output="screen",
            condition=UnlessCondition(use_mock),
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
                    "use_finder": ParameterValue(use_finder, value_type=bool),
                    "profile_file": profile_file,
                    "commissioning_report": commissioning_report,
                },
            ],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2_pick_pipeline",
            output="screen",
            arguments=["-d", str(package / "rviz" / "pick_pipeline.rviz")],
            condition=IfCondition(start_rviz),
        ),
    ])
