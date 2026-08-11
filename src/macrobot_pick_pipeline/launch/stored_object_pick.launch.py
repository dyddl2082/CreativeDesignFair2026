from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = Path(get_package_share_directory("macrobot_pick_pipeline"))
    profile_file = LaunchConfiguration("profile_file")
    recordings_dir = LaunchConfiguration("recordings_dir")
    dry_run_base = LaunchConfiguration("dry_run_base")
    start_visible_pick_test = LaunchConfiguration("start_visible_pick_test")

    return LaunchDescription([
        DeclareLaunchArgument(
            "profile_file",
            default_value=str(
                Path.home()
                / "MacRobot"
                / "data"
                / "stored_objects"
                / "runtime_profiles.yaml"
            ),
        ),
        DeclareLaunchArgument(
            "recordings_dir",
            default_value=str(Path.home() / "MacRobot" / "data" / "arm_primitives"),
        ),
        DeclareLaunchArgument("dry_run_base", default_value="false"),
        DeclareLaunchArgument("start_visible_pick_test", default_value="true"),
        Node(
            package="macrobot_pick_pipeline",
            executable="stored_object_pick_node",
            name="macrobot_stored_object_pick",
            output="screen",
            parameters=[
                str(share / "config" / "stored_object_pick.yaml"),
                {
                    "profile_file": profile_file,
                    "recordings_dir": recordings_dir,
                    "dry_run_base": ParameterValue(dry_run_base, value_type=bool),
                },
            ],
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="visible_pick_test_node",
            name="macrobot_visible_pick_test",
            output="screen",
            condition=IfCondition(start_visible_pick_test),
            parameters=[str(share / "config" / "stored_object_pick.yaml")],
        ),
    ])
