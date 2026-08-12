from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    package = Path(get_package_share_directory("macrobot_pick_pipeline"))
    arm_control = Path(get_package_share_directory("macrobot_arm_control"))
    description = Path(get_package_share_directory("macrobot_description"))

    safe_region_csv = LaunchConfiguration("safe_region_csv")
    serial_port = LaunchConfiguration("serial_port")
    start_pico_debug = LaunchConfiguration("start_pico_debug")
    profile_file = LaunchConfiguration("profile_file")
    commissioning_report = LaunchConfiguration("commissioning_report")
    start_teach = LaunchConfiguration("start_teach")  # legacy alias for camera teach
    start_camera_teach = LaunchConfiguration("start_camera_teach")
    start_arm_demo_recorder = LaunchConfiguration("start_arm_demo_recorder")
    allow_teach_motion = LaunchConfiguration("allow_teach_motion")
    generated_profile_file = LaunchConfiguration("generated_profile_file")
    recordings_dir = LaunchConfiguration("recordings_dir")
    start_base_alignment = LaunchConfiguration("start_base_alignment")
    start_visible_pick_test = LaunchConfiguration("start_visible_pick_test")
    start_grasp_keyframes = LaunchConfiguration("start_grasp_keyframes")
    grasp_keyframe_profile_file = LaunchConfiguration("grasp_keyframe_profile_file")
    stored_object_profile_file = LaunchConfiguration("stored_object_profile_file")
    alignment_dry_run = LaunchConfiguration("alignment_dry_run")
    perception_input_mode = LaunchConfiguration("perception_input_mode")

    camera_teach_condition = IfCondition(
        PythonExpression([
            "'", start_camera_teach, "'.lower() == 'true' or '",
            start_teach, "'.lower() == 'true'",
        ])
    )

    return LaunchDescription([
        DeclareLaunchArgument("safe_region_csv"),
        DeclareLaunchArgument("serial_port", default_value="/dev/ttyACM0"),
        DeclareLaunchArgument("start_pico_debug", default_value="true"),
        DeclareLaunchArgument("start_teach", default_value="false"),
        DeclareLaunchArgument("start_camera_teach", default_value="false"),
        DeclareLaunchArgument("start_arm_demo_recorder", default_value="true"),
        DeclareLaunchArgument("start_base_alignment", default_value="true"),
        DeclareLaunchArgument("start_visible_pick_test", default_value="true"),
        DeclareLaunchArgument("start_grasp_keyframes", default_value="true"),
        DeclareLaunchArgument("alignment_dry_run", default_value="false"),
        DeclareLaunchArgument("perception_input_mode", default_value="legacy"),
        DeclareLaunchArgument("allow_teach_motion", default_value="true"),
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
            "recordings_dir",
            default_value=str(Path.home() / "MacRobot" / "data" / "arm_primitives"),
        ),
        DeclareLaunchArgument(
            "grasp_keyframe_profile_file",
            default_value=str(
                Path.home() / "MacRobot" / "data" / "grasp_keyframes" / "profiles.yaml"
            ),
        ),
        DeclareLaunchArgument(
            "stored_object_profile_file",
            default_value=str(
                Path.home()
                / "MacRobot"
                / "data"
                / "stored_objects"
                / "runtime_profiles.yaml"
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
            parameters=[
                str(package / "config" / "perception.yaml"),
                {"input_mode": perception_input_mode},
            ],
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
        Node(
            package="macrobot_pick_pipeline",
            executable="grasp_keyframe_node",
            name="macrobot_grasp_keyframes",
            output="screen",
            condition=IfCondition(start_grasp_keyframes),
            parameters=[
                str(package / "config" / "grasp_keyframes.yaml"),
                {
                    "profile_file": grasp_keyframe_profile_file,
                    "safe_region_csv": safe_region_csv,
                    "require_safe_region_preflight": True,
                },
            ],
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="stored_object_pick_node",
            name="macrobot_stored_object_pick",
            output="screen",
            condition=IfCondition(start_base_alignment),
            parameters=[
                str(package / "config" / "stored_object_pick.yaml"),
                {
                    "profile_file": stored_object_profile_file,
                    "recordings_dir": recordings_dir,
                    "grasp_keyframe_profile_file": grasp_keyframe_profile_file,
                    "dry_run_base": ParameterValue(
                        alignment_dry_run, value_type=bool
                    ),
                },
            ],
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="visible_pick_test_node",
            name="macrobot_visible_pick_test",
            output="screen",
            condition=IfCondition(start_visible_pick_test),
            parameters=[str(package / "config" / "stored_object_pick.yaml")],
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="arm_demo_recorder_node",
            name="macrobot_arm_demo_recorder",
            output="screen",
            condition=IfCondition(start_arm_demo_recorder),
            parameters=[
                str(package / "config" / "arm_demo.yaml"),
                {
                    "allow_motion_commands": ParameterValue(
                        allow_teach_motion, value_type=bool
                    ),
                    "report_path": commissioning_report,
                    "recordings_dir": recordings_dir,
                },
            ],
        ),
        Node(
            package="macrobot_pick_pipeline",
            executable="camera_teach_node",
            name="macrobot_camera_teach",
            output="screen",
            condition=camera_teach_condition,
            parameters=[
                str(package / "config" / "camera_teach.yaml"),
                {
                    "use_finder": True,
                    "allow_motion_commands": ParameterValue(
                        allow_teach_motion, value_type=bool
                    ),
                    "report_path": commissioning_report,
                    "generated_profile_file": generated_profile_file,
                    "kinematics_file": str(
                        description / "config" / "kinematics.yaml"
                    ),
                },
            ],
        ),
    ])
