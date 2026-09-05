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
    object_memory_file = LaunchConfiguration("object_memory_file")
    dry_run_base = LaunchConfiguration("dry_run_base")
    task_executable = LaunchConfiguration("task_executable")
    start_visible_pick_test = LaunchConfiguration("start_visible_pick_test")
    start_depth_clearance = LaunchConfiguration("start_depth_clearance")
    aligned_depth_topic = LaunchConfiguration("aligned_depth_topic")

    return LaunchDescription([
        DeclareLaunchArgument(
            "profile_file",
            default_value=str(
                Path.home() / "MacRobot" / "data" / "stored_objects" / "runtime_profiles.yaml"
            ),
        ),
        DeclareLaunchArgument(
            "recordings_dir",
            default_value=str(Path.home() / "MacRobot" / "data" / "arm_primitives"),
        ),
        DeclareLaunchArgument(
            "object_memory_file",
            default_value=str(Path.home() / "MacRobot" / "data" / "object_memory" / "memory.yaml"),
        ),
        DeclareLaunchArgument(
            "task_executable",
            default_value="resilient_object_task_node",
            description="Use stored_object_pick_node only for legacy rollback.",
        ),
        DeclareLaunchArgument("dry_run_base", default_value="false"),
        DeclareLaunchArgument("start_visible_pick_test", default_value="false"),
        DeclareLaunchArgument("start_depth_clearance", default_value="true"),
        DeclareLaunchArgument(
            "aligned_depth_topic",
            default_value="/camera/camera/aligned_depth_to_color/image_raw",
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="depth_clearance_node",
            name="macrobot_depth_clearance",
            output="screen",
            condition=IfCondition(start_depth_clearance),
            parameters=[
                str(share / "config" / "depth_clearance.yaml"),
                {"input_topic": aligned_depth_topic},
            ],
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable=task_executable,
            name="macrobot_stored_object_pick",
            output="screen",
            parameters=[
                str(share / "config" / "stored_object_pick.yaml"),
                {
                    "profile_file": profile_file,
                    "recordings_dir": recordings_dir,
                    "object_memory_file": object_memory_file,
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
