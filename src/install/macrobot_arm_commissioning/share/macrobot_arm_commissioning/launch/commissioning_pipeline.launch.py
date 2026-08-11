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
    description_pkg = Path(get_package_share_directory("macrobot_description"))
    safe_pkg = Path(get_package_share_directory("macrobot_safe_region"))
    control_pkg = Path(get_package_share_directory("macrobot_arm_control"))

    dry_run = LaunchConfiguration("dry_run")
    require_safe_region = LaunchConfiguration("require_safe_region")
    safe_region_csv = LaunchConfiguration("safe_region_csv")
    actuator_limits_file = LaunchConfiguration("actuator_limits_file")
    start_rviz = LaunchConfiguration("start_rviz")
    start_pico_debug = LaunchConfiguration("start_pico_debug")
    serial_port = LaunchConfiguration("serial_port")

    default_actuator_file = safe_pkg / "config" / "actuator_limits.yaml"
    control_defaults = control_pkg / "config" / "control_defaults.yaml"

    return LaunchDescription([
        DeclareLaunchArgument("dry_run", default_value="true"),
        DeclareLaunchArgument("require_safe_region", default_value="true"),
        DeclareLaunchArgument("safe_region_csv", default_value=""),
        DeclareLaunchArgument(
            "actuator_limits_file",
            default_value=str(default_actuator_file),
        ),
        DeclareLaunchArgument("start_rviz", default_value="true"),
        DeclareLaunchArgument("start_pico_debug", default_value="false"),
        DeclareLaunchArgument("serial_port", default_value="/dev/ttyACM0"),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(description_pkg / "launch" / "display_full.launch.py")
            ),
            launch_arguments={
                "use_sim_time": "false",
                "auto_apply_ik": "false",
                "start_rviz": start_rviz,
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
                "send_stop_on_shutdown": True,
            }],
        ),

        Node(
            package="macrobot_arm_control",
            executable="ik_validator_node",
            name="macrobot_ik_validator",
            output="screen",
            parameters=[
                str(control_defaults),
                {
                    "actuator_limits_file": actuator_limits_file,
                    "safe_region_csv": safe_region_csv,
                    "require_safe_region": ParameterValue(
                        require_safe_region, value_type=bool
                    ),
                    "path_step_rad": 0.00872664626,
                },
            ],
        ),

        Node(
            package="macrobot_arm_control",
            executable="servo_bridge_node",
            name="macrobot_arm_servo_bridge",
            output="screen",
            parameters=[
                str(control_defaults),
                {
                    "actuator_limits_file": actuator_limits_file,
                    "safe_region_csv": safe_region_csv,
                    "require_safe_region": ParameterValue(
                        require_safe_region, value_type=bool
                    ),
                    "dry_run": ParameterValue(dry_run, value_type=bool),
                    "command_home_on_start": False,
                    "update_rate_hz": 20.0,
                    "q1_max_velocity": 0.08,
                    "q2_max_velocity": 0.08,
                    "q3_max_velocity": 0.12,
                    "minimum_duration_sec": 0.5,
                    "preempt_active_goal": False,
                },
            ],
        ),
    ])
