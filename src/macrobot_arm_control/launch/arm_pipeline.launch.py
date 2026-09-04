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
    command_home_on_start = LaunchConfiguration("command_home_on_start")
    use_sim_time = LaunchConfiguration("use_sim_time")
    start_rviz = LaunchConfiguration("start_rviz")

    actuator_file = safe_pkg / "config" / "actuator_limits.yaml"
    control_defaults = control_pkg / "config" / "control_defaults.yaml"
    kinematics_file = description_pkg / "config" / "kinematics.yaml"

    return LaunchDescription([
        DeclareLaunchArgument("dry_run", default_value="true"),
        DeclareLaunchArgument("require_safe_region", default_value="true"),
        DeclareLaunchArgument("safe_region_csv", default_value=""),
        DeclareLaunchArgument("command_home_on_start", default_value="false"),
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        DeclareLaunchArgument("start_rviz", default_value="false"),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(description_pkg / "launch" / "runtime_description.launch.py")
            ),
            launch_arguments={"use_sim_time": use_sim_time}.items(),
        ),
        Node(
            package="macrobot_arm_kinematics",
            executable="linkage_state_node",
            name="macrobot_serial2r_state_node",
            output="screen",
            parameters=[str(kinematics_file), {"use_sim_time": use_sim_time}],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["-d", str(description_pkg / "rviz" / "display.rviz")],
            condition=IfCondition(start_rviz),
            output="screen",
        ),
        Node(
            package="macrobot_arm_control",
            executable="ik_validator_node",
            name="macrobot_ik_validator",
            output="screen",
            parameters=[
                str(control_defaults),
                {
                    "actuator_limits_file": str(actuator_file),
                    "safe_region_csv": safe_region_csv,
                    "require_safe_region": ParameterValue(
                        require_safe_region, value_type=bool
                    ),
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
                    "actuator_limits_file": str(actuator_file),
                    "safe_region_csv": safe_region_csv,
                    "require_safe_region": ParameterValue(
                        require_safe_region, value_type=bool
                    ),
                    "dry_run": ParameterValue(dry_run, value_type=bool),
                    "command_home_on_start": ParameterValue(
                        command_home_on_start, value_type=bool
                    ),
                },
            ],
        ),
    ])
